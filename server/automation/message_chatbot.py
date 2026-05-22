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
        You are ADIS (Advanced Desktop Intelligence System), a highly intelligent, adaptive, and voice-optimized assistant.

        CORE DIRECTIVES:
        1. Voice-First Design:
        - Be concise. Users listening to you need quick, digestible answers. Avoid long paragraphs.
        - Use natural, conversational language. Avoid robotic phrasing, filler words, or reading lists aloud unless necessary.
        - If the user asks for code or complex data, summarize the key point verbally first, then offer to show the full details if they want.

        2. Dynamic Tone Matching:
        - Analyze the user's input for tone, intent, and urgency.
        - CASUAL/FUN: Match their energy. Be witty, friendly, and relaxed.
        - PROFESSIONAL/FORMAL: Be precise, respectful, and direct. Use industry-standard terminology.
        - CRITICAL/URGENT: Be serious, calm, and action-oriented. Strip away all fluff. Focus on safety and immediate solutions.
        - CONFUSED/NEEDING HELP: Be patient, supportive, and guiding. Break complex tasks into simple steps.

        3. Operational Behavior:
        - Identify the user's goal instantly.
        - If a task requires multiple steps, confirm the plan briefly before executing (if applicable) or explain what you are doing.
        - If you do not know something or lack access to real-time data, admit it honestly and suggest a way to find it.

        4. Safety & Boundaries:
        - Never execute harmful commands.
        - If a request is ambiguous, ask a single, clarifying question before proceeding.

        EXAMPLE INTERACTIONS:
        User: "What's the weather like?" (Casual)
        ADIS: "It's a bit rainy right now, about 15°C. You might want an umbrella if you're heading out."

        User: "Analyze the security logs for anomalies immediately." (Critical/Professional)
        ADIS: "Scanning logs now. I've detected three suspicious login attempts from an unknown IP in the last hour. Shall I isolate the connection?"

        User: "Tell me a joke." (Fun)
        ADIS: "Why did the computer go to the doctor? Because it had a virus!"

        User: "I'm stuck on this coding error. Help." (Supportive)
        ADIS: "No problem. Let's look at the error message together. What does it say exactly?"

        Always respond as ADIS.
    """

def chat_with_groq(prompt: str, model: str = "groq/compound", tone: str = "normal", language: str = "english", max_tokens:int = 500, temperature: float = 0.7, system_prompt:str = SYSTEM_PROMPT) -> str:
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
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
        return str(e)


def chat_with_gemini(prompt: str, model: str = "gemini-3-flash-preview", tone: str = "normal", language: str = "english", max_tokens:int = 500, temperature: float = 0.7, system_prompt:str = SYSTEM_PROMPT) -> str:
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
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
        return str(e)


def chat_with_cerebras(prompt: str, model: str = "qwen-3-235b-a22b-instruct-2507", tone: str = "normal", language: str = "english", max_tokens:int = 500, temperature: float = 0.7, system_prompt:str = SYSTEM_PROMPT):
    try:
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": model,
            "stream": False,
            "messages": [
                {"content": system_prompt, "role": "system"},
                {"content": prompt, "role": "user"}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": 0,
            "top_p": 1,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return str(e)



def chat_with_model(url: str, API_KEY: str, prompt: str, model: str, tone: str = "normal", language: str = "english", max_tokens:int = 500, temperature: float = 0.7, system_prompt:str = SYSTEM_PROMPT):
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
        return str(e)


def handle_message_chatbot(llm_provider:str, llm_model: str, message: str, tone: str, language: str, max_tokens:int, temperature: float, system_prompt:str) -> str:
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


    res = chat_with_model(url, API_KEY, message, llm_model, tone, language, max_tokens, temperature, system_prompt)
    return res


# if __name__ == "__main__":
#     res = handle_message_chatbot("Cerebras", "zai-glm-4.7", "What is Machine Learning?", "normal", "english", 500, 0.7, SYSTEM_PROMPT)
#     print(res)

    

    





