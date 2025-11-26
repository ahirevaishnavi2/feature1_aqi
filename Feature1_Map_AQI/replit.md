# GeoSense+ | AI-Powered Urban Analytics Platform

## Overview

GeoSense+ is an advanced location-based analytics platform that uses AI/ML and TomTom APIs to analyze urban areas, traffic patterns, environmental metrics, and mobility data. The platform features predictive analytics, an AI chatbot, gamified eco-rewards, and dual-mode visualization for both citizens and urban planning experts.

## Recent Changes (November 6, 2025)

- Initial project setup with Flask backend and responsive frontend
- Integrated TomTom APIs for Maps, Search, Routing, and Traffic analysis
- Implemented ML-based pattern recognition using scikit-learn (K-means clustering)
- Created AI chatbot using OpenAI API for conversational queries
- Built gamification system with eco-points, badges, and leaderboards
- Designed dual-mode interactive map (Citizen mode: emoji-based, Expert mode: detailed layers)
- Developed PostgreSQL database schema for users, badges, posts, and analytics
- Created mobile-responsive UI with circular gauges and real-time metrics

## Project Architecture

### Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Leaflet.js for mapping
- **Backend**: Flask (Python)
- **Database**: PostgreSQL (Neon-backed Replit database)
- **APIs**: TomTom (Maps, Search, Routing, Traffic), OpenAI (GPT-3.5)
- **ML/AI**: scikit-learn (clustering, pattern analysis), pandas, numpy

### Key Features

1. **Location Analysis**: TomTom API integration for POI search, route planning, and traffic data
2. **ML Pattern Recognition**: K-means clustering to identify urban zones (busy/moderate/calm)
3. **AI Insights**: OpenAI-powered chatbot and contextual recommendations
4. **Eco-Dashboard**: Real-time AQI, noise, traffic metrics with circular gauges
5. **Route Planning**: Eco-friendly vs fastest routes with CO₂ savings calculation
6. **Gamification**: Points, badges, streaks, and leaderboards
7. **Community Feed**: User posts, upvotes, eco-route sharing
8. **Dual-Mode Map**: Citizen (simple, emoji-based) and Expert (detailed layers)

### Database Schema

- `users`: User profiles, eco-points, green scores, streaks
- `badges`: Achievement tracking with icons and timestamps
- `community_posts`: User-generated content with location tags
- `location_analytics`: ML-analyzed location patterns and traffic data
- `user_routes`: Route history with eco-points earned

### API Integration

- **TomTom Search API**: POI discovery and location search
- **TomTom Routing API**: Route calculation with eco-friendly options
- **TomTom Traffic API**: Real-time traffic flow data (integrated in routing)
- **OpenAI API**: Chatbot responses and AI-generated insights

### ML Components

- Clustering algorithm for zone identification
- Traffic pattern analysis with time-based predictions
- Predictive analytics for busy hours and calm zones

## Environment Setup

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `SESSION_SECRET`: Flask session encryption key (auto-configured)
- `OPENAI_API_KEY`: For AI chatbot (optional, has fallback)
- `TOMTOM_API_KEY`: For maps and routing (optional, has mock data fallback)

## User Preferences

- Focus on AI/ML implementation and real-world data integration
- Mobile-responsive design with simple, intuitive UI
- Gamification to encourage eco-friendly behavior
- Both technical (expert) and casual (citizen) user interfaces

## Development Notes

- Mock data fallbacks ensure the platform works without API keys for demo purposes
- Real TomTom integration requires TOMTOM_API_KEY environment variable
- AI chatbot uses OpenAI when OPENAI_API_KEY is provided, otherwise uses smart fallbacks
- Database initializes automatically on first run
- Frontend uses Leaflet.js with OpenStreetMap tiles for map visualization
