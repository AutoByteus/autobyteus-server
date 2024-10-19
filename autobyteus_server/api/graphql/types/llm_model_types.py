import strawberry
from enum import Enum
from autobyteus.llm.llm_factory import LLMFactory

def create_llm_model_enum():
    models = LLMFactory.get_all_models()
    # Ensure unique and valid Enum member names
    enum_members = {}
    for model in models:
        # Replace invalid characters and convert to uppercase
        member_name = model.upper().replace('-', '_').replace('.', '_').replace(':', '_')
        # Handle duplicates by appending a unique identifier if necessary
        original_member_name = member_name
        counter = 1
        while member_name in enum_members:
            member_name = f"{original_member_name}_{counter}"
            counter += 1
        enum_members[member_name] = model
    return Enum('DynamicLLMModelEnum', enum_members)

DynamicLLMModelEnum = create_llm_model_enum()

# Directly use the dynamic enum with Strawberry without subclassing
LLMModel = strawberry.enum(DynamicLLMModelEnum, name="LLMModel")