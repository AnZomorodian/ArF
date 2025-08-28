# Track.lytix - F1 Data Analysis Platform

## Overview
Track.lytix is a comprehensive Formula 1 data analysis platform that provides advanced race data visualization and analytics. It leverages the FastF1 library to access official F1 timing data and creates interactive visualizations. The platform offers capabilities such as telemetry analysis, race progression tracking, tire strategy visualization, track dominance mapping, advanced driver performance analytics, weather impact analysis, and sophisticated race strategy evaluation. The project aims to offer a professional, mobile-responsive web application experience with F1-themed aesthetics.

## User Preferences
Preferred communication style: Simple, everyday language.
Design preferences: Professional, minimal, attractive design with enhanced F1-themed styling.
Data formatting: Lap times in M:SS.mmm format (e.g., 1:34.342).
Analysis requirements: Comprehensive sector analysis, detailed driver comparisons, enhanced track dominance visualization.

## System Architecture

### UI/UX Decisions
The platform features a modern, mobile-responsive F1 web application with dynamic animations and F1-themed styling. This includes professional F1 gradient backgrounds, racing animations, championship-style effects, and the Orbitron racing font. The layout is centered, often using a three-column structure, with an app-like tab system. Interactive elements like data tables and metric cards are designed with racing themes and team colors, incorporating glass morphism, glow effects, and high-contrast F1 styling for enhanced visibility.

### Technical Implementations
The system has evolved to a modern architecture but maintains a legacy Streamlit interface.

**Current (Next.js/TypeScript) Architecture:**
- **Frontend Framework**: Next.js 14 with React 18 and TypeScript.
- **Build Tool**: Turbopack.
- **Styling**: Tailwind CSS with a high-contrast F1-themed design system and professional glass morphism.
- **Animations**: Framer Motion for smooth transitions.
- **UI Components**: Headless UI, Heroicons, and custom F1-themed components.
- **Data Visualization**: Recharts for interactive charts.
- **Layout**: Responsive design with dynamic tab system and mobile-first approach.
- **API Integration**: Axios for seamless communication with FastAPI.

**Legacy (Streamlit) Architecture (Preserved):**
- **Framework**: Streamlit web application with custom CSS styling.
- **Visualization Library**: Plotly for interactive charts and graphs.
- **UI Components**: Custom F1-themed styling with team colors and gradients.
- **Layout**: Wide layout with an expandable sidebar.

**Backend Architecture:**
- **API Server**: FastAPI with automatic OpenAPI documentation and CORS support.
- **Data Processing**: Python-based backend using the FastF1 library for F1 data access.
- **Data Management**: Modular utility classes for brake analysis, composite performance, and advanced analytics.
- **Caching Strategy**: Session-level caching with FastF1's built-in system.
- **Session Management**: Global session state with intelligent driver-team mapping.
- **RESTful Endpoints**: Comprehensive API for telemetry, brake analysis, composite performance, and tire analytics.

### Feature Specifications
- **Telemetry Analysis**: Multi-parameter telemetry analysis (speed, throttle, brake, RPM, gear) with 6-channel visualization.
- **Race Progression Tracking**: Visualization of position changes and annotations.
- **Tire Strategy Visualization**: Detailed tire strategy statistics, compound performance analysis, stint length annotations, and gradient effects.
- **Track Dominance Mapping**: Generation of track dominance maps showing fastest sectors, including track coordinate interpolation and mini-sector analysis.
- **Advanced Driver Performance Analytics**: Comprehensive driver analysis, consistency metrics, and sector dominance metrics.
- **Weather Impact Analysis**: Correlation of weather data with lap time performance.
- **Race Strategy Evaluation**: Advanced pit stop strategy and fuel effect analysis with pace evolution tracking.
- **Brake Analysis**: Comprehensive brake efficiency analysis with force and duration metrics.
- **Composite Performance Index**: Advanced performance calculation combining speed, acceleration, and efficiency.
- **Dynamic Driver Management**: Real-time driver information management and intelligent driver-team mapping from session data.

### System Design Choices
- **Data Flow**: User selects session -> DataLoader fetches data via FastF1 -> Data processed and cleaned -> Plotly charts generated -> Streamlit renders visualizations -> Data cached locally.
- **Data Storage**: Local file system caching via FastF1, in-memory storage for loaded F1 session data, JSON for configuration, and temporary storage in the system temp directory for cache.
- **Modularity**: Prioritizes modularity and maintainability with clearly defined modules for data loading, visualization, track dominance, constants, and driver management.

## External Dependencies

- **FastF1**: Primary library for accessing official F1 telemetry and timing data.
- **Streamlit**: Web application framework (for the preserved legacy interface).
- **Plotly**: Interactive visualization library.
- **Pandas/NumPy**: For data manipulation and numerical computing.
- **SciPy**: For scientific computing and data interpolation.
- **Next.js**: Frontend framework for the modern web application.
- **React**: JavaScript library for building user interfaces.
- **TypeScript**: Superset of JavaScript for type safety.
- **Tailwind CSS**: Utility-first CSS framework for styling.
- **Framer Motion**: Animation library for React.
- **Recharts**: Charting library for React (for the modern frontend).
- **FastAPI**: Backend API server framework.
- **Axios**: HTTP client for browser and Node.js (for API integration).