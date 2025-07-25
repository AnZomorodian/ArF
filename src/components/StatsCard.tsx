import React from 'react';
import { motion } from 'framer-motion';

interface StatsCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  color: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ icon, title, value, color }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass-card p-4 text-center"
    >
      <div className={`flex justify-center mb-2 ${color}`}>
        {icon}
      </div>
      <h3 className="text-xs text-gray-400 uppercase tracking-wide font-medium">
        {title}
      </h3>
      <p className="text-lg font-bold text-white mt-1">
        {value}
      </p>
    </motion.div>
  );
};

export default StatsCard;