# E1 Assistant

Personal AI Assistant with multi-model support, crypto trading swarm agents, and webhook integrations.

![E1 Assistant](https://img.shields.io/badge/E1-Assistant-blue)
![Models](https://img.shields.io/badge/AI%20Models-11-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Multi-Model AI Chat** - Claude, Gemini, GPT, Kimi K2.5 (11 models)
- **Persistent Memory** - Conversation history stored in MongoDB
- **Swarm Agents** - Multi-agent system for crypto trading analysis
- **Live Crypto Prices** - Real-time ticker from CoinGecko
- **Webhook Integrations** - Connect external apps and services
- **Wallet Connections** - Binance & Coinbase API key storage

## Quick Install (Windows)

### One-Line Install (PowerShell)

```powershell
irm https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/install.ps1 | iex
```

### Prerequisites

- [Python 3.9+](https://python.org)
- [Node.js 18+](https://nodejs.org)
- [Git](https://git-scm.com)
- [MongoDB](https://mongodb.com) (local or cloud like MongoDB Atlas)

## Manual Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git e1-assistant
cd e1-assistant

# Install backend
cd backend
pip install -r requirements.txt

# Install frontend
cd ../frontend
npm install
```

### Configure Environment

**Backend** (`backend/.env`):
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="e1_assistant"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=your_emergent_key_here
```

**Frontend** (`frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Start the App

**Windows:**
```cmd
start.bat
```

**Manual:**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn server:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend
npm start
```

Open http://localhost:3000

## Getting Your Emergent LLM Key

1. Go to [Emergent](https://emergentagent.com)
2. Navigate to Profile → Universal Key
3. Copy your key and add to `backend/.env`

## AI Models Available

| Provider | Models |
|----------|--------|
| Anthropic | Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5 |
| Google | Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash |
| OpenAI | GPT-5.2, GPT-5.1, GPT-4o, O3 Mini |
| Moonshot | Kimi K2.5 (Agent Swarm Ready) |

## Crypto Wallet Setup

1. Go to Settings in the app
2. Enter your Binance or Coinbase API keys
3. Keys are stored locally in MongoDB

**Note:** Only add API keys with **read** and **trade** permissions. Never enable withdrawal permissions.

## Tech Stack

- **Frontend:** React 19, Tailwind CSS, Lucide Icons
- **Backend:** FastAPI, Python 3.11
- **Database:** MongoDB
- **AI:** Emergent LLM Key (Universal)

## License

MIT License - Feel free to modify and use as you wish.

---

Built with ❤️ using [Emergent](https://emergentagent.com)
