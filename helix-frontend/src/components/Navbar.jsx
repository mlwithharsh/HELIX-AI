import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bot, Heart, MessageSquare, Info, Menu, Trees, X } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const location = useLocation();

  const navItems = [
    { name: 'Home', path: '/', icon: Heart },
    { name: 'Agent', path: '/agent', icon: Bot },
    { name: 'Smart Parks', path: '/smart-parks', icon: Trees },
    { name: 'Chat', path: '/chat', icon: MessageSquare },
    { name: 'About', path: '/about', icon: Info },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[rgba(244,239,230,0.82)] backdrop-blur-lg border-b border-black/5">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-solace-purple to-solace-blue flex items-center justify-center shadow-glow-purple group-hover:scale-110 transition-transform duration-500">
            <Heart className="w-5 h-5 text-white fill-white/20" />
          </div>
          <span className="text-xl font-bold tracking-tight text-text-primary uppercase tracking-[0.1em]">
            H<span className="text-solace-purple">ELIX</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center space-x-8">
          <Link to="/" className={`nav-link flex items-center space-x-2 ${location.pathname === '/' ? 'text-text-primary' : ''}`}>
            <Heart className="w-4 h-4" />
            <span>Home</span>
          </Link>
          <Link to="/agent" className={`nav-link flex items-center space-x-2 ${location.pathname === '/agent' ? 'text-text-primary' : ''}`}>
            <Bot className="w-4 h-4" />
            <span>Agent</span>
          </Link>
          <Link to="/smart-parks" className={`nav-link flex items-center space-x-2 ${location.pathname === '/smart-parks' ? 'text-text-primary' : ''}`}>
            <Trees className="w-4 h-4" />
            <span>Smart Parks</span>
          </Link>
          <Link to="/chat" className={`nav-link flex items-center space-x-2 ${location.pathname === '/chat' ? 'text-text-primary' : ''}`}>
            <MessageSquare className="w-4 h-4" />
            <span>Chat</span>
          </Link>
          <Link to="/about" className={`nav-link flex items-center space-x-2 ${location.pathname === '/about' ? 'text-text-primary' : ''}`}>
            <Info className="w-4 h-4" />
            <span>About</span>
          </Link>
          
          <div className="h-4 w-px bg-black/10 mx-2" /> {/* Divider */}

          {localStorage.getItem('helix_user_id') ? (
            <button 
              onClick={() => { localStorage.removeItem('helix_user_id'); window.location.href = '/'; }}
              className="btn-solace-outline !py-2 !px-6 text-sm"
            >
              Logout
            </button>
          ) : (
            <div className="flex items-center space-x-6">
              <Link to="/login" className="text-sm font-bold text-text-secondary hover:text-solace-purple transition-colors">
                Login
              </Link>
              <Link to="/signup" className="btn-solace-primary !py-2 !px-6 text-sm">
                Sign up
              </Link>
              <Link to="/agent" className="rounded-2xl border border-black/8 bg-white/70 px-4 py-2 text-sm font-bold text-text-primary transition-all duration-300 hover:bg-white">
                Agent
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button className="md:hidden text-text-primary" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Nav */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden bg-background-soft border-b border-black/5 px-6 py-8 space-y-6"
        >
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className="flex items-center space-x-4 text-text-secondary"
            >
              <item.icon className="w-5 h-5" />
              <span className="text-lg font-medium">{item.name}</span>
            </Link>
          ))}
          {localStorage.getItem('helix_user_id') ? (
            <button
               onClick={() => { localStorage.removeItem('helix_user_id'); window.location.href = '/'; }}
              className="block w-full btn-solace-outline text-center"
            >
              Logout
            </button>
          ) : (
            <div className="space-y-4">
               <Link
                to="/login"
                onClick={() => setIsOpen(false)}
                className="block text-center text-text-secondary font-bold"
              >
                Login
              </Link>
              <Link
                to="/signup"
                onClick={() => setIsOpen(false)}
                className="block btn-solace-primary text-center"
              >
                Sign up
              </Link>
            </div>
          )}
        </motion.div>
      )}
    </nav>
  );
};

export default Navbar;
