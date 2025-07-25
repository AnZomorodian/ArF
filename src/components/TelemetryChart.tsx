import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Driver } from '../types';

interface TelemetryChartProps {
  drivers: Driver[];
}

const TelemetryChart: React.FC<TelemetryChartProps> = ({ drivers }) => {
  // Mock telemetry data - in real implementation, this would come from FastF1 API
  const mockData = Array.from({ length: 100 }, (_, i) => ({
    distance: i * 50,
    VER_speed: 300 + Math.sin(i * 0.1) * 50 + Math.random() * 20,
    HAM_speed: 295 + Math.sin(i * 0.12) * 45 + Math.random() * 20,
    LEC_speed: 298 + Math.sin(i * 0.08) * 48 + Math.random() * 20,
    VER_throttle: 80 + Math.sin(i * 0.15) * 20 + Math.random() * 10,
    HAM_throttle: 78 + Math.sin(i * 0.18) * 22 + Math.random() * 10,
    LEC_throttle: 82 + Math.sin(i * 0.12) * 18 + Math.random() * 10,
  }));

  const selectedDriverIds = drivers.map(d => d.id);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Speed Comparison</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="distance" 
                stroke="#9CA3AF"
                label={{ value: 'Distance (m)', position: 'insideBottom', offset: -10, style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <YAxis 
                stroke="#9CA3AF"
                label={{ value: 'Speed (km/h)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
              <Legend />
              {drivers.map((driver) => (
                <Line
                  key={`${driver.id}_speed`}
                  type="monotone"
                  dataKey={`${driver.id}_speed`}
                  stroke={driver.color}
                  strokeWidth={2}
                  dot={false}
                  name={`${driver.name} Speed`}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Throttle Input</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="distance" 
                stroke="#9CA3AF"
                label={{ value: 'Distance (m)', position: 'insideBottom', offset: -10, style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <YAxis 
                stroke="#9CA3AF"
                label={{ value: 'Throttle (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
              <Legend />
              {drivers.map((driver) => (
                <Line
                  key={`${driver.id}_throttle`}
                  type="monotone"
                  dataKey={`${driver.id}_throttle`}
                  stroke={driver.color}
                  strokeWidth={2}
                  dot={false}
                  name={`${driver.name} Throttle`}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {drivers.length === 0 && (
        <div className="flex items-center justify-center h-96 text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No drivers selected</p>
            <p className="text-sm">Select drivers from the sidebar to view telemetry data</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TelemetryChart;