# File: autobyteus_server/workflow/steps/subtask_implementation/subtask_implementation_step.py

import os
import base64
from PIL import Image
import pytesseract
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.agent.agent import StandaloneAgent
from autobyteus.llm.models import LLMModel
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.llm_factory import LLMFactory
from typing import List, Optional, Dict
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
        super().process_requirement(requirement, context_file_paths, llm_model)
        context = self._construct_context(context_file_paths)

        if not self.agent:
            # This is the beginning of a new conversation
            llm_factory = LLMFactory()
            llm = llm_factory.create_llm(llm_model)
            initial_prompt = self.construct_initial_prompt(requirement, context, llm_model)
            self.agent = self._create_agent(llm, initial_prompt)
            self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.response_queue = asyncio.Queue()
            self.agent.start()
        else:
            # This is a continuation of an existing conversation
            prompt = self.construct_subsequent_prompt(requirement, context)
            await self.agent.receive_user_message(prompt)

    def stop_agent(self):
        if self.agent:
            self.unsubscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, self.agent.agent_id)
            self.agent.stop()
            self.agent = None

    def _construct_context(self, context_file_paths: List[Dict[str, str]]) -> str:
        context = ""
        for file in context_file_paths:
            path = file['path']
            file_type = file['type']
            if file_type.startswith('image/'):
                try:
                    # Open the image file
                    with Image.open(path) as img:
                        # Convert image to Base64
                        buffered = io.BytesIO()
                        img.save(buffered, format=img.format)
                        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    
                    # Append to context
                    context += f"Image: {path}\n"
                    context += f"data:{file_type};base64,{img_str}\n\n"
                except Exception as e:
                    context += f"Error processing image {path}: {str(e)}\n\n"
            elif file_type.startswith('video/'):
                context += f"Video: {path}\n"
                # Optionally, extract metadata or descriptions
            elif file_type in ['application/pdf', 'text/plain', 'application/json', 'text/markdown']:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context += f"File: {path}\n{content}\n\n"
                except Exception as e:
                    context += f"Error reading file {path}: {str(e)}\n\n"
            else:
                # Handle other file types or skip
                context += f"File: {path} (Type: {file_type})\n"
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
