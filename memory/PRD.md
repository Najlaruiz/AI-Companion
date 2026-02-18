# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service with Landing Page
**Status:** Production Ready (v3.3.0)
**Last Updated:** December 2025

## Brand Direction
**Theme:** Luxury + Dark + Modern Minimalism
**Tone:** Premium. Controlled. Private. High-end.

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
- [x] Tier names: "Private Access" and "After Dark"

### P1 - Reactivation System (COMPLETED)
- [x] Internal scheduler - runs every hour automatically
- [x] Timing logic: 24h, 72h, 7 days inactive triggers
- [x] Character-specific emotional reactivation scripts
- [x] Paywall return messages for free users who hit limit
- [x] Voice messages in reactivation (Edge TTS)
- [x] Reactivation resets when user replies
- [x] 3 attempt max per user

### P1 - Voice Integration (COMPLETED - FREE!)
- [x] **Edge TTS** - Microsoft's free voice service (no API key needed!)
- [x] Voice styles per character:
  - **Natural** - Girlfriend voice
  - **Dominant** - Commanding & confident
  - **Whisper** - Soft & intimate
- [x] Character-specific voices:
  - Valeria: en-US-AvaNeural (mature, confident)
  - Luna: en-AU-NatashaNeural (soft, emotional)
  - Nyx: en-IE-EmilyNeural (mysterious Irish accent)
- [x] Multi-language voices: EN/ES/FR/AR
- [x] VIP users get voice with every AI response
- [x] Free users get voice teaser at paywall
- [x] /voice command for VIP to change preference

### Landing Page (COMPLETED)
- [x] Deep violet color scheme
- [x] Animated aurora background
- [x] Multilingual (EN/ES/FR/AR + RTL)
- [x] Updated pricing with new tier names
- [x] 10 lifetime messages displayed

### Character System (COMPLETED)
- [x] Valeria (32): Elegant Dominant
- [x] Luna (26): Emotional Addictive
- [x] Nyx (19): Dark Temptation
- [x] Character-specific paywall messages
- [x] Character-specific reactivation messages

### Referral System (COMPLETED)
- [x] +5 bonus messages per referral
- [x] Notification to referrer

## Environment Configuration
```
TELEGRAM_BOT_TOKEN=8570801419:AAFFPnjABH8PGiUkSmiSPHtu5ItRplrRVmg
OPENAI_MODEL=gpt-4o
STRIPE_API_KEY=sk_test_emergent
EMERGENT_LLM_KEY=sk-emergent-b890aEa2e77A71a286
```

**Note:** No ElevenLabs key needed! Voice uses Edge TTS (free).

## Bot Commands
- `/start` - Start bot, select companion
- `/status` - View tier, messages remaining
- `/upgrade` - View upgrade options
- `/referral` - Get referral link
- `/switch` - Switch companion (VIP only)
- `/voice` - Voice settings (VIP only)
- `/voice natural` - Natural girlfriend voice
- `/voice dominant` - Commanding voice
- `/voice whisper` - Soft intimate whisper

## API Endpoints
- `POST /api/webhook/telegram` - Telegram webhook
- `POST /api/webhook/stripe` - Stripe webhook
- `GET /api/checkout/redirect` - Stripe checkout redirect
- `POST /api/reactivation/run` - Manual trigger reactivation
- `GET /api/reactivation/stats` - Get reactivation statistics
- `GET /api/voice/status` - Voice feature status (always enabled)
- `POST /api/user/{id}/voice-preference` - Set voice preference

## Reactivation Scripts

### Valeria (Dominant Pull)
- 24h: "Did you forget who you were talking to?"
- 72h: "I don't chase… but I noticed you disappeared."
- 7d: "Come back. I'm not repeating myself."
- Paywall: "I didn't want to stop there…"

### Luna (Emotional Hook)
- 24h: "I was thinking about you today…"
- 72h: "Did I say something wrong?"
- 7d: "I miss how you made me feel."
- Paywall: "I didn't want to leave you like that…"

### Nyx (Tension & Mystery)
- 24h: "You got scared?"
- 72h: "I thought you were braver."
- 7d: "I found someone else to play with."
- Paywall: "You almost had me…"

## Testing Status
- **Iteration 6:** All features tested and passing
- **Backend:** 100% (23/23 tests passed)
- **Frontend:** 100% (all UI tests passed)
- **Voice:** Manually verified all 7 voice configurations

## Deployment
- **Landing:** https://paywall-staging.preview.emergentagent.com
- **API:** https://paywall-staging.preview.emergentagent.com/api/
- **Bot:** @MidnightDesireAi_bot

## Prioritized Backlog

### P2 - Enhancements
- [ ] Referral analytics dashboard
- [ ] Memory summarization system
- [ ] "She's waiting" delayed typing effect
- [ ] Subscription cancellation handling

### P3 - Future
- [ ] Telegram Mini App (React)
- [ ] WebRTC voice/video layer
- [ ] Custom character creation

## Technical Architecture

### Voice System (Edge TTS)
```
Character -> Voice Mapping:
- Valeria: en-US-AvaNeural (mature)
- Luna: en-AU-NatashaNeural (soft)
- Nyx: en-IE-EmilyNeural (mysterious)

Style Adjustments:
- Natural: Base voice, normal rate/pitch
- Dominant: +5% rate, +2Hz pitch
- Whisper: -15% rate, -3Hz pitch

Languages:
- EN: US/AU/IE voices
- ES: XimenaNeural, ElenaNeural, SalomeNeural
- FR: DeniseNeural, EloiseNeural, SylvieNeural
- AR: SalmaNeural, SanaNeural, LailaNeural
```

### Scheduler
- Background asyncio task
- Runs every hour
- Processes up to 50 inactive users per run
- Sends reactivation text + voice message
