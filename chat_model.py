"""Configuration and model construction for the Foundry-hosted chat deployment."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

DEFAULT_API_VERSION = "2025-04-01-preview"


@dataclass(frozen=True)
class Settings:
    endpoint: str | None
    api_key: str | None
    deployment: str | None
    api_version: str

    def missing(self) -> list[str]:
        required = {
            "AZURE_OPENAI_ENDPOINT": self.endpoint,
            "AZURE_OPENAI_DEPLOYMENT": self.deployment,
        }
        return [name for name, value in required.items() if not value]


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION),
    )


def build_chat_model(settings: Settings) -> AzureChatOpenAI:
    """Use the API key when provided, otherwise fall back to Microsoft Entra ID (az login)."""
    # No temperature / max_tokens: gpt-5 family reasoning models only accept defaults.
    common = dict(
        azure_endpoint=settings.endpoint,
        azure_deployment=settings.deployment,
        api_version=settings.api_version,
        streaming=True,
    )
    if settings.api_key:
        return AzureChatOpenAI(api_key=settings.api_key, **common)

    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    return AzureChatOpenAI(azure_ad_token_provider=token_provider, **common)
