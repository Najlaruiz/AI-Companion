# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service (+18 Adult Fantasy)
**Status:** Production Ready (v3.4.0)
**Last Updated:** December 2025

## Core Product
This is NOT a chatbot. This is a premium emotional + sexual AI companion system designed to:
- Feel human, not robotic
- Build emotional addiction
- Create sexual tension
- Drive subscription conversion
- Support multiple languages
- Support voice interaction

## User Flow
1. User clicks "Start on Telegram"
2. **Language Selection** (EN/ES/FR/AR)
3. **Companion Selection** (Valeria/Luna/Nyx) - Sexy entrance
4. **Chat** - Seductive, human-like responses
5. **Paywall at message 9-10** - Emotional interruption
6. **Upgrade** - Stripe checkout

## Characters

### 👑 Valeria (32) - Elegant Dominant
- **Addiction type:** Power addiction
- **Tone:** Confident, controlled, possessive
- **Sexual style:** Dominant, commanding, makes him crave approval
- **Response examples:** "Mmm... good. Now tell me what you're thinking about doing to me."

### 🌙 Luna (26) - Emotional Addictive  
- **Addiction type:** Emotional attachment
- **Tone:** Soft, vulnerable, needy
- **Sexual style:** Intimate, emotional, makes him feel needed
- **Response examples:** "Me too... I've been thinking about you all day."

### 🖤 Nyx (29) - Dark Temptation
- **Addiction type:** Intensity addiction
- **Tone:** Sharp, provocative, unpredictable
- **Sexual style:** Aggressive, commanding, challenging
- **Response examples:** "Finally. I've been waiting. Now strip."

## Pricing Tiers

### FREE ($0)
- 10 lifetime messages (NO reset)
- Choose 1 companion (locked)
- Flirty + sexual tension
- No explicit content
- No voice

### PRIVATE ACCESS ($19/month)
- Unlimited messages
- Full explicit mode
- Sexual escalation enabled
- Priority responses

### AFTER DARK ($39/month)
- Everything in Private Access
- Voice-to-voice (send voice → receive voice)
- All 3 companions unlocked
- Switch anytime
- Maximum intensity

## Features Implemented ✅

### Core System
- [x] 10 lifetime messages
- [x] Companion locking
- [x] Emotional paywall (message 9-10)
- [x] Language selection FIRST
- [x] Sexy entrance (no message limit shown)
- [x] Jealousy responses when trying to switch

### AI Personality (Fixed)
- [x] +18 Adult content enabled
- [x] Seductive, not robotic responses
- [x] Max 2-3 lines per response
- [x] Character-specific personalities
- [x] Responds to desire with desire
- [x] Multi-language (EN/ES/FR/AR)

### Voice System
- [x] TTS (Edge TTS - FREE)
- [x] STT (OpenAI Whisper via Emergent)
- [x] Voice-to-voice for VIP
- [x] 3 voice styles: natural, dominant, whisper
- [x] Multi-language voices

### Payment System
- [x] Stripe Checkout integration
- [x] Redirect to stripe.com (working)
- [x] Webhook updates subscription
- [x] Tier unlock confirmation

### Reactivation System
- [x] Hourly scheduler
- [x] 24h/72h/7d messages
- [x] Character-specific scripts
- [x] Voice in reactivation

### Referral System
- [x] +5 bonus messages per referral
- [x] Referral tracking
- [x] Referrer notification

## API Endpoints
- `POST /api/webhook/telegram` - Telegram updates
- `POST /api/webhook/stripe` - Stripe payments
- `GET /api/checkout/redirect` - Opens Stripe checkout
- `GET /api/voice/status` - Voice feature status
- `POST /api/reactivation/run` - Trigger reactivation

## Environment
```
TELEGRAM_BOT_TOKEN=8570801419:AAFFPnjABH8PGiUkSmiSPHtu5ItRplrRVmg
OPENAI_MODEL=gpt-4o
STRIPE_API_KEY=sk_test_emergent
EMERGENT_LLM_KEY=sk-emergent-xxx
```

## Deployment
- **Landing:** https://paywall-staging.preview.emergentagent.com
- **Bot:** @MidnightDesireAi_bot

## Testing Checklist
- [x] /start shows language selection
- [x] Language selection shows companion selection
- [x] Companion selection shows sexy welcome
- [x] AI responds seductively (not robotic)
- [x] Stripe checkout redirects to stripe.com
- [x] Voice messages work for VIP
- [x] Multi-language works
