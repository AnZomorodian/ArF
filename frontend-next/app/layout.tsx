import './globals.css'
import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
})

const jetbrains = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-jetbrains',
})

export const metadata: Metadata = {
  title: 'F1 Data Analysis Platform | Professional Racing Analytics',
  description: 'Advanced Formula 1 data analysis platform with real-time telemetry, comprehensive performance metrics, and professional-grade visualizations for racing enthusiasts and teams.',
  keywords: ['F1', 'Formula 1', 'Racing', 'Data Analysis', 'Telemetry', 'Performance Analytics'],
  authors: [{ name: 'F1 Data Platform Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#00FFE6',
  openGraph: {
    title: 'F1 Data Analysis Platform',
    description: 'Professional Formula 1 data analysis with advanced telemetry and performance insights',
    type: 'website',
    images: ['/og-image.jpg'],
  },
  robots: 'index, follow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="bg-f1-dark min-h-screen text-white antialiased">
        <div className="relative min-h-screen bg-gradient-to-br from-f1-dark via-f1-darker to-black">
          {/* Background Pattern */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,255,230,0.1),transparent_50%)] pointer-events-none" />
          <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,0,51,0.05)_25%,rgba(255,0,51,0.05)_50%,transparent_50%,transparent_75%,rgba(0,255,230,0.05)_75%)] bg-[length:60px_60px] pointer-events-none" />
          
          {/* Main Content */}
          <div className="relative z-10">
            {children}
          </div>
        </div>
      </body>
    </html>
  )
}