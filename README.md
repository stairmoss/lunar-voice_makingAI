# 🌙 Lunar-Voice Making AI

Lunar-Voice is a web-based AI application designed to generate and manage voice synthesis. Built with a Python Flask backend and a clean HTML/CSS frontend, it provides an interface to create and store AI-generated audio clips.

## 🚀 Features
- **AI Voice Generation**: Create audio from text using advanced AI models.
- **Web Dashboard**: Simple and intuitive UI for managing voice outputs.
- **Audio Management**: Automatically stores generated clips in a structured directory (`static/audio/`).
- **Flask Backend**: Lightweight and fast server-side processing.

## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5
- **Storage**: Local static directory for audio files
- **Deployment Ready**: Includes `requirements.txt` and `.gitignore` for easy setup.

## 📁 Project Structure
```text
lunar-voice_makingAI/
├── app.py              # Main Flask application
├── static/
│   └── audio/          # Directory for generated audio files
├── templates/          # HTML templates for the web UI
├── requirements.txt    # Python dependencies
└── .gitignore          # Files to exclude from Git
