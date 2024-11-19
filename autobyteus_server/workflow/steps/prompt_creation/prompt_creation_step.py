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
from autobyteus_server.workflow.persistence.conversation.domain.models import Message as PersistenceMessage
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation
from autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy import PersistenceProxy

class PromptCreationStep(BaseStep):
    name = "prompt_creation"

    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)
        self.tools = []  # Add more tools as needed
        self.agents: Dict[str, StandaloneAgent] = {}  # Handle multiple agents
        self.response_queues: Dict[str, asyncio.Queue] = {}  # Queues per conversation

    def init_response_queue(self, conversation_id: str):
        if conversation_id not in self.response_queues:
            self.response_queues[conversation_id] = asyncio.Queue()

    def construct_initial_prompt(self, prompt_request: str, context: str, llm_model: str) -> str:
        prompt_template = self.get_prompt_template(llm_model)
        return prompt_template.fill({
            "prompt_request": prompt_request,
            "context": context
        })

    def construct_subsequent_prompt(self, prompt_request: str, context: str) -> str:
        prompt = ""
        if context:
            prompt += f"[Context]\n{context}\n\n"
        prompt += f"{prompt_request}"
        return prompt

    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[Dict[str, str]],  # List of dicts with 'path' and 'type'
        llm_model: Optional[str],
        conversation_id: Optional[str] = None  # New parameter
    ) -> str:
        context, image_file_paths = self._construct_context(context_file_paths)

        if not conversation_id:
            # This is the beginning of a new conversation
            llm_instance = LLMFactory.create_llm(llm_model)
            initial_prompt = self.construct_initial_prompt(requirement, context, llm_model)
            user_message = UserMessage(content=initial_prompt, file_paths=image_file_paths)
            new_conversation = self.persistence_proxy.store_message(
                step_name=self.name,
                role='user',
                message=initial_prompt,
                original_message=requirement,
                context_paths=[file['path'] for file in context_file_paths]
            )
            conversation_id = new_conversation.step_conversation_id

            self.init_response_queue(conversation_id)
            await self.clear_response_queue(conversation_id)
            agent = self._create_agent(llm_instance, user_message, conversation_id)
            self.agents[conversation_id] = agent
            self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, agent.agent_id)
            agent.start()

            return conversation_id
        else:
            # This is a continuation of an existing conversation
            if conversation_id not in self.agents:
                llm_instance = LLMFactory.create_llm(llm_model)
                agent = self._create_agent(llm_instance, UserMessage(content="", file_paths=[]), conversation_id)
                self.agents[conversation_id] = agent
                self.subscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, agent.agent_id)
                agent.start()

            prompt = self.construct_subsequent_prompt(requirement, context)
            user_message = UserMessage(content=prompt, file_paths=image_file_paths)
            await self.agents[conversation_id].receive_user_message(user_message)

            updated_conversation = self.persistence_proxy.store_message(
                step_name=self.name,
                role='user',
                message=prompt,
                original_message=requirement,
                context_paths=[file['path'] for file in context_file_paths],
                conversation_id=conversation_id
            )

            return conversation_id

    async def clear_response_queue(self, conversation_id: str):
        self.init_response_queue(conversation_id)
        queue = self.response_queues[conversation_id]
        while not queue.empty():
            try:
                queue.get_nowait()
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

    def _create_agent(self, llm: BaseLLM, initial_user_message: UserMessage, conversation_id: str) -> StandaloneAgent:
        agent_id = f"prompt_creation_{uuid.uuid4()}"
        return StandaloneAgent(
            role=self.name,
            llm=llm,
            tools=self.tools,
            use_xml_parser=True,
            agent_id=agent_id,
            initial_user_message=initial_user_message,
        )

    def on_assistant_response(self, *args, **kwargs):
        response = kwargs.get('response')
        agent_id = kwargs.get('agent_id')
        if response and agent_id:
            conversation_id = None
            for cid, agent in self.agents.items():
                if agent.agent_id == agent_id:
                    conversation_id = cid
                    break
            if conversation_id:
                self.init_response_queue(conversation_id)
                asyncio.create_task(self.response_queues[conversation_id].put(response))

                self.persistence_proxy.store_message(
                    step_name=self.name,
                    role='assistant',
                    message=response,
                    original_message=None,
                    context_paths=None,
                    conversation_id=conversation_id
                )

    async def get_latest_response(self, conversation_id: str, timeout: float = 30.0) -> Optional[str]:
        self.init_response_queue(conversation_id)
        try:
            return await asyncio.wait_for(self.response_queues[conversation_id].get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def stop_agent(self, conversation_id: str):
        if conversation_id in self.agents:
            agent = self.agents[conversation_id]
            self.unsubscribe(EventType.ASSISTANT_RESPONSE, self.on_assistant_response, agent.agent_id)
            agent.stop()
            del self.agents[conversation_id]
            del self.response_queues[conversation_id]

    def close_conversation(self, conversation_id: str) -> None:
        if conversation_id not in self.agents:
            raise ValueError(f"No active conversation found with ID: {conversation_id}")
            
        try:
            self.stop_agent(conversation_id)
        except Exception as e:
            raise Exception(f"Failed to close conversation {conversation_id}: {str(e)}")