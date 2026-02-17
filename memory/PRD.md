# Private After Dark - Product Requirements Document

## Project Overview
**Name:** Private After Dark
**Type:** Telegram AI Companion Service with Landing Page
**Status:** MVP Complete
**Last Updated:** January 2026

## Original Problem Statement
Build a monetizable Telegram AI Companion system with 3 distinct fantasy personalities (Valeria Voss, Luna Mirelle, Nyx), subscription-based access, and a high-converting landing page. Premium AI fantasy companion service - NOT a dating app.

## User Personas
1. **Free User:** Adults 18+ exploring AI companionship, limited to 15 messages/day
2. **Premium Subscriber ($19/mo):** Users wanting unlimited messages with emotional memory
3. **VIP Subscriber ($39/mo):** Power users wanting explicit mode, voice messages, and full memory persistence

## Core Requirements (Static)
- Telegram bot with 3 distinct AI personalities
- Character selection (Valeria, Luna, Nyx)
- Daily message limits for free tier (15/day)
- Stripe subscription payments ($19 Premium, $39 VIP)
- OpenAI GPT integration for chat responses
- ElevenLabs TTS for VIP voice messages
- MongoDB for user data and chat history
- Luxury dark-themed landing page

## Architecture

### Backend (FastAPI)
- `/api/webhook/telegram` - Telegram bot updates
- `/api/webhook/stripe` - Stripe payment webhooks
- `/api/checkout/create` - Create Stripe checkout sessions
- `/api/checkout/status/{session_id}` - Check payment status
- `/api/telegram/info` - Get bot info
- `/api/telegram/set-webhook` - Configure Telegram webhook

### Frontend (React)
- Landing page with Hero, Characters, How It Works, Pricing, Safety sections
- Payment success/cancel pages
- Framer Motion animations
- Dark luxury theme (#0F0F14, #E91E8C, #7C3AED)

### Database (MongoDB)
Collections:
- `users` - Telegram users with tier, character selection, message counts
- `chat_messages` - Chat history per user/character
- `payment_transactions` - Stripe payment records

## What's Been Implemented ✅
- [x] Complete landing page with all sections
- [x] 3 Character system (Valeria, Luna, Nyx) with unique prompts
- [x] Telegram webhook handler with /start, /status, /switch, /explicit commands
- [x] Character selection via inline keyboard
- [x] Daily message limit logic (15 for free, unlimited for paid)
- [x] Stripe checkout integration ($19 Premium, $39 VIP)
- [x] Payment webhook handling and tier upgrades
- [x] OpenAI chat via Emergent Universal Key
- [x] ElevenLabs TTS wiring (mocked until API key provided)
- [x] MongoDB user storage and chat history
- [x] VIP explicit mode toggle

## Environment Variables
- `TELEGRAM_BOT_TOKEN` - **USER MUST PROVIDE** via @BotFather
- `OPENAI_MODEL` - Default: gpt-4o
- `ELEVENLABS_API_KEY` - Optional, enables VIP voice
- `STRIPE_API_KEY` - Test key active
- `EMERGENT_LLM_KEY` - Pre-configured

## Prioritized Backlog

### P0 - Critical (Before Go-Live)
- [ ] User provides Telegram Bot Token
- [ ] Set webhook URL via /api/telegram/set-webhook
- [ ] Test live bot conversation flow

### P1 - High Priority
- [ ] Add ElevenLabs API key for voice messages
- [ ] Memory summarization for Premium/VIP users
- [ ] Subscription cancellation handling

### P2 - Medium Priority  
- [ ] Custom character creation
- [ ] Voice-to-text input
- [ ] Web-based chat UI option
- [ ] Analytics dashboard

## Next Action Items
1. Get Telegram Bot Token from @BotFather
2. Configure webhook URL
3. Add ElevenLabs key for voice (optional)
4. Test full conversation flow with real bot
5. Deploy to production (Railway/Render)
