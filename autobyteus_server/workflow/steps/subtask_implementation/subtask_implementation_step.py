from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.models import LLMModel
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus.tools.base_tool import BaseTool
from autobyteus.prompt.prompt_builder import PromptBuilder
from typing import List, Optional

class SubtaskImplementationStep(BaseStep):
    name = "implementation"

    def __init__(self, workflow):
        super().__init__(workflow)
        self.tools = [FileTool()]  # Add more tools as needed
        self.agent: Optional[StandaloneAgent] = None

    def _construct_context(self, context_file_paths: List[str]) -> str:
        context = ""
        for path in context_file_paths:
            with open(path, 'r') as file:
                content = file.read()
                context += f"File: {path}\n{content}\n\n"
        return context

    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        prompt_builder = PromptBuilder.from_file("subtask_implementation.prompt")
        prompt = (prompt_builder
                  .set_variable_value("implementation_requirement", requirement)
                  .set_variable_value("context", context)
                  .build())
        return prompt

    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str], 
        llm_model: Optional[LLMModel] = None
    ) -> str:
        if llm_model and not self.agent:
            # This is the initial call
            llm_factory = LLMFactory()
            llm = llm_factory.create_llm(llm_model)
            context = self._construct_context(context_file_paths)
            initial_prompt = self.construct_initial_prompt(requirement, context)
            self.agent = self._create_agent(llm, initial_prompt)
            self.agent.start()
            return self.agent.conversation.get_last_assistant_message()

        if not self.agent:
            raise ValueError("Agent not initialized. Provide LLM model for the initial call.")

        # For subsequent calls
        context = self._construct_context(context_file_paths)
        prompt = self.construct_initial_prompt(requirement, context)
        await self.agent.receive_user_message(prompt)
        return self.agent.conversation.get_last_assistant_message()

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
