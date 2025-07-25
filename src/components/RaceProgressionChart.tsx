import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Driver } from '../types';

interface RaceProgressionChartProps {
  drivers: Driver[];
}

const RaceProgressionChart: React.FC<RaceProgressionChartProps> = ({ drivers }) => {
  // Mock race progression data
  const mockData = Array.from({ length: 50 }, (_, i) => {
    const lap = i + 1;
    const data: any = { lap };
    
    drivers.forEach(driver => {
      // Simulate realistic position changes
      let basePosition = drivers.indexOf(driver) + 1;
      let variation = Math.sin(lap * 0.1) * 2 + Math.random() * 1.5 - 0.75;
      
      // Add pit stop effects
      if (lap === 15 || lap === 35) {
        variation += Math.random() * 8; // Pit stop position loss
      }
      
      data[driver.id] = Math.max(1, Math.min(20, basePosition + variation));
    });
    
    return data;
  });

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Race Position Progression</h3>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="lap" 
                stroke="#9CA3AF"
                label={{ value: 'Lap Number', position: 'insideBottom', offset: -10, style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <YAxis 
                stroke="#9CA3AF"
                reversed={true}
                domain={[1, 20]}
                label={{ value: 'Position', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
                formatter={(value: number) => [Math.round(value), 'Position']}
              />
              <Legend />
              {drivers.map((driver) => (
                <Line
                  key={driver.id}
                  type="monotone"
                  dataKey={driver.id}
                  stroke={driver.color}
                  strokeWidth={3}
                  dot={{ fill: driver.color, strokeWidth: 2, r: 3 }}
                  name={driver.name}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Position Changes Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Biggest Gainers</h4>
          <div className="space-y-2">
            {drivers.slice(0, 5).map((driver, index) => {
              const positionGain = Math.floor(Math.random() * 8) + 1;
              return (
                <div key={driver.id} className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-6 h-6 rounded-full"
                      style={{ backgroundColor: driver.color }}
                    />
                    <span className="font-medium text-white">{driver.name}</span>
                  </div>
                  <span className="text-green-400 font-medium">+{positionGain}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Race Statistics</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">Lead Changes</span>
              <span className="text-white font-medium">7</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">Safety Cars</span>
              <span className="text-white font-medium">2</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">DRS Zones</span>
              <span className="text-white font-medium">3</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
              <span className="text-sm text-gray-300">Overtakes</span>
              <span className="text-white font-medium">42</span>
            </div>
          </div>
        </div>
      </div>

      {/* Lap-by-lap position table for selected drivers */}
      {drivers.length > 0 && (
        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Position Timeline</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-600">
                  <th className="text-left p-2 text-gray-300">Lap</th>
                  {drivers.map(driver => (
                    <th key={driver.id} className="text-center p-2 text-gray-300">
                      {driver.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mockData.slice(0, 10).map((lapData, index) => (
                  <tr key={index} className="border-b border-gray-700/50">
                    <td className="p-2 font-medium text-white">{lapData.lap}</td>
                    {drivers.map(driver => (
                      <td key={driver.id} className="text-center p-2">
                        <span 
                          className="inline-block w-8 h-8 rounded-full text-white font-bold text-xs leading-8"
                          style={{ backgroundColor: driver.color }}
                        >
                          {Math.round(lapData[driver.id])}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {drivers.length === 0 && (
        <div className="flex items-center justify-center h-96 text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No drivers selected</p>
            <p className="text-sm">Select drivers from the sidebar to view race progression data</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RaceProgressionChart;