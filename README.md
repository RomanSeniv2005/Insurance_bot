# 🚗 Car Insurance Telegram Bot

A smart, user-friendly Telegram bot for fast and easy car insurance policy creation. The bot guides users through document submission, data extraction, price confirmation, and policy generation—all in a conversational, AI-powered flow.

---

## ✨ Features
- 📸 Upload passport and car documents (both sides)
- 🤖 Automatic data extraction (Mindee API)
- 🧠 Intelligent conversation (OpenAI integration)
- 💵 Fixed price quotation and confirmation
- 📝 Instant PDF policy generation and delivery
- 🛡️ Error handling and user-friendly prompts
---

## 🛠️ Technologies Used
- **Python 3.10+**
- [aiogram](https://github.com/aiogram/aiogram) (Telegram Bot API)
- [OpenAI API](https://platform.openai.com/)
- [Mindee API](https://mindee.com/)
- [ReportLab](https://www.reportlab.com/) (PDF generation)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 📁 Folder Structure
```
project_root/
├── hendler.py                # Main bot handlers
├── main.py                   # Bot entry point
├── mindee_local/             # Mindee API integration modules
│   ├── passport.py
│   └── car_docs.py
├── openai_local/             # OpenAI integration
│   └── openai_interaction.py
├── pdf_creation/             # PDF generation logic and assets
│   ├── pdf_creation.py
│   ├── fonts/
│   └── assets/
├── .env                      # Environment variables (not in git)
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🚀 Quick Start

1. **Clone the repo:**
   ```sh
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up your `.env` file:**
   ```env
   BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   MINDEE_V2_API_KEY=your_mindee_api_key
   CAR_DOC_MODEL_ID=your_mindee_car_doc_model_id
   PASSPORT_MODEL_ID=your_mindee_passport_model_id
   ```
5. **Run the bot:**
   ```sh
   python main.py
   ```

---

## ⚙️ Environment Variables
| Variable              | Description                        |
|---------------------- |------------------------------------|
| BOT_TOKEN             | Telegram Bot API token              |
| OPENAI_API_KEY        | OpenAI API key                      |
| MINDEE_V2_API_KEY     | Mindee API key                      |
| CAR_DOC_MODEL_ID      | Mindee Car Doc model ID             |
| PASSPORT_MODEL_ID     | Mindee Passport model ID            |

---

## 💬 Main Commands & Menu
- `/start` — Start the bot and show main menu
- **Оформити страховку** — Begin insurance process
- **Підтримка** — Get support info
- **FAQ** — Frequently asked questions
- **Розпочати все знову** — Restart the process
- **Скасувати** — Cancel current operation
- **Мій поліс** — Get your policy again

---

## 📝 Usage
1. Start the bot with `/start` or by messaging it in Telegram.
2. Follow the prompts to upload your passport and car documents.
3. Confirm the extracted data and agree to the price.
4. Receive your insurance policy as a PDF directly in chat!
5.You can also chat with AI if you have any questions directly in the chat.

---

## 🧑‍💻 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📫 Contact
- Author: [Your Name](mailto:your.email@example.com)
- Telegram: [@yourusername](https://t.me/yourusername)

---

> **Note:** This project is for educational/demo purposes. Do not use real personal data in production without proper security and compliance. 