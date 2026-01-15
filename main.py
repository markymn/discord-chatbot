import discord
import os
import collections
import logging
import time
import secrets
import string
from dotenv import load_dotenv
import ai_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BudSwayze')

load_dotenv()

# Define intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Generate a unique session ID for this instance
SESSION_ID = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))

# Memory for the bot (last 10 messages per channel: 5 pairings)
channel_histories = collections.defaultdict(list)

# Global cooldown (2 seconds)
LAST_RESPONSE_TIME = 0.0

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user} (ID: {client.user.id}) [SESSION: {SESSION_ID}]')
    logger.info('------')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    triggered = False
    clean_prompt = ""
    msg_lower = message.content.lower()

    # Mention trigger
    if client.user.mentioned_in(message):
        clean_prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        triggered = True
    # Wake word triggers
    elif msg_lower.startswith("bud,") or msg_lower.startswith("bud "):
        clean_prompt = message.content[4:].strip()
        triggered = True
    elif msg_lower.startswith("hey bud") or msg_lower.startswith("yo bud"):
        if msg_lower.startswith("hey bud"):
            clean_prompt = message.content[7:].strip()
        else:
            clean_prompt = message.content[6:].strip()
        
        # Strip leading comma if present
        if clean_prompt.startswith(","):
            clean_prompt = clean_prompt[1:].strip()
        triggered = True

    if triggered:
        logger.info(f'[{SESSION_ID}] Triggered by {message.author.name} in {message.channel}')
        
        # Global cooldown check
        global LAST_RESPONSE_TIME
        current_time = time.time()
        if current_time - LAST_RESPONSE_TIME < 2.0:
            logger.info(f"[{SESSION_ID}] Cooldown active. Skipping.")
            return
        
        LAST_RESPONSE_TIME = current_time
        
        # Get channel history
        history = channel_histories[message.channel.id]
        
        # Handle special user rules
        special_instruction = None
        
        # Kenneth's special rule
        if message.author.name == "kennethlemons" and clean_prompt.lower().strip().endswith("right?"):
            special_instruction = "YOU MUST AGREE WITH THE USER'S STATEMENT. DO NOT BE NONCHALANT. AGREE STRONGLY."
        
        # Devaricate & Shub's special rule
        if message.author.name in ["devaricate", "shub1212"]:
            special_instruction = "end your message by calling the user a 'dweeb', 'twerp', or 'chif'"
            
        try:
            async with message.channel.typing():
                response = ai_manager.get_response(clean_prompt, history, special_instruction)
            
            if response:
                # Update history (user + assistant)
                history.append({"role": "user", "content": clean_prompt})
                history.append({"role": "assistant", "content": response})
                
                # Maintain history limit (last 10 messages = 5 pairings)
                channel_histories[message.channel.id] = history[-10:]
                
                await message.reply(response)
        except Exception as e:
            logger.error(f'Error generating response: {e}')
            await message.reply("idk man, something went wrong. internal brain error.")

def run_bot():
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        logger.error("DISCORD_TOKEN not found. Check your .env file.")
        return

    try:
        client.run(token)
    except Exception as e:
        logger.critical(f"Failed to run bot: {e}")

if __name__ == "__main__":
    run_bot()
