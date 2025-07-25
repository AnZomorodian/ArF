import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Flag, Zap, TrendingUp, MapPin, Timer, Users } from 'lucide-react';
import Header from './components/Header';
import SessionSelector from './components/SessionSelector';
import DriverSelector from './components/DriverSelector';
import TelemetryChart from './components/TelemetryChart';
import LapTimesChart from './components/LapTimesChart';
import TireStrategyChart from './components/TireStrategyChart';
import RaceProgressionChart from './components/RaceProgressionChart';
import TrackMapVisualization from './components/TrackMapVisualization';
import WeatherWidget from './components/WeatherWidget';
import StatsCard from './components/StatsCard';
import { SessionInfo, Driver } from './types';

const App: React.FC = () => {
  const [selectedSession, setSelectedSession] = useState<SessionInfo | null>(null);
  const [selectedDrivers, setSelectedDrivers] = useState<Driver[]>([]);
  const [activeTab, setActiveTab] = useState<'telemetry' | 'laptimes' | 'strategy' | 'progression' | 'track'>('telemetry');

  // Mock data - in real implementation, this would come from FastF1 API
  const mockStats = {
    fastestLap: '1:41.252',
    topSpeed: '342.7 km/h',
    totalLaps: 44,
    averageSpeed: '218.3 km/h'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="racing-stripes opacity-5 absolute inset-0" />
      
      <div className="relative z-10">
        <Header />
        
        {/* Main Content */}
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            
            {/* Left Sidebar - Controls */}
            <div className="lg:col-span-1 space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <SessionSelector 
                  selectedSession={selectedSession}
                  onSessionChange={setSelectedSession}
                />
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <DriverSelector
                  selectedDrivers={selectedDrivers}
                  onDriversChange={setSelectedDrivers}
                />
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <WeatherWidget />
              </motion.div>
            </div>
            
            {/* Main Content Area */}
            <div className="lg:col-span-3 space-y-6">
              
              {/* Stats Cards */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="grid grid-cols-2 md:grid-cols-4 gap-4"
              >
                <StatsCard
                  icon={<Timer className="w-5 h-5" />}
                  title="Fastest Lap"
                  value={mockStats.fastestLap}
                  color="text-yellow-400"
                />
                <StatsCard
                  icon={<Zap className="w-5 h-5" />}
                  title="Top Speed"
                  value={mockStats.topSpeed}
                  color="text-red-400"
                />
                <StatsCard
                  icon={<Flag className="w-5 h-5" />}
                  title="Total Laps"
                  value={mockStats.totalLaps.toString()}
                  color="text-blue-400"
                />
                <StatsCard
                  icon={<TrendingUp className="w-5 h-5" />}
                  title="Avg Speed"
                  value={mockStats.averageSpeed}
                  color="text-green-400"
                />
              </motion.div>
              
              {/* Tab Navigation */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="glass-card p-1"
              >
                <div className="flex space-x-1">
                  {[
                    { id: 'telemetry', label: 'Telemetry', icon: <TrendingUp className="w-4 h-4" /> },
                    { id: 'laptimes', label: 'Lap Times', icon: <Timer className="w-4 h-4" /> },
                    { id: 'strategy', label: 'Tire Strategy', icon: <Users className="w-4 h-4" /> },
                    { id: 'progression', label: 'Race Progress', icon: <Flag className="w-4 h-4" /> },
                    { id: 'track', label: 'Track Map', icon: <MapPin className="w-4 h-4" /> }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                        activeTab === tab.id
                          ? 'bg-f1-red text-white shadow-lg'
                          : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                      }`}
                    >
                      {tab.icon}
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
              
              {/* Chart Area */}
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="glass-card p-6"
              >
                {activeTab === 'telemetry' && <TelemetryChart drivers={selectedDrivers} />}
                {activeTab === 'laptimes' && <LapTimesChart drivers={selectedDrivers} />}
                {activeTab === 'strategy' && <TireStrategyChart drivers={selectedDrivers} />}
                {activeTab === 'progression' && <RaceProgressionChart drivers={selectedDrivers} />}
                {activeTab === 'track' && <TrackMapVisualization drivers={selectedDrivers} />}
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;