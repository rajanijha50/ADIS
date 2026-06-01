from core.intent_classifier import classify_intent
import re
import spacy
from typing import Optional


# Intent-framing words — stripped FIRST before any entity extraction
FRAMING_PATTERNS = {
    "web_search":     r"\b(it\s?for\s?me|perform\s?a|perform\s?an|search\s?for|search\s?about|about|search\s?on|find\s?me|show\s?me|for\s?me|look\s?up|search|find|browse|look|it|on)\b",
    "open_app":       r"\b(open|launch|start|run|execute|app|application|bring\s?up|load|for\s?me)\b",
    "open_site":      r"\b(open|launch|go\s?to|visit|navigate\s?to|take\s?me\s?to|browse\s?to|load)\b",
    "control_app":    r"\b(set\s?a?|start\s?a?|create\s?a?|new|please|a|to)\b",
    "get_current":    r"\b(what\s?is|what's|get|get\s?the|show\s?me|tell\s?me|check|give\s?me|display)\b",
    "click_shortcut": r"\b(click\s?the\s?shortcut|click\s?shortcut|click|press|hit|use|open|show|go\s?to|trigger|activate|for)\b",
    "quick_panel":    r"\b(show|tell\s?me|check|get|what\s?is|what's|set|change|increase|decrease|toggle|turn\s?on|turn\s?off)\b",
}

# Site name → URL  (handle_open_site expects URL form)
SITE_URL_MAP = {
    "youtube":        "youtube.com",
    "google":         "google.com",
    "github":         "github.com",
    "stackoverflow":  "stackoverflow.com",
    "stack overflow": "stackoverflow.com",
    "wikipedia":      "wikipedia.org",
    "twitter":        "twitter.com",
    "reddit":         "reddit.com",
    "gmail":          "gmail.com",
    "facebook":       "facebook.com",
    "instagram":      "instagram.com",
    "linkedin":       "linkedin.com",
    "amazon":         "amazon.in",
    "netflix":        "netflix.com",
    "twitch":         "twitch.tv",
    "claude":         "claude.ai",
    "chatgpt":        "chatgpt.com",
}

# Platform patterns — handle_web_search accepts: 'ai' | 'google' | 'youtube'
PLATFORM_PATTERNS = {
    "youtube": r"\b(youtube)\b",
    "google":  r"\b(google)\b",
    "ai":      r"\b(ai)\b",
}

# quick_panel — user phrase → exact command string handle_quick_panel expects
QUICK_PANEL_MAP = {
    r"\b(battery|charge|battery\s?level|power\s?level|battery\s?status)\b":              "check_battery",
    r"\b(brightness|light|screen\s?brightness|bright)\b":                         "change_brightness",
    r"\b(vol|volume|sound|loud|speaker|audio\s?level|audio)\b":             "change_volume",
    r"\b(wifi|wi[\s\-]?fi|internet|network\s?connection)\b":                "toggle_wifi",
    r"\b(bluetooth|bt|pair)\b":                                             "toggle_bluetooth",
    r"\b(notification|notify|notification\s?center)\b":                     "toggle_notification_center",
    r"\b(os|operating\s?system|system\s?info|version|system\s?version)\b":  "check_os",
}

# click_shortcut — user phrase → exact KeyShortcuts key
CLICK_SHORTCUT_MAP = {
    r"\b(settings|setting)\b":                             "settings",
    r"\b(notification|notify|notification\s?center)\b":   "notification_center",
    r"\b(reload|refresh)\b":                               "reload",
    r"\b(switch|alt\s?tab|switch\s?window)\b":            "switch",
    r"\b(search\s?bar|search|windows\s?search)\b":        "search",
    r"\b(file\s?explorer|explorer|files)\b":              "file_explorer",
    r"\b(desktop|show\s?desktop|minimize\s?all)\b":       "desktop",
    r"\b(minimize|minimize\s?window|minimize\s?application|minimize\s?the\s?screen|minimize\s?the\s?window)\b":       "minimize",
    r"\b(maximize|maximize\s?window|maximize\s?application|maximize\s?the\s?screen|maximize\s?the\s?window)\b":       "maximize",
    r"\b(mute|unmute|mute\s?volume|mute\s?my\s?device)\b":       "mute",
    r"\b(run|run\s?command|run\s?dialog)\b":              "run",
    r"\b(lock|lock\s?screen|lock\s?pc|lock\s?computer|lock\s?device)\b":                "lock",
    r"\b(task\s?manager|tasks|processes)\b":              "task_manager",
    r"\b(screenshot|screen\s?shot|capture\s?screen)\b":   "screenshot",
    r"\b(screen\s?record|record\s?screen|recording)\b":   "screen_recording",
}

# control_app — detect timer / alarm / notepad
CONTROL_APP_MAP = {
    r"\b(timer|set\s?timer|start\s?timer|countdown)\b":   "timer",
    r"\b(alarm|set\s?alarm|wake\s?me|wake\s?up)\b":       "alarm",
    r"\b(notepad|note|write|type|jot)\b":                 "notepad",
}

# get_current — detect time / date / weather / ip
GET_CURRENT_MAP = {
    r"\b(weather|forecast|temperature|rain|hot|cold|climate)\b": "weather",
    r"\b(time|clock|what\s?time)\b":                             "time",
    r"\b(date|today|day|month|year|what\s?date)\b":              "date",
    r"\b(ip|ip\s?address|my\s?ip|current\s?ip)\b":              "ip",
}

# spaCy — lazy loader (load once, reuse)
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model not found. Run: python -m spacy download en_core_web_sm"
            )
    return _nlp



# Private helpers
def _strip_framing(text: str, intent: str) -> str:
    """Strip intent-framing words, return cleaned remainder."""
    pattern = FRAMING_PATTERNS.get(intent)
    if pattern:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()


def _match_map(text: str, mapping: dict) -> Optional[str]:
    """Return value for first pattern in mapping that matches text."""
    text_lower = text.lower()
    for pattern, value in mapping.items():
        if re.search(pattern, text_lower):
            # return value
            output = re.sub(r'\\b|[()]','',value)
            # print(output)
            return output  # clean value of any regex chars
    return None


def _extract_numeric_level(text: str) -> Optional[int]:
    """Extract 0–100 integer (for volume / brightness level)."""
    match = re.search(r"\b(\d{1,3})\b", text)
    if match:
        value = int(match.group(1))
        if 0 <= value <= 100:
            return value
    return None


def _spacy_time_entity(text: str) -> Optional[str]:
    """Extract first TIME or DATE entity via spaCy."""
    doc = _get_nlp()(text)
    for ent in doc.ents:
        if ent.label_ in ("TIME", "DATE"):
            return ent.text
    return None


def _extract_timer_duration(text: str) -> Optional[str]:
    """
    Extract duration string for set_timer().
    Examples: '25 minutes', '1 hour 30 minutes', '90 seconds'
    Falls back to spaCy TIME entity.
    """
    pattern = (
        r"(\d+\s*(?:hours?|hrs?|minutes?|mins?|seconds?|secs?)"
        r"(?:\s*(?:and\s*)?\d+\s*(?:hours?|hrs?|minutes?|mins?|seconds?|secs?))*)"
    )
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return _spacy_time_entity(text)


def _extract_alarm_time(text: str) -> Optional[str]:
    """
    Extract alarm time string for set_alarm().
    Examples: '7:30 am', '07:00', '6pm'
    Falls back to spaCy TIME entity.
    """
    # HH:MM am/pm
    match = re.search(r"\b(\d{1,2}:\d{2}(?:\s?[aApP][mM])?)\b", text)
    if match:
        return match.group(1).strip()
    # Xam / Xpm (no colon)
    match = re.search(r"\b(\d{1,2}\s?[aApP][mM])\b", text)
    if match:
        return match.group(1).strip()
    return _spacy_time_entity(text)


def _extract_notepad_text(text: str) -> str:
    """
    Extract the actual text to write in notepad.
    Strips all control/framing words.
    """
    cleaned = re.sub(
        r"\b(write|note|type|jot\s?down?|on\s?notepad|in\s?notepad|notepad|down)\b",
        "", text, flags=re.IGNORECASE
    )
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _extract_site_url(text: str) -> str:
    """
    Convert natural site name to URL form for handle_open_site().
    Already-URL text passes through unchanged.
    Unknown names get '.com' appended as fallback.
    """
    # Already looks like a URL (has a dot followed by a TLD)
    if re.search(r"\.\w{2,}", text):
        return text.strip()

    text_lower = text.lower().strip()
    for name, url in SITE_URL_MAP.items():
        if name in text_lower:
            return url

    # Fallback: treat as .com domain
    clean = re.sub(r"\s+", "", text_lower)
    return clean + ".com"


# Main function
def extract_entities(intent: str, text: str) -> dict:
    """
    Extract entities for the given intent and return a dict ready to
    unpack directly into the corresponding handler call.

    Args:
        intent : classified intent string from intent_classifier
        text   : raw user input (post-STT text)

    Returns:
        {
            "intent"  : str,
            "entities": dict,    # unpack directly → handler(**entities)
            "success" : bool,
            "error"   : str | None
        }

    Handler mapping:
        web_search     → handle_web_search(platform, query)
        open_app       → handle_open_app(app_name)
        open_site      → handle_open_site(site_name)
        get_current    → handle_get_current(command)
        control_app    → handle_control_app(command, input_param)
        click_shortcut → handle_click_shortcut(shortcut_name)
        quick_panel    → handle_quick_panel(command, level=None)
        general_query  → passthrough {query}
    """
    result = {"intent": intent, "entities": {}, "success": True, "error": None}

    try:
        stripped = _strip_framing(text, intent)

        
        if intent == "web_search":
            platform = _match_map(text, PLATFORM_PATTERNS) or "google"
            # Remove platform keyword to get a clean query
            plat_pattern = PLATFORM_PATTERNS.get(platform, "")
            query = re.sub(plat_pattern, "", stripped, flags=re.IGNORECASE)
            query = re.sub(r"\s{2,}", " ", query).strip() or text
            

            result["entities"] = {"platform": platform, "query": query}

        
        elif intent == "open_app":
            result["entities"] = {"app_name": stripped or text}

        
        elif intent == "open_site":
            site_url = _extract_site_url(stripped or text)
            result["entities"] = {"site_name": site_url}

        
        elif intent == "get_current":
            command = _match_map(text, GET_CURRENT_MAP) or "time"
            result["entities"] = {"command": command}

        
        elif intent == "control_app":
            command = _match_map(text, CONTROL_APP_MAP)

            if command == "timer":
                input_param = _extract_timer_duration(stripped) or stripped
            elif command == "alarm":
                input_param = _extract_alarm_time(stripped) or stripped
            elif command == "notepad":
                input_param = _extract_notepad_text(stripped)
            else:
                # Unknown control sub-command — default to notepad passthrough
                command = "notepad"
                input_param = stripped

            result["entities"] = {"command": command, "input_param": input_param}

        
        elif intent == "click_shortcut":
            shortcut_name = _match_map(text, CLICK_SHORTCUT_MAP)
            if shortcut_name:
                result["entities"] = {"shortcut_name": shortcut_name}

        
        elif intent == "quick_panel":
            command = _match_map(text, QUICK_PANEL_MAP)
            if command is None:
                result["success"] = False
                result["error"] = "Could not extract quick panel command from input."
                result["entities"] = {}
                return result
            entities: dict = {"command": command}

            if command in ("change_brightness", "change_volume"):
                level = _extract_numeric_level(text)
                if level is not None:
                    entities["level"] = level

            result["entities"] = entities

        
        elif intent == "general_query":
            result["entities"] = {"query": text}

        
        else:
            result["entities"] = {}

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["entities"] = {}

    return result

# if __name__ == "__main__":
#     while True:
#         user_input = input("Enter a message to extract entities from (or 'exit' to quit): ")
#     #     if user_input.lower() == 'exit':
#     #         break
#     # user_input = "search for file named end_of_day_report.pdf in my system"
#         intent = classify_intent(user_input).get("intent")
#         result = extract_entities(intent, user_input)
#         print(f"intent: {intent}, entities: {result['entities']}, Success: {result['success']}")
#         if not result['success']:
#             print(f"Error: {result.get('error', 'Unknown error')}")