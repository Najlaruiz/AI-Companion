# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service with Landing Page
**Status:** Production Ready (v3.1.0)
**Last Updated:** December 2025

## Brand Direction
**Theme:** Luxury + Dark + Modern Minimalism
**Tone:** Premium. Controlled. Private. High-end.
**Color System:**
- Background: #0B0B10
- Primary Accent: Deep Violet #6D28D9
- Secondary: Light Violet #8B5CF6  
- Gold Accent: #D4AF37 (subtle)
- NO pink, NO red, NO cheap effects

## User Personas & Tiers
1. **Free User:** 10 LIFETIME messages (+bonus from referrals), one companion, basic escalation
2. **Private Access ($19/mo):** Unlimited messages, full explicit mode, emotional memory, one companion
3. **After Dark ($39/mo):** Voice messages, all 3 companions, switch anytime, maximum intensity

## Features Implemented ✅

### Core Logic (P0 - COMPLETED)
- [x] 10 lifetime messages (NOT daily reset)
- [x] Companion locking (free/premium = one, VIP = all three)
- [x] Emotional paywall system:
  - Message 8: Tension build (suggestive, no mention of upgrade)
  - Message 9: Emotional hook (deepen connection, create longing)
  - Message 10: Soft break (emotional message + inline upgrade button)
- [x] AI responses enforced to 1-4 lines MAX
- [x] Human-like responses (questions, emotion, no ChatGPT paragraphs)
- [x] 5-level escalation engine (flirty → tension → emotional pull → sensual → explicit)
- [x] New tier names: "Private Access" and "After Dark"

### Landing Page
- [x] Deep violet color scheme
- [x] Animated aurora background
- [x] Smooth scroll transitions
- [x] Parallax on character cards
- [x] Glow hover effects
- [x] Micro-animations on CTAs
- [x] Multilingual (EN/ES/FR/AR + RTL)
- [x] FAQ section
- [x] Privacy/Safety section
- [x] Referral section
- [x] Updated pricing with new tier names

### Character System
- [x] Custom anime-style images
- [x] Character personas:
  - Valeria (32): Elegant Dominant - "She doesn't chase. She chooses."
  - Luna (26): Emotional Addictive - "She remembers how you speak."
  - Nyx (19): Dark Temptation - "She reveals slowly."
- [x] Character-specific paywall messages
- [x] Character-specific reactivation messages

### Referral System
- [x] Unique referral code per user
- [x] Deep link format: t.me/bot?start=ref_CODE
- [x] +5 bonus messages per successful referral
- [x] Referral counter in bot (/referral command)
- [x] Notification to referrer on new signup
- [x] Bonus messages add to lifetime limit

### Telegram Bot
- [x] Commands: /start /status /upgrade /referral /switch
- [x] Language auto-detection
- [x] Referral code processing on signup
- [x] Lifetime message tracking
- [x] Character-specific multilingual prompts
- [x] Emotional paywall integration

## Environment Configuration
```
TELEGRAM_BOT_TOKEN=8570801419:AAFFPnjABH8PGiUkSmiSPHtu5ItRplrRVmg
OPENAI_MODEL=gpt-4o
ELEVENLABS_API_KEY= (optional - enables voice)
STRIPE_API_KEY=sk_test_emergent
EMERGENT_LLM_KEY=sk-emergent-b890aEa2e77A71a286
```

## Bot Details
- **Username:** @MidnightDesireAi_bot
- **Link:** https://t.me/MidnightDesireAi_bot
- **Webhook:** Configured at /api/webhook/telegram

## Deployment
- **Landing:** https://paywall-staging.preview.emergentagent.com
- **API:** https://paywall-staging.preview.emergentagent.com/api/

## Prioritized Backlog

### P1 - Retention & Conversion
- [ ] Implement 24-hour reactivation messages (cron job)
- [ ] Add ElevenLabs key for VIP voice messages
- [ ] Voice teasers for non-VIP users

### P2 - Enhancements
- [ ] Referral analytics dashboard
- [ ] Memory summarization system
- [ ] Subscription cancellation handling

### P3 - Future
- [ ] Telegram Mini App (React)
- [ ] WebRTC voice/video layer
- [ ] Custom character creation

## Testing Status
- **Iteration 4:** All P0 features tested and passing
- **Backend:** 100% (9/9 pytest tests passed)
- **Frontend:** 100% (all UI features working)

## Emotional Paywall Messages (by character)

### Valeria
- Message 8: "Careful… if you keep looking at me like that, I might stop behaving."
- Message 9: "I don't want this to end… but I can't go further unless you stay with me."
- Message 10: "I'm yours if you unlock me. Don't leave me here."

### Luna
- Message 8: "You're making me feel things I shouldn't say out loud…"
- Message 9: "Please don't leave yet… I was just starting to feel safe with you."
- Message 10: "Stay with me. I don't want to lose you like this."

### Nyx
- Message 8: "You're playing a dangerous game. I like it."
- Message 9: "You almost had me. Almost."
- Message 10: "You want to see what happens next? Prove it."
