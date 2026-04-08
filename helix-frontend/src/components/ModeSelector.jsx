import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAI } from '../context/AIContext';
import { Cpu, Cloud, Zap, ChevronDown } from 'lucide-react';

const modes = [
  { 
    id: 'auto', 
    name: 'Auto', 
    desc: 'Hybrid Intelligence', 
    icon: Zap,
    color: '#7f9476'
  },
  { 
    id: 'edge', 
    name: 'Edge', 
    desc: 'Local & Private', 
    icon: Cpu,
    color: '#bda98a'
  },
  { 
    id: 'cloud', 
    name: 'Cloud', 
    desc: 'High Performance', 
    icon: Cloud,
    color: '#6d7b68'
  }
];

const ModeSelector = () => {
  const { mode, setMode } = useAI();
  const [isOpen, setIsOpen] = React.useState(false);
  
  const activeMode = modes.find(m => m.id === mode) || modes[0];

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 px-4 py-2 rounded-2xl bg-white/70 border border-black/5 hover:bg-white transition-all duration-300 shadow-sm"
      >
        <div 
          className="w-6 h-6 rounded-lg flex items-center justify-center shadow-sm"
          style={{ backgroundColor: `${activeMode.color}20` }}
        >
          <activeMode.icon className="w-3.5 h-3.5" style={{ color: activeMode.color }} />
        </div>
        <div className="text-left hidden xs:block">
          <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest leading-none mb-1">Model Route</p>
          <p className="text-xs font-black text-text-primary uppercase tracking-tighter">{activeMode.name}</p>
        </div>
        <ChevronDown className={`w-4 h-4 text-text-muted transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              className="absolute right-0 mt-3 w-64 z-50 bg-white/95 backdrop-blur-md rounded-2xl p-2 border border-black/5 shadow-2xl"
            >
              <div className="px-3 py-2 mb-2">
                <p className="text-[10px] font-black text-text-muted uppercase tracking-[0.2em]">Routing Strategy</p>
              </div>
              
              <div className="space-y-1">
                {modes.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => {
                      setMode(m.id);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center space-x-4 p-3 rounded-xl transition-all duration-300 group ${
                      mode === m.id 
                        ? 'bg-[#f6f1e8] border-black/5 shadow-sm' 
                        : 'hover:bg-[#faf6ef] border-transparent'
                    } border`}
                  >
                    <div 
                      className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform duration-300"
                      style={{ backgroundColor: `${m.color}20` }}
                    >
                      <m.icon className="w-5 h-5" style={{ color: m.color }} />
                    </div>
                    <div className="text-left">
                      <p className="text-sm font-bold text-text-primary leading-none mb-1">{m.name}</p>
                      <p className="text-[10px] text-text-muted font-medium">{m.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ModeSelector;
