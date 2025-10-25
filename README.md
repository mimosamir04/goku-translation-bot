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
   git clone https://github.com/yourusername/goku-translation-bot.git
   cd goku-translation-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

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

## 🛠️ Technical Details

### Technologies Used
- **Python 3.8+**
- **python-telegram-bot** - Telegram Bot API
- **google-generativeai** - Google Gemini AI
- **python-dotenv** - Environment variable management

### Bot Architecture
- **Smart Language Detection**: Uses AI to detect input language
- **Bidirectional Translation**: Supports both French→Arabic and Arabic→French
- **Auto-Correction**: Automatically fixes spelling and grammar errors
- **Rate Limiting**: 20 requests per minute per user
- **Error Handling**: Comprehensive error handling and logging

## 📊 Features in Detail

### Smart Translation
The bot automatically:
1. Detects the input language
2. Corrects any spelling/grammar mistakes
3. Translates to the target language
4. Preserves proper names, numbers, and formatting

### User Statistics
Track your usage with:
- Total translations
- Characters translated
- Usage duration
- Average translations per day

### Interactive Features
- Greet the bot by name
- Ask questions about the bot
- Get help and information
- View your personal statistics

## 🔒 Security & Privacy

- **No Data Storage**: The bot doesn't store your messages
- **Rate Limiting**: Prevents abuse and spam
- **Secure API**: Uses official Telegram and Google APIs
- **Environment Variables**: Sensitive data stored securely

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

Created by [@anes_miih19](https://t.me/anes_miih19)

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/yourusername/goku-translation-bot/issues) page
2. Contact the developer: [@anes_miih19](https://t.me/anes_miih19)

## 🎯 Roadmap

- [ ] Support for more languages
- [ ] Voice message translation
- [ ] Image text translation
- [ ] Group chat management
- [ ] Translation history

---

⭐ **Star this repository if you found it helpful!**
