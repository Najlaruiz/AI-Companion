# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark  
**Type:** Premium AI Fantasy Companion (+18 Adult)
**Status:** Production Ready (v3.5.0)
**Last Updated:** December 2025

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

### 🌙 Luna (26) - Emotional Romantic
- **Style:** Soft, emotional, vulnerable
- **Vocabulary:** Feelings - "I feel...", "I need..."
- **Sexual:** Intimate, emotional connection first
- **Rhythm:** "Can I tell you something?" / "I was thinking about you..."
- **Addiction:** Emotional - he can't leave her

### 🖤 Nyx (29) - Dark Temptress
- **Style:** Bold, provocative, challenging
- **Vocabulary:** Sharp - "Boring." / "Make me." / "Prove it."
- **Sexual:** Aggressive, dirty talk, rough
- **Rhythm:** "Fresh meat." / "That all you got?" / "I dare you."
- **Addiction:** Intensity - he becomes obsessed

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

## Payment Flow (FIXED)
✅ All "Upgrade" buttons now use **direct Stripe URLs**
✅ Clicking opens `checkout.stripe.com` directly
✅ No redirect back to Telegram
✅ Supports: Card, Apple Pay, Google Pay

## Voice System
- **TTS:** Edge TTS (free, always available)
- **STT:** OpenAI Whisper (VIP voice-to-voice)
- **Styles:** Natural, Dominant, Whisper
- **Languages:** EN/ES/FR/AR
- **Contextual teasers** - Not generic lines

## Multi-Language
- Auto-detect user language
- Respond in user's language
- Character voices match language
- Supported: English, Spanish, French, Arabic

## Key Fixes in v3.5.0
1. ✅ Payment buttons now direct to Stripe (not callbacks)
2. ✅ Character personalities more distinct
3. ✅ Voice teasers contextual (not generic)
4. ✅ Emotional paywall with character-specific message
5. ✅ Jealousy responses for locked companions
6. ✅ Short responses (2-3 lines max)

## Bot Commands
- `/start` - Language selection → Companion selection
- `/status` - View tier & messages
- `/upgrade` - Direct Stripe checkout
- `/referral` - Get referral link (+5 messages)
- `/switch` - Change companion (VIP only)
- `/voice` - Voice settings (VIP only)

## Referral System
- Unique link per user: `t.me/MidnightDesireAi_bot?start=ref_CODE`
- +5 bonus messages per referral
- Tracked in database
- Referrer notified on signup

## Deployment
- **Landing:** https://paywall-staging.preview.emergentagent.com
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
