import strawberry
from typing import List
from autobyteus.llm.models import Provider, LLMModel

@strawberry.type
class Model:
    name: str
    value: str

@strawberry.type
class ProviderModels:
    provider: str
    models: List[Model]

@strawberry.type
class Query:
    @strawberry.field
    def get_models_by_provider(self) -> List[ProviderModels]:
        """
        Retrieve all LLM models grouped by their providers.

        Returns:
            List[ProviderModels]: A list of providers each containing their respective models.
        """
        provider_dict = {}
        for model in LLMModel:
            provider = model.provider.value
            if provider not in provider_dict:
                provider_dict[provider] = []
            provider_dict[provider].append(Model(name=model.name, value=model.value))
        
        return [ProviderModels(provider=prov, models=models) for prov, models in provider_dict.items()]