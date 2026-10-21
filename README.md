# foundry-langchain-chat

A local chatbot built with Streamlit and LangChain, backed by a model deployed in Azure AI Foundry (Azure OpenAI). Responses stream token by token and the conversation is kept in session state.

## Architecture

```
Streamlit UI (app.py)  ->  LangChain AzureChatOpenAI (chat_model.py)  ->  Azure AI Foundry deployment
```

- `app.py` – chat UI, history handling, streaming render
- `chat_model.py` – env-based settings and model construction (API key, or Entra ID via `az login` when no key is set)

## Setup

1. In Azure AI Foundry, deploy a chat model (e.g. `gpt-5-nano`) and note the endpoint, key and deployment name.
2. Install and configure:

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # macOS/Linux: cp .env.example .env
```

3. Fill in `.env`, then run:

```bash
streamlit run app.py
```

## Notes

- `AZURE_OPENAI_DEPLOYMENT` is the *deployment name*, which may differ from the model name; it must not contain spaces.
- Reasoning models (gpt-5 family) reject custom `temperature` and `max_tokens`, so the app uses model defaults.
- `.env` is git-ignored; never commit keys.
