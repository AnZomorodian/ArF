import React from 'react';
import { motion } from 'framer-motion';
import { Cloud, Thermometer, Wind, Droplets } from 'lucide-react';

const WeatherWidget: React.FC = () => {
  // Mock weather data - in real implementation, this would come from FastF1 API
  const weatherData = {
    temperature: 28,
    humidity: 65,
    windSpeed: 12,
    trackTemp: 42,
    condition: 'Partly Cloudy'
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      className="glass-card p-6 space-y-4"
    >
      <div className="flex items-center space-x-2 mb-4">
        <Cloud className="w-5 h-5 text-blue-400" />
        <h2 className="text-lg font-semibold">Weather Conditions</h2>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Thermometer className="w-4 h-4 text-orange-400" />
            <span className="text-sm text-gray-300">Air Temp</span>
          </div>
          <span className="text-white font-medium">{weatherData.temperature}°C</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Thermometer className="w-4 h-4 text-red-400" />
            <span className="text-sm text-gray-300">Track Temp</span>
          </div>
          <span className="text-white font-medium">{weatherData.trackTemp}°C</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Droplets className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-gray-300">Humidity</span>
          </div>
          <span className="text-white font-medium">{weatherData.humidity}%</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Wind className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300">Wind Speed</span>
          </div>
          <span className="text-white font-medium">{weatherData.windSpeed} km/h</span>
        </div>
      </div>
      
      <div className="mt-4 p-3 bg-gray-800/50 rounded-lg">
        <p className="text-center text-sm text-gray-300">{weatherData.condition}</p>
      </div>
    </motion.div>
  );
};

export default WeatherWidget;