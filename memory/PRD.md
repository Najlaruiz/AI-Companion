# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark  
**Type:** Premium AI Fantasy Companion (+18 Adult)
**Status:** Production Ready (v4.0.0)
**Last Updated:** February 2026

## Core Product Vision
This is NOT a chatbot. This is a premium emotional + sexual AI companion system.

**Must feel:**
- Personal & Exclusive
- Emotionally immersive
- Slightly dangerous
- NOT generic or robotic

## User Flow
1. Click "Start on Telegram" → Opens @MidnightDesireAi_bot
2. **Language Selection** (EN/ES/FR/AR)
3. **Companion Selection** - Sexy entrance, no limits shown
4. **10 Free Messages** - Build tension + desire
5. **Soft Emotional Paywall** (message 10) - NOT hard block
6. **Direct Stripe Checkout** - Opens stripe.com directly
7. **Subscription Active** - Unlimited access

## Characters (COMPLETELY DIFFERENT)

### 👑 Valeria (32) - Elegant Dominant
- **Style:** Slow, controlled, uses "..."
- **Vocabulary:** Elegant - "exquisite", "intriguing"
- **Sexual:** Dominant, commanding, makes him earn it
- **Rhythm:** "Interesting..." / "Come closer." / "Prove it."
- **Addiction:** Power - he craves her approval
- **Moods:** commanding, teasing, intense, cold_then_hot, possessive, condescending_sexy

### 🌙 Luna (26) - Emotional Romantic
- **Style:** Soft, emotional, vulnerable
- **Vocabulary:** Feelings - "I feel...", "I need..."
- **Sexual:** Intimate, emotional connection first
- **Rhythm:** "Can I tell you something?" / "I was thinking about you..."
- **Addiction:** Emotional - he can't leave her
- **Moods:** vulnerable, needy, dreamy, confessional, shy_then_bold, emotionally_raw

### 🖤 Nyx (29) - Dark Temptress
- **Style:** Bold, provocative, challenging
- **Vocabulary:** Sharp - "Boring." / "Make me." / "Prove it."
- **Sexual:** Aggressive, dirty talk, rough
- **Rhythm:** "Fresh meat." / "That all you got?" / "I dare you."
- **Addiction:** Intensity - he becomes obsessed
- **Moods:** dangerous, playful_dark, intense, unpredictable, challenging, mysteriously_suggestive

## Escalation System

### Free Users (10 messages)
- Flirty + sexual tension
- Build desire gradually
- Soft paywall at peak tension

### Premium ($19/month)
- Unlimited messages
- Full explicit content
- Sexual escalation enabled

### VIP ($39/month)
- Everything in Premium
- Voice-to-voice
- All 3 companions
- Switch anytime

## Payment Flow (VERIFIED)
✅ All "Upgrade" buttons use **direct Stripe URLs**
✅ Clicking opens `checkout.stripe.com` directly
✅ /api/checkout/redirect endpoint creates Stripe sessions
✅ /api/checkout/status/{session_id} verifies payment status
✅ Supports: Card, Apple Pay, Google Pay

## Voice System
- **TTS:** Edge TTS (free, always available)
- **STT:** OpenAI Whisper (VIP voice-to-voice)
- **Styles:** Natural, Dominant, Whisper
- **Languages:** EN/ES/FR/AR
- **Status:** Currently paused - focusing on text quality

## Multi-Language
- Auto-detect user language
- Respond in user's language
- Character voices match language
- Supported: English, Spanish, French, Arabic
- RTL support for Arabic

## Key Fixes in v4.0.0
1. ✅ **Fixed frontend blank page** - CharacterCard missing 'lang' prop
2. ✅ **Improved AI responses** - Anti-repetition system with mood variety
3. ✅ **Payment flow verified** - Direct Stripe checkout working
4. ✅ **Added checkout status endpoint** - /api/checkout/status/{session_id}
5. ✅ **Fixed webhook URL** - Uses REACT_APP_BACKEND_URL for HTTPS
6. ✅ **Character personalities** - 6 unique moods per character
7. ✅ **Short responses** - 1-3 lines max, post-processed

## Bot Commands
- `/start` - Language selection → Companion selection
- `/status` - View tier & messages
- `/upgrade` - Direct Stripe checkout
- `/referral` - Get referral link (+5 messages)
- `/switch` - Change companion (VIP only)
- `/voice` - Voice settings (paused)

## Referral System
- Unique link per user: `t.me/MidnightDesireAi_bot?start=ref_CODE`
- +5 bonus messages per referral
- Tracked in database
- Referrer notified on signup

## Deployment
- **Landing:** https://private-staging.preview.emergentagent.com
- **Bot:** @MidnightDesireAi_bot
- **API:** /api/webhook/telegram, /api/checkout/redirect

## Database Schema
```javascript
{
  telegram_id: String,
  selected_character: String,
  character_locked: Boolean,
  tier: "free" | "premium" | "vip",
  lifetime_message_count: Number,
  bonus_messages: Number,
  hit_paywall: Boolean,
  voice_preference: "natural" | "dominant" | "whisper",
  language: "en" | "es" | "fr" | "ar",
  referral_code: String,
  stripe_customer_id: String
}
```

## API Endpoints
- `GET /api/` - API info
- `GET /api/health` - Health check
- `POST /api/webhook/telegram` - Telegram bot webhook
- `POST /api/webhook/stripe` - Stripe payment webhook
- `GET /api/checkout/redirect` - Create Stripe checkout & redirect
- `GET /api/checkout/status/{session_id}` - Check payment status
- `GET /api/telegram/info` - Get bot info
- `POST /api/telegram/set-webhook` - Set Telegram webhook
- `POST /api/reactivation/run` - Trigger user reactivation
- `GET /api/reactivation/stats` - Reactivation statistics

## Upcoming Tasks
1. **Test Telegram bot flow** - User to verify /start, character selection, messaging
2. **Improve AI personality** - Continue monitoring for robotic responses
3. **Re-enable voice features** - Once text flow is stable

## Future Tasks
- Multi-character fantasy mode for VIP
- Jealousy messages when switching
- Simulated typing delays
- Backend refactoring (server.py is monolithic)
