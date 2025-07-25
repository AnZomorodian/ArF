import React from 'react';
import { motion } from 'framer-motion';
import { Flag, Activity } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-card mx-4 mt-4 p-6 border-2 border-gray-700/30"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Flag className="w-8 h-8 text-f1-red" />
            <h1 className="text-3xl font-bold f1-gradient">
              F1 Analysis Platform
            </h1>
          </div>
          <div className="hidden md:flex items-center space-x-2 text-gray-400">
            <Activity className="w-4 h-4" />
            <span className="text-sm">Real-time Data Analysis</span>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right text-sm text-gray-400">
            <p>2024 Season</p>
            <p className="text-xs">Version 2.0</p>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;