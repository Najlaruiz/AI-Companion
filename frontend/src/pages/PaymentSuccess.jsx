import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Send, Loader2 } from 'lucide-react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('loading');
  const [paymentInfo, setPaymentInfo] = useState(null);
  
  const sessionId = searchParams.get('session_id');
  const telegramId = searchParams.get('telegram_id');

  useEffect(() => {
    if (!sessionId) {
      setStatus('error');
      return;
    }

    const pollPaymentStatus = async (attempts = 0) => {
      const maxAttempts = 5;
      const pollInterval = 2000;

      if (attempts >= maxAttempts) {
        setStatus('timeout');
        return;
      }

      try {
        const response = await axios.get(`${BACKEND_URL}/api/checkout/status/${sessionId}`);
        const data = response.data;

        if (data.payment_status === 'paid') {
          setPaymentInfo(data);
          setStatus('success');
          return;
        } else if (data.status === 'expired') {
          setStatus('expired');
          return;
        }

        // Continue polling
        setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
      } catch (error) {
        console.error('Error checking payment status:', error);
        if (attempts >= maxAttempts - 1) {
          setStatus('error');
        } else {
          setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
        }
      }
    };

    pollPaymentStatus();
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-[#0F0F14] flex items-center justify-center px-6">
      {/* Background glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full animate-breathe"
          style={{ 
            background: 'radial-gradient(circle, rgba(34,197,94,0.2) 0%, transparent 70%)',
            filter: 'blur(80px)'
          }}
        />
      </div>

      <motion.div 
        className="relative z-10 text-center max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {status === 'loading' && (
          <>
            <div className="w-20 h-20 rounded-full glass flex items-center justify-center mx-auto mb-8">
              <Loader2 className="w-10 h-10 text-pink-500 animate-spin" />
            </div>
            <h1 className="text-3xl font-bold mb-4" data-testid="payment-loading">Processing Payment...</h1>
            <p className="text-zinc-400">Please wait while we confirm your payment.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <motion.div 
              className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-8"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", duration: 0.6, delay: 0.2 }}
            >
              <CheckCircle className="w-10 h-10 text-green-500" />
            </motion.div>
            <h1 className="text-3xl font-bold mb-4" data-testid="payment-success">Welcome to Premium!</h1>
            <p className="text-zinc-400 mb-8">
              Your subscription is now active. Enjoy your enhanced experience with unlimited messages and exclusive features.
            </p>
            <a
              href="https://t.me"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white px-8 py-4 rounded-full font-bold hover:shadow-[0_0_30px_rgba(233,30,140,0.4)] transition-all duration-300"
              data-testid="return-telegram-btn"
            >
              <Send className="w-5 h-5" />
              Return to Telegram
            </a>
          </>
        )}

        {(status === 'error' || status === 'timeout' || status === 'expired') && (
          <>
            <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-8">
              <span className="text-4xl">⚠️</span>
            </div>
            <h1 className="text-3xl font-bold mb-4" data-testid="payment-error">
              {status === 'expired' ? 'Session Expired' : 'Something went wrong'}
            </h1>
            <p className="text-zinc-400 mb-8">
              {status === 'expired' 
                ? 'Your payment session has expired. Please try again.'
                : 'We couldn\'t confirm your payment. Please check your Telegram messages or try again.'}
            </p>
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full glass glass-hover font-medium"
              data-testid="return-home-btn"
            >
              Return Home
            </Link>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default PaymentSuccess;
