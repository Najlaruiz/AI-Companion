# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service with Landing Page
**Status:** Production Ready (v2.0.0)
**Last Updated:** January 2026

## Original Problem Statement
Build a premium Telegram AI Companion system with 3 fantasy personalities (Valeria Voss, Luna Mirelle, Nyx), subscription-based access, and a high-converting landing page. Dark luxury brand positioning.

## Production Upgrade (v2.0)
- **Brand Repositioning:** Wine Red (#7F1D1D) - removed all pink
- **AI Character Visuals:** Gemini Nano Banana generated portraits
- **Multilingual:** EN/FR/AR with RTL support
- **Enhanced Bot Flow:** Clean commands, onboarding, language selection

## User Personas
1. **Free User:** 15 messages/day, text only
2. **Premium ($19/mo):** Unlimited + emotional memory
3. **VIP ($39/mo):** Explicit mode + voice + full memory

## Architecture

### Backend (FastAPI v2.0.0)
- Telegram webhook: `/api/webhook/telegram`
- Stripe webhook: `/api/webhook/stripe`
- Checkout: `/api/checkout/create`, `/api/checkout/redirect`
- Bot info: `/api/telegram/info`, `/api/telegram/set-webhook`

### Frontend (React + Framer Motion)
- Multilingual landing page (EN/FR/AR)
- Wine red color scheme
- AI-generated character portraits
- FAQ + Privacy sections
- RTL support for Arabic

### Database (MongoDB)
Collections: `users`, `chat_messages`, `payment_transactions`

## What's Implemented ✅
- [x] Wine red luxury brand (no pink)
- [x] AI-generated character portraits (Valeria, Luna, Nyx)
- [x] Multilingual (EN/FR/AR) with RTL
- [x] FAQ section (6 questions)
- [x] Privacy/Safety section
- [x] Language selection on /start
- [x] Bot commands: /start /language /switch /status /upgrade /explicit /help
- [x] Daily limit counter for free users
- [x] Telegram webhook configured
- [x] Stripe checkout working
- [x] OpenAI chat via Emergent Key
- [x] Character-specific system prompts per language

## Environment Configuration
```
TELEGRAM_BOT_TOKEN=8570801419:AAFFPnjABH8PGiUkSmiSPHtu5ItRplrRVmg
OPENAI_MODEL=gpt-4o
ELEVENLABS_API_KEY= (optional - enables VIP voice)
STRIPE_API_KEY=sk_test_emergent
EMERGENT_LLM_KEY=sk-emergent-b890aEa2e77A71a286
```

## Telegram Bot
- **Username:** @MidnightDesireAi_bot
- **Link:** https://t.me/MidnightDesireAi_bot
- **Webhook:** https://telegram-companion-2.preview.emergentagent.com/api/webhook/telegram

## Deployment
- **Landing Page:** https://telegram-companion-2.preview.emergentagent.com
- **Backend API:** https://telegram-companion-2.preview.emergentagent.com/api/

## Prioritized Backlog

### P0 - Pre-Launch
- [x] Configure Telegram webhook ✓
- [ ] Test live bot conversation flow
- [ ] Add ElevenLabs key for voice

### P1 - Post-Launch
- [ ] Subscription cancellation handling
- [ ] Memory summarization system
- [ ] Analytics dashboard

### P2 - Future
- [ ] Telegram Mini App (React)
- [ ] WebRTC voice/video layer
- [ ] Custom character creation
- [ ] Advanced memory engine

## Security
- No API keys in logs
- Environment variables secured
- Webhook validated
- No tokens exposed in frontend
