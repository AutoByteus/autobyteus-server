import os
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.models import LLMModel
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

        # Read the prompt template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompt", "subtask_implementation.prompt")
        self.read_prompt_template(prompt_path)

    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        return self.prompt_template.fill({
            "implementation_requirement": requirement,
            "context": context
        })

    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str]
    ) -> None:
        if not self.llm_model:
            raise ValueError("LLM model not configured for this step.")
        
        if not self.agent:
            context = self._construct_context(context_file_paths)
            initial_prompt = self.construct_initial_prompt(requirement, context)
            self.agent = self._create_agent(self.llm_model, initial_prompt)
            self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.response_queue = asyncio.Queue()
            self.agent.start()
        else:
            context = self._construct_context(context_file_paths)
            prompt = self.construct_initial_prompt(requirement, context)
            await self.agent.receive_user_message(prompt)

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
        if self.response_queue is None:
            return None
        try:
            return await asyncio.wait_for(self.response_queue.get(), timeout=60)
        except asyncio.TimeoutError:
            return None

    def _create_agent(self, llm_model: LLMModel, initial_prompt: str) -> StandaloneAgent:
        agent_id = f"subtask_implementation_{id(self)}"
        return StandaloneAgent(
            role="Subtask_Implementation",
            llm=llm_model,
            tools=self.tools,
            use_xml_parser=True,
            agent_id=agent_id,
            initial_prompt=initial_prompt
        )