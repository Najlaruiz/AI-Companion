# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service with Landing Page
**Status:** Production Ready (v2.1.0)
**Last Updated:** January 2026

## Brand Direction
**Theme:** Luxury + Dark + Modern Minimalism
**Tone:** Premium. Controlled. Private. High-end.
**Color System:**
- Background: #0B0B10
- Primary Accent: Deep Violet #6D28D9
- Secondary: Light Violet #8B5CF6  
- Gold Accent: #D4AF37 (subtle)
- NO pink, NO red, NO cheap effects

## User Personas
1. **Free User:** 15 messages/day (+bonus from referrals), text only
2. **Premium ($19/mo):** Unlimited + emotional memory
3. **VIP ($39/mo):** Explicit mode + voice + full memory

## Features Implemented ✅

### Landing Page
- [x] Deep violet color scheme
- [x] Animated particles background
- [x] Smooth scroll transitions
- [x] Parallax on character cards
- [x] Glow hover effects
- [x] Micro-animations on CTAs
- [x] Multilingual (EN/FR/AR + RTL)
- [x] FAQ section
- [x] Privacy/Safety section
- [x] Referral section

### Character System
- [x] Custom anime-style images (user-provided)
- [x] Updated taglines:
  - Valeria: "Classy. Controlled. Intensely selective."
  - Luna: "Soft. Emotional. Deeply attached."
  - Nyx: "Mysterious. Slow. Unpredictable."
- [x] Consistent dark fantasy aesthetic

### Referral System
- [x] Unique referral code per user
- [x] Deep link format: t.me/bot?start=ref_CODE
- [x] +5 bonus messages per successful referral
- [x] Referral counter in bot (/referral command)
- [x] Notification to referrer on new signup
- [x] Bonus messages add to daily limit

### Telegram Bot
- [x] Commands: /start /language /switch /status /upgrade /referral /explicit /help
- [x] Language auto-detection from /start
- [x] Referral code processing on signup
- [x] Daily limit + bonus message tracking
- [x] Character-specific multilingual prompts

## Environment Configuration
```
TELEGRAM_BOT_TOKEN=8570801419:AAFFPnjABH8PGiUkSmiSPHtu5ItRplrRVmg
OPENAI_MODEL=gpt-4o
ELEVENLABS_API_KEY= (optional - enables VIP voice)
STRIPE_API_KEY=sk_test_emergent
EMERGENT_LLM_KEY=sk-emergent-b890aEa2e77A71a286
```

## Bot Details
- **Username:** @MidnightDesireAi_bot
- **Link:** https://t.me/MidnightDesireAi_bot
- **Webhook:** Configured and active

## Deployment
- **Landing:** https://paywall-staging.preview.emergentagent.com
- **API:** https://paywall-staging.preview.emergentagent.com/api/

## Prioritized Backlog

### P0 - Pre-Launch
- [ ] Test live bot conversation flow
- [ ] Add ElevenLabs key for voice

### P1 - Post-Launch
- [ ] Referral analytics dashboard
- [ ] Memory summarization system
- [ ] Subscription cancellation handling

### P2 - Future
- [ ] Telegram Mini App (React)
- [ ] WebRTC voice/video layer
- [ ] Custom character creation
