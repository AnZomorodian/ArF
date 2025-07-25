import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, X } from 'lucide-react';
import { Driver } from '../types';

interface DriverSelectorProps {
  selectedDrivers: Driver[];
  onDriversChange: (drivers: Driver[]) => void;
}

const DriverSelector: React.FC<DriverSelectorProps> = ({ selectedDrivers, onDriversChange }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Mock drivers data - in real implementation, this would come from FastF1 API
  const availableDrivers: Driver[] = [
    { id: 'VER', name: 'Max Verstappen', team: 'Red Bull Racing', color: '#1E41FF', number: 1 },
    { id: 'PER', name: 'Sergio Pérez', team: 'Red Bull Racing', color: '#1E41FF', number: 11 },
    { id: 'HAM', name: 'Lewis Hamilton', team: 'Mercedes', color: '#00D2BE', number: 44 },
    { id: 'RUS', name: 'George Russell', team: 'Mercedes', color: '#00D2BE', number: 63 },
    { id: 'LEC', name: 'Charles Leclerc', team: 'Ferrari', color: '#DC0000', number: 16 },
    { id: 'SAI', name: 'Carlos Sainz', team: 'Ferrari', color: '#DC0000', number: 55 },
    { id: 'NOR', name: 'Lando Norris', team: 'McLaren', color: '#FF8700', number: 4 },
    { id: 'PIA', name: 'Oscar Piastri', team: 'McLaren', color: '#FF8700', number: 81 },
  ];

  const toggleDriver = (driver: Driver) => {
    const isSelected = selectedDrivers.some(d => d.id === driver.id);
    if (isSelected) {
      onDriversChange(selectedDrivers.filter(d => d.id !== driver.id));
    } else {
      onDriversChange([...selectedDrivers, driver]);
    }
  };

  const removeDriver = (driverId: string) => {
    onDriversChange(selectedDrivers.filter(d => d.id !== driverId));
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className="glass-card p-6 space-y-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-f1-red" />
          <h2 className="text-lg font-semibold">Driver Selection</h2>
        </div>
        <span className="text-sm text-gray-400">
          {selectedDrivers.length}/8 selected
        </span>
      </div>

      {/* Selected Drivers */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-300">Selected Drivers</h3>
        <div className="min-h-[80px] space-y-2">
          <AnimatePresence>
            {selectedDrivers.map((driver) => (
              <motion.div
                key={driver.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center justify-between p-3 rounded-lg border-l-4 bg-gray-800/50"
                style={{ borderLeftColor: driver.color }}
              >
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
                    style={{ backgroundColor: driver.color }}
                  >
                    {driver.number}
                  </div>
                  <div>
                    <p className="text-white font-medium">{driver.name}</p>
                    <p className="text-xs text-gray-400">{driver.team}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeDriver(driver.id)}
                  className="p-1 hover:bg-red-500/20 rounded-full transition-colors"
                >
                  <X className="w-4 h-4 text-red-400" />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
          {selectedDrivers.length === 0 && (
            <div className="flex items-center justify-center h-20 text-gray-500 text-sm">
              No drivers selected
            </div>
          )}
        </div>
      </div>

      {/* Driver Grid */}
      <div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full text-left text-sm font-medium text-gray-300 mb-2 hover:text-white transition-colors"
        >
          Available Drivers {isExpanded ? '▼' : '▶'}
        </button>
        
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="grid grid-cols-2 gap-2"
            >
              {availableDrivers.map((driver) => {
                const isSelected = selectedDrivers.some(d => d.id === driver.id);
                return (
                  <motion.button
                    key={driver.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => toggleDriver(driver)}
                    className={`p-2 rounded-lg border text-left transition-all duration-200 ${
                      isSelected
                        ? 'border-white bg-gray-700 shadow-lg'
                        : 'border-gray-600 bg-gray-800/30 hover:border-gray-500'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-6 h-6 rounded-full flex items-center justify-center text-white font-bold text-xs"
                        style={{ backgroundColor: driver.color }}
                      >
                        {driver.number}
                      </div>
                      <div>
                        <p className="text-xs font-medium text-white">{driver.id}</p>
                        <p className="text-xs text-gray-400 truncate">{driver.name}</p>
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default DriverSelector;