# E1 Assistant - Product Requirements Document

## Original Problem Statement
Build a personal AI assistant web application similar to OpenClaw but customized based on user documentation (persistent memory, webhooks for system control, and security features). Features include:
- Multi-model AI support (Claude Sonnet 4.5, Gemini 3 Flash, GPT via Emergent LLM key)
- Chat interface with persistent memory
- App integrations/webhooks with simple setup
- Swarm capability for multi-agent crypto trading
- Dark theme UI like OpenClaw
- Self-hostable and deployable anywhere

## User Personas
1. **Power User / Developer**: Needs a customizable AI assistant with webhook integrations
2. **Crypto Trader**: Wants multi-agent swarm for market analysis and trading signals
3. **Business User**: Requires persistent memory for context-aware conversations

## Core Requirements (Static)
- [x] Multi-model AI chat (Claude, Gemini, GPT)
- [x] Persistent conversation memory (MongoDB)
- [x] Webhook/integration management
- [x] Swarm agent system for multi-agent tasks
- [x] Dark tactical theme UI
- [x] Settings management
- [x] Security features (rate limiting, logging)

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Lucide Icons
- **Backend**: FastAPI + emergentintegrations library
- **Database**: MongoDB (conversations, webhooks, agents, tasks, settings)
- **AI Models**: Via Emergent LLM Key (universal key)

## What's Been Implemented (Jan 2026)

### Backend (`/app/backend/server.py`)
- Chat API with multi-model support (POST /api/chat)
- Conversation CRUD (GET/DELETE /api/conversations)
- Webhook management (CRUD /api/webhooks)
- Swarm agent management (CRUD /api/swarm/agents)
- Swarm task execution (POST /api/swarm/tasks)
- Settings management (GET/PUT /api/settings)
- Models listing (GET /api/models)
- Rate limiting (30/min on chat)
- Comprehensive logging

### Frontend (`/app/frontend/src/App.js`)
- Sidebar navigation (Chat, Integrations, Swarm, Settings)
- Chat interface with model selector
- Conversation history sidebar
- Integrations page with webhook form
- Swarm Agents page with agent/task management
- Settings page with model preferences
- Dark tactical theme with IBM Plex Sans + Manrope fonts

### Available AI Models
1. Claude Sonnet 4.5 (anthropic) - Recommended
2. Claude Haiku 4.5 (anthropic)
3. Claude Opus 4.5 (anthropic)
4. Gemini 3 Flash (gemini) - Recommended
5. Gemini 2.5 Pro (gemini)
6. Gemini 2.5 Flash (gemini)
7. GPT-5.2 (openai)
8. GPT-5.1 (openai) - Recommended
9. GPT-4o (openai)
10. O3 Mini (openai)

## Prioritized Backlog

### P0 - Done
- [x] Basic chat functionality
- [x] Multi-model support
- [x] Conversation persistence
- [x] Dark theme UI

### P1 - Next
- [ ] PDF document upload and analysis
- [ ] Webhook execution from chat commands
- [ ] Real-time crypto price feeds integration
- [ ] User authentication system

### P2 - Future
- [ ] Voice input/output
- [ ] Scheduled tasks (cron jobs)
- [ ] Export conversations
- [ ] Custom system prompts per conversation
- [ ] Plugin system for extensions

## Next Tasks
1. Add PDF upload functionality for document analysis
2. Integrate real-time crypto data (CoinGecko API) for swarm trading
3. Add webhook triggering from chat interface
4. Implement user authentication
