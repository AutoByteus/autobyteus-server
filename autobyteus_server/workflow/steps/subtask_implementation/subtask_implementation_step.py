import os
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.models import LLMModel
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.llm_factory import LLMFactory
from typing import List, Optional
from autobyteus.events.event_types import EventType
import asyncio

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

    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        prompt_template = self.get_prompt_template(self.llm_model)
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
        context_file_paths: List[str],
        llm_model: Optional[LLMModel] = None
    ) -> None:
        context = self._construct_context(context_file_paths)

        if llm_model:
            # This is the beginning of a new conversation
            if self.agent:
                self.stop_agent()
            
            llm_factory = LLMFactory()
            llm = llm_factory.create_llm(llm_model)
            initial_prompt = self.construct_initial_prompt(requirement, context)
            self.agent = self._create_agent(llm, initial_prompt)
            self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.response_queue = asyncio.Queue()
            self.agent.start()
        else:
            # This is a continuation of an existing conversation
            if not self.agent:
                raise ValueError("No existing agent found for continuation. Please provide an LLM model to start a new conversation.")
            
            prompt = self.construct_subsequent_prompt(requirement, context)
            await self.agent.receive_user_message(prompt)

    def stop_agent(self):
        if self.agent:
            self.unsubscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.agent.stop()
            self.agent = None

    def _construct_context(self, context_file_paths: List[str]) -> str:
        context = ""
        for path in context_file_paths:
            with open(path, 'r') as file:
                content = file.read()
                context += f"File: {path}\n{content}\n\n"
        return context

    def on_assistant_response(self, *args, **kwargs):
        response = kwargs.get('response')
        if response:
            asyncio.create_task(self.response_queue.put(response))

    async def get_latest_response(self) -> Optional[str]:
        return await self.response_queue.get()

    def _create_agent(self, llm: BaseLLM, initial_prompt: str) -> StandaloneAgent:
        agent_id = f"subtask_implementation_{id(self)}"
        return StandaloneAgent(
            role="Subtask_Implementation",
            llm=llm,
            tools=self.tools,
            use_xml_parser=True,
            agent_id=agent_id,
            initial_prompt=initial_prompt
        )