import React, { useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Crown, Moon, Heart, Sparkles, Shield, Lock, MessageCircle, Zap, Check, ChevronDown, Send } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Character data
const characters = [
  {
    id: 'valeria',
    name: 'Valeria Voss',
    emoji: '👑',
    icon: Crown,
    tagline: 'Classy. Intense. Controlled power.',
    description: "She doesn't chase.\nShe chooses.",
    image: 'https://images.unsplash.com/photo-1756441082607-ea083d06e6ed?q=80&w=1974&auto=format&fit=crop',
    gradient: 'from-pink-600 to-rose-500',
    glowColor: 'rgba(233, 30, 140, 0.4)'
  },
  {
    id: 'luna',
    name: 'Luna Mirelle',
    emoji: '🌙',
    icon: Moon,
    tagline: 'Soft. Romantic. Emotionally addictive.',
    description: "She remembers how you speak.\nAnd how you feel.",
    image: 'https://images.unsplash.com/photo-1565014208903-fdfd6c464221?q=80&w=1974&auto=format&fit=crop',
    gradient: 'from-purple-600 to-violet-500',
    glowColor: 'rgba(124, 58, 237, 0.4)'
  },
  {
    id: 'nyx',
    name: 'Nyx',
    emoji: '🖤',
    icon: Heart,
    tagline: 'Mysterious. Dark. Unpredictable.',
    description: "She reveals slowly.\nIf you can handle it.",
    image: 'https://images.unsplash.com/photo-1642290460481-76a5f2e18c3e?q=80&w=1974&auto=format&fit=crop',
    gradient: 'from-violet-600 to-purple-800',
    glowColor: 'rgba(139, 92, 246, 0.4)'
  }
];

// Pricing tiers
const pricingTiers = [
  {
    name: 'Free',
    price: '0',
    period: '',
    features: [
      '15 messages per day',
      'Text conversations',
      'Basic interaction',
      'Character selection'
    ],
    cta: 'Start Free',
    highlighted: false
  },
  {
    name: 'Premium',
    price: '19',
    period: '/month',
    features: [
      'Unlimited messages',
      'Emotional memory',
      'Faster responses',
      'Priority access'
    ],
    cta: 'Upgrade Premium',
    highlighted: true,
    tier: 'premium'
  },
  {
    name: 'VIP',
    price: '39',
    period: '/month',
    features: [
      'Everything in Premium',
      'Explicit mode toggle',
      'Voice messages',
      'Custom fantasy flow',
      'Memory persistence'
    ],
    cta: 'Go VIP',
    highlighted: false,
    tier: 'vip'
  }
];

// How it works steps
const steps = [
  {
    number: '01',
    title: 'Choose your companion',
    description: 'Three distinct personalities, each with their own allure.',
    icon: Sparkles
  },
  {
    number: '02',
    title: 'Start chatting instantly',
    description: 'No downloads. Just open Telegram and say hello.',
    icon: MessageCircle
  },
  {
    number: '03',
    title: 'Unlock deeper access',
    description: 'Premium tiers reveal new depths of connection.',
    icon: Lock
  }
];

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.2 }
  }
};

const LandingPage = () => {
  const [botLink, setBotLink] = useState('https://t.me/your_bot');
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  
  useEffect(() => {
    // Fetch bot info
    const fetchBotInfo = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/telegram/info`);
        if (response.data.configured && response.data.link) {
          setBotLink(response.data.link);
        }
      } catch (error) {
        console.log('Bot info not available yet');
      }
    };
    fetchBotInfo();
  }, []);

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#0F0F14] text-white overflow-hidden">
      {/* Noise overlay */}
      <div className="noise-overlay" />
      
      {/* Hero Section */}
      <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Animated background orbs */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full hero-gradient-orb"
            style={{ background: 'radial-gradient(circle, rgba(233,30,140,0.3) 0%, transparent 70%)' }}
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full hero-gradient-orb"
            style={{ background: 'radial-gradient(circle, rgba(124,58,237,0.3) 0%, transparent 70%)' }}
            animate={{ scale: [1.2, 1, 1.2], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          />
        </div>
        
        <motion.div 
          className="relative z-10 text-center px-6 max-w-5xl mx-auto"
          style={{ opacity: heroOpacity }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <span className="inline-block px-4 py-2 rounded-full glass text-sm text-zinc-400 mb-8">
              Private AI Companion Service
            </span>
          </motion.div>
          
          <motion.h1 
            className="text-5xl sm:text-6xl lg:text-8xl font-bold tracking-tight mb-6 leading-none"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            data-testid="hero-headline"
          >
            Three fantasies.
            <br />
            <span className="gradient-text">One private line.</span>
          </motion.h1>
          
          <motion.p 
            className="text-lg sm:text-xl text-zinc-400 mb-12 max-w-2xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            Choose your companion. Step into a private conversation.
            <br className="hidden sm:block" />
            Unlock deeper modes when you're ready.
          </motion.p>
          
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <a
              href={botLink}
              target="_blank"
              rel="noopener noreferrer"
              className="cta-button inline-flex items-center gap-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:shadow-[0_0_40px_rgba(233,30,140,0.5)] transition-all duration-300 transform hover:-translate-y-1"
              data-testid="start-telegram-btn"
            >
              <Send className="w-5 h-5" />
              Start on Telegram
            </a>
            <button
              onClick={() => scrollToSection('characters')}
              className="inline-flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
              data-testid="meet-companions-btn"
            >
              Meet the companions
              <ChevronDown className="w-4 h-4" />
            </button>
          </motion.div>
          
          <motion.p
            className="mt-8 text-sm text-zinc-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
          >
            18+ Only — Private & Secure
          </motion.p>
        </motion.div>
        
        {/* Scroll indicator */}
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
          <motion.div
            className="text-center mb-16"
            variants={fadeInUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="characters-title">
              Choose Your Companion
            </h2>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
              Three distinct personalities. Each with their own allure.
            </p>
          </motion.div>
          
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {characters.map((character) => (
              <CharacterCard key={character.id} character={character} botLink={botLink} />
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 md:py-32 px-6 bg-zinc-900/30">
        <div className="max-w-5xl mx-auto">
          <motion.div
            className="text-center mb-16"
            variants={fadeInUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="how-it-works-title">
              How It Works
            </h2>
            <p className="text-zinc-400 text-lg">
              No apps. No downloads. Just you — and who you choose.
            </p>
          </motion.div>
          
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                className="text-center"
                variants={fadeInUp}
              >
                <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl glass mb-6">
                  <step.icon className="w-7 h-7 text-pink-500" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-gradient-to-r from-pink-600 to-purple-600 flex items-center justify-center text-xs font-bold">
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

      {/* Pricing Section */}
      <section id="pricing" className="py-24 md:py-32 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-16"
            variants={fadeInUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4" data-testid="pricing-title">
              Unlock Deeper Access
            </h2>
            <p className="text-zinc-400 text-lg">
              Choose the level of connection that suits you.
            </p>
          </motion.div>
          
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {pricingTiers.map((tier) => (
              <PricingCard key={tier.name} tier={tier} botLink={botLink} />
            ))}
          </motion.div>
        </div>
      </section>

      {/* Safety Section */}
      <section id="safety" className="py-24 md:py-32 px-6 bg-zinc-900/30">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            variants={fadeInUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl glass mb-8">
              <Shield className="w-8 h-8 text-pink-500" />
            </div>
            
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-8" data-testid="safety-title">
              Your Privacy Matters
            </h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
              {[
                { icon: Lock, text: '18+ Only' },
                { icon: Heart, text: 'Consent-First' },
                { icon: Shield, text: 'Private & Encrypted' },
                { icon: Zap, text: 'No Public Profiles' }
              ].map((item, index) => (
                <motion.div
                  key={item.text}
                  className="glass rounded-2xl p-6"
                  variants={fadeInUp}
                  custom={index}
                >
                  <item.icon className="w-6 h-6 text-pink-500 mx-auto mb-3" />
                  <p className="text-sm text-zinc-300">{item.text}</p>
                </motion.div>
              ))}
            </div>
            
            <p className="text-zinc-500 text-sm max-w-2xl mx-auto">
              Private After Dark is an AI fantasy companion service designed for adults 18+. 
              All interactions are private, consensual, and never shared publicly.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-zinc-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-pink-600 to-purple-600 flex items-center justify-center">
                <Moon className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg">Private After Dark</span>
            </div>
            
            <div className="flex items-center gap-8 text-sm text-zinc-500">
              <span>18+ Only</span>
              <span>•</span>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <span>•</span>
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            </div>
            
            <a
              href={botLink}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full glass glass-hover text-sm font-medium"
              data-testid="footer-telegram-btn"
            >
              <Send className="w-4 h-4" />
              Open in Telegram
            </a>
          </div>
          
          <div className="mt-8 pt-8 border-t border-zinc-800/50 text-center">
            <p className="text-xs text-zinc-600">
              © 2026 Private After Dark. An AI fantasy companion service for adults 18+.
              <br />
              All characters are AI-generated personas. No real individuals are represented.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Character Card Component
const CharacterCard = ({ character, botLink }) => {
  const Icon = character.icon;
  
  return (
    <motion.div
      className="character-card relative aspect-[3/4] rounded-2xl overflow-hidden group cursor-pointer"
      variants={fadeInUp}
      data-testid={`character-card-${character.id}`}
    >
      {/* Glow effect */}
      <div 
        className="character-glow absolute inset-0 opacity-0 transition-opacity duration-500 z-10"
        style={{ boxShadow: `0 0 80px 20px ${character.glowColor}` }}
      />
      
      {/* Image */}
      <div className="absolute inset-0 overflow-hidden">
        <img
          src={character.image}
          alt={character.name}
          className="character-image w-full h-full object-cover transition-transform duration-700"
        />
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0F0F14] via-[#0F0F14]/50 to-transparent" />
      </div>
      
      {/* Content */}
      <div className="absolute inset-0 flex flex-col justify-end p-6 z-20">
        <div className="mb-4">
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r ${character.gradient} text-sm font-medium mb-3`}>
            <Icon className="w-4 h-4" />
            {character.emoji} {character.name}
          </div>
          <h3 className="text-xl font-semibold mb-2">{character.tagline}</h3>
          <p className="text-zinc-400 text-sm whitespace-pre-line">{character.description}</p>
        </div>
        
        <a
          href={botLink}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 w-full py-3 rounded-xl glass glass-hover font-medium text-sm transition-all duration-300 group-hover:bg-white/10"
          data-testid={`chat-with-${character.id}-btn`}
        >
          <MessageCircle className="w-4 h-4" />
          Chat with {character.name.split(' ')[0]}
        </a>
      </div>
    </motion.div>
  );
};

// Pricing Card Component
const PricingCard = ({ tier, botLink }) => {
  return (
    <motion.div
      className={`relative rounded-3xl p-8 ${
        tier.highlighted 
          ? 'pricing-highlight bg-zinc-900' 
          : 'glass'
      }`}
      variants={fadeInUp}
      data-testid={`pricing-card-${tier.name.toLowerCase()}`}
    >
      {tier.highlighted && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-pink-600 to-purple-600 text-xs font-bold">
          Most Popular
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
            <Check className="w-5 h-5 text-pink-500 flex-shrink-0 mt-0.5" />
            <span className="text-zinc-300 text-sm">{feature}</span>
          </li>
        ))}
      </ul>
      
      <a
        href={botLink}
        target="_blank"
        rel="noopener noreferrer"
        className={`block w-full py-3 rounded-xl font-medium text-center transition-all duration-300 ${
          tier.highlighted
            ? 'bg-gradient-to-r from-pink-600 to-purple-600 hover:shadow-[0_0_30px_rgba(233,30,140,0.4)] hover:-translate-y-0.5'
            : 'glass glass-hover'
        }`}
        data-testid={`pricing-cta-${tier.name.toLowerCase()}`}
      >
        {tier.cta}
      </a>
    </motion.div>
  );
};

export default LandingPage;
