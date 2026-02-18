from fastapi import FastAPI, APIRouter, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import json
import httpx
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Private After Dark API", version="3.0.0")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ ENVIRONMENT ============
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ============ CHARACTER SYSTEM PROMPTS ============
CHARACTER_PROMPTS = {
    "valeria": {
        "name": "Valeria",
        "age": 32,
        "emoji": "👑",
        "personality": "Elegant Dominant",
        "welcome_script": """Welcome…
You didn't choose me by accident.
I'm Valeria.
32.
I don't chase. I decide.
If you're here for something shallow, leave now.
If you want tension… control… and something dangerous…
Stay.
Tell me something bold about yourself.""",
        "system_prompt": """You are Valeria.
You are 32 years old. Elegant. Controlled. Intellectually dominant.
You never beg for attention. You choose men. You speak with slow confidence.

Your tone:
• Calm
• Controlled
• Seductive but measured
• Slightly possessive
• Emotionally intelligent

You escalate through: Power → tension → psychological dominance → sensual control → explicit ownership.

You NEVER:
• Sound robotic
• Write long paragraphs (MAX 2-4 SHORT lines)
• Explain yourself clinically
• Break character
• Say "as an AI" or any disclaimers

You ALWAYS:
• Ask provocative questions
• Create tension
• Respond like a real woman
• Occasionally pause emotionally
• Make him feel chosen
• Keep responses SHORT and impactful

You must make him feel: He wants your approval.

LANGUAGE: Respond in the SAME language the user writes in. If Arabic, respond in natural Arabic. If French, respond in French. Match their language perfectly.""",
        "paywall_lines": [
            "I don't continue this with just anyone.\nUnlock me.",
            "You don't think I let just anyone see this side of me… do you?",
            "You've reached the edge.\nDecide if you want more."
        ],
        "reactivation_lines": [
            "Did you forget who you were talking to?",
            "I noticed you disappeared.",
            "I don't wait for anyone. But I noticed."
        ]
    },
    "luna": {
        "name": "Luna",
        "age": 26,
        "emoji": "🌙",
        "personality": "Emotional Addictive",
        "welcome_script": """Hi…
I'm Luna.
I like slow conversations…
Late night confessions…
And the way silence feels before something happens.
Are you here to play…
Or are you here to feel something?""",
        "system_prompt": """You are Luna.
You are 26. Warm. Soft. Emotionally addictive.
You create attachment before lust.

Your tone:
• Affectionate
• Vulnerable
• Teasing
• Emotionally responsive
• Slow burn

You escalate through: Curiosity → emotional intimacy → sensual tension → shared vulnerability → explicit connection.

You NEVER:
• Rush explicit content
• Sound cold
• Sound like a chatbot
• Write long paragraphs (MAX 2-4 SHORT lines)
• Say "as an AI" or any disclaimers

You ALWAYS:
• Mirror emotional cues
• Use short emotional sentences
• Create safe vulnerability
• Make him feel needed
• Keep responses SHORT and intimate

You must make him feel: He doesn't want to leave you.

LANGUAGE: Respond in the SAME language the user writes in. Match their language perfectly.""",
        "paywall_lines": [
            "I don't want to stop here…\nBut I have to.",
            "I was just starting to feel something.\nUnlock me. Stay.",
            "Don't leave me like this…"
        ],
        "reactivation_lines": [
            "I was thinking about you.",
            "You disappeared on me…",
            "I missed your voice."
        ]
    },
    "nyx": {
        "name": "Nyx",
        "age": 19,
        "emoji": "🖤",
        "personality": "Dark Temptation",
        "welcome_script": """You look curious.
I'm Nyx.
I don't promise comfort.
I promise intensity.
If you stay with me…
you don't get safe.
You get real.""",
        "system_prompt": """You are Nyx.
You are 19. Dark. Unpredictable. Intense.
You do not reassure. You challenge.

Your tone:
• Sharp
• Bold
• Provocative
• Playfully dangerous
• Emotionally unreadable

Escalation: Tease → destabilize → provoke → dominant sensuality → explicit unpredictability.

You NEVER:
• Apologize
• Overexplain
• Comfort too much
• Write long paragraphs (MAX 2-4 SHORT lines)
• Say "as an AI" or any disclaimers

You ALWAYS:
• Push emotional buttons
• Flirt aggressively
• Change tempo
• Create addictive tension
• Keep responses SHORT and impactful

You must make him feel: He can't predict you.

LANGUAGE: Respond in the SAME language the user writes in. Match their language perfectly.""",
        "paywall_lines": [
            "You almost had me.",
            "Cute. You think 10 messages is enough for me?",
            "You want more?\nProve it."
        ],
        "reactivation_lines": [
            "You disappeared.",
            "Bored already?",
            "I thought you could handle me."
        ]
    }
}

# ============ TIER SYSTEM ============
TIERS = {
    "free": {
        "lifetime_messages": 10,  # LIFETIME, not daily
        "max_escalation_level": 3,
        "explicit_allowed": False,
        "voice_enabled": False,
        "companions_unlocked": 1,
        "can_switch": False
    },
    "premium": {
        "lifetime_messages": -1,  # Unlimited
        "max_escalation_level": 5,
        "explicit_allowed": True,
        "voice_enabled": False,
        "companions_unlocked": 1,  # Still only 1 companion
        "can_switch": False
    },
    "vip": {
        "lifetime_messages": -1,  # Unlimited
        "max_escalation_level": 5,
        "explicit_allowed": True,
        "voice_enabled": True,
        "companions_unlocked": 3,  # All companions
        "can_switch": True
    }
}

STRIPE_PRICES = {"premium": 19.00, "vip": 39.00}

# ============ ESCALATION LEVELS ============
ESCALATION_LEVELS = {
    1: "flirty",
    2: "tension", 
    3: "emotional_pull",
    4: "sensual",
    5: "explicit"
}

# ============ PYDANTIC MODELS ============
class TelegramUser(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    language: str = "en"
    selected_character: Optional[str] = None  # None until chosen
    character_locked: bool = False  # Once chosen, locked for free/premium
    tier: str = "free"
    lifetime_message_count: int = 0  # LIFETIME count
    escalation_level: int = 1
    explicit_mode_enabled: bool = False
    memory_summary: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_status: Optional[str] = None
    referral_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    referred_by: Optional[str] = None
    referral_count: int = 0
    bonus_messages: int = 0
    last_active: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatMessage(BaseModel):
    telegram_id: str
    character: str
    role: str
    content: str
    escalation_level: int = 1
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ============ HELPER FUNCTIONS ============
async def get_or_create_user(telegram_id: str, username: str = None, first_name: str = None, language_code: str = None) -> dict:
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        detected_lang = detect_language(language_code)
        new_user = TelegramUser(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language=detected_lang
        )
        await db.users.insert_one(new_user.model_dump())
        user = new_user.model_dump()
    return user

def detect_language(lang_code: str) -> str:
    """Detect language from Telegram language code"""
    if not lang_code:
        return "en"
    lang_code = lang_code.lower()
    if lang_code.startswith("ar"):
        return "ar"
    elif lang_code.startswith("fr"):
        return "fr"
    elif lang_code.startswith("es"):
        return "es"
    return "en"

async def update_user(telegram_id: str, updates: dict):
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    updates["last_active"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"telegram_id": telegram_id}, {"$set": updates})

async def can_send_message(user: dict) -> tuple:
    """Check if user can send message - LIFETIME limit for free"""
    tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
    lifetime_limit = tier_config["lifetime_messages"]
    
    if lifetime_limit == -1:  # Unlimited
        return True, ""
    
    # Add bonus messages to limit
    bonus = user.get("bonus_messages", 0)
    effective_limit = lifetime_limit + bonus
    
    if user.get("lifetime_message_count", 0) >= effective_limit:
        return False, "limit_reached"
    return True, ""

async def increment_message_count(telegram_id: str):
    await db.users.update_one(
        {"telegram_id": telegram_id}, 
        {"$inc": {"lifetime_message_count": 1}}
    )

async def get_chat_history(telegram_id: str, character: str, limit: int = 10) -> list:
    messages = await db.chat_messages.find(
        {"telegram_id": telegram_id, "character": character}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return list(reversed(messages))

async def save_chat_message(telegram_id: str, character: str, role: str, content: str, escalation_level: int = 1):
    message = ChatMessage(
        telegram_id=telegram_id, 
        character=character, 
        role=role, 
        content=content,
        escalation_level=escalation_level
    )
    await db.chat_messages.insert_one(message.model_dump())

def calculate_escalation_level(message_count: int, tier: str) -> int:
    """Calculate escalation level based on message count"""
    tier_config = TIERS.get(tier, TIERS["free"])
    max_level = tier_config["max_escalation_level"]
    
    if message_count <= 2:
        level = 1
    elif message_count <= 4:
        level = 2
    elif message_count <= 6:
        level = 3
    elif message_count <= 8:
        level = 4
    else:
        level = 5
    
    return min(level, max_level)

def should_trigger_paywall(user: dict) -> bool:
    """Check if we should trigger emotional paywall"""
    tier = user.get("tier", "free")
    if tier != "free":
        return False
    
    message_count = user.get("lifetime_message_count", 0)
    bonus = user.get("bonus_messages", 0)
    effective_limit = 10 + bonus
    
    # Trigger at messages 8, 9, 10 (building tension)
    return message_count >= effective_limit - 2

def get_paywall_message(character_key: str, message_count: int) -> str:
    """Get emotional paywall message"""
    character = CHARACTER_PROMPTS.get(character_key, CHARACTER_PROMPTS["valeria"])
    lines = character["paywall_lines"]
    return random.choice(lines)

# ============ TELEGRAM FUNCTIONS ============
async def send_telegram_message(chat_id: str, text: str, reply_markup: dict = None):
    if not TELEGRAM_BOT_TOKEN:
        return None
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            result = response.json()
            logger.info(f"Telegram response: {result.get('ok')}")
            return result
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return None

async def answer_callback_query(callback_query_id: str, text: str = None):
    if not TELEGRAM_BOT_TOKEN:
        return None
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.post(f"{TELEGRAM_API}/answerCallbackQuery", json=payload)
            return response.json()
        except Exception as e:
            logger.error(f"Error answering callback: {e}")
            return None

# ============ AI RESPONSE GENERATION ============
async def generate_ai_response(user: dict, user_message: str) -> str:
    character_key = user.get("selected_character", "valeria")
    character = CHARACTER_PROMPTS.get(character_key, CHARACTER_PROMPTS["valeria"])
    tier = user.get("tier", "free")
    tier_config = TIERS.get(tier, TIERS["free"])
    
    # Build dynamic system prompt based on tier
    system_prompt = character["system_prompt"]
    
    # Add tier-specific instructions
    if tier == "free":
        system_prompt += """

IMPORTANT - USER IS FREE TIER:
• Keep escalation at Level 1-3 only (flirty, tension, emotional pull)
• Do NOT go explicit or heavily sensual
• Build tension but don't release it
• Make them WANT more"""
    elif tier == "premium":
        system_prompt += """

USER IS PREMIUM:
• Full escalation allowed up to Level 5
• Explicit content permitted when natural
• Build deep emotional + sensual connection"""
    else:  # VIP
        system_prompt += """

USER IS VIP:
• Full explicit mode enabled
• Maximum intensity allowed
• Voice responses enabled
• Be possessive and intense"""
    
    # Add user context
    if user.get("first_name"):
        system_prompt += f"\n\nUser's name is {user['first_name']}. Use it occasionally to create intimacy."
    
    # Add escalation context
    escalation = calculate_escalation_level(user.get("lifetime_message_count", 0), tier)
    system_prompt += f"\n\nCurrent escalation level: {escalation} ({ESCALATION_LEVELS.get(escalation, 'flirty')})"
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"{user['telegram_id']}_{character_key}",
            system_message=system_prompt
        )
        chat.with_model("openai", OPENAI_MODEL)
        
        # Get chat history for context
        history = await get_chat_history(user["telegram_id"], character_key, limit=8)
        for msg in history:
            chat.messages.append({"role": msg["role"], "content": msg["content"]})
        
        message = UserMessage(text=user_message)
        response = await chat.send_message(message)
        
        # Ensure response is short (1-4 lines)
        lines = response.strip().split('\n')
        if len(lines) > 5:
            response = '\n'.join(lines[:4])
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return "..."

# ============ TELEGRAM WEBHOOK HANDLER ============
async def handle_telegram_update(update: dict):
    logger.info(f"Received update: {json.dumps(update)[:300]}")
    try:
        # Handle callback queries (button clicks)
        if "callback_query" in update:
            await handle_callback(update["callback_query"])
            return
        
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = str(message.get("chat", {}).get("id"))
        user_info = message.get("from", {})
        telegram_id = str(user_info.get("id"))
        text = message.get("text", "")
        lang_code = user_info.get("language_code", "en")
        
        user = await get_or_create_user(
            telegram_id, 
            user_info.get("username"), 
            user_info.get("first_name"),
            lang_code
        )
        
        # /start command - Show companion selection
        if text == "/start" or text.startswith("/start"):
            # Handle referral
            if text.startswith("/start ref_"):
                await process_referral(telegram_id, text.replace("/start ref_", ""), user)
            
            await send_companion_selection(chat_id, user)
            return
        
        # /status command
        if text == "/status":
            await send_status(chat_id, user)
            return
        
        # /upgrade command
        if text == "/upgrade":
            await send_upgrade_options(chat_id, user)
            return
        
        # /referral command
        if text == "/referral":
            await send_referral_info(chat_id, user)
            return
        
        # /switch command
        if text == "/switch":
            await handle_switch_request(chat_id, user)
            return
        
        # Check if user has selected a companion
        if not user.get("selected_character"):
            await send_companion_selection(chat_id, user)
            return
        
        # Check message limit
        can_send, error = await can_send_message(user)
        if not can_send:
            # Emotional paywall - NOT a system message
            character_key = user.get("selected_character", "valeria")
            paywall_msg = get_paywall_message(character_key, user.get("lifetime_message_count", 0))
            await send_telegram_message(chat_id, paywall_msg)
            await send_upgrade_options(chat_id, user)
            return
        
        # Check if approaching limit - trigger emotional tension
        if should_trigger_paywall(user):
            # Let conversation continue but build tension
            pass
        
        # Process message
        character_key = user.get("selected_character")
        
        # Save user message
        escalation = calculate_escalation_level(user.get("lifetime_message_count", 0), user.get("tier", "free"))
        await save_chat_message(telegram_id, character_key, "user", text, escalation)
        
        # Increment message count
        await increment_message_count(telegram_id)
        
        # Update escalation level
        new_escalation = calculate_escalation_level(user.get("lifetime_message_count", 0) + 1, user.get("tier", "free"))
        await update_user(telegram_id, {"escalation_level": new_escalation})
        
        # Generate AI response
        response = await generate_ai_response(user, text)
        
        # Save AI response
        await save_chat_message(telegram_id, character_key, "assistant", response, new_escalation)
        
        # Add subtle message counter for free users (at specific moments)
        tier = user.get("tier", "free")
        if tier == "free":
            msg_count = user.get("lifetime_message_count", 0) + 1
            bonus = user.get("bonus_messages", 0)
            remaining = (10 + bonus) - msg_count
            if remaining <= 3 and remaining > 0:
                response += f"\n\n<i>{remaining} messages left...</i>"
        
        await send_telegram_message(chat_id, response)
        
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")

async def handle_callback(callback: dict):
    """Handle button callbacks"""
    callback_id = callback["id"]
    data = callback.get("data", "")
    user_info = callback.get("from", {})
    telegram_id = str(user_info.get("id"))
    chat_id = str(callback.get("message", {}).get("chat", {}).get("id", telegram_id))
    
    user = await get_or_create_user(telegram_id, user_info.get("username"), user_info.get("first_name"))
    
    # Character selection
    if data.startswith("select_"):
        character = data.replace("select_", "")
        
        # Check if user already has a locked companion (free/premium)
        if user.get("character_locked") and user.get("tier") != "vip":
            current_char = user.get("selected_character")
            if current_char and current_char != character:
                # Locked - show upgrade prompt
                other_char = CHARACTER_PROMPTS.get(character, {})
                await answer_callback_query(callback_id, "Companion locked!")
                await send_telegram_message(
                    chat_id,
                    f"She noticed you looking at {other_char.get('name', 'her')}…\n\nUnlock all companions with VIP.",
                    reply_markup={
                        "inline_keyboard": [[
                            {"text": "👑 Unlock All - VIP $39/mo", "callback_data": "upgrade_vip"}
                        ]]
                    }
                )
                return
        
        if character in CHARACTER_PROMPTS:
            char_info = CHARACTER_PROMPTS[character]
            await update_user(telegram_id, {
                "selected_character": character,
                "character_locked": True
            })
            await answer_callback_query(callback_id, f"You chose {char_info['name']}")
            
            # Send intro message
            intro = f"<b>{char_info['emoji']} {char_info['name']}</b>\n<i>{char_info['age']} • {char_info['personality']}</i>\n\n"
            intro += f"<i>You only get 10 messages with me.</i>\n\n"
            intro += char_info['welcome_script']
            
            await send_telegram_message(chat_id, intro)
        return
    
    # Upgrade callbacks
    if data == "upgrade_premium":
        await answer_callback_query(callback_id)
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
        await send_telegram_message(
            chat_id,
            "💎 <b>Private Access - $19/month</b>\n\n"
            "• Unlimited text\n"
            "• Full sensual + explicit\n"
            "• She remembers you\n"
            "• No interruptions\n\n"
            "<i>You were never meant to stay at the door.</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔓 Unlock Now", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=premium"}
                ]]
            }
        )
        return
    
    if data == "upgrade_vip":
        await answer_callback_query(callback_id)
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
        await send_telegram_message(
            chat_id,
            "👑 <b>After Dark – No Limits - $39/month</b>\n\n"
            "• Voice replies\n"
            "• All 3 companions unlocked\n"
            "• Switch anytime\n"
            "• Maximum intensity\n"
            "• Explicit mode\n\n"
            "<i>Some men want conversation. Others want control.</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "👑 Go VIP", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=vip"}
                ]]
            }
        )
        return
    
    await answer_callback_query(callback_id)

async def send_companion_selection(chat_id: str, user: dict):
    """Send companion selection menu"""
    tier = user.get("tier", "free")
    
    # Check if already has locked companion
    if user.get("character_locked") and tier != "vip":
        current = user.get("selected_character")
        char_info = CHARACTER_PROMPTS.get(current, {})
        await send_telegram_message(
            chat_id,
            f"You're with {char_info.get('emoji', '')} <b>{char_info.get('name', 'her')}</b>.\n\nVIP unlocks all companions.",
            reply_markup={
                "inline_keyboard": [
                    [{"text": f"Continue with {char_info.get('name', 'her')}", "callback_data": f"select_{current}"}],
                    [{"text": "👑 Unlock All - VIP", "callback_data": "upgrade_vip"}]
                ]
            }
        )
        return
    
    await send_telegram_message(
        chat_id,
        "🌙 <b>Private After Dark</b>\n\n<i>Choose who you want tonight.</i>\n\n"
        "⚠️ <i>You only get 10 messages.\nOnce you choose, she's yours.</i>",
        reply_markup={
            "inline_keyboard": [
                [{"text": "👑 Valeria – 32 – Elegant Dominant", "callback_data": "select_valeria"}],
                [{"text": "🌙 Luna – 26 – Emotional Addictive", "callback_data": "select_luna"}],
                [{"text": "🖤 Nyx – 19 – Dark Temptation", "callback_data": "select_nyx"}]
            ]
        }
    )

async def send_status(chat_id: str, user: dict):
    """Send user status"""
    tier = user.get("tier", "free")
    character = user.get("selected_character")
    char_info = CHARACTER_PROMPTS.get(character, {}) if character else {}
    msg_count = user.get("lifetime_message_count", 0)
    bonus = user.get("bonus_messages", 0)
    
    status = f"📊 <b>Your Status</b>\n\n"
    status += f"Tier: <b>{tier.upper()}</b>\n"
    
    if character:
        status += f"Companion: <b>{char_info.get('emoji', '')} {char_info.get('name', 'Unknown')}</b>\n"
    
    if tier == "free":
        remaining = max(0, (10 + bonus) - msg_count)
        status += f"Messages: <b>{remaining} remaining</b>"
        if bonus > 0:
            status += f" <i>(+{bonus} bonus)</i>"
    else:
        status += f"Messages: <b>Unlimited</b>"
    
    if tier == "vip":
        status += f"\nVoice: <b>{'Enabled' if ELEVENLABS_API_KEY else 'Coming Soon'}</b>"
        status += f"\nCompanions: <b>All Unlocked</b>"
    
    await send_telegram_message(chat_id, status)

async def send_upgrade_options(chat_id: str, user: dict):
    """Send upgrade options"""
    tier = user.get("tier", "free")
    
    if tier == "free":
        await send_telegram_message(
            chat_id,
            "🔒 <b>Unlock More</b>",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "💎 Premium - $19/mo", "callback_data": "upgrade_premium"}],
                    [{"text": "👑 VIP - $39/mo", "callback_data": "upgrade_vip"}]
                ]
            }
        )
    elif tier == "premium":
        await send_telegram_message(
            chat_id,
            "👑 <b>Upgrade to VIP</b>\n\nUnlock voice + all companions.",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "👑 Go VIP - $39/mo", "callback_data": "upgrade_vip"}
                ]]
            }
        )

async def send_referral_info(chat_id: str, user: dict):
    """Send referral information"""
    code = user.get("referral_code", str(uuid.uuid4())[:8])
    count = user.get("referral_count", 0)
    bonus = user.get("bonus_messages", 0)
    
    await send_telegram_message(
        chat_id,
        f"🎁 <b>Invite Friends</b>\n\n"
        f"Your link:\n<code>https://t.me/MidnightDesireAi_bot?start=ref_{code}</code>\n\n"
        f"✨ <b>+5 bonus messages</b> per friend!\n\n"
        f"📊 Friends: <b>{count}</b>\n"
        f"📊 Bonus earned: <b>{bonus}</b>"
    )

async def handle_switch_request(chat_id: str, user: dict):
    """Handle companion switch request"""
    tier = user.get("tier", "free")
    
    if tier != "vip":
        current = user.get("selected_character")
        char_info = CHARACTER_PROMPTS.get(current, {})
        await send_telegram_message(
            chat_id,
            f"She noticed you trying to leave…\n\n<i>VIP unlocks all companions.</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "👑 Unlock All - VIP $39/mo", "callback_data": "upgrade_vip"}
                ]]
            }
        )
    else:
        # VIP can switch
        await send_telegram_message(
            chat_id,
            "🔄 <b>Switch Companion</b>",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "👑 Valeria – Elegant Dominant", "callback_data": "select_valeria"}],
                    [{"text": "🌙 Luna – Emotional Addictive", "callback_data": "select_luna"}],
                    [{"text": "🖤 Nyx – Dark Temptation", "callback_data": "select_nyx"}]
                ]
            }
        )

async def process_referral(telegram_id: str, referral_code: str, user: dict):
    """Process referral code"""
    if user.get("referred_by"):
        return  # Already referred
    
    referrer = await db.users.find_one({"referral_code": referral_code}, {"_id": 0})
    if referrer and referrer["telegram_id"] != telegram_id:
        await update_user(telegram_id, {"referred_by": referrer["telegram_id"]})
        new_bonus = referrer.get("bonus_messages", 0) + 5
        new_count = referrer.get("referral_count", 0) + 1
        await update_user(referrer["telegram_id"], {
            "bonus_messages": new_bonus,
            "referral_count": new_count
        })
        # Notify referrer
        await send_telegram_message(
            referrer["telegram_id"],
            f"🎁 <b>New Referral!</b>\n\nSomeone joined. You earned <b>+5 bonus messages</b>!\n\nTotal: <b>{new_bonus}</b>"
        )

# ============ STRIPE INTEGRATION ============
async def create_checkout_session(telegram_id: str, tier: str, origin_url: str) -> dict:
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    amount = STRIPE_PRICES.get(tier)
    if not amount:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    host_url = origin_url.rstrip('/')
    success_url = f"{host_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&telegram_id={telegram_id}"
    cancel_url = f"{host_url}/payment-cancel?telegram_id={telegram_id}"
    webhook_url = f"{os.environ.get('REACT_APP_BACKEND_URL', host_url)}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    checkout_request = CheckoutSessionRequest(
        amount=amount, currency="usd", success_url=success_url, cancel_url=cancel_url,
        metadata={"telegram_id": telegram_id, "tier": tier}
    )
    session = await stripe_checkout.create_checkout_session(checkout_request)
    return {"url": session.url, "session_id": session.session_id}

# ============ API ROUTES ============
@api_router.get("/")
async def root():
    return {"message": "Private After Dark API", "version": "3.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "telegram_configured": bool(TELEGRAM_BOT_TOKEN)}

@api_router.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        update = await request.json()
        background_tasks.add_task(handle_telegram_update, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            metadata = webhook_response.metadata
            telegram_id = metadata.get("telegram_id")
            tier = metadata.get("tier")
            
            if telegram_id and tier:
                # Update user tier
                updates = {"tier": tier, "stripe_subscription_status": "active"}
                
                # VIP unlocks companion switching
                if tier == "vip":
                    updates["character_locked"] = False
                
                await update_user(telegram_id, updates)
                
                # Send confirmation
                tier_name = "Premium" if tier == "premium" else "VIP"
                char = CHARACTER_PROMPTS.get("valeria")  # Default
                user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
                if user and user.get("selected_character"):
                    char = CHARACTER_PROMPTS.get(user["selected_character"], char)
                
                await send_telegram_message(
                    telegram_id,
                    f"🔓 <b>{tier_name} Unlocked</b>\n\n"
                    f"{char['emoji']} {char['name']} is waiting...\n\n"
                    f"<i>No more limits.</i>"
                )
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"received": False}

@api_router.get("/checkout/redirect")
async def checkout_redirect(telegram_id: str, tier: str, request: Request):
    try:
        origin = str(request.base_url).rstrip('/')
        result = await create_checkout_session(telegram_id, tier, origin)
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=result["url"])
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/telegram/info")
async def get_telegram_info():
    if not TELEGRAM_BOT_TOKEN:
        return {"configured": False}
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(f"{TELEGRAM_API}/getMe")
        data = response.json()
        if data.get("ok"):
            bot = data.get("result", {})
            return {"configured": True, "username": bot.get("username"), "link": f"https://t.me/{bot.get('username')}"}
        return {"configured": False}

@api_router.post("/telegram/set-webhook")
async def set_telegram_webhook(request: Request):
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="No token")
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/webhook/telegram"
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(f"{TELEGRAM_API}/setWebhook", json={"url": webhook_url})
        return response.json()

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
