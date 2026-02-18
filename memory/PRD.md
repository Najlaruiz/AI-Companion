# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service with Landing Page
**Status:** Production Ready (v3.2.0)
**Last Updated:** December 2025

## Brand Direction
**Theme:** Luxury + Dark + Modern Minimalism
**Tone:** Premium. Controlled. Private. High-end.
**Color System:**
- Background: #0B0B10
- Primary Accent: Deep Violet #6D28D9
- Secondary: Light Violet #8B5CF6  
- Gold Accent: #D4AF37 (subtle)

## User Personas & Tiers
1. **Free User:** 10 LIFETIME messages (+bonus from referrals), one companion, basic escalation
2. **Private Access ($19/mo):** Unlimited messages, full explicit mode, emotional memory, one companion
3. **After Dark ($39/mo):** Voice messages, all 3 companions, switch anytime, maximum intensity

## Features Implemented ✅

### P0 - Core Logic (COMPLETED)
- [x] 10 lifetime messages (NOT daily reset)
- [x] Companion locking (free/premium = one, VIP = all three)
- [x] Emotional paywall system (Message 8, 9, 10)
- [x] AI responses enforced to 1-4 lines MAX
- [x] Human-like responses (questions, emotion)
- [x] 5-level escalation engine
- [x] New tier names: "Private Access" and "After Dark"

### P1 - Reactivation System (COMPLETED)
- [x] Internal scheduler - runs every hour automatically
- [x] Timing logic: 24h, 72h, 7 days inactive triggers
- [x] Character-specific emotional reactivation scripts
- [x] Paywall return messages for free users who hit limit
- [x] Reactivation resets when user replies
- [x] 3 attempt max per user
- [x] Cron endpoint: POST /api/reactivation/run
- [x] Stats endpoint: GET /api/reactivation/stats

### P1 - Voice Integration (COMPLETED - NEEDS PAID API KEY)
- [x] ElevenLabs TTS integration code complete
- [x] Voice styles: natural (girlfriend), dominant (commanding), whisper (intimate)
- [x] VIP users get voice messages with AI responses
- [x] Voice teasers for free users at paywall
- [x] /voice command for VIP to change preference
- [x] Voice callback buttons
- [x] Voice status endpoint: GET /api/voice/status
- [x] API key configured in backend/.env
- ⚠️ **ISSUE:** ElevenLabs free tier is restricted. Need paid plan for voice to work.

### Landing Page
- [x] Deep violet color scheme
- [x] Animated aurora background
- [x] Multilingual (EN/ES/FR/AR + RTL)
- [x] Updated pricing with new tier names

### Character System
- [x] Valeria (32): Elegant Dominant
- [x] Luna (26): Emotional Addictive
- [x] Nyx (19): Dark Temptation
- [x] Character-specific paywall/reactivation messages

### Referral System
- [x] +5 bonus messages per referral
- [x] Notification to referrer

## Environment Configuration
```
TELEGRAM_BOT_TOKEN=8570801419:AAFFPnjABH8PGiUkSmiSPHtu5ItRplrRVmg
OPENAI_MODEL=gpt-4o
ELEVENLABS_API_KEY=sk_c40a3b71967c0301d2dd391d50173f34c7018dabb40b3ac9
STRIPE_API_KEY=sk_test_emergent
EMERGENT_LLM_KEY=sk-emergent-b890aEa2e77A71a286
```

## ⚠️ Voice Integration Note
The ElevenLabs API key provided is a free tier key. ElevenLabs has detected unusual activity and requires a **paid plan** to enable voice generation.

**To enable voice:**
1. Upgrade your ElevenLabs account to a paid plan ($5/month Starter or higher)
2. The existing API key should start working, OR
3. Generate a new API key and update backend/.env

## Bot Commands
- `/start` - Start bot, select companion
- `/status` - View tier, messages remaining
- `/upgrade` - View upgrade options
- `/referral` - Get referral link
- `/switch` - Switch companion (VIP only)
- `/voice` - Voice settings (VIP only)
- `/voice natural` - Set natural girlfriend voice
- `/voice dominant` - Set commanding voice
- `/voice whisper` - Set soft intimate whisper

## Reactivation Scripts

### Valeria (Dominant Pull)
- 24h: "Did you forget who you were talking to?"
- 72h: "I don't chase… but I noticed you disappeared."
- 7d: "Come back. I'm not repeating myself."
- Paywall return: "I didn't want to stop there…"

### Luna (Emotional Hook)
- 24h: "I was thinking about you today…"
- 72h: "Did I say something wrong?"
- 7d: "I miss how you made me feel."
- Paywall return: "I didn't want to leave you like that…"

### Nyx (Tension & Mystery)
- 24h: "You got scared?"
- 72h: "I thought you were braver."
- 7d: "I found someone else to play with."
- Paywall return: "You almost had me…"

## API Endpoints
- `POST /api/webhook/telegram` - Telegram webhook
- `POST /api/webhook/stripe` - Stripe webhook
- `GET /api/checkout/redirect` - Stripe checkout redirect
- `POST /api/reactivation/run` - Manual trigger reactivation job
- `GET /api/reactivation/stats` - Get reactivation statistics
- `GET /api/voice/status` - Check voice feature status
- `POST /api/user/{id}/voice-preference` - Set voice preference

## Testing Status
- **Iteration 5:** All P1 features tested and passing
- **Backend:** 100% (21/21 pytest tests passed)
- **Scheduler:** Running automatically every hour

## Deployment
- **Landing:** https://paywall-staging.preview.emergentagent.com
- **API:** https://paywall-staging.preview.emergentagent.com/api/
- **Bot:** @MidnightDesireAi_bot

## Prioritized Backlog

### P2 - Immediate
- [ ] Upgrade ElevenLabs to paid plan for voice

### P2 - Enhancements
- [ ] Referral analytics dashboard
- [ ] Memory summarization system
- [ ] Subscription cancellation handling

### P3 - Future
- [ ] Telegram Mini App (React)
- [ ] WebRTC voice/video layer
- [ ] Custom character creation
- [ ] "She's waiting" delayed typing effect
