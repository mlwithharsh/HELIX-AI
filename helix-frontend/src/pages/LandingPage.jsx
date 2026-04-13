import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { MessageSquare, Shield, Sparkles, ArrowRight, Heart, Brain, Zap, Bot, CalendarClock, LineChart, RadioTower, Trees, Waves } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="pt-20">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-solace-purple/20 rounded-full blur-[120px] animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-solace-blue/20 rounded-full blur-[120px] animate-float" style={{ animationDelay: '-5s' }} />
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10 space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-white/60 border border-black/5 text-solace-purple text-xs font-bold uppercase tracking-widest"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Conversation + Autonomous Agent</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-5xl md:text-7xl font-bold tracking-tight leading-tight"
          >
            Helix now runs as <br />
            <span className="text-gradient">an active AI operator.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed"
          >
            Keep the adaptive chat system, then step into the Agent workspace to build local-first campaigns, approve variants, schedule execution, and learn from results without fragile browser automation.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
          >
            <Link to="/agent" className="btn-solace-primary flex items-center space-x-2 group">
              <span>Open Agent Workspace</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/chat" className="btn-solace-primary flex items-center space-x-2 group">
              <span>Start Your Conversation</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/smart-parks" className="btn-solace-outline flex items-center space-x-2 group">
              <span>Explore Smart Parks</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/about" className="btn-solace-outline">
              Learn More
            </Link>
          </motion.div>
        </div>
      </section>

      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">Agent Layer</h2>
            <p className="text-text-secondary max-w-2xl mx-auto">
              Helix can now work as a local marketing engine with strategy, approval, scheduling, and learning in one surface.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <StepCard
              number="A1"
              icon={Bot}
              title="Generate platform variants"
              desc="Turn one campaign goal into channel-specific copy for LinkedIn, X, Telegram, email, and more."
            />
            <StepCard
              number="A2"
              icon={CalendarClock}
              title="Schedule and dispatch"
              desc="Approve variants, convert them into jobs, and run dry-runs or live delivery through API-native adapters."
            />
            <StepCard
              number="A3"
              icon={LineChart}
              title="Optimize from feedback"
              desc="Store performance signals locally and let Helix bias future prompts toward what actually works."
            />
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-[linear-gradient(180deg,rgba(239,245,239,0.9),rgba(247,249,246,0.86))]">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-16">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full border border-[#325742]/10 bg-white/70 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.22em] text-[#35553f]">
                <Trees className="w-3.5 h-3.5" />
                <span>New Helix Segment</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-bold">Smart Parks</h2>
              <p className="text-text-secondary max-w-2xl">
                Helix now includes a dedicated urban monitoring segment for the DDA Smart Parks concept: telemetry, pilot readiness, and scale planning in one place.
              </p>
            </div>
            <Link to="/smart-parks" className="btn-solace-primary flex items-center space-x-2 group">
              <span>Open Smart Parks</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <StepCard
              number="S1"
              icon={RadioTower}
              title="Map live sensor layers"
              desc="Frame tree health, soil quality, and water quality as one integrated sensing network."
            />
            <StepCard
              number="S2"
              icon={Waves}
              title="Track pilot signal health"
              desc="Review park-level risk bands and convert pitch assumptions into an operator dashboard."
            />
            <StepCard
              number="S3"
              icon={Trees}
              title="Plan city-scale rollout"
              desc="Move from a 3-park pilot to a repeatable expansion model with local data ownership."
            />
          </div>
        </div>
      </section>

      {/* Why Wellness Matters Section */}
      <section className="py-24 px-6 bg-[rgba(235,227,214,0.38)]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <h2 className="text-3xl md:text-4xl font-bold leading-tight">
              Why Emotional <br />
              <span className="text-solace-purple">Wellness Matters</span>
            </h2>
            <p className="text-text-secondary leading-relaxed">
              Thoughtful assistance works better when it adapts to the person, not just the prompt. HELIX uses memory, retrieval, and feedback loops to stay useful without becoming erratic.
            </p>
            <div className="space-y-6">
              <FeatureItem 
                icon={Shield} 
                title="Judgment-Free Space" 
                desc="Express yourself freely without fear of being misunderstood or labeled." 
              />
              <FeatureItem 
                icon={Heart} 
                title="Emotional Resonance" 
                desc="Our AI is designed to detect and respond to the nuance of your feelings." 
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-4">
              <StatCard label="Burnout Rate" value="62%" />
              <StatCard label="Silent Struggles" value="1 in 4" />
            </div>
            <div className="pt-12 space-y-4">
              <StatCard label="Confidentiality" value="100%" />
              <StatCard label="AI Empathy" value="Active" />
            </div>
          </div>
        </div>
      </section>

      {/* Brand Line Section */}
      <section className="py-32 px-6 text-center border-y border-white/5 bg-gradient-to-b from-transparent via-solace-purple/5 to-transparent">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto space-y-6"
        >
          <blockquote className="text-3xl md:text-5xl font-bold italic text-text-primary">
            "HELIX — Where your emotions find understanding."
          </blockquote>
          <p className="text-solace-purple font-medium uppercase tracking-[0.3em] text-sm">
            Not just AI. A space that listens.
          </p>
        </motion.div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-6 max-w-7xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">Simple Path to Peace</h2>
          <p className="text-text-secondary">Three steps to a clearer mind.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <StepCard 
            number="01" 
            icon={MessageSquare} 
            title="Share your thoughts" 
            desc="Type freely about whatever is on your mind, no matter how small or large." 
          />
          <StepCard 
            number="02" 
            icon={Brain} 
            title="AI understands emotionally" 
            desc="Our neural links analyze the sentiment and core intent of your message." 
          />
          <StepCard 
            number="03" 
            icon={Zap} 
            title="Receive empathetic guidance" 
            desc="Get immediate, supportive feedback designed to validate and comfort." 
          />
        </div>
      </section>
    </div>
  );
};

const FeatureItem = ({ icon: Icon, title, desc }) => (
  <div className="flex items-start space-x-4">
    <div className="w-12 h-12 rounded-xl bg-white/60 border border-black/5 flex items-center justify-center shrink-0">
      <Icon className="w-6 h-6 text-solace-purple" />
    </div>
    <div>
      <h4 className="font-bold text-text-primary mb-1">{title}</h4>
      <p className="text-sm text-text-secondary leading-relaxed">{desc}</p>
    </div>
  </div>
);

const StatCard = ({ label, value }) => (
  <div className="glass-card p-6 text-center space-y-2">
    <div className="text-3xl font-bold text-text-primary">{value}</div>
    <div className="text-[10px] font-bold text-text-muted uppercase tracking-widest">{label}</div>
  </div>
);

const StepCard = ({ number, icon: Icon, title, desc }) => (
  <div className="glass-card p-8 space-y-6 group hover:border-solace-purple/20 transition-colors duration-500">
    <div className="flex justify-between items-center">
      <div className="w-14 h-14 rounded-2xl bg-white/60 border border-black/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
        <Icon className="w-7 h-7 text-solace-blue" />
      </div>
      <span className="text-4xl font-black text-black/5">{number}</span>
    </div>
    <div className="space-y-3">
      <h3 className="text-xl font-bold text-text-primary">{title}</h3>
      <p className="text-text-secondary leading-relaxed">{desc}</p>
    </div>
  </div>
);

export default LandingPage;
