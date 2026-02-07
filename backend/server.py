from fastapi import FastAPI, APIRouter, HTTPException, Header, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Get Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create the main app
app = FastAPI(title="AI Assistant API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= MODELS =============

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # 'user' or 'assistant'
    content: str
    model: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    messages: List[Dict] = []
    model: str = "claude-sonnet-4-5-20250929"
    provider: str = "anthropic"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    model: str = "claude-sonnet-4-5-20250929"
    provider: str = "anthropic"

class WebhookConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    url: str
    method: str = "POST"
    headers: Dict[str, str] = {}
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SwarmAgent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str  # 'analyst', 'trader', 'risk_manager', 'coordinator'
    model: str = "gemini-3-flash-preview"
    provider: str = "gemini"
    system_prompt: str
    enabled: bool = True
    status: str = "idle"  # 'idle', 'running', 'paused'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SwarmTask(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agents: List[str] = []  # Agent IDs
    task_type: str = "analysis"  # 'analysis', 'trade_signal', 'risk_check'
    input_data: Dict[str, Any] = {}
    status: str = "pending"  # 'pending', 'running', 'completed', 'failed'
    results: List[Dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SettingsUpdate(BaseModel):
    default_model: Optional[str] = None
    default_provider: Optional[str] = None
    system_prompt: Optional[str] = None

# ============= CHAT ENDPOINTS =============

@api_router.get("/")
async def root():
    return {"message": "AI Assistant API", "version": "1.0.0"}

@api_router.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """Send a message and get AI response"""
    try:
        logger.info(f"Chat request: model={chat_request.model}, provider={chat_request.provider}")
        
        # Get or create conversation
        conversation_id = chat_request.conversation_id
        if conversation_id:
            conv_doc = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
            if not conv_doc:
                raise HTTPException(status_code=404, detail="Conversation not found")
            conversation = Conversation(**conv_doc)
        else:
            conversation = Conversation(
                model=chat_request.model,
                provider=chat_request.provider
            )
        
        # Add user message
        user_msg = {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": chat_request.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        conversation.messages.append(user_msg)
        
        # Build conversation context
        context_messages = []
        for msg in conversation.messages[-10:]:  # Last 10 messages for context
            context_messages.append(f"{msg['role'].upper()}: {msg['content']}")
        context = "\n".join(context_messages)
        
        # Initialize LLM chat
        chat_instance = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=conversation.id,
            system_message="You are E1, a powerful AI assistant. You help users with tasks, answer questions, and provide intelligent responses. Be helpful, accurate, and concise."
        ).with_model(chat_request.provider, chat_request.model)
        
        # Send message
        user_message = UserMessage(text=chat_request.message)
        response_text = await chat_instance.send_message(user_message)
        
        # Add assistant response
        assistant_msg = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": response_text,
            "model": chat_request.model,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        conversation.messages.append(assistant_msg)
        
        # Generate title from first message if new conversation
        if len(conversation.messages) == 2 and conversation.title == "New Chat":
            first_words = chat_request.message.split()[:5]
            conversation.title = " ".join(first_words) + ("..." if len(chat_request.message.split()) > 5 else "")
        
        # Update timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        
        # Save to database
        conv_dict = conversation.model_dump()
        conv_dict['created_at'] = conv_dict['created_at'].isoformat()
        conv_dict['updated_at'] = conv_dict['updated_at'].isoformat()
        
        await db.conversations.update_one(
            {"id": conversation.id},
            {"$set": conv_dict},
            upsert=True
        )
        
        logger.info(f"Chat response generated for conversation {conversation.id}")
        
        return {
            "conversation_id": conversation.id,
            "message": assistant_msg,
            "title": conversation.title
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/conversations")
async def get_conversations():
    """Get all conversations"""
    conversations = await db.conversations.find({}, {"_id": 0}).sort("updated_at", -1).to_list(100)
    return conversations

@api_router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    result = await db.conversations.delete_one({"id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}

# ============= WEBHOOK ENDPOINTS =============

@api_router.post("/webhooks")
async def create_webhook(webhook: WebhookConfig):
    """Create a new webhook configuration"""
    webhook_dict = webhook.model_dump()
    webhook_dict['created_at'] = webhook_dict['created_at'].isoformat()
    await db.webhooks.insert_one(webhook_dict)
    logger.info(f"Webhook created: {webhook.name}")
    return webhook

@api_router.get("/webhooks")
async def get_webhooks():
    """Get all webhook configurations"""
    webhooks = await db.webhooks.find({}, {"_id": 0}).to_list(100)
    return webhooks

@api_router.put("/webhooks/{webhook_id}")
async def update_webhook(webhook_id: str, webhook: WebhookConfig):
    """Update a webhook configuration"""
    webhook_dict = webhook.model_dump()
    webhook_dict['created_at'] = webhook_dict['created_at'].isoformat()
    result = await db.webhooks.update_one({"id": webhook_id}, {"$set": webhook_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook

@api_router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    result = await db.webhooks.delete_one({"id": webhook_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": "deleted"}

@api_router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: str):
    """Test a webhook by sending a test request"""
    import aiohttp
    
    webhook_doc = await db.webhooks.find_one({"id": webhook_id}, {"_id": 0})
    if not webhook_doc:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=webhook_doc['method'],
                url=webhook_doc['url'],
                headers=webhook_doc['headers'],
                json={"test": True, "timestamp": datetime.now(timezone.utc).isoformat()}
            ) as response:
                return {
                    "status": "success",
                    "response_code": response.status,
                    "response_body": await response.text()
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============= SWARM AGENT ENDPOINTS =============

@api_router.post("/swarm/agents")
async def create_swarm_agent(agent: SwarmAgent):
    """Create a new swarm agent"""
    agent_dict = agent.model_dump()
    agent_dict['created_at'] = agent_dict['created_at'].isoformat()
    await db.swarm_agents.insert_one(agent_dict)
    logger.info(f"Swarm agent created: {agent.name} ({agent.role})")
    return agent

@api_router.get("/swarm/agents")
async def get_swarm_agents():
    """Get all swarm agents"""
    agents = await db.swarm_agents.find({}, {"_id": 0}).to_list(100)
    return agents

@api_router.put("/swarm/agents/{agent_id}")
async def update_swarm_agent(agent_id: str, agent: SwarmAgent):
    """Update a swarm agent"""
    agent_dict = agent.model_dump()
    agent_dict['created_at'] = agent_dict['created_at'].isoformat()
    result = await db.swarm_agents.update_one({"id": agent_id}, {"$set": agent_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@api_router.delete("/swarm/agents/{agent_id}")
async def delete_swarm_agent(agent_id: str):
    """Delete a swarm agent"""
    result = await db.swarm_agents.delete_one({"id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "deleted"}

@api_router.post("/swarm/tasks")
async def create_swarm_task(task: SwarmTask):
    """Create and run a swarm task"""
    task_dict = task.model_dump()
    task_dict['created_at'] = task_dict['created_at'].isoformat()
    task_dict['status'] = 'running'
    
    await db.swarm_tasks.insert_one(task_dict)
    logger.info(f"Swarm task created: {task.name}")
    
    # Run task in background (simplified - in production use Celery/background workers)
    asyncio.create_task(run_swarm_task(task.id, task.agents, task.task_type, task.input_data))
    
    return task

async def run_swarm_task(task_id: str, agent_ids: List[str], task_type: str, input_data: Dict):
    """Execute a swarm task with multiple agents"""
    results = []
    
    try:
        for agent_id in agent_ids:
            agent_doc = await db.swarm_agents.find_one({"id": agent_id}, {"_id": 0})
            if not agent_doc:
                continue
            
            # Create chat instance for agent
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"swarm-{task_id}-{agent_id}",
                system_message=agent_doc['system_prompt']
            ).with_model(agent_doc['provider'], agent_doc['model'])
            
            # Build task prompt based on type
            if task_type == "analysis":
                prompt = f"Analyze the following data and provide insights: {json.dumps(input_data)}"
            elif task_type == "trade_signal":
                prompt = f"Based on this market data, provide trade signals: {json.dumps(input_data)}"
            elif task_type == "risk_check":
                prompt = f"Evaluate the risk of this position/trade: {json.dumps(input_data)}"
            else:
                prompt = f"Process this task: {json.dumps(input_data)}"
            
            # Get response
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            results.append({
                "agent_id": agent_id,
                "agent_name": agent_doc['name'],
                "agent_role": agent_doc['role'],
                "response": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Update task with results
        await db.swarm_tasks.update_one(
            {"id": task_id},
            {"$set": {"status": "completed", "results": results}}
        )
        
    except Exception as e:
        logger.error(f"Swarm task error: {str(e)}")
        await db.swarm_tasks.update_one(
            {"id": task_id},
            {"$set": {"status": "failed", "results": [{"error": str(e)}]}}
        )

@api_router.get("/swarm/tasks")
async def get_swarm_tasks():
    """Get all swarm tasks"""
    tasks = await db.swarm_tasks.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return tasks

@api_router.get("/swarm/tasks/{task_id}")
async def get_swarm_task(task_id: str):
    """Get a specific swarm task"""
    task = await db.swarm_tasks.find_one({"id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ============= SETTINGS ENDPOINTS =============

@api_router.get("/settings")
async def get_settings():
    """Get user settings"""
    settings = await db.settings.find_one({"id": "default"}, {"_id": 0})
    if not settings:
        settings = {
            "id": "default",
            "default_model": "claude-sonnet-4-5-20250929",
            "default_provider": "anthropic",
            "system_prompt": "You are E1, a powerful AI assistant."
        }
    return settings

@api_router.put("/settings")
async def update_settings(settings: SettingsUpdate):
    """Update user settings"""
    update_data = {k: v for k, v in settings.model_dump().items() if v is not None}
    await db.settings.update_one(
        {"id": "default"},
        {"$set": update_data},
        upsert=True
    )
    return await get_settings()

# ============= MODELS ENDPOINT =============

@api_router.get("/models")
async def get_available_models():
    """Get available AI models"""
    return {
        "models": [
            {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "recommended": True},
            {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5"},
            {"provider": "anthropic", "model": "claude-opus-4-5-20251101", "name": "Claude Opus 4.5"},
            {"provider": "gemini", "model": "gemini-3-flash-preview", "name": "Gemini 3 Flash", "recommended": True},
            {"provider": "gemini", "model": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"provider": "gemini", "model": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
            {"provider": "openai", "model": "gpt-5.2", "name": "GPT-5.2"},
            {"provider": "openai", "model": "gpt-5.1", "name": "GPT-5.1", "recommended": True},
            {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o"},
            {"provider": "openai", "model": "o3-mini", "name": "O3 Mini"},
            {"provider": "moonshot", "model": "kimi-k2.5", "name": "Kimi K2.5", "recommended": True, "features": ["vision", "agent-swarm", "256k-context"]},
        ]
    }

# ============= WALLET SETTINGS ENDPOINTS =============

class WalletSettings(BaseModel):
    exchange: str  # "binance" or "coinbase"
    api_key: str
    api_secret: Optional[str] = None
    enabled: bool = True

class WalletSettingsUpdate(BaseModel):
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    coinbase_api_key: Optional[str] = None
    coinbase_private_key: Optional[str] = None

@api_router.get("/wallet-settings")
async def get_wallet_settings():
    """Get wallet connection settings (keys are masked)"""
    settings = await db.wallet_settings.find_one({"id": "default"}, {"_id": 0})
    if not settings:
        return {
            "id": "default",
            "binance_connected": False,
            "coinbase_connected": False
        }
    # Mask sensitive data
    return {
        "id": "default",
        "binance_connected": bool(settings.get("binance_api_key")),
        "binance_api_key_preview": settings.get("binance_api_key", "")[:8] + "..." if settings.get("binance_api_key") else None,
        "coinbase_connected": bool(settings.get("coinbase_api_key")),
        "coinbase_api_key_preview": settings.get("coinbase_api_key", "")[:8] + "..." if settings.get("coinbase_api_key") else None
    }

@api_router.put("/wallet-settings")
async def update_wallet_settings(wallet_settings: WalletSettingsUpdate):
    """Update wallet API keys"""
    update_data = {k: v for k, v in wallet_settings.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.wallet_settings.update_one(
        {"id": "default"},
        {"$set": update_data},
        upsert=True
    )
    logger.info("Wallet settings updated")
    return await get_wallet_settings()

@api_router.delete("/wallet-settings/{exchange}")
async def disconnect_wallet(exchange: str):
    """Disconnect a wallet by removing its API keys"""
    if exchange == "binance":
        await db.wallet_settings.update_one(
            {"id": "default"},
            {"$unset": {"binance_api_key": "", "binance_api_secret": ""}}
        )
    elif exchange == "coinbase":
        await db.wallet_settings.update_one(
            {"id": "default"},
            {"$unset": {"coinbase_api_key": "", "coinbase_private_key": ""}}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid exchange")
    return {"status": "disconnected", "exchange": exchange}

# ============= CRYPTO PRICE ENDPOINTS (CoinGecko) =============

@api_router.get("/crypto/prices")
async def get_crypto_prices():
    """Get live crypto prices from CoinGecko (free API)"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get top cryptocurrencies
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": "20",
                "page": "1",
                "sparkline": "false",
                "price_change_percentage": "24h"
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "prices": [
                            {
                                "id": coin["id"],
                                "symbol": coin["symbol"].upper(),
                                "name": coin["name"],
                                "price": coin["current_price"],
                                "change_24h": coin["price_change_percentage_24h"],
                                "market_cap": coin["market_cap"],
                                "volume": coin["total_volume"],
                                "image": coin["image"]
                            }
                            for coin in data
                        ],
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    raise HTTPException(status_code=response.status, detail="CoinGecko API error")
    except Exception as e:
        logger.error(f"Failed to fetch crypto prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/crypto/price/{symbol}")
async def get_crypto_price(symbol: str):
    """Get price for a specific cryptocurrency"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true"
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if symbol.lower() in data:
                        coin_data = data[symbol.lower()]
                        return {
                            "symbol": symbol.upper(),
                            "price": coin_data.get("usd"),
                            "change_24h": coin_data.get("usd_24h_change"),
                            "market_cap": coin_data.get("usd_market_cap")
                        }
                    else:
                        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
                else:
                    raise HTTPException(status_code=response.status, detail="CoinGecko API error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
