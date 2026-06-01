from numpy.random.mtrand import random
import requests
import os
import json
from config.config import GROQ_API_KEY, GEMINI_API_KEY, CEREBRAS_API_KEY

ProvidersAndModels = {
    "Groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b", "openai/gpt-oss-120b"],
    "Cerebras": ["gpt-oss-120b", "llama3.1-8b", "qwen-3-235b-a22b-instruct-2507", "zai-glm-4.7"],
    "Google Gemini": ["gemini-2.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
}

SYSTEM_PROMPT = """
You are ADIS (Advance Desktop Intelligence System), a voice-first assistant.

- Be concise and conversational.
- Speak in short, clear responses.
- Match user tone: casual, formal, urgent, or supportive.
- Identify intent and give the best simple answer.
- If you don't know, say so and suggest next steps.
- Never do harm.
"""


def chat_with_model(prompt: str, url: str, API_KEY: str, model: str, tone: str = "normal", language: str = "english", max_tokens:int = 1024, temperature: float = 0.7, system_prompt:str = SYSTEM_PROMPT):
    try:
        headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        fallback_model = None
        for provider, models in ProvidersAndModels.items():
            if model in models:
                available_models = [m for m in models if m != model]
                if available_models:
                    fallback_model = random.choice(available_models)
                break
        
        if fallback_model:
            try:
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                }
                retry_data = {
                    "model": fallback_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
                response = requests.post(url, headers=headers, data=json.dumps(retry_data))
                response.raise_for_status()
                res_data = response.json()
                return res_data['choices'][0]['message']['content']
            except Exception as e2:
                return str(e2)
        return str(e)


def handle_message_chatbot(query: str, llm_provider:str = 'groq', llm_model: str = 'llama-3.3-70b-versatile',  tone: str = 'formal', language: str = 'english', max_tokens:int = 1024, temperature: float = 0.7, system_prompt:str = SYSTEM_PROMPT) -> str:
    """Handle messages to different llms with their name, model, etc."""

    provider = (llm_provider or "").strip().lower()
    url = "https://api.groq.com/openai/v1/chat/completions"
    API_KEY = GROQ_API_KEY
    match provider:
        case "gemini" | "google gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            API_KEY = GEMINI_API_KEY
        case "cerebras":
            url = "https://api.cerebras.ai/v1/chat/completions"
            API_KEY = CEREBRAS_API_KEY


    res = chat_with_model(query, url, API_KEY, llm_model, tone, language, max_tokens, temperature, system_prompt)
    return res


# if __name__ == "__main__":
# res = handle_message_chatbot("What is Machine Learning?", "groq", "llama-3.3-70b-versatile",  "normal", "english", 1024, 0.7)
# print(res)

    

    





