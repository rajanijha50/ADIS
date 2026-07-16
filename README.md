# ADIS - Advanced Desktop Intelligence System

ADIS is a sophisticated, voice-enabled desktop assistant built with a modern tech stack, featuring a high-performance **FastAPI** backend and a stunning **Electron + React** desktop application.

---

## 🚀 Project Overview

ADIS combines the power of Python's automation and AI capabilities with a rich, interactive 3D frontend powered by Three.js and React. It provides an intelligent assistant that can understand voice commands, control applications, search the web, and interact with various services.

### Key Features
- **Voice Intelligence**: Advanced speech-to-text (STT) and text-to-speech (TTS) processing using Whisper
- **Desktop Automation**: Open applications, open websites, manage system settings
- **AI-Powered**: Command parsing, intent classification, and entity extraction
- **Cross-Platform**: Built with Electron for a seamless desktop experience
- **Modern UI**: Beautiful interface with Tailwind CSS and React Three Fiber for 3D visualizations
- **FastAPI Backend**: High-performance asynchronous processing with Python
- **Authentication**: Integrated Google and Microsoft OAuth systems
- **Database Support**: MongoDB for cloud data and SQLite for local storage
- **Web Search**: Integration with Tavily for real-time information retrieval

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v18.x or later)
- **Python** (v3.10.x or later)
- **MongoDB** (Local or Cloud instance) - optional for cloud features
- **Git**

---

## 📂 Project Structure

```text
ADIS/
├── client/                      # Electron + Vite + React Frontend
│   ├── src/
│   │   ├── components/          # React components (Auth, Chat, Settings, Assistant UI)
│   │   ├── features/            # Redux slices (assistant, message, user state)
│   │   ├── app/                 # Redux store configuration
│   │   └── assets/              # Images and static files
│   ├── electron/                # Electron main process, preload, and Python bridge
│   ├── vite.config.ts           # Vite configuration
│   ├── electron-builder.json5   # Electron packaging configuration
│   └── package.json
│
├── server/                      # FastAPI Backend
│   ├── api/                     # API endpoints
│   │   ├── auth/                # Authentication (Google, Microsoft, Email)
│   │   ├── session/             # Session management
│   │   ├── text/                # Text processing endpoints
│   │   ├── user/                # User management
│   │   └── voice/               # Voice API endpoints
│   ├── automation/              # Automation modules
│   │   ├── llm_handler.py       # LLM integration
│   │   ├── message_chatbot.py   # Chat message processing
│   │   ├── open_app.py          # Application launcher
│   │   ├── open_site.py         # Website launcher
│   │   ├── get_current.py       # Get current date, time, weather, etc.
│   │   ├── web_search.py        # Web search functionality
│   │   ├── click_shortcut.py    # Manages keyboard shortcuts
│   │   ├── quick_panel.py       # Controls quick panel
│   │   └── control_app.py       # Write in notepad, set alarms, etc.
│   ├── core/                    # Core AI/ML modules
│   │   ├── command_dispatcher.py # Route commands to appropriate handlers
│   │   ├── entity_extractor.py   # Extract entities from user input
│   │   ├── intent_classifier.py  # Classify user intent
│   │   └── models/              # ML datasets and models
│   ├── voice/                   # Voice processing
│   │   ├── stt.py               # Speech-to-Text (Whisper)
│   │   ├── tts.py               # Text-to-Speech (Piper)
│   │   └── models/              # Pre-trained voice models
│   ├── db/                      # Database modules
│   │   ├── mongoDB.py           # MongoDB operations
│   │   ├── sqliteDB.py          # SQLite operations
│   │   └── utils.py             # Database utilities
│   ├── config/                  # Configuration management
│   ├── others/                  # Utility scripts (WiFi/Bluetooth toggle)
│   ├── main.py                  # FastAPI application entry point
│   ├── pyproject.toml           # Python project configuration
│   ├── requirements.txt         # Project dependencies
│
└── README.md                    # Project documentation
```

---

## 📦 Setting Up the Server (Backend)

The server handles all business logic, database interactions, automation, voice processing, and API endpoints.

### 1. Navigate to Server Directory
```powershell
cd server
```

### 2. Create a Virtual Environment
Create an isolated Python environment to keep dependencies separate from your system Python.

```powershell
python -m venv .adis
```

### 3. Activate Virtual Environment
- **Windows**:
  ```powershell
  .\.adis\Scripts\activate
  ```
- **Linux/macOS**:
  ```bash
  source .adis/bin/activate
  ```

### 4. Install Dependencies
Install all required packages from the requirements file. **Note**: Install dependencies only after activating the virtual environment.

```powershell
pip install -r requirements.txt
```


### 5. Setup Project Structure for Imports
Configure the package installation for easy imports throughout the codebase.

```powershell
pip install -e .
```

### 6. Configure Environment Variables
Create a `.env` file in the `server/` directory with your credentials.

Use `.env.example` as a template:

### 7. Run the Server
```powershell
fastapi dev main.py

OR

uvicorn main:app --reload
```

The server will start at `http://localhost:8000` with auto-reload enabled during development.

---

## 💻 Setting Up the Client (Frontend)

The client is the user interface and desktop shell for ADIS, built with Electron, React, and Vite.

### 1. Navigate to Client Directory
```powershell
cd client
```

### 2. Install Dependencies
Install all required Node.js packages.

```powershell
npm install
```

### 3. Configure Environment Variables
Create a `.env` file in the `client/` directory.

Use `.env.example` as a template:


### 4. Run in Development Mode
This will launch the Vite development server and the Electron application with hot module replacement.

```powershell
npm run dev
```

The Electron window will open automatically showing the ADIS interface connected to your local backend.

### 5. Build for Production
To package the application for distribution and create an installer:

```powershell
npm run build
```

This generates:
- Packaged Electron app in `dist-electron/`
- Installer in `dist/` (see `electron-builder.json5` for packaging configuration)

`NOTE: when using the .exe app(after npm run build) make sure local server is running. For development only, the npm run dev runs the client and server both.`

---
