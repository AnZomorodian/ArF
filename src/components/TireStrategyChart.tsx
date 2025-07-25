import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Driver } from '../types';

interface TireStrategyChartProps {
  drivers: Driver[];
}

const TireStrategyChart: React.FC<TireStrategyChartProps> = ({ drivers }) => {
  const tireColors = {
    'Soft': '#FF3333',
    'Medium': '#FFFF00', 
    'Hard': '#FFFFFF',
    'Intermediate': '#00FF00',
    'Wet': '#0000FF'
  };

  // Mock tire strategy data
  const mockData = drivers.map(driver => ({
    driver: driver.name,
    color: driver.color,
    stints: [
      { compound: 'Medium', startLap: 1, endLap: 15, laps: 15 },
      { compound: 'Hard', startLap: 16, endLap: 35, laps: 20 },
      { compound: 'Soft', startLap: 36, endLap: 50, laps: 15 }
    ]
  }));

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Tire Strategy Overview</h3>
        
        {/* Tire Strategy Timeline */}
        <div className="space-y-4">
          {mockData.map((driverData, index) => (
            <div key={driverData.driver} className="glass-card p-4">
              <div className="flex items-center space-x-3 mb-3">
                <div 
                  className="w-6 h-6 rounded-full"
                  style={{ backgroundColor: driverData.color }}
                />
                <span className="font-medium text-white">{driverData.driver}</span>
              </div>
              
              <div className="relative h-8 bg-gray-800 rounded-lg overflow-hidden">
                {driverData.stints.map((stint, stintIndex) => {
                  const width = (stint.laps / 50) * 100; // Assuming 50 lap race
                  const left = ((stint.startLap - 1) / 50) * 100;
                  
                  return (
                    <div
                      key={stintIndex}
                      className="absolute h-full flex items-center justify-center text-xs font-bold"
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                        backgroundColor: tireColors[stint.compound as keyof typeof tireColors],
                        color: stint.compound === 'Medium' ? '#000' : '#fff'
                      }}
                    >
                      {stint.compound[0]}
                    </div>
                  );
                })}
              </div>
              
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Lap 1</span>
                <span>Lap 25</span>
                <span>Lap 50</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tire Compound Legend */}
      <div className="glass-card p-4">
        <h4 className="text-lg font-semibold mb-3 text-white">Tire Compounds</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(tireColors).map(([compound, color]) => (
            <div key={compound} className="flex items-center space-x-2">
              <div 
                className="w-4 h-4 rounded-full border border-gray-600"
                style={{ backgroundColor: color }}
              />
              <span className="text-sm text-gray-300">{compound}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Pit Stop Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Pit Stop Times</h4>
          <div className="space-y-2">
            {drivers.slice(0, 5).map((driver, index) => {
              const pitTime = 2.3 + Math.random() * 0.8;
              return (
                <div key={driver.id} className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-6 h-6 rounded-full"
                      style={{ backgroundColor: driver.color }}
                    />
                    <span className="font-medium text-white">{driver.name}</span>
                  </div>
                  <span className="font-mono text-sm text-gray-300">{pitTime.toFixed(3)}s</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Strategy Analysis</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">One-Stop Strategy</span>
              <span className="text-white font-medium">4 drivers</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">Two-Stop Strategy</span>
              <span className="text-white font-medium">16 drivers</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">Average Pit Time</span>
              <span className="text-white font-medium">2.847s</span>
            </div>
          </div>
        </div>
      </div>

      {drivers.length === 0 && (
        <div className="flex items-center justify-center h-96 text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No drivers selected</p>
            <p className="text-sm">Select drivers from the sidebar to view tire strategy data</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TireStrategyChart;