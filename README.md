# 🐉 Goku Translation Bot

A powerful Telegram bot for bidirectional translation between French and Arabic using Google's Gemini AI.

## ✨ Features

- **🔄 Bidirectional Translation**: French ↔ Arabic
- **🧠 Smart Language Detection**: Automatically detects input language
- **✏️ Auto-Correction**: Fixes spelling and grammar mistakes automatically
- **📊 User Statistics**: Track your translation usage
- **⚡ Fast & Accurate**: Powered by Google Gemini 2.0 Flash
- **🎯 Interactive Commands**: Chat with the bot using its name
- **🛡️ Rate Limiting**: Prevents spam and abuse

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google AI API Key (from [Google AI Studio](https://ai.google.dev/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mimosamir04/goku-translation-bot.git
   cd goku-translation-bot
   ```

2. **Run setup**
   ```bash
   python setup.py
   ```

3. **Create .env file**
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

4. **Run the bot**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Getting API Keys

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token to your `.env` file

#### Google AI API Key
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key to your `.env` file

## 📱 Usage

### Basic Translation
Simply send any text to the bot:
- **French text** → Gets translated to Arabic
- **Arabic text** → Gets translated to French

### Interactive Commands
Use the bot's name for special interactions:
- `Goku مرحباً!` - Greet the bot
- `ڨوكو من صنعك؟` - Ask who created the bot
- `Goku كيف حالك؟` - Ask how the bot is doing

### Available Commands
- `/start` - Start the bot and see welcome message
- `/help` - Show comprehensive help guide
- `/stats` - View your translation statistics
- `/language` - See supported languages
- `/about` - Learn about the bot
- `/ping` - Test bot connectivity

## 🚀 Deployment

### Render (Recommended)
1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically

### Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set environment variables
4. Deploy: `git push heroku main`

### Local Development
```bash
python app.py
```

## 🔄 Auto-Deploy

To update and deploy automatically:

```bash
# Quick update
python deploy.py

# With custom message
python deploy.py "Fixed translation bug"
```

## 📁 Project Structure

```
goku-translation-bot/
├── app.py              # Main application (web + bot)
├── bot.py              # Telegram bot logic
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── Procfile            # Heroku deployment
├── deploy.py           # Auto-deployment script
├── setup.py            # Setup script
├── env.example         # Environment template
└── README.md           # This file
```

## 🛠️ Technical Details

### Technologies Used
- **Python 3.8+**
- **python-telegram-bot** - Telegram Bot API
- **google-generativeai** - Google Gemini AI
- **flask** - Web server for health checks
- **python-dotenv** - Environment variable management

## 🔒 Security & Privacy

- **No Data Storage**: The bot doesn't store your messages
- **Rate Limiting**: Prevents abuse and spam
- **Secure API**: Uses official Telegram and Google APIs
- **Environment Variables**: Sensitive data stored securely

## 👨‍💻 Developer

Created by [@anes_miih19](https://t.me/anes_miih19)

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/mimosamir04/goku-translation-bot/issues) page
2. Contact the developer: [@anes_miih19](https://t.me/anes_miih19)

---

⭐ **Star this repository if you found it helpful!**