import React from 'react';
import { motion } from 'framer-motion';
import { XCircle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const PaymentCancel = () => {
  return (
    <div className="min-h-screen bg-[#0B0B10] flex items-center justify-center px-6">
      {/* Background glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full animate-breathe"
          style={{ 
            background: 'radial-gradient(circle, rgba(127,29,29,0.1) 0%, transparent 70%)',
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
        <motion.div 
          className="w-20 h-20 rounded-full bg-zinc-800 flex items-center justify-center mx-auto mb-8"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", duration: 0.6, delay: 0.2 }}
        >
          <XCircle className="w-10 h-10 text-zinc-500" />
        </motion.div>
        
        <h1 className="text-3xl font-bold mb-4" data-testid="payment-cancelled-title">Payment Cancelled</h1>
        <p className="text-zinc-400 mb-8">
          No worries! Your payment was cancelled and you haven't been charged. 
          You can always upgrade later when you're ready.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full glass glass-hover font-medium"
            data-testid="return-home-btn"
          >
            <ArrowLeft className="w-4 h-4" />
            Return Home
          </Link>
          <Link
            to="/#pricing"
            className="btn-wine inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full font-medium"
            data-testid="view-plans-btn"
          >
            View Plans
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default PaymentCancel;
