from autobyteus.prompt.prompt_builder import PromptBuilder
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.tools.base_tool import BaseTool
from typing import List, Optional
import os

class SubtaskImplementationStep(BaseStep):
    name = "implementation"

    def __init__(self, llm: BaseLLM, tools: List[BaseTool]):
        super().__init__()
        self.llm = llm
        self.tools = tools
        self.context_file_paths: Optional[List[str]] = None
        self.implementation_requirement: Optional[str] = None

    def construct_prompt(self) -> str:
        context = self._construct_context()
        prompt_builder = PromptBuilder.from_file("subtask_implementation.prompt")
        prompt = (prompt_builder
                  .set_variable_value("implementation_requirement", self.implementation_requirement)
                  .set_variable_value("context", context)
                  .build())
        return prompt

    def _construct_context(self) -> str:
        context = ""
        for path in self.context_file_paths:
            with open(path, 'r') as file:
                content = file.read()
                context += f"File: {path}\n{content}\n\n"
        return context

    async def execute(self, context_file_paths: List[str], implementation_requirement: str) -> str:
        self.context_file_paths = context_file_paths
        self.implementation_requirement = implementation_requirement

        agent = self._create_agent()
        await agent.run()
        return agent.conversation.get_last_assistant_message()

    def _create_agent(self) -> StandaloneAgent:
        agent_id = f"subtask_implementation_{id(self)}"
        initial_prompt = self.construct_prompt()

        return StandaloneAgent(
            role="Subtask_Implementation",
            llm=self.llm,
            tools=self.tools,
            use_xml_parser=True,
            agent_id=agent_id,
            initial_prompt=initial_prompt
        )
