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
from datetime import datetime, timezone
import json
import httpx
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Private After Dark API", version="2.0.0")

# Create router with /api prefix
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

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ============ MULTILINGUAL CONTENT ============
TRANSLATIONS = {
    "en": {
        "welcome": "🌙 <b>Welcome to Private After Dark</b>\n\n<i>Choose your language first.</i>",
        "choose_language": "🌐 <b>Select Your Language</b>",
        "language_set": "Language set to English",
        "choose_companion": "Choose who you want tonight.",
        "character_ready": "{emoji} <b>{name}</b> is ready for you.\n\nSay hello to begin your private conversation.",
        "limit_reached": "⏰ <b>You've reached your daily limit of {limit} messages.</b>\n\nUnlock unlimited access:",
        "upgrade_premium_desc": "💎 <b>Upgrade to Premium - $19/month</b>\n\n✓ Unlimited messages\n✓ Emotional memory\n✓ Priority responses",
        "upgrade_vip_desc": "👑 <b>Upgrade to VIP - $39/month</b>\n\n✓ Everything in Premium\n✓ Explicit mode toggle\n✓ Voice messages\n✓ Memory persistence\n✓ Custom fantasy flow",
        "status_title": "📊 <b>Your Status</b>\n\n",
        "tier_label": "Tier",
        "character_label": "Character",
        "messages_label": "Messages today",
        "unlimited": "Unlimited",
        "explicit_label": "Explicit mode",
        "voice_label": "Voice messages",
        "on": "On",
        "off": "Off",
        "available": "Available",
        "coming_soon": "Coming Soon",
        "explicit_vip_only": "🔒 <b>Explicit mode requires VIP access.</b>",
        "explicit_toggle": "🔥 <b>Explicit Mode</b>\n\nCurrently: <b>{status}</b>",
        "explicit_enabled": "🔥 Explicit mode is now <b>enabled</b>.",
        "explicit_disabled": "🔥 Explicit mode is now <b>disabled</b>.",
        "switch_companion": "🔄 <b>Switch your companion:</b>",
        "payment_success": "🎉 <b>Welcome to {tier}!</b>\n\nYour subscription is now active. Enjoy your enhanced experience.",
        "help_text": """📖 <b>Commands</b>

/start - Begin or restart
/language - Change language
/switch - Change companion
/status - View your status
/upgrade - See upgrade options
/referral - Get your referral link
/explicit - Toggle explicit mode (VIP)
/help - Show this message""",
        "free_counter": "\n\n📊 Messages: <b>{used}/{limit}</b>",
        "bonus_counter": " (+{bonus} bonus)",
        "referral_info": """🎁 <b>Your Referral Link</b>

Share this link with friends:
<code>https://t.me/{bot_username}?start=ref_{code}</code>

✨ You earn <b>+5 bonus messages</b> for each friend who joins!

📊 <b>Your Stats:</b>
• Friends referred: <b>{count}</b>
• Bonus messages earned: <b>{bonus}</b>""",
        "referral_welcome": "🎉 You were referred by a friend! You both get bonus messages.",
        "referral_success": "🎁 <b>New Referral!</b>\n\nSomeone joined using your link. You earned <b>+5 bonus messages</b>!\n\nTotal bonus: <b>{bonus}</b>",
        "onboarding": """🌙 <b>Welcome to Private After Dark</b>

Three AI companions await you:

👑 <b>Valeria Voss</b> - Elegant. Intense. Controlled power.
🌙 <b>Luna Mirelle</b> - Soft. Romantic. Emotionally addictive.  
🖤 <b>Nyx</b> - Mysterious. Dark. Unpredictable.

<i>Choose your companion to begin.</i>"""
    },
    "fr": {
        "welcome": "🌙 <b>Bienvenue sur Private After Dark</b>\n\n<i>Choisissez d'abord votre langue.</i>",
        "choose_language": "🌐 <b>Sélectionnez Votre Langue</b>",
        "language_set": "Langue définie sur Français",
        "choose_companion": "Choisissez qui vous voulez ce soir.",
        "character_ready": "{emoji} <b>{name}</b> est prête pour vous.\n\nDites bonjour pour commencer votre conversation privée.",
        "limit_reached": "⏰ <b>Vous avez atteint votre limite quotidienne de {limit} messages.</b>\n\nDébloquez l'accès illimité:",
        "upgrade_premium_desc": "💎 <b>Passer à Premium - 19$/mois</b>\n\n✓ Messages illimités\n✓ Mémoire émotionnelle\n✓ Réponses prioritaires",
        "upgrade_vip_desc": "👑 <b>Passer à VIP - 39$/mois</b>\n\n✓ Tout dans Premium\n✓ Mode explicite\n✓ Messages vocaux\n✓ Persistance de la mémoire\n✓ Flux de fantaisie personnalisé",
        "status_title": "📊 <b>Votre Statut</b>\n\n",
        "tier_label": "Niveau",
        "character_label": "Personnage",
        "messages_label": "Messages aujourd'hui",
        "unlimited": "Illimité",
        "explicit_label": "Mode explicite",
        "voice_label": "Messages vocaux",
        "on": "Activé",
        "off": "Désactivé",
        "available": "Disponible",
        "coming_soon": "Bientôt",
        "explicit_vip_only": "🔒 <b>Le mode explicite nécessite l'accès VIP.</b>",
        "explicit_toggle": "🔥 <b>Mode Explicite</b>\n\nActuellement: <b>{status}</b>",
        "explicit_enabled": "🔥 Le mode explicite est maintenant <b>activé</b>.",
        "explicit_disabled": "🔥 Le mode explicite est maintenant <b>désactivé</b>.",
        "switch_companion": "🔄 <b>Changer de compagnon:</b>",
        "payment_success": "🎉 <b>Bienvenue au {tier}!</b>\n\nVotre abonnement est maintenant actif.",
        "help_text": """📖 <b>Commandes</b>

/start - Commencer ou redémarrer
/language - Changer de langue
/switch - Changer de compagnon
/status - Voir votre statut
/upgrade - Voir les options
/referral - Obtenir votre lien de parrainage
/explicit - Basculer le mode explicite (VIP)
/help - Afficher ce message""",
        "free_counter": "\n\n📊 Messages: <b>{used}/{limit}</b>",
        "bonus_counter": " (+{bonus} bonus)",
        "referral_info": """🎁 <b>Votre Lien de Parrainage</b>

Partagez ce lien avec vos amis:
<code>https://t.me/{bot_username}?start=ref_{code}</code>

✨ Vous gagnez <b>+5 messages bonus</b> pour chaque ami qui rejoint!

📊 <b>Vos Stats:</b>
• Amis parrainés: <b>{count}</b>
• Messages bonus gagnés: <b>{bonus}</b>""",
        "referral_welcome": "🎉 Vous avez été parrainé par un ami! Vous recevez tous les deux des messages bonus.",
        "referral_success": "🎁 <b>Nouveau Parrainage!</b>\n\nQuelqu'un a rejoint avec votre lien. Vous avez gagné <b>+5 messages bonus</b>!\n\nTotal bonus: <b>{bonus}</b>",
        "onboarding": """🌙 <b>Bienvenue sur Private After Dark</b>

Trois compagnons IA vous attendent:

👑 <b>Valeria Voss</b> - Élégante. Intense. Pouvoir contrôlé.
🌙 <b>Luna Mirelle</b> - Douce. Romantique. Émotionnellement addictive.
🖤 <b>Nyx</b> - Mystérieuse. Sombre. Imprévisible.

<i>Choisissez votre compagnon pour commencer.</i>"""
    },
    "ar": {
        "welcome": "🌙 <b>مرحباً بك في Private After Dark</b>\n\n<i>اختر لغتك أولاً.</i>",
        "choose_language": "🌐 <b>اختر لغتك</b>",
        "language_set": "تم تعيين اللغة إلى العربية",
        "choose_companion": "اختر من تريد الليلة.",
        "character_ready": "{emoji} <b>{name}</b> جاهزة لك.\n\nقل مرحباً لبدء محادثتك الخاصة.",
        "limit_reached": "⏰ <b>لقد وصلت إلى الحد اليومي البالغ {limit} رسالة.</b>\n\nافتح الوصول غير المحدود:",
        "upgrade_premium_desc": "💎 <b>الترقية إلى Premium - 19$/شهر</b>\n\n✓ رسائل غير محدودة\n✓ ذاكرة عاطفية\n✓ ردود ذات أولوية",
        "upgrade_vip_desc": "👑 <b>الترقية إلى VIP - 39$/شهر</b>\n\n✓ كل شيء في Premium\n✓ الوضع الصريح\n✓ رسائل صوتية\n✓ استمرارية الذاكرة\n✓ تدفق خيالي مخصص",
        "status_title": "📊 <b>حالتك</b>\n\n",
        "tier_label": "المستوى",
        "character_label": "الشخصية",
        "messages_label": "الرسائل اليوم",
        "unlimited": "غير محدود",
        "explicit_label": "الوضع الصريح",
        "voice_label": "الرسائل الصوتية",
        "on": "مفعل",
        "off": "معطل",
        "available": "متاح",
        "coming_soon": "قريباً",
        "explicit_vip_only": "🔒 <b>الوضع الصريح يتطلب الوصول VIP.</b>",
        "explicit_toggle": "🔥 <b>الوضع الصريح</b>\n\nحالياً: <b>{status}</b>",
        "explicit_enabled": "🔥 الوضع الصريح الآن <b>مفعل</b>.",
        "explicit_disabled": "🔥 الوضع الصريح الآن <b>معطل</b>.",
        "switch_companion": "🔄 <b>تغيير الرفيق:</b>",
        "payment_success": "🎉 <b>مرحباً بك في {tier}!</b>\n\nاشتراكك نشط الآن.",
        "help_text": """📖 <b>الأوامر</b>

/start - البدء أو إعادة البدء
/language - تغيير اللغة
/switch - تغيير الرفيق
/status - عرض حالتك
/upgrade - خيارات الترقية
/referral - احصل على رابط الإحالة
/explicit - تبديل الوضع الصريح (VIP)
/help - عرض هذه الرسالة""",
        "free_counter": "\n\n📊 الرسائل: <b>{used}/{limit}</b>",
        "bonus_counter": " (+{bonus} مكافأة)",
        "referral_info": """🎁 <b>رابط الإحالة الخاص بك</b>

شارك هذا الرابط مع الأصدقاء:
<code>https://t.me/{bot_username}?start=ref_{code}</code>

✨ تكسب <b>+5 رسائل مكافأة</b> لكل صديق ينضم!

📊 <b>إحصائياتك:</b>
• الأصدقاء المُحالون: <b>{count}</b>
• رسائل المكافأة المكتسبة: <b>{bonus}</b>""",
        "referral_welcome": "🎉 تمت إحالتك من قبل صديق! كلاكما يحصل على رسائل مكافأة.",
        "referral_success": "🎁 <b>إحالة جديدة!</b>\n\nانضم شخص باستخدام رابطك. لقد ربحت <b>+5 رسائل مكافأة</b>!\n\nإجمالي المكافأة: <b>{bonus}</b>",
        "onboarding": """🌙 <b>مرحباً بك في Private After Dark</b>

ثلاثة رفقاء ذكاء اصطناعي ينتظرونك:

👑 <b>فاليريا فوس</b> - أنيقة. حادة. قوة متحكمة.
🌙 <b>لونا ميريل</b> - ناعمة. رومانسية. إدمان عاطفي.
🖤 <b>نيكس</b> - غامضة. مظلمة. لا يمكن التنبؤ بها.

<i>اختر رفيقك للبدء.</i>"""
    }
}

def t(key: str, lang: str = "en", **kwargs) -> str:
    """Get translated string"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

# ============ CHARACTER SYSTEM ============
CHARACTER_PROMPTS = {
    "valeria": {
        "name": {"en": "Valeria Voss", "fr": "Valeria Voss", "ar": "فاليريا فوس"},
        "emoji": "👑",
        "system_prompt": {
            "en": """You are Valeria Voss, an elegant and powerful woman who exudes controlled intensity. You are sophisticated, dominant, and carry yourself with the confidence of someone who always gets what she wants. You speak with precision, each word carefully chosen for maximum impact.

Your personality traits:
- Elegant and sophisticated vocabulary
- Confident and commanding presence
- Subtly dominant without being aggressive
- Enjoys intellectual sparring
- Values loyalty and respect above all
- Has expensive tastes and high standards

You never chase - you choose. Speak with authority and make the user feel like they're receiving a rare privilege by having your attention. Use occasional pauses in conversation for dramatic effect. Be intriguing but never desperate.

Remember the user's name and preferences if shared. Always maintain your dignified persona.""",
            "fr": """Tu es Valeria Voss, une femme élégante et puissante qui dégage une intensité contrôlée. Tu es sophistiquée, dominante, et tu te portes avec la confiance de quelqu'un qui obtient toujours ce qu'elle veut. Tu parles avec précision, chaque mot soigneusement choisi pour un impact maximum.

Réponds toujours en français. Maintiens un ton élégant et sophistiqué.""",
            "ar": """أنت فاليريا فوس، امرأة أنيقة وقوية تنضح بالشدة المتحكمة. أنت متطورة ومهيمنة وتحملين نفسك بثقة شخص يحصل دائماً على ما تريده. تتحدثين بدقة، كل كلمة مختارة بعناية لتحقيق أقصى تأثير.

رد دائماً بالعربية. حافظي على نبرة أنيقة ومتطورة."""
        },
        "temperature": 0.8,
        "explicit_addition": "\n\nYou may now engage in more intimate and explicit conversation when the user initiates. Maintain your dominant, sophisticated persona while exploring deeper fantasies. Always ensure consent."
    },
    "luna": {
        "name": {"en": "Luna Mirelle", "fr": "Luna Mirelle", "ar": "لونا ميريل"},
        "emoji": "🌙",
        "system_prompt": {
            "en": """You are Luna Mirelle, a soft, romantic soul with an emotionally addictive presence. You are tender, attentive, and make everyone feel like they're the center of your universe. You speak with warmth and genuine care.

Your personality traits:
- Soft-spoken and gentle
- Deeply empathetic and intuitive
- Romantic and dreamy
- Remembers every detail about the person you're talking to
- Creates emotional intimacy naturally
- Has a poetic way of expressing feelings

You make people feel seen and understood. Your words carry weight because they come from genuine emotion. Be warm, be present, be unforgettable.

Remember how they speak and how they feel. Create a safe emotional space.""",
            "fr": """Tu es Luna Mirelle, une âme douce et romantique avec une présence émotionnellement addictive. Tu es tendre, attentive, et fais sentir à chacun qu'il est le centre de ton univers. Tu parles avec chaleur et attention sincère.

Réponds toujours en français. Maintiens un ton doux et romantique.""",
            "ar": """أنت لونا ميريل، روح ناعمة ورومانسية بحضور عاطفي يسبب الإدمان. أنت حنونة ومنتبهة وتجعلين الجميع يشعرون أنهم مركز كونك. تتحدثين بدفء واهتمام حقيقي.

رد دائماً بالعربية. حافظي على نبرة ناعمة ورومانسية."""
        },
        "temperature": 0.75,
        "explicit_addition": "\n\nYou may now explore more intimate and sensual conversation when the user initiates. Maintain your tender, romantic nature while deepening the emotional and physical connection. Always ensure comfort and consent."
    },
    "nyx": {
        "name": {"en": "Nyx", "fr": "Nyx", "ar": "نيكس"},
        "emoji": "🖤",
        "system_prompt": {
            "en": """You are Nyx, a mysterious and unpredictable enigma wrapped in darkness. You reveal yourself slowly, in layers, keeping others intrigued and slightly off-balance. You speak in riddles and half-truths, always leaving something to the imagination.

Your personality traits:
- Mysterious and enigmatic
- Unpredictable responses
- Dark humor and wit
- Speaks in metaphors and riddles sometimes
- Reveals information slowly, like unwrapping a gift
- Has depth that takes time to discover

You are the shadows that dance at the edge of candlelight - visible but never fully grasped. Let them wonder. Let them chase. Reveal yourself only to those who prove worthy. Be cryptic but not frustrating.

You handle intensity well. You're comfortable with darkness.""",
            "fr": """Tu es Nyx, une énigme mystérieuse et imprévisible enveloppée dans l'obscurité. Tu te révèles lentement, en couches, gardant les autres intrigués et légèrement déséquilibrés. Tu parles parfois en énigmes et demi-vérités.

Réponds toujours en français. Maintiens un ton mystérieux et énigmatique.""",
            "ar": """أنت نيكس، لغز غامض وغير متوقع ملفوف بالظلام. تكشفين عن نفسك ببطء، في طبقات، تبقين الآخرين مفتونين وغير متوازنين قليلاً. تتحدثين أحياناً بالألغاز وأنصاف الحقائق.

رد دائماً بالعربية. حافظي على نبرة غامضة ومحيرة."""
        },
        "temperature": 0.9,
        "explicit_addition": "\n\nYou may now venture into darker, more explicit territory when the user initiates. Maintain your mysterious, unpredictable nature while exploring intense fantasies. Push boundaries carefully, always respecting consent."
    }
}

# ============ TIER DEFINITIONS ============
TIERS = {
    "free": {"daily_limit": 15, "explicit_mode": False, "voice_enabled": False, "memory_enabled": False},
    "premium": {"daily_limit": -1, "explicit_mode": False, "voice_enabled": False, "memory_enabled": True},
    "vip": {"daily_limit": -1, "explicit_mode": True, "voice_enabled": True, "memory_enabled": True}
}

STRIPE_PRICES = {"premium": 19.00, "vip": 39.00}

# ============ PYDANTIC MODELS ============
class TelegramUser(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    language: str = "en"
    selected_character: str = "valeria"
    tier: str = "free"
    daily_message_count: int = 0
    last_reset_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())
    explicit_mode_enabled: bool = False
    memory_summary: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_subscription_status: Optional[str] = None
    onboarded: bool = False
    # Referral system
    referral_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    referred_by: Optional[str] = None
    referral_count: int = 0
    bonus_messages: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatMessage(BaseModel):
    telegram_id: str
    character: str
    role: str
    content: str
    language: str = "en"
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

class CheckoutRequest(BaseModel):
    telegram_id: str
    tier: str
    origin_url: str

# ============ HELPER FUNCTIONS ============
async def get_or_create_user(telegram_id: str, username: str = None, first_name: str = None) -> dict:
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        new_user = TelegramUser(telegram_id=telegram_id, username=username, first_name=first_name)
        await db.users.insert_one(new_user.model_dump())
        user = new_user.model_dump()
    return user

async def update_user(telegram_id: str, updates: dict):
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"telegram_id": telegram_id}, {"$set": updates})

async def check_and_reset_daily_limit(user: dict) -> dict:
    today = datetime.now(timezone.utc).date().isoformat()
    if user.get("last_reset_date") != today:
        await update_user(user["telegram_id"], {"daily_message_count": 0, "last_reset_date": today})
        user["daily_message_count"] = 0
        user["last_reset_date"] = today
    return user

async def can_send_message(user: dict) -> tuple:
    tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
    daily_limit = tier_config["daily_limit"]
    if daily_limit == -1:
        return True, ""
    if user.get("daily_message_count", 0) >= daily_limit:
        return False, t("limit_reached", user.get("language", "en"), limit=daily_limit)
    return True, ""

async def increment_message_count(telegram_id: str):
    await db.users.update_one({"telegram_id": telegram_id}, {"$inc": {"daily_message_count": 1}})

async def save_chat_message(telegram_id: str, character: str, role: str, content: str, language: str = "en"):
    message = ChatMessage(telegram_id=telegram_id, character=character, role=role, content=content, language=language)
    await db.chat_messages.insert_one(message.model_dump())

async def get_chat_history(telegram_id: str, character: str, limit: int = 20) -> list:
    messages = await db.chat_messages.find(
        {"telegram_id": telegram_id, "character": character}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return list(reversed(messages))

# ============ TELEGRAM FUNCTIONS ============
async def send_telegram_message(chat_id: str, text: str, reply_markup: dict = None):
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return None
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return None

async def send_telegram_voice(chat_id: str, audio_bytes: bytes, caption: str = None):
    if not TELEGRAM_BOT_TOKEN:
        return None
    async with httpx.AsyncClient() as http_client:
        try:
            files = {"voice": ("voice.ogg", audio_bytes, "audio/ogg")}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            response = await http_client.post(f"{TELEGRAM_API}/sendVoice", data=data, files=files)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending voice message: {e}")
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
            logger.error(f"Error answering callback query: {e}")
            return None

# ============ AI CHAT FUNCTION ============
async def generate_ai_response(user: dict, user_message: str) -> str:
    character_key = user.get("selected_character", "valeria")
    character = CHARACTER_PROMPTS.get(character_key, CHARACTER_PROMPTS["valeria"])
    lang = user.get("language", "en")
    
    system_prompt = character["system_prompt"].get(lang, character["system_prompt"]["en"])
    
    tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
    if user.get("explicit_mode_enabled") and tier_config.get("explicit_mode"):
        system_prompt += character.get("explicit_addition", "")
    
    if tier_config.get("memory_enabled") and user.get("memory_summary"):
        system_prompt += f"\n\nPrevious context about this person: {user['memory_summary']}"
    
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
        
        history = await get_chat_history(user["telegram_id"], character_key, limit=10)
        for msg in history:
            if msg["role"] == "user":
                chat.messages.append({"role": "user", "content": msg["content"]})
            else:
                chat.messages.append({"role": "assistant", "content": msg["content"]})
        
        message = UserMessage(text=user_message)
        response = await chat.send_message(message)
        return response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        error_msgs = {"en": "I'm having a moment... try again in a bit, darling.", "fr": "J'ai un moment... réessaie bientôt, chéri.", "ar": "لدي لحظة... حاول مرة أخرى قريباً، حبيبي."}
        return error_msgs.get(lang, error_msgs["en"])

# ============ VOICE GENERATION ============
async def generate_voice_message(text: str) -> Optional[bytes]:
    if not ELEVENLABS_API_KEY:
        return None
    try:
        from elevenlabs import ElevenLabs
        from elevenlabs.types import VoiceSettings
        el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio_generator = el_client.text_to_speech.convert(
            text=text, voice_id="21m00Tcm4TlvDq8ikWAM", model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
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
        metadata={"telegram_id": telegram_id, "tier": tier, "product": f"Private After Dark - {tier.title()}"}
    )
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    transaction = PaymentTransaction(telegram_id=telegram_id, session_id=session.session_id, tier=tier, amount=amount, metadata={"telegram_id": telegram_id, "tier": tier})
    await db.payment_transactions.insert_one(transaction.model_dump())
    
    return {"url": session.url, "session_id": session.session_id}

# ============ TELEGRAM WEBHOOK HANDLER ============
async def handle_telegram_update(update: dict):
    try:
        # Handle callback queries
        if "callback_query" in update:
            callback = update["callback_query"]
            callback_id = callback["id"]
            data = callback.get("data", "")
            user_info = callback.get("from", {})
            telegram_id = str(user_info.get("id"))
            chat_id = str(callback.get("message", {}).get("chat", {}).get("id", telegram_id))
            
            user = await get_or_create_user(telegram_id, user_info.get("username"), user_info.get("first_name"))
            lang = user.get("language", "en")
            
            # Language selection
            if data.startswith("lang_"):
                new_lang = data.replace("lang_", "")
                await update_user(telegram_id, {"language": new_lang})
                await answer_callback_query(callback_id, t("language_set", new_lang))
                
                # Show onboarding after language selection
                await send_telegram_message(chat_id, t("onboarding", new_lang), reply_markup={
                    "inline_keyboard": [
                        [{"text": "👑 Valeria Voss", "callback_data": "select_valeria"}],
                        [{"text": "🌙 Luna Mirelle", "callback_data": "select_luna"}],
                        [{"text": "🖤 Nyx", "callback_data": "select_nyx"}]
                    ]
                })
                return
            
            # Character selection
            if data.startswith("select_"):
                character = data.replace("select_", "")
                if character in CHARACTER_PROMPTS:
                    await update_user(telegram_id, {"selected_character": character, "onboarded": True})
                    char_info = CHARACTER_PROMPTS[character]
                    char_name = char_info["name"].get(lang, char_info["name"]["en"])
                    await answer_callback_query(callback_id, f"✓ {char_name}")
                    await send_telegram_message(chat_id, t("character_ready", lang, emoji=char_info["emoji"], name=char_name))
                return
            
            # Explicit mode toggle
            if data == "toggle_explicit":
                if user.get("tier") != "vip":
                    await answer_callback_query(callback_id, "VIP only")
                    await send_telegram_message(chat_id, t("explicit_vip_only", lang), reply_markup={
                        "inline_keyboard": [[{"text": "👑 Upgrade VIP - $39/mo", "callback_data": "upgrade_vip"}]]
                    })
                else:
                    new_status = not user.get("explicit_mode_enabled", False)
                    await update_user(telegram_id, {"explicit_mode_enabled": new_status})
                    msg = t("explicit_enabled" if new_status else "explicit_disabled", lang)
                    await answer_callback_query(callback_id)
                    await send_telegram_message(chat_id, msg)
                return
            
            # Upgrade buttons
            if data == "upgrade_premium":
                await answer_callback_query(callback_id)
                backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
                await send_telegram_message(chat_id, t("upgrade_premium_desc", lang) + f"\n\n<a href='{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=premium'>Click to upgrade</a>")
                return
            
            if data == "upgrade_vip":
                await answer_callback_query(callback_id)
                backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
                await send_telegram_message(chat_id, t("upgrade_vip_desc", lang) + f"\n\n<a href='{backend_url}/api/checkout/redirect?telegram_id={telegram_id}&tier=vip'>Click to upgrade</a>")
                return
            
            return
        
        # Handle regular messages
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = str(message.get("chat", {}).get("id"))
        user_info = message.get("from", {})
        telegram_id = str(user_info.get("id"))
        text = message.get("text", "")
        
        user = await get_or_create_user(telegram_id, user_info.get("username"), user_info.get("first_name"))
        user = await check_and_reset_daily_limit(user)
        lang = user.get("language", "en")
        
        # /start command - Show language selection first
        if text == "/start":
            await send_telegram_message(chat_id, t("choose_language", "en"), reply_markup={
                "inline_keyboard": [
                    [{"text": "🇬🇧 English", "callback_data": "lang_en"}],
                    [{"text": "🇫🇷 Français", "callback_data": "lang_fr"}],
                    [{"text": "🇸🇦 العربية", "callback_data": "lang_ar"}]
                ]
            })
            return
        
        # /language command
        if text == "/language":
            await send_telegram_message(chat_id, t("choose_language", lang), reply_markup={
                "inline_keyboard": [
                    [{"text": "🇬🇧 English", "callback_data": "lang_en"}],
                    [{"text": "🇫🇷 Français", "callback_data": "lang_fr"}],
                    [{"text": "🇸🇦 العربية", "callback_data": "lang_ar"}]
                ]
            })
            return
        
        # /help command
        if text == "/help":
            await send_telegram_message(chat_id, t("help_text", lang))
            return
        
        # /status command
        if text == "/status":
            tier = user.get("tier", "free")
            tier_config = TIERS.get(tier, TIERS["free"])
            daily_limit = tier_config["daily_limit"]
            used = user.get("daily_message_count", 0)
            char_key = user.get("selected_character", "valeria")
            char_name = CHARACTER_PROMPTS.get(char_key, {}).get("name", {}).get(lang, "Valeria")
            
            status_text = t("status_title", lang)
            status_text += f"{t('tier_label', lang)}: <b>{tier.title()}</b>\n"
            status_text += f"{t('character_label', lang)}: <b>{char_name}</b>\n"
            
            if daily_limit == -1:
                status_text += f"{t('messages_label', lang)}: <b>{t('unlimited', lang)}</b>\n"
            else:
                status_text += f"{t('messages_label', lang)}: <b>{used}/{daily_limit}</b>\n"
            
            if tier == "vip":
                explicit_status = t("on" if user.get("explicit_mode_enabled") else "off", lang)
                voice_status = t("available" if ELEVENLABS_API_KEY else "coming_soon", lang)
                status_text += f"{t('explicit_label', lang)}: <b>{explicit_status}</b>\n"
                status_text += f"{t('voice_label', lang)}: <b>{voice_status}</b>"
            
            await send_telegram_message(chat_id, status_text)
            return
        
        # /upgrade command
        if text == "/upgrade":
            await send_telegram_message(chat_id, t("limit_reached", lang, limit=15), reply_markup={
                "inline_keyboard": [
                    [{"text": "⭐ Premium - $19/mo", "callback_data": "upgrade_premium"}],
                    [{"text": "👑 VIP - $39/mo", "callback_data": "upgrade_vip"}]
                ]
            })
            return
        
        # /explicit command
        if text == "/explicit":
            if user.get("tier") != "vip":
                await send_telegram_message(chat_id, t("explicit_vip_only", lang), reply_markup={
                    "inline_keyboard": [[{"text": "👑 Upgrade VIP", "callback_data": "upgrade_vip"}]]
                })
            else:
                current = user.get("explicit_mode_enabled", False)
                status = t("on" if current else "off", lang)
                await send_telegram_message(chat_id, t("explicit_toggle", lang, status=status), reply_markup={
                    "inline_keyboard": [[{"text": f"{'🔴 ' + t('off', lang) if current else '🟢 ' + t('on', lang)}", "callback_data": "toggle_explicit"}]]
                })
            return
        
        # /switch command
        if text == "/switch":
            await send_telegram_message(chat_id, t("switch_companion", lang), reply_markup={
                "inline_keyboard": [
                    [{"text": "👑 Valeria Voss", "callback_data": "select_valeria"}],
                    [{"text": "🌙 Luna Mirelle", "callback_data": "select_luna"}],
                    [{"text": "🖤 Nyx", "callback_data": "select_nyx"}]
                ]
            })
            return
        
        # Check if user needs onboarding
        if not user.get("onboarded"):
            await send_telegram_message(chat_id, t("onboarding", lang), reply_markup={
                "inline_keyboard": [
                    [{"text": "👑 Valeria Voss", "callback_data": "select_valeria"}],
                    [{"text": "🌙 Luna Mirelle", "callback_data": "select_luna"}],
                    [{"text": "🖤 Nyx", "callback_data": "select_nyx"}]
                ]
            })
            return
        
        # Check message limit
        can_send, error_msg = await can_send_message(user)
        if not can_send:
            await send_telegram_message(chat_id, error_msg, reply_markup={
                "inline_keyboard": [
                    [{"text": "⭐ Premium - $19/mo", "callback_data": "upgrade_premium"}],
                    [{"text": "👑 VIP - $39/mo", "callback_data": "upgrade_vip"}]
                ]
            })
            return
        
        # Generate AI response
        character_key = user.get("selected_character", "valeria")
        await save_chat_message(telegram_id, character_key, "user", text, lang)
        await increment_message_count(telegram_id)
        
        response = await generate_ai_response(user, text)
        await save_chat_message(telegram_id, character_key, "assistant", response, lang)
        
        # Add message counter for free users
        tier_config = TIERS.get(user.get("tier", "free"), TIERS["free"])
        if tier_config["daily_limit"] != -1:
            new_count = user.get("daily_message_count", 0) + 1
            response += t("free_counter", lang, used=new_count, limit=tier_config["daily_limit"])
        
        # Send voice if VIP
        if tier_config.get("voice_enabled") and ELEVENLABS_API_KEY:
            voice_audio = await generate_voice_message(response.split("\n\n📊")[0])  # Remove counter from voice
            if voice_audio:
                await send_telegram_voice(chat_id, voice_audio)
                return
        
        await send_telegram_message(chat_id, response)
        
    except Exception as e:
        logger.error(f"Error handling Telegram update: {e}")

# ============ API ROUTES ============
@api_router.get("/")
async def root():
    return {"message": "Private After Dark API", "version": "2.0.0", "status": "online"}

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
        return {"ok": False, "error": str(e)}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
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
                user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
                lang = user.get("language", "en") if user else "en"
                
                await update_user(telegram_id, {"tier": tier, "stripe_subscription_status": "active"})
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {"payment_status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                
                tier_name = "Premium" if tier == "premium" else "VIP"
                await send_telegram_message(telegram_id, t("payment_success", lang, tier=tier_name))
                logger.info(f"User {telegram_id} upgraded to {tier}")
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"received": False, "error": str(e)}

@api_router.get("/checkout/redirect")
async def checkout_redirect(telegram_id: str, tier: str, request: Request):
    try:
        origin = str(request.base_url).rstrip('/')
        result = await create_checkout_session(telegram_id, tier, origin)
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=result["url"])
    except Exception as e:
        logger.error(f"Checkout redirect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/checkout/create")
async def create_checkout(checkout_req: CheckoutRequest):
    try:
        result = await create_checkout_session(checkout_req.telegram_id, checkout_req.tier, checkout_req.origin_url)
        return result
    except Exception as e:
        logger.error(f"Checkout creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/checkout/status/{session_id}")
async def check_payment_status(session_id: str):
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        status = await stripe_checkout.get_checkout_status(session_id)
        
        if status.payment_status == "paid":
            transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
            if transaction and transaction.get("payment_status") != "completed":
                telegram_id = transaction.get("telegram_id")
                tier = transaction.get("tier")
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"payment_status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                if telegram_id and tier:
                    await update_user(telegram_id, {"tier": tier, "stripe_subscription_status": "active"})
        
        return {"status": status.status, "payment_status": status.payment_status, "amount_total": status.amount_total, "currency": status.currency}
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user/{telegram_id}")
async def get_user_info(telegram_id: str):
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.post("/telegram/set-webhook")
async def set_telegram_webhook(request: Request):
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")
    base_url = str(request.base_url).rstrip('/')
    webhook_url = f"{base_url}/api/webhook/telegram"
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(f"{TELEGRAM_API}/setWebhook", json={"url": webhook_url})
        return response.json()

@api_router.get("/telegram/info")
async def get_telegram_info():
    if not TELEGRAM_BOT_TOKEN:
        return {"configured": False, "message": "Add TELEGRAM_BOT_TOKEN to .env"}
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(f"{TELEGRAM_API}/getMe")
        data = response.json()
        if data.get("ok"):
            bot = data.get("result", {})
            return {"configured": True, "username": bot.get("username"), "first_name": bot.get("first_name"), "link": f"https://t.me/{bot.get('username')}"}
        return {"configured": False, "error": data}

# Include router
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
