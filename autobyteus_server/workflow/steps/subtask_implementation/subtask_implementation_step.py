# File: autobyteus_server/workflow/steps/subtask_implementation/subtask_implementation_step.py

import os
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.models import LLMModel
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.llm_factory import LLMFactory
from typing import List, Optional, Dict, Tuple
from autobyteus.events.event_types import EventType
import asyncio
from autobyteus.conversation.user_message import UserMessage

class SubtaskImplementationStep(BaseStep):
    name = "implementation"

    def __init__(self, workflow):
        super().__init__(workflow)
        self.tools = []  # Add more tools as needed
        self.agent: Optional[StandaloneAgent] = None
        self.response_queue = None

        # Read the prompt templates
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        self.load_prompt_templates(prompt_dir)

    def construct_initial_prompt(self, requirement: str, context: str, llm_model: LLMModel) -> str:
        prompt_template = self.get_prompt_template(llm_model)
        return prompt_template.fill({
            "requirement": requirement,
            "context": context
        })

    def construct_subsequent_prompt(self, requirement: str, context: str) -> str:
        prompt = ""
        if context:
            prompt += f"[Context]\n{context}\n\n"
        prompt += f"[UserFeedback]\n{requirement}"
        return prompt

    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[Dict[str, str]],  # List of dicts with 'path' and 'type'
        llm_model: LLMModel
    ) -> None:
        context, image_file_paths = self._construct_context(context_file_paths)

        if not self.agent:
            # This is the beginning of a new conversation
            llm_factory = LLMFactory()
            llm = llm_factory.create_llm(llm_model)
            initial_prompt = self.construct_initial_prompt(requirement, context, llm_model)
            initial_user_message = UserMessage(content=initial_prompt, file_paths=image_file_paths)
            self.agent = self._create_agent(llm, initial_user_message)
            self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.response_queue = asyncio.Queue()
            self.agent.start()
            user_message = initial_user_message
        else:
            # This is a continuation of an existing conversation
            prompt = self.construct_subsequent_prompt(requirement, context)
            user_message = UserMessage(content=prompt, file_paths=image_file_paths)
            await self.agent.receive_user_message(user_message)

    def _construct_context(self, context_file_paths: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        context = ""
        image_file_paths = []
        for file in context_file_paths:
            path = file['path']
            file_type = file['type']
            
            if file_type == 'image':
                image_file_paths.append(path)
            elif file_type == 'text':
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context += f"File: {path}\n{content}\n\n"
            else:
                raise ValueError(f"Unsupported file type: {file_type} for file: {path}")
        
        return context, image_file_paths

    def _create_agent(self, llm: BaseLLM, initial_user_message: UserMessage) -> StandaloneAgent:
        agent_id = f"subtask_implementation_{id(self)}"
        return StandaloneAgent(
            role="Subtask_Implementation",
            llm=llm,
            tools=self.tools,
            use_xml_parser=True,
            agent_id=agent_id,
            initial_user_message=initial_user_message
        )

    def on_assistant_response(self, *args, **kwargs):
        response = kwargs.get('response')
        if response:
            asyncio.create_task(self.response_queue.put(response))

    async def get_latest_response(self) -> Optional[str]:
        return await self.response_queue.get()

    def stop_agent(self):
        if self.agent:
            self.unsubscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.agent.stop()
            self.agent = None