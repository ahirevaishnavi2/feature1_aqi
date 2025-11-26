# AimlMapInsights - AI/ML Urban Analytics Platform

A Flask application with **MongoDB** database integration for urban analytics, traffic patterns, and eco-friendly route planning.

## Features

- **MongoDB Database** - User profiles, badges, community posts, analytics
- **ML Clustering** - KMeans clustering for zone pattern analysis
- **TomTom API Integration** - POI search, routing, traffic data
- **OpenAI Integration** - AI-powered insights and chatbot
- **Eco Points System** - Gamified rewards for eco-friendly actions
- **Community Feed** - User-generated posts and upvotes
- **Leaderboard** - Top eco-commuters ranking

## Prerequisites

1. **MongoDB Database** - You need a MongoDB database running
   - Local: Install MongoDB locally
   - Cloud: Use MongoDB Atlas (free tier available)

2. **Python 3.11+**

3. **API Keys**:
   - TomTom API Key (from https://developer.tomtom.com/)
   - OpenAI API Key (from https://platform.openai.com/)

## Setup Instructions

### 1. Install Dependencies

```bash
cd AimlMapInsights
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `AimlMapInsights` folder:

```env
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=aimlmapinsights

# OR for MongoDB Atlas (cloud):
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
# DATABASE_NAME=aimlmapinsights

# API Keys
TOMTOM_API_KEY=YOUR_TOMTOM_API_KEY
OPENAI_API_KEY=YOUR_OPENAI_API_KEY

# Session Secret (optional)
SESSION_SECRET=your-secret-key-here
```

### 3. MongoDB Setup

#### Option A: Local MongoDB (Recommended for Development)

1. **Install MongoDB Community Edition**:
   - Windows: Download from https://www.mongodb.com/try/download/community
   - Or use Chocolatey: `choco install mongodb`
   
2. **Start MongoDB Service**:
   ```bash
   # Windows - MongoDB usually starts automatically as a service
   # Check if running:
   net start MongoDB
   ```

3. **Verify Installation**:
   ```bash
   mongosh  # Opens MongoDB shell
   # Or: mongo (older versions)
   ```

4. **Update `.env`**:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=aimlmapinsights
   ```

#### Option B: MongoDB Atlas (Cloud - Free Tier)

1. **Sign up**: Go to https://www.mongodb.com/cloud/atlas/register
2. **Create a free cluster** (M0 - Free tier)
3. **Create a database user**:
   - Go to Database Access → Add New Database User
   - Set username and password
4. **Whitelist your IP**:
   - Go to Network Access → Add IP Address
   - Add `0.0.0.0/0` for all IPs (or your specific IP)
5. **Get connection string**:
   - Go to Clusters → Connect → Connect your application
   - Copy the connection string
   - Replace `<password>` with your database user password
6. **Update `.env`**:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   DATABASE_NAME=aimlmapinsights
   ```

### 4. Initialize Database

The database collections and indexes will be created automatically when you run the app for the first time.

Or manually run:
```python
python -c "from app import init_db; init_db()"
```

### 5. Run the Application

```bash
python app.py
```

The app will run on `http://localhost:5000`

**Note**: If MongoDB is not available, the app will use fallback demo data and still run (but data won't persist).

## Project Structure

```
AimlMapInsights/
├── app.py                 # Main Flask application
├── main.py               # Simple test script
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── templates/
│   └── index.html        # Frontend template
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   ├── js/
│   │   └── app.js        # Frontend JavaScript
│   └── images/           # Images
└── README.md             # This file
```

## API Endpoints

- `GET /` - Homepage
- `GET /api/dashboard` - Dashboard data (user stats, badges, metrics)
- `POST /api/location/analyze` - Analyze location with ML clustering
- `POST /api/route/plan` - Plan eco-friendly route
- `POST /api/chatbot` - AI chatbot responses
- `GET /api/community/posts` - Get community posts
- `POST /api/community/post` - Create community post
- `POST /api/community/upvote/<id>` - Upvote a post
- `GET /api/leaderboard` - Get leaderboard

## Database Schema

The app creates these tables automatically:

- **users** - User profiles, eco points, green scores
- **badges** - Earned badges
- **community_posts** - User posts
- **location_analytics** - Location pattern analysis
- **user_routes** - Saved routes

## Troubleshooting

### Database Connection Error

- Check PostgreSQL is running: `pg_isready` (Linux/Mac) or check services (Windows)
- Verify `DATABASE_URL` in `.env` is correct
- Ensure database exists and user has permissions

### Module Not Found Errors

- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Port Already in Use

- Change port in `app.py`: `app.run(host='0.0.0.0', port=5001, debug=True)`
- Or stop the other process using port 5000

### API Key Errors

- Verify API keys in `.env` file
- Check API key validity on TomTom/OpenAI dashboards

## Notes

- The app uses PostgreSQL for persistence (unlike the in-memory version in `Katathon/`)
- ML clustering requires at least 3 location points
- Database tables are auto-created on first run
- Demo data is seeded if no community posts exist

