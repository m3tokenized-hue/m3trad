from fastapi import FastAPI, APIRouter, HTTPException, Request
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
import openai
import anthropic

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'e1_assistant')]

# API Keys - Support both Emergent key and direct provider keys
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', EMERGENT_LLM_KEY)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', EMERGENT_LLM_KEY)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create the main app
app = FastAPI(title="E1 Assistant API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============= MODELS =============

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str
    content: str
    model: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    messages: List[Dict] = []
    model: str = "gpt-4o"
    provider: str = "openai"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    model: str = "gpt-4o"
    provider: str = "openai"

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
    role: str
    model: str = "gpt-4o"
    provider: str = "openai"
    system_prompt: str
    enabled: bool = True
    status: str = "idle"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SwarmTask(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agents: List[str] = []
    task_type: str = "analysis"
    input_data: Dict[str, Any] = {}
    status: str = "pending"
    results: List[Dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SettingsUpdate(BaseModel):
    default_model: Optional[str] = None
    default_provider: Optional[str] = None
    system_prompt: Optional[str] = None

class WalletSettingsUpdate(BaseModel):
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    coinbase_api_key: Optional[str] = None
    coinbase_private_key: Optional[str] = None

# ============= LLM HELPER FUNCTIONS =============

async def call_openai(messages: List[Dict], model: str) -> str:
    """Call OpenAI API"""
    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def call_anthropic(messages: List[Dict], model: str, system: str = "") -> str:
    """Call Anthropic API"""
    try:
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        # Convert messages format for Anthropic
        anthropic_messages = []
        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            system=system or "You are E1, a powerful AI assistant.",
            messages=anthropic_messages
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Anthropic error: {e}")
        raise HTTPException(status_code=500, detail=f"Anthropic API error: {str(e)}")

async def call_llm(messages: List[Dict], model: str, provider: str) -> str:
    """Route to appropriate LLM provider"""
    if provider == "anthropic":
        return await call_anthropic(messages, model)
    else:  # Default to OpenAI (works for openai, gemini via compatible endpoint)
        return await call_openai(messages, model)

# ============= CHAT ENDPOINTS =============

@api_router.get("/")
async def root():
    return {"message": "E1 Assistant API", "version": "1.0.0"}

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
            conversation = Conversation(model=chat_request.model, provider=chat_request.provider)
        
        # Add user message
        user_msg = {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": chat_request.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        conversation.messages.append(user_msg)
        
        # Build messages for LLM
        llm_messages = [{"role": "system", "content": "You are E1, a powerful AI assistant. Be helpful, accurate, and concise."}]
        for msg in conversation.messages[-10:]:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Call LLM
        response_text = await call_llm(llm_messages, chat_request.model, chat_request.provider)
        
        # Add assistant response
        assistant_msg = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": response_text,
            "model": chat_request.model,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        conversation.messages.append(assistant_msg)
        
        # Generate title from first message
        if len(conversation.messages) == 2 and conversation.title == "New Chat":
            first_words = chat_request.message.split()[:5]
            conversation.title = " ".join(first_words) + ("..." if len(chat_request.message.split()) > 5 else "")
        
        # Update timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        
        # Save to database
        conv_dict = conversation.model_dump()
        conv_dict['created_at'] = conv_dict['created_at'].isoformat()
        conv_dict['updated_at'] = conv_dict['updated_at'].isoformat()
        
        await db.conversations.update_one({"id": conversation.id}, {"$set": conv_dict}, upsert=True)
        
        return {"conversation_id": conversation.id, "message": assistant_msg, "title": conversation.title}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/conversations")
async def get_conversations():
    conversations = await db.conversations.find({}, {"_id": 0}).sort("updated_at", -1).to_list(100)
    return conversations

@api_router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    result = await db.conversations.delete_one({"id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}

# ============= WEBHOOK ENDPOINTS =============

@api_router.post("/webhooks")
async def create_webhook(webhook: WebhookConfig):
    webhook_dict = webhook.model_dump()
    webhook_dict['created_at'] = webhook_dict['created_at'].isoformat()
    await db.webhooks.insert_one(webhook_dict)
    return webhook

@api_router.get("/webhooks")
async def get_webhooks():
    webhooks = await db.webhooks.find({}, {"_id": 0}).to_list(100)
    return webhooks

@api_router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    result = await db.webhooks.delete_one({"id": webhook_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": "deleted"}

@api_router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: str):
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
                return {"status": "success", "response_code": response.status}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============= SWARM AGENT ENDPOINTS =============

@api_router.post("/swarm/agents")
async def create_swarm_agent(agent: SwarmAgent):
    agent_dict = agent.model_dump()
    agent_dict['created_at'] = agent_dict['created_at'].isoformat()
    await db.swarm_agents.insert_one(agent_dict)
    return agent

@api_router.get("/swarm/agents")
async def get_swarm_agents():
    agents = await db.swarm_agents.find({}, {"_id": 0}).to_list(100)
    return agents

@api_router.delete("/swarm/agents/{agent_id}")
async def delete_swarm_agent(agent_id: str):
    result = await db.swarm_agents.delete_one({"id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "deleted"}

@api_router.post("/swarm/tasks")
async def create_swarm_task(task: SwarmTask):
    task_dict = task.model_dump()
    task_dict['created_at'] = task_dict['created_at'].isoformat()
    task_dict['status'] = 'running'
    await db.swarm_tasks.insert_one(task_dict)
    asyncio.create_task(run_swarm_task(task.id, task.agents, task.task_type, task.input_data))
    return task

async def run_swarm_task(task_id: str, agent_ids: List[str], task_type: str, input_data: Dict):
    results = []
    try:
        for agent_id in agent_ids:
            agent_doc = await db.swarm_agents.find_one({"id": agent_id}, {"_id": 0})
            if not agent_doc:
                continue
            
            if task_type == "analysis":
                prompt = f"Analyze the following data: {json.dumps(input_data)}"
            elif task_type == "trade_signal":
                prompt = f"Based on this market data, provide trade signals: {json.dumps(input_data)}"
            else:
                prompt = f"Process this task: {json.dumps(input_data)}"
            
            messages = [
                {"role": "system", "content": agent_doc['system_prompt']},
                {"role": "user", "content": prompt}
            ]
            
            response = await call_llm(messages, agent_doc['model'], agent_doc['provider'])
            
            results.append({
                "agent_id": agent_id,
                "agent_name": agent_doc['name'],
                "agent_role": agent_doc['role'],
                "response": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        await db.swarm_tasks.update_one({"id": task_id}, {"$set": {"status": "completed", "results": results}})
    except Exception as e:
        logger.error(f"Swarm task error: {str(e)}")
        await db.swarm_tasks.update_one({"id": task_id}, {"$set": {"status": "failed", "results": [{"error": str(e)}]}})

@api_router.get("/swarm/tasks")
async def get_swarm_tasks():
    tasks = await db.swarm_tasks.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return tasks

@api_router.get("/swarm/tasks/{task_id}")
async def get_swarm_task(task_id: str):
    task = await db.swarm_tasks.find_one({"id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ============= SETTINGS ENDPOINTS =============

@api_router.get("/settings")
async def get_settings():
    settings = await db.settings.find_one({"id": "default"}, {"_id": 0})
    if not settings:
        settings = {"id": "default", "default_model": "gpt-4o", "default_provider": "openai", "system_prompt": "You are E1, a powerful AI assistant."}
    return settings

@api_router.put("/settings")
async def update_settings(settings: SettingsUpdate):
    update_data = {k: v for k, v in settings.model_dump().items() if v is not None}
    await db.settings.update_one({"id": "default"}, {"$set": update_data}, upsert=True)
    return await get_settings()

# ============= WALLET SETTINGS ENDPOINTS =============

@api_router.get("/wallet-settings")
async def get_wallet_settings():
    settings = await db.wallet_settings.find_one({"id": "default"}, {"_id": 0})
    if not settings:
        return {"id": "default", "binance_connected": False, "coinbase_connected": False}
    return {
        "id": "default",
        "binance_connected": bool(settings.get("binance_api_key")),
        "binance_api_key_preview": settings.get("binance_api_key", "")[:8] + "..." if settings.get("binance_api_key") else None,
        "coinbase_connected": bool(settings.get("coinbase_api_key")),
        "coinbase_api_key_preview": settings.get("coinbase_api_key", "")[:8] + "..." if settings.get("coinbase_api_key") else None
    }

@api_router.put("/wallet-settings")
async def update_wallet_settings(wallet_settings: WalletSettingsUpdate):
    update_data = {k: v for k, v in wallet_settings.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.wallet_settings.update_one({"id": "default"}, {"$set": update_data}, upsert=True)
    return await get_wallet_settings()

@api_router.delete("/wallet-settings/{exchange}")
async def disconnect_wallet(exchange: str):
    if exchange == "binance":
        await db.wallet_settings.update_one({"id": "default"}, {"$unset": {"binance_api_key": "", "binance_api_secret": ""}})
    elif exchange == "coinbase":
        await db.wallet_settings.update_one({"id": "default"}, {"$unset": {"coinbase_api_key": "", "coinbase_private_key": ""}})
    return {"status": "disconnected", "exchange": exchange}

# ============= CRYPTO PRICE ENDPOINTS =============

@api_router.get("/crypto/prices")
async def get_crypto_prices():
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": "20", "page": "1", "sparkline": "false", "price_change_percentage": "24h"}
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "prices": [{"id": c["id"], "symbol": c["symbol"].upper(), "name": c["name"], "price": c["current_price"], "change_24h": c["price_change_percentage_24h"], "market_cap": c["market_cap"], "volume": c["total_volume"], "image": c["image"]} for c in data],
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                return {"prices": [], "error": "API unavailable"}
    except Exception as e:
        logger.error(f"Crypto prices error: {e}")
        return {"prices": [], "error": str(e)}

# ============= MODELS ENDPOINT =============

@api_router.get("/models")
async def get_available_models():
    return {
        "models": [
            {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o", "recommended": True},
            {"provider": "openai", "model": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"provider": "openai", "model": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "recommended": True},
            {"provider": "anthropic", "model": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
            {"provider": "anthropic", "model": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
        ]
    }

# Include the router
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
