import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { Driver } from '../types';

interface LapTimesChartProps {
  drivers: Driver[];
}

const LapTimesChart: React.FC<LapTimesChartProps> = ({ drivers }) => {
  // Mock lap times data - in real implementation, this would come from FastF1 API
  const mockData = Array.from({ length: 20 }, (_, i) => {
    const lapNumber = i + 1;
    return {
      lap: lapNumber,
      VER: 90.5 + Math.random() * 2 + (i > 15 ? Math.random() * 3 : 0),
      HAM: 91.2 + Math.random() * 2 + (i > 15 ? Math.random() * 3 : 0),
      LEC: 90.8 + Math.random() * 2 + (i > 15 ? Math.random() * 3 : 0),
      NOR: 91.5 + Math.random() * 2 + (i > 15 ? Math.random() * 3 : 0),
    };
  });

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(3);
    return `${minutes}:${secs.padStart(6, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Lap Time Progression</h3>
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
                domain={['dataMin - 1', 'dataMax + 1']}
                tickFormatter={formatTime}
                label={{ value: 'Lap Time', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
                formatter={(value: number) => [formatTime(value), 'Lap Time']}
              />
              <Legend />
              {drivers.map((driver) => (
                <Line
                  key={driver.id}
                  type="monotone"
                  dataKey={driver.id}
                  stroke={driver.color}
                  strokeWidth={2}
                  dot={{ fill: driver.color, strokeWidth: 2, r: 4 }}
                  name={driver.name}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Fastest Laps Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Fastest Laps</h4>
          <div className="space-y-2">
            {drivers.slice(0, 5).map((driver, index) => {
              const fastestTime = Math.min(...mockData.map(d => d[driver.id as keyof typeof d] as number).filter(Boolean));
              return (
                <div key={driver.id} className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                      index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-yellow-600' : ''
                    }`} style={index > 2 ? { backgroundColor: driver.color } : {}}>
                      {index + 1}
                    </div>
                    <span className="font-medium text-white">{driver.name}</span>
                  </div>
                  <span className="font-mono text-sm text-gray-300">{formatTime(fastestTime)}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Sector Analysis</h4>
          <div className="space-y-3">
            {['Sector 1', 'Sector 2', 'Sector 3'].map((sector, index) => (
              <div key={sector} className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">{sector}</span>
                  <span className="text-sm font-mono text-white">
                    {formatTime(25 + Math.random() * 5)}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${70 + Math.random() * 30}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {drivers.length === 0 && (
        <div className="flex items-center justify-center h-96 text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No drivers selected</p>
            <p className="text-sm">Select drivers from the sidebar to view lap time data</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LapTimesChart;