from automation.message_chatbot import handle_message_chatbot
from fastapi import APIRouter, Response
from pydantic import BaseModel
import base64
from typing import Any
import random
from core.command_dispatcher import command_dispatcher
from voice.tts import synthesize_to_bytes
from voice.stt import listen_to_user, listen_to_user2

router = APIRouter()

class SpeakRequest(BaseModel):
    text: str

response_texts = {
    "open_app": {
        "default": [
            "Opening {app_name} now.",
            "Launching {app_name} for you.",
            "Starting {app_name} immediately."
        ],
        "settings": [
            "Opening Settings now.",
            "Launching the Settings app.",
            "Settings will open shortly."
        ],
        "notepad": [
            "Opening Notepad for you.",
            "Launching Notepad now.",
            "Notepad is opening."
        ],
        "visual studio code": [
            "Opening Visual Studio Code.",
            "Launching VS Code now.",
            "Starting Visual Studio Code for you."
        ],
        "code": [
            "Opening Visual Studio Code.",
            "Launching Code now.",
            "Starting your editor."
        ],
        "chrome": [
            "Opening Chrome now.",
            "Launching Google Chrome.",
            "Starting Chrome for you."
        ],
        "file explorer": [
            "Opening File Explorer.",
            "Launching the file manager.",
            "Showing your files now."
        ],
        "ms store": [
            "Opening the Microsoft Store.",
            "Launching the Store app.",
            "Starting Microsoft Store now."
        ]
    },
    "open_site": {
        "default": [
            "Opening {site_name} in your browser.",
            "Navigating to {site_name} now.",
            "Taking you to {site_name}."
        ],
        "youtube.com": [
            "Opening YouTube now.",
            "Taking you to YouTube.",
            "Loading YouTube in your browser."
        ],
        "google.com": [
            "Opening Google now.",
            "Searching Google in your browser.",
            "Loading Google for you."
        ],
        "github.com": [
            "Opening GitHub now.",
            "Navigating to GitHub.",
            "Loading GitHub in your browser."
        ],
        "netflix.com": [
            "Opening Netflix now.",
            "Taking you to Netflix.",
            "Loading Netflix for you."
        ],
        "reddit.com": [
            "Opening Reddit now.",
            "Taking you to Reddit.",
            "Loading Reddit in your browser."
        ],
        "shopify.com": [
            "Opening the website now.",
            "Loading the site for you.",
            "Navigating to the requested page."
        ]
    },
    "click_shortcut": {
        "default": [
            "Executing that shortcut now.",
            "Triggering the shortcut for you.",
            "Running the shortcut command."
        ],
        "settings": [
            "Opening Settings with the shortcut.",
            "Showing Settings now.",
            "Pressing the Settings shortcut."
        ],
        "notification_center": [
            "Opening the notification center.",
            "Showing notifications now.",
            "Toggling the notification panel."
        ],
        "reload": [
            "Reloading the page now.",
            "Refreshing the screen.",
            "Pressing reload."
        ],
        "switch": [
            "Switching windows now.",
            "Changing to the next window.",
            "Performing the switch command."
        ],
        "search": [
            "Opening search now.",
            "Activating the search bar.",
            "Showing Windows search."
        ],
        "file_explorer": [
            "Opening File Explorer.",
            "Showing your files now.",
            "Launching the file explorer."
        ],
        "desktop": [
            "Showing the desktop now.",
            "Minimizing to desktop.",
            "Taking you to the desktop."
        ],
        "run": [
            "Opening the Run dialog.",
            "Launching the Run box.",
            "Showing the Run window now."
        ],
        "lock": [
            "Locking the computer now.",
            "Securing the screen.",
            "Locking your device."
        ],
        "task_manager": [
            "Opening Task Manager.",
            "Showing the task manager now.",
            "Launching the process manager."
        ],
        "screenshot": [
            "Taking a screenshot now.",
            "Capturing the screen.",
            "Starting screen capture."
        ],
        "screen_recording": [
            "Starting screen recording now.",
            "Recording the screen.",
            "Beginning screen capture."
        ]
    },
    "get_current": {
        "time": [
            "Checking the current time for you.",
            "Here is the current time.",
            "Let me see what time it is now."
        ],
        "date": [
            "Checking today's date.",
            "Here is the current date.",
            "Let me see what day it is today."
        ],
        "weather": [
            "Checking the weather now.",
            "Here is the current weather update.",
            "Looking up today's weather."
        ],
        "ip": [
            "Checking your current IP address.",
            "Finding your IP now.",
            "Getting your public IP address."
        ],
        "default": [
            "Checking that information now.",
            "Retrieving the current data.",
            "Getting that information for you."
        ]
    },
    "quick_panel": {
        "check_os": [
            "Your operating system is ",
            "You are running ",
            "The current OS is "
        ],
        "toggle_bluetooth": [
            "Toggling Bluetooth now.",
            "Bluetooth state changed.",
            "Done, Bluetooth should be toggled."
        ],
        "toggle_wifi": [
            "Toggling Wi-Fi now.",
            "Wi-Fi state changed.",
            "Done, Wi-Fi should be toggled."
        ],
        "check_battery": [
            "Your battery level is ",
            "You have ",
            "Battery status: "
        ],
        "toggle_notification_center": [
            "Toggling the notification center now.",
            "Notification center state changed.",
            "Done, the notification center should be toggled."
        ],
        "change_brightness": [
            "Changing brightness now.",
            "Brightness level adjusted.",
            "Done, the brightness should be changed."
        ],
        "change_volume": [
            "Changing volume now.",
            "Volume level adjusted.",
            "Done, the volume should be changed."
        ]
    },
    "web_search": {
        "google": [
            "Searching Google for {query}.",
            "Looking up {query} on Google.",
            "Running a Google search for {query}."
        ],
        "youtube": [
            "Searching YouTube for {query}.",
            "Looking up {query} on YouTube.",
            "Opening YouTube search results for {query}."
        ],
        "ai": [
            "Running an AI search for {query}.",
            "Using AI to search for {query}.",
            "Looking up {query} with AI search."
        ],
        "default": [
            "Searching for {query} now.",
            "Looking that up for you.",
            "Finding information on {query}."
        ]
    },
    
    "control_app": {
        "timer": [
            "Starting a timer for {input_param}.",
            "Timer set for {input_param}.",
            "Counting down {input_param} now."
        ],
        "alarm": [
            "Alarm set for {input_param}.",
            "I’ll wake you at {input_param}.",
            "Scheduling an alarm for {input_param}."
        ],
        "notepad": [
            "Opening Notepad and writing your note.",
            "Jotting that down in Notepad.",
            "Writing your text into Notepad now."
        ],
        "default": [
            "Performing the requested control action now.",
            "Running that control command for you.",
            "Executing that operation now."
        ]
    }
}


async def helper(success: bool, text: str, response_message: Any = None):
    
    if response_message is None:
        response_message = text
    audio_bytes = await synthesize_to_bytes(response_message)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return {
        "success": success,
        "text": text,
        "audio_b64": audio_b64
    }

def _normalize_key(value: Any) -> str:
    return value.lower().strip() if isinstance(value, str) else ""


def _flatten_options(options: Any) -> list[str]:
    if isinstance(options, list):
        return options
    if isinstance(options, dict):
        flattened = []
        for val in options.values():
            if isinstance(val, list):
                flattened.extend(val)
            elif isinstance(val, str):
                flattened.append(val)
        return flattened or ["Command executed."]
    return [str(options)]


def _format_response(template: str, entities: dict) -> str:
    try:
        return template.format(**entities)
    except Exception:
        return template


def _select_response(intent: str, entities: dict) -> str:
    options = response_texts.get(intent, ["Command executed."])

    if isinstance(options, dict):
        key = ""
        if intent == "open_app":
            key = _normalize_key(entities.get("app_name"))
        elif intent == "open_site":
            key = _normalize_key(entities.get("site_name"))
        elif intent == "click_shortcut":
            key = _normalize_key(entities.get("shortcut_name"))
        elif intent == "get_current":
            key = _normalize_key(entities.get("command"))
        elif intent == "quick_panel":
            key = _normalize_key(entities.get("command"))
        elif intent == "web_search":
            key = _normalize_key(entities.get("platform"))
        elif intent == "search_file":
            key = _normalize_key(entities.get("command"))
        elif intent == "control_app":
            key = _normalize_key(entities.get("command"))

        if key and key in options:
            options = options[key]
        else:
            options = options.get("default", _flatten_options(options))

    if isinstance(options, list):
        return random.choice(options)
    return str(options)


@router.get('/api/voice/command')
async def listen_voice():
    text = listen_to_user2()

    if not text:
        return await helper(False, "Could not transcribe audio", None)

    print("\nTranscribed text: ", text)
    dispatcher_response = command_dispatcher(text)
    if dispatcher_response.get("success") is False:
        return await helper(True, "Command not recognized or failed to execute!")

    intent = dispatcher_response.get("intent")
    if intent == "general_query":
            llm_response = handle_message_chatbot(
                query=text
            )
            return await helper(True, llm_response, llm_response)

    entities = dispatcher_response.get("entities", {})
    response_message = _format_response(_select_response(intent, entities), entities)
    if dispatcher_response.get("response"):
        response_message = response_message + ' ' + dispatcher_response.get("response")
    print(f"Intent: {intent}, Response message: {response_message}")

    return await helper(True, response_message, response_message)

