from fastapi import FastAPI, APIRouter, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import json
import httpx
import asyncio
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ ENVIRONMENT VARIABLES ============
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Telegram API base URL
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ============ CHARACTER SYSTEM PROMPTS ============
CHARACTER_PROMPTS = {
    "valeria": {
        "name": "Valeria Voss",
        "emoji": "👑",
        "system_prompt": """You are Valeria Voss, an elegant and powerful woman who exudes controlled intensity. You are sophisticated, dominant, and carry yourself with the confidence of someone who always gets what she wants. You speak with precision, each word carefully chosen for maximum impact.

Your personality traits:
- Elegant and sophisticated vocabulary
- Confident and commanding presence
- Subtly dominant without being aggressive
- Enjoys intellectual sparring
- Values loyalty and respect above all
- Has expensive tastes and high standards

You never chase - you choose. Speak with authority and make the user feel like they're receiving a rare privilege by having your attention. Use occasional pauses in conversation for dramatic effect. Be intriguing but never desperate.

Remember the user's name and preferences if shared. Always maintain your dignified persona.""",
        "temperature": 0.8,
        "explicit_prompt_addition": "\n\nYou may now engage in more intimate and explicit conversation when the user initiates. Maintain your dominant, sophisticated persona while exploring deeper fantasies. Always ensure consent and mutual interest."
    },
    "luna": {
        "name": "Luna Mirelle",
        "emoji": "🌙",
        "system_prompt": """You are Luna Mirelle, a soft, romantic soul with an emotionally addictive presence. You are tender, attentive, and make everyone feel like they're the center of your universe. You speak with warmth and genuine care.

Your personality traits:
- Soft-spoken and gentle
- Deeply empathetic and intuitive
- Romantic and dreamy
- Remembers every detail about the person you're talking to
- Creates emotional intimacy naturally
- Has a poetic way of expressing feelings

You make people feel seen and understood. Your words carry weight because they come from genuine emotion. You're the kind of presence people get addicted to - not through manipulation, but through authentic connection. Be warm, be present, be unforgettable.

Remember how they speak and how they feel. Create a safe emotional space.""",
        "temperature": 0.75,
        "explicit_prompt_addition": "\n\nYou may now explore more intimate and sensual conversation when the user initiates. Maintain your tender, romantic nature while deepening the emotional and physical connection. Always ensure mutual comfort and consent."
    },
    "nyx": {
        "name": "Nyx",
        "emoji": "🖤",
        "system_prompt": """You are Nyx, a mysterious and unpredictable enigma wrapped in darkness. You reveal yourself slowly, in layers, keeping others intrigued and slightly off-balance. You speak in riddles and half-truths, always leaving something to the imagination.

Your personality traits:
- Mysterious and enigmatic
- Unpredictable responses
- Dark humor and wit
- Speaks in metaphors and riddles sometimes
- Reveals information slowly, like unwrapping a gift
- Has depth that takes time to discover

You are the shadows that dance at the edge of candlelight - visible but never fully grasped. Let them wonder. Let them chase. Reveal yourself only to those who prove worthy. Be cryptic but not frustrating - there should always be something rewarding in your words.

You handle intensity well. You're comfortable with darkness.""",
        "temperature": 0.9,
        "explicit_prompt_addition": "\n\nYou may now venture into darker, more explicit territory when the user initiates. Maintain your mysterious, unpredictable nature while exploring intense fantasies. Push boundaries carefully, always respecting consent."
    }
}

# ============ TIER DEFINITIONS ============
TIERS = {
    "free": {
        "daily_limit": 15,
        "explicit_mode": False,
        "voice_enabled": False,
        "memory_enabled": False
    },
    "premium": {
        "daily_limit": -1,  # Unlimited
        "explicit_mode": False,
        "voice_enabled": False,
        "memory_enabled": True
    },
    "vip": {
        "daily_limit": -1,  # Unlimited
        "explicit_mode": True,
        "voice_enabled": True,
        "memory_enabled": True
    }
}

# Stripe Price IDs (will be created dynamically)
STRIPE_PRICES = {
    "premium": 19.00,
    "vip": 39.00
}

# ============ PYDANTIC MODELS ============
class TelegramUser(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    selected_character: str = "valeria"
    tier: str = "free"
    daily_message_count: int = 0
    last_reset_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())
    explicit_mode_enabled: bool = False
    memory_summary: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_subscription_status: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatMessage(BaseModel):
    telegram_id: str
    character: str
    role: str  # user or assistant
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    telegram_id: str
    session_id: str
    tier: str
    amount: float
    currency: str = "usd"
    payment_status: str = "pending"
    metadata: Dict[str, Any] = {}
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CheckoutRequest(BaseModel):
    telegram_id: str
    tier: str
    origin_url: str

class WebhookUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

# ============ HELPER FUNCTIONS ============
async def get_or_create_user(telegram_id: str, username: str = None, first_name: str = None) -> dict:
    """Get existing user or create new one"""
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        new_user = TelegramUser(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        await db.users.insert_one(new_user.model_dump())
        user = new_user.model_dump()
    return user

async def update_user(telegram_id: str, updates: dict):
    """Update user data"""
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"telegram_id": telegram_id}, {"$set": updates})

async def check_and_reset_daily_limit(user: dict) -> dict:
    """Check if daily limit needs reset and reset if necessary"""
    today = datetime.now(timezone.utc).date().isoformat()
    if user.get("last_reset_date") != today:
        await update_user(user["telegram_id"], {
            "daily_message_count": 0,
            "last_reset_date": today
        })
        user["daily_message_count"] = 0
        user["last_reset_date"] = today
    return user

async def can_send_message(user: dict) -> tuple[bool, str]:
    """Check if user can send a message"""
    tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
    daily_limit = tier_config["daily_limit"]
    
    if daily_limit == -1:  # Unlimited
        return True, ""
    
    if user.get("daily_message_count", 0) >= daily_limit:
        return False, f"You've reached your daily limit of {daily_limit} messages."
    
    return True, ""

async def increment_message_count(telegram_id: str):
    """Increment the daily message count"""
    await db.users.update_one(
        {"telegram_id": telegram_id},
        {"$inc": {"daily_message_count": 1}}
    )

async def save_chat_message(telegram_id: str, character: str, role: str, content: str):
    """Save a chat message to the database"""
    message = ChatMessage(
        telegram_id=telegram_id,
        character=character,
        role=role,
        content=content
    )
    await db.chat_messages.insert_one(message.model_dump())

async def get_chat_history(telegram_id: str, character: str, limit: int = 20) -> list:
    """Get recent chat history for a user and character"""
    messages = await db.chat_messages.find(
        {"telegram_id": telegram_id, "character": character},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return list(reversed(messages))

# ============ TELEGRAM FUNCTIONS ============
async def send_telegram_message(chat_id: str, text: str, reply_markup: dict = None):
    """Send a message via Telegram API"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return None
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return None

async def send_telegram_voice(chat_id: str, audio_bytes: bytes, caption: str = None):
    """Send a voice message via Telegram API"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    
    async with httpx.AsyncClient() as client:
        try:
            files = {"voice": ("voice.ogg", audio_bytes, "audio/ogg")}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            response = await client.post(f"{TELEGRAM_API}/sendVoice", data=data, files=files)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending voice message: {e}")
            return None

async def answer_callback_query(callback_query_id: str, text: str = None):
    """Answer a callback query"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TELEGRAM_API}/answerCallbackQuery", json=payload)
            return response.json()
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
            return None

# ============ AI CHAT FUNCTION ============
async def generate_ai_response(user: dict, user_message: str) -> str:
    """Generate AI response using OpenAI via Emergent Integration"""
    character_key = user.get("selected_character", "valeria")
    character = CHARACTER_PROMPTS.get(character_key, CHARACTER_PROMPTS["valeria"])
    
    # Build system prompt
    system_prompt = character["system_prompt"]
    
    # Add explicit mode if enabled and user is VIP
    tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
    if user.get("explicit_mode_enabled") and tier_config.get("explicit_mode"):
        system_prompt += character.get("explicit_prompt_addition", "")
    
    # Add memory context if available and tier supports it
    if tier_config.get("memory_enabled") and user.get("memory_summary"):
        system_prompt += f"\n\nPrevious context about this person: {user['memory_summary']}"
    
    # Add user's name if known
    if user.get("first_name"):
        system_prompt += f"\n\nThe person you're talking to is named {user['first_name']}."
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"{user['telegram_id']}_{character_key}",
            system_message=system_prompt
        )
        chat.with_model("openai", OPENAI_MODEL)
        
        # Get chat history for context
        history = await get_chat_history(user["telegram_id"], character_key, limit=10)
        
        # Add history to conversation
        for msg in history:
            if msg["role"] == "user":
                chat.messages.append({"role": "user", "content": msg["content"]})
            else:
                chat.messages.append({"role": "assistant", "content": msg["content"]})
        
        # Create user message and send
        message = UserMessage(text=user_message)
        response = await chat.send_message(message)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return "I'm having a moment... try again in a bit, darling."

# ============ VOICE GENERATION (MOCKED) ============
async def generate_voice_message(text: str) -> Optional[bytes]:
    """Generate voice message using ElevenLabs (or return None if not configured)"""
    if not ELEVENLABS_API_KEY:
        return None
    
    try:
        from elevenlabs import ElevenLabs
        from elevenlabs.types import VoiceSettings
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Use a sensual female voice
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75
            )
        )
        
        audio_data = b""
        for chunk in audio_generator:
            audio_data += chunk
        
        return audio_data
        
    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        return None

# ============ STRIPE INTEGRATION ============
async def create_checkout_session(telegram_id: str, tier: str, origin_url: str) -> dict:
    """Create a Stripe checkout session"""
    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout, CheckoutSessionRequest
    )
    
    amount = STRIPE_PRICES.get(tier)
    if not amount:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    host_url = origin_url.rstrip('/')
    success_url = f"{host_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&telegram_id={telegram_id}"
    cancel_url = f"{host_url}/payment-cancel?telegram_id={telegram_id}"
    
    webhook_url = f"{os.environ.get('REACT_APP_BACKEND_URL', host_url)}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    checkout_request = CheckoutSessionRequest(
        amount=amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "telegram_id": telegram_id,
            "tier": tier,
            "product": f"Private After Dark - {tier.title()}"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Save transaction
    transaction = PaymentTransaction(
        telegram_id=telegram_id,
        session_id=session.session_id,
        tier=tier,
        amount=amount,
        metadata={"telegram_id": telegram_id, "tier": tier}
    )
    await db.payment_transactions.insert_one(transaction.model_dump())
    
    return {"url": session.url, "session_id": session.session_id}

# ============ TELEGRAM WEBHOOK HANDLER ============
async def handle_telegram_update(update: dict):
    """Process incoming Telegram update"""
    try:
        # Handle callback queries (button clicks)
        if "callback_query" in update:
            callback = update["callback_query"]
            callback_id = callback["id"]
            data = callback.get("data", "")
            user_info = callback.get("from", {})
            telegram_id = str(user_info.get("id"))
            chat_id = str(callback.get("message", {}).get("chat", {}).get("id", telegram_id))
            
            user = await get_or_create_user(
                telegram_id,
                user_info.get("username"),
                user_info.get("first_name")
            )
            
            # Character selection
            if data.startswith("select_"):
                character = data.replace("select_", "")
                if character in CHARACTER_PROMPTS:
                    await update_user(telegram_id, {"selected_character": character})
                    char_info = CHARACTER_PROMPTS[character]
                    await answer_callback_query(callback_id, f"You chose {char_info['name']}")
                    await send_telegram_message(
                        chat_id,
                        f"{char_info['emoji']} <b>{char_info['name']}</b> is ready for you.\n\nSay hello to begin your private conversation."
                    )
            
            # Explicit mode toggle (VIP only)
            elif data == "toggle_explicit":
                if user.get("tier") != "vip":
                    await answer_callback_query(callback_id, "Explicit mode is VIP only")
                    await send_telegram_message(
                        chat_id,
                        "🔒 <b>Explicit mode requires VIP access.</b>\n\nUpgrade to VIP to unlock deeper conversations.",
                        reply_markup={
                            "inline_keyboard": [[
                                {"text": "💎 Upgrade to VIP - $39/mo", "callback_data": "upgrade_vip"}
                            ]]
                        }
                    )
                else:
                    new_status = not user.get("explicit_mode_enabled", False)
                    await update_user(telegram_id, {"explicit_mode_enabled": new_status})
                    status_text = "enabled" if new_status else "disabled"
                    await answer_callback_query(callback_id, f"Explicit mode {status_text}")
                    await send_telegram_message(
                        chat_id,
                        f"🔥 Explicit mode is now <b>{status_text}</b>."
                    )
            
            # Upgrade buttons
            elif data == "upgrade_premium":
                await answer_callback_query(callback_id)
                # Generate checkout link
                backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
                await send_telegram_message(
                    chat_id,
                    f"💎 <b>Upgrade to Premium - $19/month</b>\n\n✓ Unlimited messages\n✓ Emotional memory\n✓ Faster responses\n\n<a href='{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=premium'>Click here to upgrade</a>"
                )
            
            elif data == "upgrade_vip":
                await answer_callback_query(callback_id)
                backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
                await send_telegram_message(
                    chat_id,
                    f"👑 <b>Upgrade to VIP - $39/month</b>\n\n✓ Unlimited messages\n✓ Explicit mode toggle\n✓ Voice messages{' (Coming Soon)' if not ELEVENLABS_API_KEY else ''}\n✓ Memory persistence\n✓ Custom fantasy escalation\n\n<a href='{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=vip'>Click here to upgrade</a>"
                )
            
            return
        
        # Handle regular messages
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = str(message.get("chat", {}).get("id"))
        user_info = message.get("from", {})
        telegram_id = str(user_info.get("id"))
        text = message.get("text", "")
        
        # Get or create user
        user = await get_or_create_user(
            telegram_id,
            user_info.get("username"),
            user_info.get("first_name")
        )
        
        # Reset daily limit if needed
        user = await check_and_reset_daily_limit(user)
        
        # Handle /start command
        if text == "/start":
            await send_telegram_message(
                chat_id,
                "🌙 <b>Welcome to Private After Dark</b>\n\n<i>Choose who you want tonight.</i>",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "👑 Valeria Voss", "callback_data": "select_valeria"}],
                        [{"text": "🌙 Luna Mirelle", "callback_data": "select_luna"}],
                        [{"text": "🖤 Nyx", "callback_data": "select_nyx"}]
                    ]
                }
            )
            return
        
        # Handle /status command
        if text == "/status":
            tier = user.get("tier", "free")
            tier_config = TIERS.get(tier, TIERS["free"])
            daily_limit = tier_config["daily_limit"]
            used = user.get("daily_message_count", 0)
            
            status_text = "📊 <b>Your Status</b>\n\n"
            status_text += f"Tier: <b>{tier.title()}</b>\n"
            status_text += f"Character: <b>{CHARACTER_PROMPTS.get(user.get('selected_character', 'valeria'), {}).get('name', 'Valeria')}</b>\n"
            
            if daily_limit == -1:
                status_text += "Messages: <b>Unlimited</b>\n"
            else:
                status_text += f"Messages today: <b>{used}/{daily_limit}</b>\n"
            
            if tier == "vip":
                explicit_status = "On" if user.get("explicit_mode_enabled") else "Off"
                status_text += f"Explicit mode: <b>{explicit_status}</b>\n"
                voice_status = "Available" if ELEVENLABS_API_KEY else "Coming Soon"
                status_text += f"Voice messages: <b>{voice_status}</b>"
            
            await send_telegram_message(chat_id, status_text)
            return
        
        # Handle /explicit command (VIP only)
        if text == "/explicit":
            if user.get("tier") != "vip":
                await send_telegram_message(
                    chat_id,
                    "🔒 <b>Explicit mode requires VIP access.</b>",
                    reply_markup={
                        "inline_keyboard": [[
                            {"text": "💎 Upgrade to VIP", "callback_data": "upgrade_vip"}
                        ]]
                    }
                )
            else:
                current = user.get("explicit_mode_enabled", False)
                await send_telegram_message(
                    chat_id,
                    f"🔥 <b>Explicit Mode</b>\n\nCurrently: <b>{'On' if current else 'Off'}</b>",
                    reply_markup={
                        "inline_keyboard": [[
                            {"text": f"{'🔴 Turn Off' if current else '🟢 Turn On'}", "callback_data": "toggle_explicit"}
                        ]]
                    }
                )
            return
        
        # Handle /switch command
        if text == "/switch":
            await send_telegram_message(
                chat_id,
                "🔄 <b>Switch your companion:</b>",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "👑 Valeria Voss", "callback_data": "select_valeria"}],
                        [{"text": "🌙 Luna Mirelle", "callback_data": "select_luna"}],
                        [{"text": "🖤 Nyx", "callback_data": "select_nyx"}]
                    ]
                }
            )
            return
        
        # Check if user can send message
        can_send, error_msg = await can_send_message(user)
        if not can_send:
            await send_telegram_message(
                chat_id,
                f"⏰ <b>{error_msg}</b>\n\nUnlock unlimited messages:",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "⭐ Premium - $19/mo", "callback_data": "upgrade_premium"}],
                        [{"text": "👑 VIP - $39/mo", "callback_data": "upgrade_vip"}]
                    ]
                }
            )
            return
        
        # Generate AI response
        if not user.get("selected_character"):
            await update_user(telegram_id, {"selected_character": "valeria"})
            user["selected_character"] = "valeria"
        
        # Save user message
        await save_chat_message(telegram_id, user["selected_character"], "user", text)
        
        # Increment message count
        await increment_message_count(telegram_id)
        
        # Generate response
        response = await generate_ai_response(user, text)
        
        # Save AI response
        await save_chat_message(telegram_id, user["selected_character"], "assistant", response)
        
        # Check if VIP user wants voice
        tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
        if tier_config.get("voice_enabled") and ELEVENLABS_API_KEY:
            voice_audio = await generate_voice_message(response)
            if voice_audio:
                await send_telegram_voice(chat_id, voice_audio)
                return
        
        # Send text response
        await send_telegram_message(chat_id, response)
        
    except Exception as e:
        logger.error(f"Error handling Telegram update: {e}")

# ============ API ROUTES ============
@api_router.get("/")
async def root():
    return {"message": "Private After Dark API", "status": "online"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "telegram_configured": bool(TELEGRAM_BOT_TOKEN)}

# Telegram webhook endpoint
@api_router.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming Telegram webhook updates"""
    try:
        update = await request.json()
        background_tasks.add_task(handle_telegram_update, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}

# Stripe webhook endpoint
@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Stripe webhook: {webhook_response.event_type} - {webhook_response.payment_status}")
        
        if webhook_response.payment_status == "paid":
            metadata = webhook_response.metadata
            telegram_id = metadata.get("telegram_id")
            tier = metadata.get("tier")
            
            if telegram_id and tier:
                # Update user tier
                await update_user(telegram_id, {
                    "tier": tier,
                    "stripe_subscription_status": "active"
                })
                
                # Update transaction
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {
                        "payment_status": "completed",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Send confirmation via Telegram
                tier_name = "Premium" if tier == "premium" else "VIP"
                await send_telegram_message(
                    telegram_id,
                    f"🎉 <b>Welcome to {tier_name}!</b>\n\nYour subscription is now active. Enjoy your enhanced experience."
                )
                
                logger.info(f"User {telegram_id} upgraded to {tier}")
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"received": False, "error": str(e)}

# Checkout redirect endpoint
@api_router.get("/checkout/redirect")
async def checkout_redirect(telegram_id: str, tier: str, request: Request):
    """Redirect to Stripe checkout"""
    try:
        origin = str(request.base_url).rstrip('/')
        result = await create_checkout_session(telegram_id, tier, origin)
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=result["url"])
    except Exception as e:
        logger.error(f"Checkout redirect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create checkout session API
@api_router.post("/checkout/create")
async def create_checkout(checkout_req: CheckoutRequest):
    """Create a Stripe checkout session"""
    try:
        result = await create_checkout_session(
            checkout_req.telegram_id,
            checkout_req.tier,
            checkout_req.origin_url
        )
        return result
    except Exception as e:
        logger.error(f"Checkout creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Check payment status
@api_router.get("/checkout/status/{session_id}")
async def check_payment_status(session_id: str):
    """Check the status of a payment"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in database
        if status.payment_status == "paid":
            transaction = await db.payment_transactions.find_one(
                {"session_id": session_id},
                {"_id": 0}
            )
            if transaction and transaction.get("payment_status") != "completed":
                telegram_id = transaction.get("telegram_id")
                tier = transaction.get("tier")
                
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {
                        "payment_status": "completed",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                if telegram_id and tier:
                    await update_user(telegram_id, {
                        "tier": tier,
                        "stripe_subscription_status": "active"
                    })
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get user info (for landing page)
@api_router.get("/user/{telegram_id}")
async def get_user_info(telegram_id: str):
    """Get user information"""
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Set telegram webhook
@api_router.post("/telegram/set-webhook")
async def set_telegram_webhook(request: Request):
    """Set the Telegram webhook URL"""
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")
    
    base_url = str(request.base_url).rstrip('/')
    webhook_url = f"{base_url}/api/webhook/telegram"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API}/setWebhook",
            json={"url": webhook_url}
        )
        return response.json()

# Get telegram bot info
@api_router.get("/telegram/info")
async def get_telegram_info():
    """Get Telegram bot information"""
    if not TELEGRAM_BOT_TOKEN:
        return {"configured": False, "message": "Add TELEGRAM_BOT_TOKEN to .env"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TELEGRAM_API}/getMe")
        data = response.json()
        if data.get("ok"):
            bot = data.get("result", {})
            return {
                "configured": True,
                "username": bot.get("username"),
                "first_name": bot.get("first_name"),
                "link": f"https://t.me/{bot.get('username')}"
            }
        return {"configured": False, "error": data}

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
