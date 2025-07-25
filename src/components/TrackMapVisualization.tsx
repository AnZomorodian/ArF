import React from 'react';
import { Driver } from '../types';

interface TrackMapVisualizationProps {
  drivers: Driver[];
}

const TrackMapVisualization: React.FC<TrackMapVisualizationProps> = ({ drivers }) => {
  // Mock track data - simplified track layout points
  const trackPoints = [
    { x: 100, y: 200 }, { x: 150, y: 180 }, { x: 200, y: 160 }, { x: 250, y: 150 },
    { x: 300, y: 160 }, { x: 350, y: 180 }, { x: 400, y: 220 }, { x: 420, y: 270 },
    { x: 400, y: 320 }, { x: 350, y: 350 }, { x: 300, y: 360 }, { x: 250, y: 350 },
    { x: 200, y: 330 }, { x: 180, y: 300 }, { x: 160, y: 270 }, { x: 150, y: 240 },
    { x: 120, y: 220 }, { x: 100, y: 200 }
  ];

  // Create SVG path from track points
  const pathData = trackPoints.reduce((path, point, index) => {
    const command = index === 0 ? 'M' : 'L';
    return `${path} ${command} ${point.x} ${point.y}`;
  }, '');

  // Mock sector data
  const sectors = [
    { name: 'Sector 1', start: 0, end: 6, color: '#00FF00', fastestDriver: 'VER' },
    { name: 'Sector 2', start: 6, end: 12, color: '#FFFF00', fastestDriver: 'HAM' },
    { name: 'Sector 3', start: 12, end: 18, color: '#FF00FF', fastestDriver: 'LEC' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Track Dominance Map</h3>
        
        <div className="glass-card p-6">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Track Visualization */}
            <div className="flex-1">
              <div className="bg-gray-800 rounded-lg p-4 h-96 flex items-center justify-center">
                <svg 
                  width="500" 
                  height="400" 
                  viewBox="0 0 500 400"
                  className="max-w-full max-h-full"
                >
                  {/* Track Layout */}
                  <path
                    d={pathData}
                    fill="none"
                    stroke="#374151"
                    strokeWidth="20"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  
                  {/* Sector Highlights */}
                  {sectors.map((sector, index) => {
                    const sectorPoints = trackPoints.slice(sector.start, sector.end + 1);
                    const sectorPath = sectorPoints.reduce((path, point, pointIndex) => {
                      const command = pointIndex === 0 ? 'M' : 'L';
                      return `${path} ${command} ${point.x} ${point.y}`;
                    }, '');
                    
                    return (
                      <path
                        key={index}
                        d={sectorPath}
                        fill="none"
                        stroke={sector.color}
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        opacity={0.8}
                      />
                    );
                  })}
                  
                  {/* Start/Finish Line */}
                  <line
                    x1={trackPoints[0].x - 10}
                    y1={trackPoints[0].y - 10}
                    x2={trackPoints[0].x + 10}
                    y2={trackPoints[0].y + 10}
                    stroke="#FFFFFF"
                    strokeWidth="4"
                  />
                  <line
                    x1={trackPoints[0].x - 10}
                    y1={trackPoints[0].y + 10}
                    x2={trackPoints[0].x + 10}
                    y2={trackPoints[0].y - 10}
                    stroke="#FFFFFF"
                    strokeWidth="4"
                  />
                  
                  {/* Track Labels */}
                  <text x="50" y="200" fill="#9CA3AF" fontSize="12" fontWeight="bold">
                    START/FINISH
                  </text>
                  
                  {/* Corner Numbers */}
                  {[
                    { x: 250, y: 140, num: "1" },
                    { x: 430, y: 220, num: "2" },
                    { x: 420, y: 330, num: "3" },
                    { x: 300, y: 370, num: "4" },
                    { x: 170, y: 310, num: "5" }
                  ].map((corner, index) => (
                    <circle key={index} cx={corner.x} cy={corner.y} r="12" fill="#DC0000" />
                  ))}
                  {[
                    { x: 250, y: 145, num: "1" },
                    { x: 430, y: 225, num: "2" },
                    { x: 420, y: 335, num: "3" },
                    { x: 300, y: 375, num: "4" },
                    { x: 170, y: 315, num: "5" }
                  ].map((corner, index) => (
                    <text key={index} x={corner.x} y={corner.y} textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                      {corner.num}
                    </text>
                  ))}
                </svg>
              </div>
            </div>
            
            {/* Sector Analysis */}
            <div className="lg:w-80 space-y-4">
              <h4 className="text-lg font-semibold text-white">Sector Analysis</h4>
              
              {sectors.map((sector, index) => {
                const fastestDriver = drivers.find(d => d.id === sector.fastestDriver);
                return (
                  <div key={index} className="bg-gray-800/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">{sector.name}</span>
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: sector.color }}
                      />
                    </div>
                    
                    {fastestDriver && (
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-6 h-6 rounded-full"
                          style={{ backgroundColor: fastestDriver.color }}
                        />
                        <span className="text-sm text-gray-300">{fastestDriver.name}</span>
                      </div>
                    )}
                    
                    <div className="mt-2 text-xs text-gray-400">
                      Fastest: {(22.5 + Math.random() * 5).toFixed(3)}s
                    </div>
                  </div>
                );
              })}
              
              {/* Mini Sectors */}
              <div className="bg-gray-800/50 rounded-lg p-4">
                <h5 className="text-white font-medium mb-3">Mini Sectors</h5>
                <div className="space-y-2">
                  {Array.from({ length: 6 }, (_, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="text-gray-300">MS{i + 1}</span>
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: drivers[i % drivers.length]?.color || '#666' }}
                        />
                        <span className="text-white font-mono">
                          {(8.2 + Math.random() * 2).toFixed(3)}s
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Speed Trap Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Speed Traps</h4>
          <div className="space-y-2">
            {drivers.slice(0, 5).map((driver, index) => {
              const maxSpeed = 320 + Math.random() * 25;
              return (
                <div key={driver.id} className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-6 h-6 rounded-full"
                      style={{ backgroundColor: driver.color }}
                    />
                    <span className="font-medium text-white">{driver.name}</span>
                  </div>
                  <span className="font-mono text-sm text-gray-300">{maxSpeed.toFixed(1)} km/h</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="glass-card p-4">
          <h4 className="text-lg font-semibold mb-3 text-white">Corner Analysis</h4>
          <div className="space-y-3">
            {['Turn 1', 'Turn 3', 'Turn 7', 'Turn 12'].map((corner, index) => (
              <div key={corner} className="flex justify-between items-center p-2 bg-gray-800/30 rounded">
                <span className="text-sm text-gray-300">{corner}</span>
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: drivers[index % drivers.length]?.color || '#666' }}
                  />
                  <span className="text-white font-medium text-sm">
                    {(180 + Math.random() * 40).toFixed(0)} km/h
                  </span>
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
            <p className="text-sm">Select drivers from the sidebar to view track dominance data</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrackMapVisualization;