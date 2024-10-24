import os
import asyncio
from typing import List, Optional, Dict, Tuple
import uuid
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus.events.event_types import EventType
from autobyteus.conversation.user_message import UserMessage

class UXDesignStep(BaseStep):
    name = "ux_design"

    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)
        self.tools = []  # Add UX design specific tools as needed
        self.agent: Optional[StandaloneAgent] = None
        self.response_queue: Optional[asyncio.Queue] = None
        
    def init_response_queue(self):
        if self.response_queue is None:
            self.response_queue = asyncio.Queue()

    def construct_initial_prompt(self, requirement: str, context: str, llm_model: str) -> str:
        prompt_template = self.get_prompt_template(llm_model)
        return prompt_template.fill({
            "requirement": requirement,
            "context": context
        })

    def construct_subsequent_prompt(self, requirement: str, context: str) -> str:
        prompt = ""
        if context:
            prompt += f"[Context]\n{context}\n\n"
        prompt += f"{requirement}"
        return prompt

    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[Dict[str, str]],
        llm_model: Optional[str]
    ) -> None:
        context, image_file_paths = self._construct_context(context_file_paths)

        if llm_model:
            self.init_response_queue()
            await self.clear_response_queue()
            llm_instance = LLMFactory.create_llm(llm_model)
            initial_prompt = self.construct_initial_prompt(requirement, context, llm_model)
            initial_user_message = UserMessage(content=initial_prompt, file_paths=image_file_paths)
            self.agent = self._create_agent(llm_instance, initial_user_message)
            self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.agent.start()
            user_message = initial_user_message
        else:
            prompt = self.construct_subsequent_prompt(requirement, context)
            user_message = UserMessage(content=prompt, file_paths=image_file_paths)
            await self.agent.receive_user_message(user_message)

    async def clear_response_queue(self):
        self.init_response_queue()
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    def _construct_context(self, context_file_paths: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        context = ""
        image_file_paths = []
        root_path = self.workflow.workspace.root_path
        for file in context_file_paths:
            path = file['path']
            file_type = file['type']
            full_path = os.path.join(root_path, path)

            if file_type == 'image':
                image_file_paths.append(full_path)
            elif file_type == 'text':
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context += f"File: {path}\n{content}\n\n"
            else:
                raise ValueError(f"Unsupported file type: {file_type} for file: {path}")

        return context, image_file_paths

    def _create_agent(self, llm: BaseLLM, initial_user_message: UserMessage) -> StandaloneAgent:
        agent_id = f"ux_design_{uuid.uuid4()}"
        return StandaloneAgent(
            role="UX_Design",
            llm=llm,
            tools=self.tools,
            use_xml_parser=True,
            agent_id=agent_id,
            initial_user_message=initial_user_message
        )

    def on_assistant_response(self, *args, **kwargs):
        response = kwargs.get('response')
        if response:
            self.init_response_queue()
            asyncio.create_task(self.response_queue.put(response))

    async def get_latest_response(self, timeout: float = 30.0) -> Optional[str]:
        self.init_response_queue()
        try:
            return await asyncio.wait_for(self.response_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def stop_agent(self):
        if self.agent:
            self.unsubscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.agent.stop()
            self.agent = None