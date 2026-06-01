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

            # print(execution_result, type(execution_result))
            return dispatcher_response(
                success = True, 
                message = f"Command Executed for intent: {intent}", 
                intent=intent, 
                entities=entities, 
                response=execution_result if type(execution_result) != bool else f'{intent}({entities})')

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