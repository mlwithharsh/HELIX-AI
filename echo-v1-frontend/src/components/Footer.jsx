import React from 'react';
import { Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-[rgba(235,227,214,0.7)] border-t border-black/5 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between space-y-6 md:space-y-0">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-white/60 flex items-center justify-center">
            <Heart className="w-4 h-4 text-solace-purple" />
          </div>
          <span className="font-bold text-text-primary tracking-widest text-sm uppercase">ECHO</span>
        </div>
        
        <div className="flex space-x-8 text-xs font-medium text-text-muted uppercase tracking-widest">
          <a href="#" className="hover:text-text-primary transition-colors">Privacy</a>
          <a href="#" className="hover:text-text-primary transition-colors">Terms</a>
          <a href="#" className="hover:text-text-primary transition-colors">Contact</a>
        </div>

        <p className="text-[10px] text-text-muted uppercase tracking-[0.2em]">
          ECHO — Built with purpose for your emotional wellness.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
