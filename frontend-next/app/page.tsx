'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  BoltIcon, 
  FireIcon, 
  ChartPieIcon,
  CpuChipIcon,
  ClockIcon 
} from '@heroicons/react/24/outline'
import Header from './components/Header'
import SessionSelector from './components/SessionSelector'
import DriverSelector from './components/DriverSelector'
import TelemetryChart from './components/TelemetryChart'
import PerformanceMetrics from './components/PerformanceMetrics'
import BrakeAnalysis from './components/BrakeAnalysis'
import CompositePerformance from './components/CompositePerformance'

interface F1Session {
  year: number
  grand_prix: string
  session_type: string
  drivers?: string[]
}

export default function HomePage() {
  const [session, setSession] = useState<F1Session | null>(null)
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState('telemetry')
  const [loading, setLoading] = useState(false)

  const tabs = [
    { id: 'telemetry', name: 'Telemetry Analysis', icon: ChartBarIcon },
    { id: 'performance', name: 'Performance Metrics', icon: BoltIcon },
    { id: 'brake', name: 'Brake Analysis', icon: FireIcon },
    { id: 'composite', name: 'Composite Performance', icon: ChartPieIcon },
    { id: 'strategy', name: 'Race Strategy', icon: CpuChipIcon },
    { id: 'weather', name: 'Weather Impact', icon: ClockIcon },
  ]

  const handleSessionLoad = async (sessionData: F1Session) => {
    setLoading(true)
    try {
      // Simulate API call to load session data
      await new Promise(resolve => setTimeout(resolve, 1500))
      setSession(sessionData)
      setSelectedDrivers([])
    } catch (error) {
      console.error('Error loading session:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Session Selection */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <SessionSelector 
            onSessionLoad={handleSessionLoad}
            loading={loading}
          />
        </motion.section>

        {/* Driver Selection */}
        {session && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8"
          >
            <DriverSelector
              session={session}
              selectedDrivers={selectedDrivers}
              onDriversChange={setSelectedDrivers}
            />
          </motion.section>
        )}

        {/* Analysis Tabs */}
        {session && selectedDrivers.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {/* Tab Navigation */}
            <div className="glass-card p-1 mb-8">
              <div className="flex flex-wrap gap-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`nav-link flex items-center gap-2 ${
                        activeTab === tab.id ? 'active' : ''
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="hidden sm:inline">{tab.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Tab Content */}
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4 }}
            >
              {activeTab === 'telemetry' && (
                <TelemetryChart 
                  session={session} 
                  drivers={selectedDrivers} 
                />
              )}
              
              {activeTab === 'performance' && (
                <PerformanceMetrics 
                  session={session} 
                  drivers={selectedDrivers} 
                />
              )}
              
              {activeTab === 'brake' && (
                <BrakeAnalysis 
                  session={session} 
                  drivers={selectedDrivers} 
                />
              )}
              
              {activeTab === 'composite' && (
                <CompositePerformance 
                  session={session} 
                  drivers={selectedDrivers} 
                />
              )}
              
              {(activeTab === 'strategy' || activeTab === 'weather') && (
                <div className="glass-card p-8 text-center">
                  <div className="animate-pulse">
                    <CpuChipIcon className="w-16 h-16 mx-auto mb-4 text-f1-teal" />
                    <h3 className="text-2xl font-bold mb-2">Coming Soon</h3>
                    <p className="text-white/70">
                      Advanced {tab.name} analysis is under development
                    </p>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.section>
        )}

        {/* Welcome State */}
        {!session && !loading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="text-center py-16"
          >
            <div className="glass-card p-12 max-w-2xl mx-auto">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="w-24 h-24 mx-auto mb-8"
              >
                <div className="w-full h-full bg-gradient-to-br from-f1-red to-f1-teal rounded-full flex items-center justify-center text-4xl font-bold">
                  F1
                </div>
              </motion.div>
              
              <h1 className="section-header mb-6">
                Professional F1 Data Analysis Platform
              </h1>
              
              <p className="text-xl text-white/70 mb-8 leading-relaxed">
                Advanced Formula 1 telemetry analysis with real-time performance metrics, 
                comprehensive driver comparisons, and professional-grade visualizations.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="p-6">
                  <ChartBarIcon className="w-12 h-12 mx-auto mb-4 text-f1-teal" />
                  <h3 className="text-lg font-semibold mb-2">Real-time Telemetry</h3>
                  <p className="text-white/60">Live data analysis with advanced visualization</p>
                </div>
                
                <div className="p-6">
                  <BoltIcon className="w-12 h-12 mx-auto mb-4 text-f1-red" />
                  <h3 className="text-lg font-semibold mb-2">Performance Insights</h3>
                  <p className="text-white/60">Comprehensive driver and team analytics</p>
                </div>
                
                <div className="p-6">
                  <CpuChipIcon className="w-12 h-12 mx-auto mb-4 text-yellow-400" />
                  <h3 className="text-lg font-semibold mb-2">AI-Powered Analysis</h3>
                  <p className="text-white/60">Machine learning driven performance predictions</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  )
}