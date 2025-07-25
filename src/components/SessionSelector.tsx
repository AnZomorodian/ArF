import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Clock } from 'lucide-react';
import { SessionInfo } from '../types';

interface SessionSelectorProps {
  selectedSession: SessionInfo | null;
  onSessionChange: (session: SessionInfo) => void;
}

const SessionSelector: React.FC<SessionSelectorProps> = ({ selectedSession, onSessionChange }) => {
  const years = [2024, 2023, 2022, 2021, 2020];
  const grandsPrix = [
    'Bahrain Grand Prix',
    'Saudi Arabian Grand Prix', 
    'Australian Grand Prix',
    'Japanese Grand Prix',
    'Chinese Grand Prix',
    'Miami Grand Prix',
    'Emilia Romagna Grand Prix',
    'Monaco Grand Prix',
    'Spanish Grand Prix',
    'Canadian Grand Prix',
    'Austrian Grand Prix',
    'British Grand Prix',
    'Hungarian Grand Prix',
    'Belgian Grand Prix',
    'Dutch Grand Prix',
    'Italian Grand Prix',
    'Azerbaijan Grand Prix',
    'Singapore Grand Prix',
    'United States Grand Prix',
    'Mexico City Grand Prix',
    'São Paulo Grand Prix',
    'Las Vegas Grand Prix',
    'Qatar Grand Prix',
    'Abu Dhabi Grand Prix'
  ];
  const sessions = ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Sprint', 'Race'];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="glass-card p-6 space-y-4"
    >
      <div className="flex items-center space-x-2 mb-4">
        <Calendar className="w-5 h-5" style={{ color: '#DC0000' }} />
        <h2 className="text-lg font-semibold">Session Selection</h2>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Year</label>
          <select className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none transition-colors">
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Grand Prix</label>
          <select className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none transition-colors">
            {grandsPrix.map(gp => (
              <option key={gp} value={gp}>{gp}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Session Type</label>
          <select className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none transition-colors">
            {sessions.map(session => (
              <option key={session} value={session}>{session}</option>
            ))}
          </select>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full text-white py-2 px-4 rounded-lg font-medium hover:shadow-lg transition-all duration-200"
          style={{ background: 'linear-gradient(to right, #DC0000, #B91C1C)' }}
        >
          Load Session Data
        </motion.button>
      </div>
      
      {selectedSession && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-4 p-3 bg-gray-800/50 rounded-lg border border-gray-600"
        >
          <div className="flex items-center space-x-2 text-sm text-gray-300">
            <MapPin className="w-4 h-4" />
            <span>{selectedSession.grandPrix}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-300 mt-1">
            <Clock className="w-4 h-4" />
            <span>{selectedSession.sessionType}</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default SessionSelector;