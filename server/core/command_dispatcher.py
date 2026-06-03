import random
from typing import Any
from core.entity_extractor import extract_entities
from core.intent_classifier import classify_intent
from automation.open_app import handle_open_app
from automation.open_site import handle_open_site
from automation.click_shortcut import handle_click_shortcut
from automation.get_current import handle_get_current
from automation.quick_panel import handle_quick_panel
from automation.web_search import handle_web_search
from automation.control_app import handle_control_app

def dispatcher_response(success: bool, message: str, intent: str = None, entities: dict = None, response: str = None):
    return {
        "success": success,
        "message": message,
        "intent": intent,
        "entities": entities,
        "response": response
    }

INTENT_REGISTRY = {
"open_app": handle_open_app,
"open_site": handle_open_site,
"click_shortcut": handle_click_shortcut,
"get_current": handle_get_current,
"quick_panel": handle_quick_panel,
"web_search": handle_web_search,
"control_app": handle_control_app,
}

 
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


def command_dispatcher(input_command: str) -> dict:
# Step 1: Get intent and entities from classifier
    intent_result = classify_intent(input_command)
    intent = intent_result.get("intent")
    if intent == "general_query":
        return dispatcher_response(
            success = True, 
            message = "General query can't be executed", 
            intent=intent, 
            entities={}, 
        )
    entity_result = extract_entities(intent, input_command)
    entities = entity_result.get("entities", {})

    print(f"INTENT: {intent}, ENTITIES: {entities}")
    if not entities or not entities.values():
        return dispatcher_response(False, f"No entities extracted for intent '{intent}'.", intent=intent, entities={})

    # Step 2: Look up handler in registry
    handler = INTENT_REGISTRY.get(intent)
    
    # Step 3: Call handler or return error
    if handler:
        try:
            execution_result = handler(**entities)

            if execution_result is False:
                return dispatcher_response(
                    success = False, 
                    message = f"Handler for intent '{intent}' failed to execute properly.", 
                    intent=intent, 
                    entities=entities)

            base_response = _format_response(_select_response(intent, entities), entities)
            if isinstance(execution_result, str):
                separator = "" if base_response.endswith(" ") else " "
                response_text = base_response + separator + execution_result
            else:
                response_text = base_response

            return dispatcher_response(
                success = True, 
                message = f"Command Executed for intent: {intent}", 
                intent=intent, 
                entities=entities, 
                response=response_text
            )
        except TypeError as e:
            # Entity extraction mismatch
            return dispatcher_response(False, f"{str(e)}", intent=intent, entities=entities)
    else:
        return dispatcher_response(False, f"Intent '{intent}' not recognized.", intent=intent, entities=entities)

# print(command_dispatcher("Could you please open youtube.com for me?"))
# print(command_dispatcher("check operating system"))
# print(command_dispatcher("toggle bluetooth"))
# print(command_dispatcher("what is programming?"))
# while True:
#     user_input = input("\nEnter a command (or 'exit' to quit): ")
#     if user_input.lower() == 'exit':
#         break
#     result = command_dispatcher(user_input)
#     print(result)