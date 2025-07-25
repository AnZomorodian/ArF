# F1 Data Analysis Platform

## Overview

This is a Formula 1 data analysis platform built with Streamlit that provides comprehensive race data visualization and analysis capabilities. The platform leverages the FastF1 library to access official F1 timing data and creates interactive visualizations using Plotly. The application focuses on telemetry analysis, race progression tracking, tire strategy visualization, and track dominance mapping.

## Recent Changes (July 25, 2025)

### Major Version 2.0 Update - TypeScript React Migration
- **Complete platform modernization**: Migrated from Streamlit to TypeScript React application
- **Advanced UI framework**: Implemented with Vite, Tailwind CSS, and Framer Motion animations  
- **Enhanced component architecture**: Modular React components with TypeScript type safety
- **Professional data visualizations**: Recharts integration for interactive F1 telemetry charts
- **Responsive modern design**: Glass morphism UI with F1-themed gradients and team colors
- **Real-time analytics dashboard**: Multi-tab interface for telemetry, lap times, tire strategy, race progression, and track maps

### Legacy Streamlit Features Preserved
- Successfully converted to professional web app format with all English code
- Enhanced tire strategy analysis with advanced performance metrics and compound comparison
- Migrated project from Replit Agent to Replit environment with proper configuration
- Fixed critical race progression plot error (Invalid property 'font' for XAxis)
- Implemented forced dark background theme to eliminate white background issues
- Enhanced driver selection interface with minimal, professional design
- Improved table styling with centered text alignment and professional F1-themed design

### Enhanced Tire Strategy Features
- Added detailed tire strategy statistics with per-driver breakdowns
- Implemented compound performance analysis with lap time comparisons
- Created enhanced tire usage visualization with team color coding
- Added stint length annotations and gradient effects for better readability
- Included consistency metrics and performance analytics
- Enhanced export functionality for charts and data files

### UI/UX Improvements  
- Enhanced sector analysis with grid layout and enhanced styling
- Upgraded fastest lap displays with modern card-based design and hover effects
- Enhanced race progression analysis with better position change visualization
- Added professional typography and button styling throughout the application
- Implemented enhanced CSS classes for consistent styling across all components
- Added position badges with animations for fastest lap indicators

### Technical Fixes
- Fixed LSP diagnostics and variable scope issues in visualizations
- Corrected TIRE_COLORS import for enhanced tire strategy functionality
- Corrected Plotly axis configuration for race progression charts
- Enhanced error handling and code robustness
- Improved responsive design and layout consistency

## User Preferences

Preferred communication style: Simple, everyday language.
Design preferences: Professional, minimal, attractive design with enhanced F1-themed styling.
Data formatting: Lap times in M:SS.mmm format (e.g., 1:34.342).
Analysis requirements: Comprehensive sector analysis, detailed driver comparisons, enhanced track dominance visualization.

## System Architecture

### Frontend Architecture - Version 2.0 (TypeScript React)
- **Framework**: React 19 with TypeScript for type safety and modern development
- **Build Tool**: Vite for fast development and optimized production builds
- **Styling**: Tailwind CSS with custom F1-themed design system and glass morphism effects
- **Animations**: Framer Motion for smooth transitions and interactive elements
- **UI Components**: Modular React components with Lucide React icons
- **Data Visualization**: Recharts for interactive charts and SVG-based track maps
- **Layout**: Responsive grid layout with collapsible sidebar and tabbed interface

### Legacy Frontend Architecture (Streamlit - Preserved)
- **Framework**: Streamlit web application with custom CSS styling
- **Visualization Library**: Plotly for interactive charts and graphs
- **UI Components**: Custom F1-themed styling with team colors and gradients
- **Layout**: Wide layout with expandable sidebar for controls and filters

### Backend Architecture
- **Data Processing**: Python-based backend using FastF1 library for F1 data access
- **Data Management**: Modular utility classes for data loading and processing
- **Caching Strategy**: FastF1 built-in caching system using system temp directory
- **Session Management**: Session-based data loading with support for different race weekend sessions
- **API Integration**: RESTful endpoints for React frontend to access F1 data

### Data Storage Solutions
- **Cache Storage**: Local file system caching via FastF1's caching mechanism
- **Session Data**: In-memory storage of loaded F1 session data
- **Configuration**: JSON-based configuration files for application settings
- **Temporary Storage**: System temp directory for cache and temporary files
- **Type Definitions**: TypeScript interfaces for F1 data structures and API responses

## Key Components

### Core Application (app.py)
- Main Streamlit application entry point
- Page configuration and custom CSS styling
- Integration of all utility modules
- User interface layout and interaction handling

### Data Loading Module (utils/data_loader.py)
- **Purpose**: Handles F1 session data loading and caching
- **Key Features**: 
  - FastF1 session management
  - Automatic cache setup and management
  - Session metadata extraction
  - Error handling for data loading failures

### Visualization Module (utils/visualizations.py)
- **Purpose**: Creates professional interactive Plotly visualizations with enhanced styling
- **Supported Charts**:
  - Telemetry comparison plots (speed, throttle, brake, RPM, gear) with enhanced legends
  - Professional tire strategy visualizations with stint analysis
  - Advanced race progression analysis with position tracking and annotations
  - Team color-coded displays with professional gradients and styling

### Track Dominance Module (utils/track_dominance.py)
- **Purpose**: Generates track dominance maps showing fastest sectors
- **Features**:
  - Track coordinate interpolation for smooth visualization
  - Mini-sector analysis with configurable granularity
  - Driver comparison across track segments
  - Fastest lap telemetry integration

### Constants Module (utils/constants.py)
- **Purpose**: Centralized configuration for F1-specific data
- **Contains**:
  - 2024 season team colors and branding
  - Driver-to-team mappings
  - Grand Prix event listings
  - Session type definitions

## Data Flow

1. **Session Selection**: User selects year, Grand Prix, and session type
2. **Data Loading**: DataLoader fetches session data via FastF1 API
3. **Data Processing**: Raw telemetry and timing data is processed and cleaned
4. **Visualization Generation**: Plotly charts are created based on processed data
5. **Interactive Display**: Streamlit renders the visualizations with user controls
6. **Caching**: Processed data is cached locally to improve performance

## External Dependencies

### Core Libraries
- **FastF1**: Official F1 data access library for telemetry and timing data
- **Streamlit**: Web application framework for the user interface
- **Plotly**: Interactive visualization library for charts and graphs
- **Pandas/NumPy**: Data manipulation and numerical computing
- **SciPy**: Scientific computing for data interpolation

### Data Sources
- **F1 Official Timing Data**: Accessed through FastF1's API integration
- **Track Coordinate Data**: Geographic coordinates for circuit mapping
- **Session Metadata**: Race weekend information and timing details

### Development Tools
- **PyQt6**: Desktop application framework (for additional tools)
- **Matplotlib**: Alternative plotting library for static visualizations
- **JSON**: Configuration file format for application settings

## Deployment Strategy

### Local Development
- **Environment**: Python virtual environment with pip dependencies
- **Cache Management**: Local file system caching in temp directory
- **Configuration**: JSON-based configuration files for customization

### Streamlit Deployment
- **Platform**: Streamlit Cloud or similar hosting service
- **Dependencies**: Requirements.txt with pinned library versions
- **Caching**: Persistent cache directory configuration
- **Error Handling**: Graceful degradation for data loading failures

### Performance Considerations
- **Data Caching**: FastF1 caching reduces API calls and improves load times
- **Memory Management**: Session-based data loading to manage memory usage
- **Async Loading**: Background data processing where possible
- **Error Recovery**: Fallback mechanisms for data loading failures

The architecture prioritizes modularity, maintainability, and user experience while providing comprehensive F1 data analysis capabilities. The platform is designed to handle the complexity of F1 telemetry data while presenting it in an accessible and visually appealing format.