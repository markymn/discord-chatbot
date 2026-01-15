import os
import logging
from groq import Groq

# Configure logging
logger = logging.getLogger('BudSwayze.AI')

# Initialize Groq client
client = None
def get_client():
    global client
    if client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment.")
            return None
        client = Groq(api_key=api_key)
    return client

def get_response(prompt, history=None, special_instruction=None):
    """
    Orchestrates the AI response flow:
    1. Safety Check (Prompt Guard)
    2. Intent Classification
    3. Routing (Search vs General) with Fallbacks
    """
    groq_client = get_client()
    if not groq_client:
        return "idk man, my brain isn't plugged in. check the api key."

    if history is None:
        history = []
    
    # --- Step 0: Safety Check ---
    try:
        safety_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-prompt-guard-2-22m"
        )
        safety_response = safety_completion.choices[0].message.content.strip().lower()
        if "unsafe" in safety_response:
             logger.warning(f"Unsafe prompt detected: {prompt}")
             return "Beat it."
    except Exception as e:
        logger.error(f"Safety Check Failed: {e}")
        # Default to safe if guard fails, but log it
        pass

    # --- Step 1: Classification ---
    intent = "GENERAL"
    try:
        classification_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a classifier. Specify if the user prompt requires a web search or external knowledge retrieval (SEARCH) or if it is a general conversation/coding/internal logic query (GENERAL). Routinely choose SEARCH for specific names, games, software, people, or events that might have recent updates. Reply ONLY with 'SEARCH' or 'GENERAL'."
                },
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        intent = classification_completion.choices[0].message.content.strip().upper()
        if intent not in ["SEARCH", "GENERAL"]:
            intent = "GENERAL"
    except Exception as e:
        logger.error(f"Classification Failed: {e}")

    # --- Step 2: Routing & Fallback ---
    logger.info(f"Routing intent: {intent}")
    if intent == "SEARCH":
         return _handle_search(prompt, history, special_instruction)
    else:
         return _handle_general(prompt, history, special_instruction)

def _handle_search(prompt, history, special_instruction):
    chain = ["groq/compound-mini", "gpt-oss-120b", "llama-3.1-8b-instant"]
    return _try_chain(chain, prompt, history, special_instruction)

def _handle_general(prompt, history, special_instruction):
    chain = ["llama-3.1-8b-instant", "groq/compound-mini", "gpt-oss-120b"]
    return _try_chain(chain, prompt, history, special_instruction)

def _try_chain(models, prompt, history, special_instruction):
    groq_client = get_client()
    for model in models:
        try:
            # Construct messages with history
            system_content = (
                "You are Bud. You're chill, low-energy, and nonchalant, but you still answer questions properly. "
                "ALWAYS use all lowercase letters. Use shortened words like 'u', 'r', 'cuz', 'idk' when possible. "
                "Keep it brief, max 5 sentences. NEVER tell the user to google something or search the web. "
                "NEVER ask follow-up questions. "
                "If the user's question is obvious, dumb, or annoying, include the :what: emoji. "
                "If you are saying something disappointing or sad, or if the topic is a bummer, include the :wilted_rose: emoji."
            )
            
            if special_instruction:
                system_content += f" Special instruction: {special_instruction}"
            
            messages = [{"role": "system", "content": system_content}]
            messages.extend(history)
            messages.append({"role": "user", "content": prompt})

            completion = groq_client.chat.completions.create(
                messages=messages,
                model=model
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Model {model} failed: {e}")
            continue
    return "i'm too tired to think right now. try again later."
