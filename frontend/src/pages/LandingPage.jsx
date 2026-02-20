import React, { useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Crown, Moon, Heart, Sparkles, Shield, Lock, MessageCircle, Zap, Check, ChevronDown, Send, ChevronUp, EyeOff, Users, Gift } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Translations
const translations = {
  en: {
    badge: "Private AI Companion Service",
    headline1: "Three fantasies.",
    headline2: "One private line.",
    subtext: "Choose your companion. Step into a private conversation. Unlock deeper modes when you're ready.",
    cta: "Start on Telegram",
    meetCompanions: "Meet the companions",
    adultOnly: "18+ Only — Private & Encrypted",
    chooseCompanion: "Choose Your Companion",
    chooseCompanionSub: "Three distinct personalities. Each with their own allure.",
    howItWorks: "How It Works",
    howItWorksSub: "No apps. No downloads. Just you — and who you choose.",
    step1: "Choose your companion",
    step1desc: "Three distinct personalities, each with their own allure.",
    step2: "Start chatting instantly",
    step2desc: "No downloads. Just open Telegram and say hello.",
    step3: "Unlock deeper access",
    step3desc: "Premium tiers reveal new depths of connection.",
    pricing: "Unlock Deeper Access",
    pricingSub: "Choose the level of connection that suits you.",
    free: "Free",
    premium: "Private Access",
    vip: "After Dark",
    month: "/month",
    mostPopular: "Most Popular",
    startFree: "Start Free",
    upgradePremium: "Unlock Private Access",
    goVip: "Go After Dark",
    freeFeatures: ["10 lifetime messages", "Text conversations", "One companion", "Basic escalation"],
    premiumFeatures: ["Unlimited messages", "Full explicit mode", "Emotional memory", "Priority responses"],
    vipFeatures: ["Everything in Private Access", "Voice messages", "All 3 companions", "Switch anytime", "Maximum intensity"],
    referral: "Invite Friends. Unlock More.",
    referralSub: "Share your unique link. Earn +5 bonus messages for each friend who joins.",
    referralCta: "Get Your Referral Link",
    referralBenefit1: "Share your unique link",
    referralBenefit2: "+5 bonus messages per referral",
    referralBenefit3: "Unlimited referral rewards",
    faq: "Frequently Asked Questions",
    faqItems: [
      { q: "What is Private After Dark?", a: "Private After Dark is a premium AI companion service that offers intimate, personalized conversations with three unique AI personalities through Telegram." },
      { q: "Is this a dating app?", a: "No. This is an AI fantasy companion service. You're interacting with AI personalities, not real people." },
      { q: "How do I start?", a: "Click 'Start on Telegram' to open our bot. Select your preferred language, choose your companion, and begin your conversation." },
      { q: "What's included in After Dark?", a: "After Dark unlocks unlimited messages, voice messages, all three companions, explicit mode, and maximum intensity." },
      { q: "Is my conversation private?", a: "Yes. All conversations are private and encrypted. We do not share or sell your data." },
      { q: "Can I switch companions?", a: "After Dark members can switch between all three companions anytime. Free and Private Access users are dedicated to one companion." }
    ],
    privacy: "Your Privacy Matters",
    privacySub: "We take your privacy seriously. Here's our commitment to you.",
    privacyItems: [
      { title: "18+ Only", desc: "Strict age verification. This service is exclusively for adults." },
      { title: "Consent-First", desc: "All interactions are consensual. You control the conversation." },
      { title: "Encrypted", desc: "End-to-end encryption protects all your messages." },
      { title: "No Exposure", desc: "No public profiles. No social features. Complete anonymity." }
    ],
    footerDisclaimer: "Private After Dark is an AI fantasy companion service for adults 18+. All characters are AI-generated personas. No real individuals are represented.",
    terms: "Terms of Service",
    privacyPolicy: "Privacy Policy",
    openTelegram: "Open in Telegram",
    chatWith: "Chat with",
    valeria: { name: "Valeria Voss", tagline: "Classy. Controlled. Intensely selective.", desc: "She doesn't chase.\nShe chooses." },
    luna: { name: "Luna Mirelle", tagline: "Soft. Emotional. Deeply attached.", desc: "She remembers how you speak.\nAnd how you feel." },
    nyx: { name: "Nyx", tagline: "Mysterious. Slow. Unpredictable.", desc: "She reveals slowly.\nIf you can handle it." }
  },
  es: {
    badge: "Servicio de Compañía IA Privado",
    headline1: "Tres fantasías.",
    headline2: "Una línea privada.",
    subtext: "Elige tu compañera. Entra en una conversación privada. Desbloquea modos más profundos cuando estés listo.",
    cta: "Empezar en Telegram",
    meetCompanions: "Conoce las compañeras",
    adultOnly: "Solo 18+ — Privado y Encriptado",
    chooseCompanion: "Elige Tu Compañera",
    chooseCompanionSub: "Tres personalidades distintas. Cada una con su propio encanto.",
    howItWorks: "Cómo Funciona",
    howItWorksSub: "Sin apps. Sin descargas. Solo tú — y quien elijas.",
    step1: "Elige tu compañera",
    step1desc: "Tres personalidades distintas, cada una con su encanto.",
    step2: "Empieza a chatear al instante",
    step2desc: "Sin descargas. Solo abre Telegram y di hola.",
    step3: "Desbloquea acceso más profundo",
    step3desc: "Los niveles premium revelan nuevas profundidades.",
    pricing: "Desbloquea Acceso Más Profundo",
    pricingSub: "Elige el nivel de conexión que te convenga.",
    free: "Gratis",
    premium: "Acceso Privado",
    vip: "After Dark",
    month: "/mes",
    mostPopular: "Más Popular",
    startFree: "Empezar Gratis",
    upgradePremium: "Desbloquear Acceso Privado",
    goVip: "Ir After Dark",
    freeFeatures: ["10 mensajes de por vida", "Conversaciones de texto", "Una compañera", "Escalada básica"],
    premiumFeatures: ["Mensajes ilimitados", "Modo explícito completo", "Memoria emocional", "Respuestas prioritarias"],
    vipFeatures: ["Todo en Acceso Privado", "Mensajes de voz", "Las 3 compañeras", "Cambia cuando quieras", "Intensidad máxima"],
    referral: "Invita Amigos. Desbloquea Más.",
    referralSub: "Comparte tu enlace único. Gana +5 mensajes bonus por cada amigo que se una.",
    referralCta: "Obtener Tu Enlace de Referido",
    referralBenefit1: "Comparte tu enlace único",
    referralBenefit2: "+5 mensajes bonus por referido",
    referralBenefit3: "Recompensas ilimitadas",
    faq: "Preguntas Frecuentes",
    faqItems: [
      { q: "¿Qué es Private After Dark?", a: "Private After Dark es un servicio premium de compañía IA que ofrece conversaciones íntimas y personalizadas con tres personalidades IA únicas a través de Telegram." },
      { q: "¿Es una app de citas?", a: "No. Es un servicio de compañía IA de fantasía. Interactúas con personalidades IA, no personas reales." },
      { q: "¿Cómo empiezo?", a: "Haz clic en 'Empezar en Telegram' para abrir nuestro bot. Selecciona tu idioma, elige tu compañera y comienza." },
      { q: "¿Qué incluye After Dark?", a: "After Dark desbloquea mensajes ilimitados, mensajes de voz, las tres compañeras, modo explícito e intensidad máxima." },
      { q: "¿Es privada mi conversación?", a: "Sí. Todas las conversaciones son privadas y encriptadas. No compartimos ni vendemos tus datos." },
      { q: "¿Puedo cambiar de compañera?", a: "Los miembros After Dark pueden cambiar entre las tres compañeras. Los usuarios Gratis y Acceso Privado están dedicados a una." }
    ],
    privacy: "Tu Privacidad Importa",
    privacySub: "Nos tomamos tu privacidad en serio. Aquí está nuestro compromiso.",
    privacyItems: [
      { title: "Solo 18+", desc: "Verificación estricta de edad. Servicio exclusivo para adultos." },
      { title: "Consentimiento Primero", desc: "Todas las interacciones son consensuadas. Tú controlas." },
      { title: "Encriptado", desc: "Encriptación de extremo a extremo protege todos tus mensajes." },
      { title: "Sin Exposición", desc: "Sin perfiles públicos. Anonimato completo." }
    ],
    footerDisclaimer: "Private After Dark es un servicio de compañía IA de fantasía para adultos 18+. Todos los personajes son personas generadas por IA.",
    terms: "Términos de Servicio",
    privacyPolicy: "Política de Privacidad",
    openTelegram: "Abrir en Telegram",
    chatWith: "Chatear con",
    valeria: { name: "Valeria Voss", tagline: "Con clase. Controlada. Intensamente selectiva.", desc: "Ella no persigue.\nElla elige." },
    luna: { name: "Luna Mirelle", tagline: "Suave. Emocional. Profundamente apegada.", desc: "Recuerda cómo hablas.\nY cómo te sientes." },
    nyx: { name: "Nyx", tagline: "Misteriosa. Lenta. Impredecible.", desc: "Se revela lentamente.\nSi puedes soportarlo." }
  },
  fr: {
    badge: "Service de Compagnon IA Privé",
    headline1: "Trois fantasmes.",
    headline2: "Une ligne privée.",
    subtext: "Choisissez votre compagnon. Entrez dans une conversation privée. Débloquez des modes plus profonds quand vous êtes prêt.",
    cta: "Commencer sur Telegram",
    meetCompanions: "Rencontrez les compagnons",
    adultOnly: "18+ Seulement — Privé & Crypté",
    chooseCompanion: "Choisissez Votre Compagnon",
    chooseCompanionSub: "Trois personnalités distinctes. Chacune avec son propre charme.",
    howItWorks: "Comment Ça Marche",
    howItWorksSub: "Pas d'applications. Pas de téléchargements. Juste vous — et qui vous choisissez.",
    step1: "Choisissez votre compagnon",
    step1desc: "Trois personnalités distinctes, chacune avec son propre charme.",
    step2: "Commencez à discuter instantanément",
    step2desc: "Pas de téléchargements. Ouvrez Telegram et dites bonjour.",
    step3: "Débloquez un accès plus profond",
    step3desc: "Les niveaux premium révèlent de nouvelles profondeurs.",
    pricing: "Débloquez un Accès Plus Profond",
    pricingSub: "Choisissez le niveau de connexion qui vous convient.",
    free: "Gratuit",
    premium: "Accès Privé",
    vip: "After Dark",
    month: "/mois",
    mostPopular: "Le Plus Populaire",
    startFree: "Commencer Gratuitement",
    upgradePremium: "Débloquer Accès Privé",
    goVip: "Passer After Dark",
    freeFeatures: ["10 messages à vie", "Conversations texte", "Un compagnon", "Escalade basique"],
    premiumFeatures: ["Messages illimités", "Mode explicite complet", "Mémoire émotionnelle", "Réponses prioritaires"],
    vipFeatures: ["Tout dans Accès Privé", "Messages vocaux", "Les 3 compagnons", "Changez quand vous voulez", "Intensité maximale"],
    referral: "Invitez des Amis. Débloquez Plus.",
    referralSub: "Partagez votre lien unique. Gagnez +5 messages bonus pour chaque ami qui rejoint.",
    referralCta: "Obtenir Votre Lien de Parrainage",
    referralBenefit1: "Partagez votre lien unique",
    referralBenefit2: "+5 messages bonus par parrainage",
    referralBenefit3: "Récompenses illimitées",
    faq: "Questions Fréquentes",
    faqItems: [
      { q: "Qu'est-ce que Private After Dark?", a: "Private After Dark est un service de compagnon IA premium offrant des conversations intimes et personnalisées avec trois personnalités IA uniques via Telegram." },
      { q: "Est-ce une application de rencontre?", a: "Non. C'est un service de compagnon IA fantasy. Vous interagissez avec des personnalités IA, pas des vraies personnes." },
      { q: "Comment commencer?", a: "Cliquez sur 'Commencer sur Telegram' pour ouvrir notre bot. Sélectionnez votre langue, choisissez votre compagnon et commencez." },
      { q: "Que comprend After Dark?", a: "After Dark débloque les messages illimités, messages vocaux, les trois compagnons, mode explicite et intensité maximale." },
      { q: "Ma conversation est-elle privée?", a: "Oui. Toutes les conversations sont privées et cryptées. Nous ne partageons pas vos données." },
      { q: "Puis-je changer de compagnon?", a: "Les membres After Dark peuvent changer entre les trois compagnons. Les utilisateurs Gratuit et Accès Privé sont dédiés à un." }
    ],
    privacy: "Votre Vie Privée Compte",
    privacySub: "Nous prenons votre vie privée au sérieux. Voici notre engagement.",
    privacyItems: [
      { title: "18+ Seulement", desc: "Vérification stricte de l'âge. Service exclusivement pour adultes." },
      { title: "Consentement d'abord", desc: "Toutes les interactions sont consensuelles. Vous contrôlez." },
      { title: "Crypté", desc: "Le cryptage de bout en bout protège tous vos messages." },
      { title: "Pas d'exposition", desc: "Pas de profils publics. Anonymat complet." }
    ],
    footerDisclaimer: "Private After Dark est un service de compagnon IA fantasy pour adultes 18+. Tous les personnages sont des personas générés par IA.",
    terms: "Conditions d'utilisation",
    privacyPolicy: "Politique de confidentialité",
    openTelegram: "Ouvrir dans Telegram",
    chatWith: "Discuter avec",
    valeria: { name: "Valeria Voss", tagline: "Classe. Contrôlée. Intensément sélective.", desc: "Elle ne chasse pas.\nElle choisit." },
    luna: { name: "Luna Mirelle", tagline: "Douce. Émotionnelle. Profondément attachée.", desc: "Elle se souvient comment vous parlez.\nEt comment vous vous sentez." },
    nyx: { name: "Nyx", tagline: "Mystérieuse. Lente. Imprévisible.", desc: "Elle se révèle lentement.\nSi vous pouvez le supporter." }
  },
  ar: {
    badge: "خدمة رفيق الذكاء الاصطناعي الخاصة",
    headline1: "ثلاثة أحلام.",
    headline2: "خط واحد خاص.",
    subtext: "اختر رفيقك. ادخل في محادثة خاصة. افتح أوضاعًا أعمق عندما تكون مستعدًا.",
    cta: "ابدأ على تيليجرام",
    meetCompanions: "قابل الرفقاء",
    adultOnly: "18+ فقط — خاص ومشفر",
    chooseCompanion: "اختر رفيقك",
    chooseCompanionSub: "ثلاث شخصيات مميزة. كل واحدة بسحرها الخاص.",
    howItWorks: "كيف يعمل",
    howItWorksSub: "لا تطبيقات. لا تنزيلات. فقط أنت — ومن تختار.",
    step1: "اختر رفيقك",
    step1desc: "ثلاث شخصيات مميزة، كل واحدة بسحرها الخاص.",
    step2: "ابدأ المحادثة فوراً",
    step2desc: "لا تنزيلات. فقط افتح تيليجرام وقل مرحباً.",
    step3: "افتح وصولاً أعمق",
    step3desc: "المستويات المميزة تكشف أعماقاً جديدة.",
    pricing: "افتح وصولاً أعمق",
    pricingSub: "اختر مستوى الاتصال الذي يناسبك.",
    free: "مجاني",
    premium: "وصول خاص",
    vip: "After Dark",
    month: "/شهر",
    mostPopular: "الأكثر شعبية",
    startFree: "ابدأ مجاناً",
    upgradePremium: "فتح الوصول الخاص",
    goVip: "اذهب After Dark",
    freeFeatures: ["10 رسائل مدى الحياة", "محادثات نصية", "رفيق واحد", "تصعيد أساسي"],
    premiumFeatures: ["رسائل غير محدودة", "وضع صريح كامل", "ذاكرة عاطفية", "ردود ذات أولوية"],
    vipFeatures: ["كل شيء في الوصول الخاص", "رسائل صوتية", "جميع الرفقاء الـ3", "غيّر في أي وقت", "أقصى كثافة"],
    referral: "ادعُ الأصدقاء. افتح المزيد.",
    referralSub: "شارك رابطك الفريد. اكسب +5 رسائل مكافأة لكل صديق ينضم.",
    referralCta: "احصل على رابط الإحالة",
    referralBenefit1: "شارك رابطك الفريد",
    referralBenefit2: "+5 رسائل مكافأة لكل إحالة",
    referralBenefit3: "مكافآت غير محدودة",
    faq: "الأسئلة الشائعة",
    faqItems: [
      { q: "ما هو Private After Dark؟", a: "Private After Dark هي خدمة رفيق ذكاء اصطناعي متميزة تقدم محادثات حميمة وشخصية مع ثلاث شخصيات ذكاء اصطناعي فريدة عبر تيليجرام." },
      { q: "هل هذا تطبيق مواعدة؟", a: "لا. هذه خدمة رفيق ذكاء اصطناعي خيالي. أنت تتفاعل مع شخصيات ذكاء اصطناعي، وليس أشخاص حقيقيين." },
      { q: "كيف أبدأ؟", a: "انقر على 'ابدأ على تيليجرام' لفتح البوت. اختر لغتك، اختر رفيقك، وابدأ محادثتك." },
      { q: "ماذا يشمل After Dark؟", a: "After Dark يفتح رسائل غير محدودة، رسائل صوتية، جميع الرفقاء الثلاثة، وضع صريح وأقصى كثافة." },
      { q: "هل محادثتي خاصة؟", a: "نعم. جميع المحادثات خاصة ومشفرة. نحن لا نشارك بياناتك." },
      { q: "هل يمكنني تغيير الرفيق؟", a: "أعضاء After Dark يمكنهم التبديل بين الرفقاء الثلاثة. المستخدمون المجانيون والوصول الخاص مخصصون لرفيق واحد." }
    ],
    privacy: "خصوصيتك مهمة",
    privacySub: "نحن نأخذ خصوصيتك على محمل الجد. إليك التزامنا لك.",
    privacyItems: [
      { title: "18+ فقط", desc: "تحقق صارم من العمر. خدمة حصرية للبالغين." },
      { title: "الموافقة أولاً", desc: "جميع التفاعلات بالتراضي. أنت تتحكم." },
      { title: "مشفر", desc: "التشفير من طرف إلى طرف يحمي جميع رسائلك." },
      { title: "لا تعرض", desc: "لا ملفات شخصية عامة. سرية كاملة." }
    ],
    footerDisclaimer: "Private After Dark هي خدمة رفيق ذكاء اصطناعي خيالي للبالغين 18+. جميع الشخصيات هي شخصيات مولدة بالذكاء الاصطناعي.",
    terms: "شروط الخدمة",
    privacyPolicy: "سياسة الخصوصية",
    openTelegram: "افتح في تيليجرام",
    chatWith: "تحدث مع",
    valeria: { name: "فاليريا فوس", tagline: "أنيقة. متحكمة. انتقائية بشدة.", desc: "هي لا تطارد.\nهي تختار." },
    luna: { name: "لونا ميريل", tagline: "ناعمة. عاطفية. متعلقة بعمق.", desc: "تتذكر كيف تتحدث.\nوكيف تشعر." },
    nyx: { name: "نيكس", tagline: "غامضة. بطيئة. لا يمكن التنبؤ بها.", desc: "تكشف ببطء.\nإذا كنت تستطيع التحمل." }
  }
};

// Character data with user-provided images
const getCharacters = (t) => [
  {
    id: 'valeria',
    name: t.valeria.name,
    emoji: '👑',
    icon: Crown,
    tagline: t.valeria.tagline,
    description: t.valeria.desc,
    image: '/characters/valeria.jpg',
    glowColor: 'rgba(109, 40, 217, 0.4)'
  },
  {
    id: 'luna',
    name: t.luna.name,
    emoji: '🌙',
    icon: Moon,
    tagline: t.luna.tagline,
    description: t.luna.desc,
    image: '/characters/luna.jpg',
    glowColor: 'rgba(139, 92, 246, 0.4)'
  },
  {
    id: 'nyx',
    name: t.nyx.name,
    emoji: '🖤',
    icon: Heart,
    tagline: t.nyx.tagline,
    description: t.nyx.desc,
    image: '/characters/nyx.jpg',
    glowColor: 'rgba(212, 175, 55, 0.3)'
  }
];

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.22, 1, 0.36, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.2, delayChildren: 0.1 } }
};

// Aurora Background Component - Flowing light animation
const AuroraBackground = () => {
  return (
    <div className="aurora-container">
      {/* Main nebula layers */}
      <motion.div 
        className="aurora-layer"
        style={{
          background: 'conic-gradient(from 0deg at 50% 50%, transparent 0deg, rgba(109, 40, 217, 0.25) 60deg, transparent 120deg, rgba(139, 92, 246, 0.2) 180deg, transparent 240deg, rgba(212, 175, 55, 0.1) 300deg, transparent 360deg)',
        }}
        animate={{ rotate: [0, 360] }}
        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
      />
      
      {/* Primary floating orb - large violet */}
      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(109, 40, 217, 0.35) 0%, rgba(109, 40, 217, 0.1) 40%, transparent 70%)',
          filter: 'blur(40px)',
          top: '10%',
          left: '10%',
        }}
        animate={{
          x: [0, 150, 80, -50, 0],
          y: [0, -80, -150, -50, 0],
          scale: [1, 1.3, 0.9, 1.2, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
      />
      
      {/* Secondary orb - purple */}
      <motion.div
        className="absolute w-[500px] h-[500px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, rgba(139, 92, 246, 0.1) 40%, transparent 70%)',
          filter: 'blur(50px)',
          bottom: '10%',
          right: '10%',
        }}
        animate={{
          x: [0, -120, 50, 100, 0],
          y: [0, 100, -60, 120, 0],
          scale: [1, 0.85, 1.2, 1.1, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut", delay: 3 }}
      />
      
      {/* Tertiary orb - gold accent */}
      <motion.div
        className="absolute w-[350px] h-[350px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0.05) 40%, transparent 70%)',
          filter: 'blur(30px)',
          top: '40%',
          right: '25%',
        }}
        animate={{
          x: [0, 80, -60, 100, 0],
          y: [0, -100, 80, -60, 0],
          scale: [1, 1.15, 0.9, 1.1, 1],
        }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut", delay: 8 }}
      />
      
      {/* Light beams */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute"
          style={{
            width: '3px',
            height: '250px',
            left: `${10 + i * 16}%`,
            top: '-15%',
            background: `linear-gradient(to bottom, transparent 0%, rgba(139, 92, 246, ${0.4 + i * 0.08}) 50%, transparent 100%)`,
            filter: 'blur(3px)',
            borderRadius: '50%',
          }}
          animate={{
            y: ['0%', '180%'],
            opacity: [0, 0.8, 0],
            scaleY: [1, 1.5, 1],
          }}
          transition={{
            duration: 6 + i * 1.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 2.5,
          }}
        />
      ))}
      
      {/* Horizontal aurora wave */}
      <motion.div
        className="absolute w-full h-[200px]"
        style={{
          top: '30%',
          background: 'linear-gradient(90deg, transparent 0%, rgba(109, 40, 217, 0.15) 25%, rgba(139, 92, 246, 0.2) 50%, rgba(109, 40, 217, 0.15) 75%, transparent 100%)',
          filter: 'blur(60px)',
        }}
        animate={{
          x: ['-50%', '50%', '-50%'],
          opacity: [0.3, 0.6, 0.3],
          scaleY: [1, 1.5, 1],
        }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
      />
      
      {/* Bottom glow */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-[300px]"
        style={{
          background: 'linear-gradient(to top, rgba(109, 40, 217, 0.15), transparent)',
        }}
      />
    </div>
  );
};

const LandingPage = () => {
  const [lang, setLang] = useState('en');
  const [botLink, setBotLink] = useState('https://t.me/MidnightDesireAi_bot');
  const [openFaq, setOpenFaq] = useState(null);
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
  
  const t = translations[lang];
  const characters = getCharacters(t);
  const isRtl = lang === 'ar';
  
  useEffect(() => {
    const fetchBotInfo = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/telegram/info`);
        if (response.data.configured && response.data.link) {
          setBotLink(response.data.link);
        }
      } catch (error) {
        console.log('Bot info not available');
      }
    };
    fetchBotInfo();
  }, []);

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const pricingTiers = [
    { name: t.free, price: '0', period: '', features: t.freeFeatures, cta: t.startFree, highlighted: false },
    { name: t.premium, price: '19', period: t.month, features: t.premiumFeatures, cta: t.upgradePremium, highlighted: true, tier: 'premium' },
    { name: t.vip, price: '39', period: t.month, features: t.vipFeatures, cta: t.goVip, highlighted: false, tier: 'vip' }
  ];

  const steps = [
    { number: '01', title: t.step1, description: t.step1desc, icon: Sparkles },
    { number: '02', title: t.step2, description: t.step2desc, icon: MessageCircle },
    { number: '03', title: t.step3, description: t.step3desc, icon: Lock }
  ];

  return (
    <div className={`min-h-screen bg-[#0B0B10] text-white overflow-hidden ${isRtl ? 'rtl' : 'ltr'}`} dir={isRtl ? 'rtl' : 'ltr'}>
      <div className="noise-overlay" />
      <AuroraBackground />
      
      {/* Language Toggle */}
      <div className="fixed top-4 right-4 z-50">
        <div className="glass rounded-full px-2 py-1 flex items-center gap-1">
          {['en', 'es', 'fr', 'ar'].map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
                lang === l ? 'bg-[#6D28D9] text-white' : 'text-zinc-400 hover:text-white'
              }`}
              data-testid={`lang-${l}`}
            >
              {l.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Hero Section */}
      <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <motion.div className="relative z-10 text-center px-6 max-w-5xl mx-auto" style={{ opacity: heroOpacity }}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}>
            <span className="inline-block px-4 py-2 rounded-full glass text-sm text-zinc-400 mb-8">{t.badge}</span>
          </motion.div>
          
          <motion.h1 
            className="text-5xl sm:text-6xl lg:text-8xl font-bold tracking-tight mb-6 leading-none"
            initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.4 }}
            data-testid="hero-headline"
          >
            {t.headline1}
            <br />
            <span className="violet-gradient-text">{t.headline2}</span>
          </motion.h1>
          
          <motion.p 
            className="text-lg sm:text-xl text-zinc-400 mb-12 max-w-2xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.6 }}
          >
            {t.subtext}
          </motion.p>
          
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.8 }}
          >
            <a
              href={botLink}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-flex items-center gap-3 text-white px-8 py-4 rounded-full font-bold text-lg"
              data-testid="start-telegram-btn"
            >
              <Send className="w-5 h-5" />
              {t.cta}
            </a>
            <button
              onClick={() => scrollToSection('characters')}
              className="btn-secondary inline-flex items-center gap-2 px-6 py-3 rounded-full text-zinc-300"
              data-testid="meet-companions-btn"
            >
              {t.meetCompanions}
              <ChevronDown className="w-4 h-4" />
            </button>
          </motion.div>
          
          <motion.p
            className="mt-8 text-sm text-zinc-600"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8, delay: 1 }}
          >
            {t.adultOnly}
          </motion.p>
        </motion.div>
        
        <motion.div 
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <ChevronDown className="w-6 h-6 text-zinc-600" />
        </motion.div>
      </section>

      {/* Characters Section */}
      <section id="characters" className="py-24 md:py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div className="text-center mb-16" variants={fadeInUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="characters-title">{t.chooseCompanion}</h2>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">{t.chooseCompanionSub}</p>
          </motion.div>
          
          <motion.div className="grid grid-cols-1 md:grid-cols-3 gap-8" variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            {characters.map((character, index) => (
              <CharacterCard key={character.id} character={character} botLink={botLink} t={t} lang={lang} index={index} />
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 md:py-32 px-6 bg-[#111118]">
        <div className="max-w-5xl mx-auto">
          <motion.div className="text-center mb-16" variants={fadeInUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="how-it-works-title">{t.howItWorks}</h2>
            <p className="text-zinc-400 text-lg">{t.howItWorksSub}</p>
          </motion.div>
          
          <motion.div className="grid grid-cols-1 md:grid-cols-3 gap-8" variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            {steps.map((step, index) => (
              <motion.div key={step.number} className="text-center group" variants={fadeInUp}>
                <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl glass glass-hover mb-6">
                  <step.icon className="w-7 h-7 text-[#8B5CF6] group-hover:animate-subtle-bounce" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full violet-gradient flex items-center justify-center text-xs font-bold">
                    {index + 1}
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                <p className="text-zinc-400">{step.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Referral Section */}
      <section id="referral" className="py-24 md:py-32 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div 
            className="referral-gradient rounded-3xl p-8 md:p-12 border border-[#6D28D9]/20"
            variants={fadeInUp} 
            initial="hidden" 
            whileInView="visible" 
            viewport={{ once: true }}
          >
            <div className="text-center">
              <motion.div 
                className="inline-flex items-center justify-center w-16 h-16 rounded-2xl violet-gradient mb-6"
                whileHover={{ scale: 1.1, rotate: 5 }}
              >
                <Gift className="w-8 h-8 text-white" />
              </motion.div>
              
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4" data-testid="referral-title">
                {t.referral}
              </h2>
              <p className="text-zinc-400 text-lg mb-8 max-w-xl mx-auto">{t.referralSub}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[t.referralBenefit1, t.referralBenefit2, t.referralBenefit3].map((benefit, i) => (
                  <div key={i} className="flex items-center gap-3 justify-center md:justify-start">
                    <div className="w-8 h-8 rounded-full bg-[#6D28D9]/20 flex items-center justify-center flex-shrink-0">
                      <Check className="w-4 h-4 text-[#8B5CF6]" />
                    </div>
                    <span className="text-zinc-300">{benefit}</span>
                  </div>
                ))}
              </div>
              
              <a
                href={botLink}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-3 text-white px-8 py-4 rounded-full font-bold"
                data-testid="referral-cta"
              >
                <Users className="w-5 h-5" />
                {t.referralCta}
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 md:py-32 px-6 bg-[#111118]">
        <div className="max-w-6xl mx-auto">
          <motion.div className="text-center mb-16" variants={fadeInUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="pricing-title">{t.pricing}</h2>
            <p className="text-zinc-400 text-lg">{t.pricingSub}</p>
          </motion.div>
          
          <motion.div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8" variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            {pricingTiers.map((tier) => (
              <PricingCard key={tier.name} tier={tier} botLink={botLink} mostPopular={t.mostPopular} />
            ))}
          </motion.div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 md:py-32 px-6">
        <div className="max-w-3xl mx-auto">
          <motion.div className="text-center mb-12" variants={fadeInUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="faq-title">{t.faq}</h2>
          </motion.div>
          
          <motion.div className="space-y-4" variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            {t.faqItems.map((item, index) => (
              <motion.div key={index} className="glass rounded-2xl overflow-hidden" variants={fadeInUp}>
                <button
                  className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  data-testid={`faq-q-${index}`}
                >
                  <span className="font-medium text-lg">{item.q}</span>
                  {openFaq === index ? <ChevronUp className="w-5 h-5 text-[#8B5CF6]" /> : <ChevronDown className="w-5 h-5 text-zinc-500" />}
                </button>
                {openFaq === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="px-6 pb-5"
                  >
                    <p className="text-zinc-400">{item.a}</p>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Privacy */}
      <section id="privacy" className="py-24 md:py-32 px-6 bg-[#111118]">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div variants={fadeInUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl glass mb-8">
              <Shield className="w-8 h-8 text-[#8B5CF6]" />
            </div>
            
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="privacy-title">{t.privacy}</h2>
            <p className="text-zinc-400 text-lg mb-12">{t.privacySub}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
              {t.privacyItems.map((item, index) => (
                <motion.div key={index} className="glass glass-hover rounded-2xl p-6" variants={fadeInUp} custom={index}>
                  {index === 0 && <Lock className="w-6 h-6 text-[#8B5CF6] mx-auto mb-3" />}
                  {index === 1 && <Heart className="w-6 h-6 text-[#8B5CF6] mx-auto mb-3" />}
                  {index === 2 && <Shield className="w-6 h-6 text-[#8B5CF6] mx-auto mb-3" />}
                  {index === 3 && <EyeOff className="w-6 h-6 text-[#8B5CF6] mx-auto mb-3" />}
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-400">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-zinc-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl violet-gradient flex items-center justify-center">
                <Moon className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg">Private After Dark</span>
            </div>
            
            <div className="flex items-center gap-6 text-sm text-zinc-500">
              <span>{t.adultOnly.split('—')[0].trim()}</span>
              <span>•</span>
              <a href="#" className="hover:text-white transition-colors">{t.terms}</a>
              <span>•</span>
              <a href="#" className="hover:text-white transition-colors">{t.privacyPolicy}</a>
            </div>
            
            <a
              href={botLink}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full glass glass-hover text-sm font-medium"
              data-testid="footer-telegram-btn"
            >
              <Send className="w-4 h-4" />
              {t.openTelegram}
            </a>
          </div>
          
          <div className="mt-8 pt-8 border-t border-zinc-800/50 text-center">
            <p className="text-xs text-zinc-600">{t.footerDisclaimer}</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Character Card with parallax effect
const CharacterCard = ({ character, botLink, t, lang, index }) => {
  const Icon = character.icon;
  
  return (
    <motion.div
      className="character-card relative aspect-[3/4] rounded-2xl overflow-hidden group cursor-pointer"
      variants={fadeInUp}
      whileHover={{ y: -12 }}
      data-testid={`character-card-${character.id}`}
    >
      {/* Gradient border on hover */}
      <div className="card-border rounded-2xl" />
      
      {/* Glow effect */}
      <div 
        className="character-glow absolute inset-0 opacity-0 transition-opacity duration-700 z-10 pointer-events-none"
        style={{ boxShadow: `0 0 100px 30px ${character.glowColor}` }}
      />
      
      {/* Image */}
      <div className="absolute inset-0 overflow-hidden rounded-2xl">
        <motion.img
          src={character.image}
          alt={character.name}
          className="character-image w-full h-full object-cover transition-all duration-700"
          style={{ objectPosition: 'center top' }}
        />
        <div className="character-overlay absolute inset-0 bg-gradient-to-t from-[#0B0B10] via-[#0B0B10]/50 to-transparent transition-all duration-500" />
      </div>
      
      {/* Content */}
      <div className="absolute inset-0 flex flex-col justify-end p-6 z-20">
        <div className="mb-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full violet-gradient text-sm font-medium mb-3">
            <Icon className="w-4 h-4" />
            {character.emoji} {character.name}
          </div>
          <h3 className="text-xl font-semibold mb-2">{character.tagline}</h3>
          <p className="text-zinc-400 text-sm whitespace-pre-line">{character.description}</p>
        </div>
        
        <a
          href={`${botLink}?start=char_${character.id}_${lang}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 w-full py-3 rounded-xl glass glass-hover font-medium text-sm transition-all duration-300"
          data-testid={`chat-with-${character.id}-btn`}
        >
          <MessageCircle className="w-4 h-4" />
          {t.chatWith} {character.name.split(' ')[0]}
        </a>
      </div>
    </motion.div>
  );
};

// Pricing Card
const PricingCard = ({ tier, botLink, mostPopular }) => {
  return (
    <motion.div
      className={`pricing-card relative rounded-3xl p-8 ${tier.highlighted ? 'pricing-highlight bg-[#111118]' : 'glass'}`}
      variants={fadeInUp}
      whileHover={{ y: -8 }}
      data-testid={`pricing-card-${tier.name.toLowerCase()}`}
    >
      {tier.highlighted && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full violet-gradient text-xs font-bold">
          {mostPopular}
        </div>
      )}
      
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2">{tier.name}</h3>
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold">${tier.price}</span>
          {tier.period && <span className="text-zinc-500">{tier.period}</span>}
        </div>
      </div>
      
      <ul className="space-y-4 mb-8">
        {tier.features.map((feature, index) => (
          <li key={index} className="flex items-start gap-3">
            <Check className="w-5 h-5 text-[#8B5CF6] flex-shrink-0 mt-0.5" />
            <span className="text-zinc-300 text-sm">{feature}</span>
          </li>
        ))}
      </ul>
      
      <a
        href={botLink}
        target="_blank"
        rel="noopener noreferrer"
        className={`block w-full py-3 rounded-xl font-medium text-center transition-all duration-300 ${
          tier.highlighted ? 'btn-primary' : 'glass glass-hover'
        }`}
        data-testid={`pricing-cta-${tier.name.toLowerCase()}`}
      >
        {tier.cta}
      </a>
    </motion.div>
  );
};

export default LandingPage;
