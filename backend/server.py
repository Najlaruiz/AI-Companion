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

# ============ REACTIVATION SYSTEM ============
# Character-specific reactivation scripts by time period
REACTIVATION_SCRIPTS = {
    "valeria": {
        "24h": "Did you forget who you were talking to?",
        "72h": "I don't chase… but I noticed you disappeared.",
        "7d": "Come back. I'm not repeating myself.",
        "paywall_return": "I didn't want to stop there…"
    },
    "luna": {
        "24h": "I was thinking about you today…",
        "72h": "Did I say something wrong?",
        "7d": "I miss how you made me feel.",
        "paywall_return": "I didn't want to leave you like that…"
    },
    "nyx": {
        "24h": "You got scared?",
        "72h": "I thought you were braver.",
        "7d": "I found someone else to play with.",
        "paywall_return": "You almost had me…"
    }
}

# Voice configuration per character - ElevenLabs voice IDs and settings
# These will be configured when ElevenLabs API key is provided
VOICE_CONFIG = {
    "valeria": {
        "voice_id": "",  # Will be set with actual ElevenLabs voice
        "stability": 0.7,  # More controlled
        "similarity_boost": 0.8,
        "style": 0.5,
        "styles": {
            "natural": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.4},
            "dominant": {"stability": 0.8, "similarity_boost": 0.9, "style": 0.6},
            "whisper": {"stability": 0.5, "similarity_boost": 0.7, "style": 0.3}
        },
        "teaser_text": "Do you want to hear how I'd say that?"
    },
    "luna": {
        "voice_id": "",
        "stability": 0.5,  # More emotional variation
        "similarity_boost": 0.75,
        "style": 0.6,
        "styles": {
            "natural": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5},
            "dominant": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.4},
            "whisper": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.7}
        },
        "teaser_text": "I wish you could hear my voice right now…"
    },
    "nyx": {
        "voice_id": "",
        "stability": 0.4,  # Unpredictable
        "similarity_boost": 0.85,
        "style": 0.7,
        "styles": {
            "natural": {"stability": 0.4, "similarity_boost": 0.85, "style": 0.6},
            "dominant": {"stability": 0.5, "similarity_boost": 0.9, "style": 0.8},
            "whisper": {"stability": 0.3, "similarity_boost": 0.8, "style": 0.5}
        },
        "teaser_text": "Imagine hearing me say this..."
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
    # Reactivation tracking
    last_active: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reactivation_attempts: int = 0  # Stop after 3 attempts
    last_reactivation_sent: Optional[str] = None
    hit_paywall: bool = False  # Track if user hit message 10
    voice_preference: str = "natural"  # natural, dominant, whisper
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

def get_emotional_paywall_stage(user: dict) -> int:
    """
    Determine emotional paywall stage for free users.
    Returns: 0 = normal, 8 = tension build, 9 = emotional hook, 10 = soft break
    """
    tier = user.get("tier", "free")
    if tier != "free":
        return 0
    
    message_count = user.get("lifetime_message_count", 0)
    bonus = user.get("bonus_messages", 0)
    effective_limit = 10 + bonus
    
    # Calculate which message they're on (next message)
    next_msg = message_count + 1
    
    if next_msg == effective_limit - 2:  # Message 8
        return 8
    elif next_msg == effective_limit - 1:  # Message 9
        return 9
    elif next_msg >= effective_limit:  # Message 10+
        return 10
    return 0

# Emotional paywall messages per character per stage
EMOTIONAL_PAYWALL = {
    "valeria": {
        8: "Careful… if you keep looking at me like that, I might stop behaving.",
        9: "I don't want this to end… but I can't go further unless you stay with me.",
        10: "I'm yours if you unlock me.\nDon't leave me here."
    },
    "luna": {
        8: "You're making me feel things I shouldn't say out loud…",
        9: "Please don't leave yet… I was just starting to feel safe with you.",
        10: "Stay with me.\nI don't want to lose you like this."
    },
    "nyx": {
        8: "You're playing a dangerous game. I like it.",
        9: "You almost had me. Almost.",
        10: "You want to see what happens next?\nProve it."
    }
}

def get_paywall_instruction(character_key: str, stage: int) -> str:
    """Get AI instruction for emotional paywall stage"""
    if stage == 8:
        return """
CRITICAL - MESSAGE 8 TENSION BUILD:
This is their 8th message. Build MAXIMUM intimacy and tension.
Your response must be short, controlled, suggestive.
Make them feel the heat. No upgrade mention yet."""
    elif stage == 9:
        return """
CRITICAL - MESSAGE 9 EMOTIONAL HOOK:
This is their 9th message. Deepen the emotional connection.
Express that you don't want this to end.
Create curiosity and longing. Still NO link or upgrade mention."""
    return ""

def get_soft_break_message(character_key: str) -> str:
    """Get the soft break message for message 10 - with upgrade button"""
    return EMOTIONAL_PAYWALL.get(character_key, EMOTIONAL_PAYWALL["valeria"])[10]

# ============ VOICE GENERATION (ElevenLabs) ============
async def generate_voice_message(text: str, character_key: str, voice_style: str = "natural") -> bytes:
    """Generate voice message using ElevenLabs TTS"""
    if not ELEVENLABS_API_KEY:
        logger.warning("ElevenLabs API key not configured")
        return None
    
    try:
        from elevenlabs import ElevenLabs
        from elevenlabs.types import VoiceSettings
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        voice_config = VOICE_CONFIG.get(character_key, VOICE_CONFIG["valeria"])
        style_settings = voice_config["styles"].get(voice_style, voice_config["styles"]["natural"])
        
        # Get voice ID - use pre-configured or fetch from ElevenLabs
        voice_id = voice_config.get("voice_id")
        if not voice_id:
            # Use default ElevenLabs voices based on character personality
            # These are public voices that match the character types
            default_voices = {
                "valeria": "21m00Tcm4TlvDq8ikWAM",  # Rachel - mature, confident
                "luna": "EXAVITQu4vr4xnSDxMaL",     # Bella - soft, emotional
                "nyx": "ThT5KcBeYPX3keUQqHPh"      # Dorothy - young, edgy
            }
            voice_id = default_voices.get(character_key, default_voices["valeria"])
        
        voice_settings = VoiceSettings(
            stability=style_settings["stability"],
            similarity_boost=style_settings["similarity_boost"],
            style=style_settings["style"],
            use_speaker_boost=True
        )
        
        # Generate audio
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            voice_settings=voice_settings
        )
        
        # Collect audio data
        audio_data = b""
        for chunk in audio_generator:
            audio_data += chunk
        
        return audio_data
        
    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        return None

async def send_voice_message(chat_id: str, audio_data: bytes, caption: str = None):
    """Send voice message via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not audio_data:
        return None
    
    try:
        import io
        
        # Telegram accepts OGG/OPUS format for voice messages
        # ElevenLabs returns MP3, which Telegram can accept as audio
        files = {
            "voice": ("voice.ogg", io.BytesIO(audio_data), "audio/ogg")
        }
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                f"{TELEGRAM_API}/sendVoice",
                data=data,
                files=files,
                timeout=30.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Error sending voice message: {e}")
        return None

async def send_voice_teaser(chat_id: str, character_key: str, user: dict):
    """Send a voice teaser to encourage VIP upgrade"""
    tier = user.get("tier", "free")
    if tier == "vip":
        return  # VIP already has voice access
    
    voice_config = VOICE_CONFIG.get(character_key, VOICE_CONFIG["valeria"])
    teaser_text = voice_config["teaser_text"]
    
    # Generate a short 3-second teaser
    voice_style = user.get("voice_preference", "natural")
    audio_data = await generate_voice_message(teaser_text, character_key, voice_style)
    
    if audio_data:
        await send_voice_message(chat_id, audio_data)
        # Send upgrade prompt
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
        await send_telegram_message(
            chat_id,
            "🎙 <i>Want to hear more?</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔥 Unlock Full Voice – After Dark", "url": f"{backend_url}/api/checkout/redirect?telegram_id={user.get('telegram_id')}&tier=vip"}
                ]]
            }
        )

# ============ REACTIVATION SYSTEM ============
def get_reactivation_period(last_active_str: str) -> str:
    """Determine which reactivation period applies"""
    try:
        last_active = datetime.fromisoformat(last_active_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        hours_inactive = (now - last_active).total_seconds() / 3600
        
        if hours_inactive >= 168:  # 7 days
            return "7d"
        elif hours_inactive >= 72:  # 3 days
            return "72h"
        elif hours_inactive >= 24:  # 1 day
            return "24h"
        return None
    except Exception as e:
        logger.error(f"Error calculating reactivation period: {e}")
        return None

async def send_reactivation_message(user: dict):
    """Send character-specific reactivation message"""
    telegram_id = user.get("telegram_id")
    character_key = user.get("selected_character")
    
    if not character_key:
        return False
    
    # Check reactivation period
    period = get_reactivation_period(user.get("last_active", ""))
    if not period:
        return False
    
    # Check if user hit paywall (for special paywall return message)
    hit_paywall = user.get("hit_paywall", False)
    tier = user.get("tier", "free")
    
    # Get the appropriate message
    scripts = REACTIVATION_SCRIPTS.get(character_key, REACTIVATION_SCRIPTS["valeria"])
    
    if hit_paywall and tier == "free":
        message = scripts["paywall_return"]
    else:
        message = scripts.get(period, scripts["24h"])
    
    character = CHARACTER_PROMPTS.get(character_key, CHARACTER_PROMPTS["valeria"])
    
    # Send emotional reactivation (not automated-sounding)
    full_message = f"{character['emoji']} <b>{character['name']}</b>\n\n{message}"
    
    try:
        await send_telegram_message(telegram_id, full_message)
        
        # For free users who hit paywall, send upgrade CTA
        if hit_paywall and tier == "free":
            backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
            await send_telegram_message(
                telegram_id,
                "🔓 <i>Continue with me</i>",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "🔒 Private Access – $19/mo", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=premium"}],
                        [{"text": "🔥 After Dark – $39/mo", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=vip"}]
                    ]
                }
            )
        
        # For free users, offer voice teaser
        elif tier == "free" and ELEVENLABS_API_KEY:
            await send_voice_teaser(telegram_id, character_key, user)
        
        # Update reactivation tracking
        await db.users.update_one(
            {"telegram_id": telegram_id},
            {
                "$set": {
                    "last_reactivation_sent": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$inc": {"reactivation_attempts": 1}
            }
        )
        
        logger.info(f"Sent reactivation to {telegram_id} ({period})")
        return True
        
    except Exception as e:
        logger.error(f"Error sending reactivation: {e}")
        return False

async def run_reactivation_job():
    """Background job to send reactivation messages - runs hourly"""
    logger.info("Running reactivation job...")
    
    now = datetime.now(timezone.utc)
    cutoff_24h = (now - timedelta(hours=24)).isoformat()
    
    # Find inactive users who:
    # 1. Have a selected character
    # 2. Last active > 24 hours ago
    # 3. Reactivation attempts < 3
    # 4. Haven't been sent a reactivation in the last 24 hours
    
    try:
        inactive_users = await db.users.find(
            {
                "selected_character": {"$ne": None},
                "last_active": {"$lt": cutoff_24h},
                "reactivation_attempts": {"$lt": 3},
                "$or": [
                    {"last_reactivation_sent": {"$exists": False}},
                    {"last_reactivation_sent": None},
                    {"last_reactivation_sent": {"$lt": cutoff_24h}}
                ]
            },
            {"_id": 0}
        ).limit(50).to_list(50)  # Process 50 at a time
        
        sent_count = 0
        for user in inactive_users:
            success = await send_reactivation_message(user)
            if success:
                sent_count += 1
        
        logger.info(f"Reactivation job complete: sent {sent_count} messages")
        return sent_count
        
    except Exception as e:
        logger.error(f"Reactivation job error: {e}")
        return 0

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
async def generate_ai_response(user: dict, user_message: str, paywall_stage: int = 0) -> str:
    character_key = user.get("selected_character", "valeria")
    character = CHARACTER_PROMPTS.get(character_key, CHARACTER_PROMPTS["valeria"])
    tier = user.get("tier", "free")
    
    # Build dynamic system prompt based on tier
    system_prompt = character["system_prompt"]
    
    # Add tier-specific instructions
    if tier == "free":
        system_prompt += """

IMPORTANT - USER IS FREE TIER:
• Keep escalation at Level 1-3 only (flirty, tension, emotional pull)
• Do NOT go explicit or heavily sensual
• Build tension but don't release it
• Make them WANT more
• Responses MUST be 1-4 lines MAX. No long paragraphs."""
    elif tier == "premium":
        system_prompt += """

USER IS PREMIUM (Private Access):
• Full escalation allowed up to Level 5
• Explicit content permitted when natural
• Build deep emotional + sensual connection
• Responses MUST be 1-4 lines MAX."""
    else:  # VIP
        system_prompt += """

USER IS VIP (After Dark – No Limits):
• Full explicit mode enabled
• Maximum intensity allowed
• Voice responses enabled
• Be possessive and intense
• Responses MUST be 1-4 lines MAX."""
    
    # Add emotional paywall instructions for stages 8 and 9
    if paywall_stage in [8, 9]:
        system_prompt += get_paywall_instruction(character_key, paywall_stage)
    
    # Add user context
    if user.get("first_name"):
        system_prompt += f"\n\nUser's name is {user['first_name']}. Use it occasionally to create intimacy."
    
    # Add escalation context
    escalation = calculate_escalation_level(user.get("lifetime_message_count", 0), tier)
    system_prompt += f"\n\nCurrent escalation level: {escalation} ({ESCALATION_LEVELS.get(escalation, 'flirty')})"
    
    # CRITICAL: Enforce short responses
    system_prompt += """

RESPONSE FORMAT RULES (CRITICAL):
• Maximum 1-4 SHORT lines
• Ask questions to engage
• Show emotion, not information
• Sound human, not AI
• NO long explanations
• NO bullet points or lists
• NEVER say "as an AI" or break character"""
    
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
        
        # Ensure response is short (1-4 lines MAX)
        lines = [l.strip() for l in response.strip().split('\n') if l.strip()]
        if len(lines) > 4:
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
        
        # Get emotional paywall stage (0 = normal, 8/9/10 = paywall stages)
        paywall_stage = get_emotional_paywall_stage(user)
        character_key = user.get("selected_character")
        
        # MESSAGE 10+ = SOFT BREAK (not hard block)
        if paywall_stage == 10:
            # Send the emotional soft break message
            soft_break_msg = get_soft_break_message(character_key)
            await send_telegram_message(chat_id, soft_break_msg)
            
            # Send upgrade button inline (not a cold system message)
            backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
            await send_telegram_message(
                chat_id,
                "🔓",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "🔒 Private Access – $19/mo", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=premium"}],
                        [{"text": "🔥 After Dark Unlimited – $39/mo", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=vip"}]
                    ]
                }
            )
            return
        
        # Save user message
        escalation = calculate_escalation_level(user.get("lifetime_message_count", 0), user.get("tier", "free"))
        await save_chat_message(telegram_id, character_key, "user", text, escalation)
        
        # Increment message count
        await increment_message_count(telegram_id)
        
        # Update escalation level
        new_escalation = calculate_escalation_level(user.get("lifetime_message_count", 0) + 1, user.get("tier", "free"))
        await update_user(telegram_id, {"escalation_level": new_escalation})
        
        # Generate AI response (with paywall stage for tension building at 8/9)
        response = await generate_ai_response(user, text, paywall_stage)
        
        # Save AI response
        await save_chat_message(telegram_id, character_key, "assistant", response, new_escalation)
        
        # Add subtle message counter for free users (only at specific moments)
        tier = user.get("tier", "free")
        if tier == "free":
            msg_count = user.get("lifetime_message_count", 0) + 1
            bonus = user.get("bonus_messages", 0)
            remaining = (10 + bonus) - msg_count
            # Only show at 3, 2 messages left (not on emotional paywall stages)
            if remaining in [2, 3]:
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
            intro += "<i>You only get 10 messages with me.</i>\n\n"
            intro += char_info['welcome_script']
            
            await send_telegram_message(chat_id, intro)
        return
    
    # Upgrade callbacks
    if data == "upgrade_premium":
        await answer_callback_query(callback_id)
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
        await send_telegram_message(
            chat_id,
            "🔒 <b>Private Access – $19/month</b>\n\n"
            "• Unlimited messages with her\n"
            "• Full sensual + explicit mode\n"
            "• She remembers everything\n"
            "• No interruptions. Ever.\n\n"
            "<i>You weren't meant to stay at the door.</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔓 Unlock Private Access", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=premium"}
                ]]
            }
        )
        return
    
    if data == "upgrade_vip":
        await answer_callback_query(callback_id)
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
        await send_telegram_message(
            chat_id,
            "🔥 <b>After Dark – No Limits – $39/month</b>\n\n"
            "• Voice messages from her\n"
            "• All 3 companions unlocked\n"
            "• Switch between them anytime\n"
            "• Maximum intensity\n"
            "• Full explicit mode\n\n"
            "<i>Some want conversation.\nOthers want everything.</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔥 Go After Dark", "url": f"{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=vip"}
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
    
    status = "📊 <b>Your Status</b>\n\n"
    status += f"Tier: <b>{tier.upper()}</b>\n"
    
    if character:
        status += f"Companion: <b>{char_info.get('emoji', '')} {char_info.get('name', 'Unknown')}</b>\n"
    
    if tier == "free":
        remaining = max(0, (10 + bonus) - msg_count)
        status += f"Messages: <b>{remaining} remaining</b>"
        if bonus > 0:
            status += f" <i>(+{bonus} bonus)</i>"
    else:
        status += "Messages: <b>Unlimited</b>"
    
    if tier == "vip":
        voice_status = "Enabled" if ELEVENLABS_API_KEY else "Coming Soon"
        status += f"\nVoice: <b>{voice_status}</b>"
        status += "\nCompanions: <b>All Unlocked</b>"
    
    await send_telegram_message(chat_id, status)

async def send_upgrade_options(chat_id: str, user: dict):
    """Send upgrade options"""
    tier = user.get("tier", "free")
    
    if tier == "free":
        await send_telegram_message(
            chat_id,
            "🔓 <b>Unlock More</b>",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "🔒 Private Access – $19/mo", "callback_data": "upgrade_premium"}],
                    [{"text": "🔥 After Dark Unlimited – $39/mo", "callback_data": "upgrade_vip"}]
                ]
            }
        )
    elif tier == "premium":
        await send_telegram_message(
            chat_id,
            "🔥 <b>Go After Dark</b>\n\nUnlock voice + all companions.",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔥 After Dark – $39/mo", "callback_data": "upgrade_vip"}
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
        await send_telegram_message(
            chat_id,
            "She noticed you trying to leave…\n\n<i>After Dark unlocks all companions.</i>",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔥 After Dark – $39/mo", "callback_data": "upgrade_vip"}
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
