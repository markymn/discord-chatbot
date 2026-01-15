# Bud Swayze - The Chill Discord Bot

Bud Swayze is a nonchalant, low-energy Discord bot powered by Groq's high-performance AI models. He's designed to be chill, helpful (when he feels like it), and strictly lowercase.

## Features

- **AI-Powered Conversations**: Uses Groq (Llama 3.1, GPT-OSS, Compound-Mini) for rapid responses.
- **Smart Routing**: Automatically decides whether to search the web for info or answer from internal logic.
- **Conversation Memory**: Remembers the last 5 pairings (10 messages) to maintain context.
- **Prompt Guard**: Built-in safety check using `meta-llama/llama-prompt-guard-2-22m`.
- **Personality**: Strictly lowercase, uses shorthand (u, r, cuz), and maintains a 5-sentence response limit.
- **Keep-Alive**: Includes a Flask server to keep the bot running 24/7 on hosting platforms like Replit.

## Setup

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/yourusername/discord-chatbot.git
   cd discord-chatbot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets**:
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Run the Bot**:
   ```bash
   python main.py
   ```

## Configuration

- **Triggers**: Responds to @mentions, "Bud,", "Bud ", "Hey Bud", and "Yo Bud".
- **Memory**: Adjustable in `main.py` via the `channel_histories` slice.
- **Personality**: Defined in the system prompt within `ai_manager.py`.

## License

MIT
