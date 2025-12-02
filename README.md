# 🎲 GameBot - Your Interactive Board Game Assistant

**An AI companion for every board game enthusiast!**  

GameBot is designed to enhance your board game experience, whether you're a casual player or a strategy master. From **explaining rules** and **offering strategic advice** to **answering all your game-related questions**, GameBot brings the fun and intelligence to your game nights.

---

## ✨ Features

- **Rule Explanation**: Never get stuck again! GameBot explains the rules of popular board games in plain language.
- **Strategy Suggestions**: Get tips and tricks to improve your gameplay and outsmart your opponents.
- **Interactive Q&A**: Ask anything about your favorite board games and get instant, intelligent responses.
- **Game Night Companion**: Perfect for casual nights with friends or serious strategy sessions.

---

## 🚀 How to Use

1. **Launch the app** (locally via Streamlit or on Hugging Face Spaces).  
2. **Type your question** or describe the game scenario.  
3. **GameBot responds** with clear, actionable advice or explanations.  
4. **Enjoy your game night** with smarter gameplay and insights from GameBot!

---

## 💡 Technology Stack

- **Streamlit** for an interactive web interface  
- **Google Generative AI** for smart conversational capabilities  
- **LangChain** and **LangGraph** for managing conversation flow and AI tools  

---

## 🔧 Setup

1. Clone the repo:  
```bash
git clone https://github.com/karl0706/Gamebot.git
cd Game
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your Google API key as a secret (or in .env for local use):
```bash
export GOOGLE_API_KEY="your_key_here"
```

4. Run locally:
```bash
streamlit run app.py
```

## 🎉 Try it Online

Check it out live on Hugging Face Spaces: [**GameBot**](https://huggingface.co/spaces/iamCodjo/Game)

---
## 🐟 Docker

1. Build the Docker image:  
```bash
docker build -t gamebot .
```

2. Run the container:
```bash
docker run -p 8501:8501 -e GOOGLE_API_KEY="your_key_here" gamebot
```

3. Open your browser and go to:
```bash
http://localhost:8501
```

## 📌 Contributing

Feel free to open issues or submit pull requests!  
GameBot is designed to grow with the community of board game enthusiasts.