import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps, loads
import requests
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from geopy.distance import geodesic
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'aimlmapinsights')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY')

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    print(f"Connected to MongoDB: {DATABASE_NAME}")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    client = None
    db = None

try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    if openai_client:
        print(f"OpenAI client initialized with model {OPENAI_MODEL}")
except Exception as e:
    print(f"OpenAI client initialization error: {e}")
    openai_client = None

def init_db():
    """Initialize database collections and indexes"""
    if not db:
        return
    
    # Create indexes for better performance
    db.users.create_index("username", unique=True)
    db.badges.create_index("user_id")
    db.community_posts.create_index("created_at")
    db.community_posts.create_index("user_id")
    db.location_analytics.create_index("analyzed_at")
    db.user_routes.create_index("user_id")
    
    print("Database initialized with indexes")

def get_or_create_user(username='demo_user'):
    """Get or create a user session"""
    if not db:
        # Fallback if MongoDB not available
        return {
            'id': 'demo',
            'username': username,
            'eco_points': 150,
            'green_score': 65,
            'streak_days': 3,
            'co2_saved': 12.5,
            'clean_trips': 8,
            'created_at': datetime.now()
        }
    
    user = db.users.find_one({"username": username})
    
    if not user:
        # Create new user
        user_data = {
            "username": username,
            "eco_points": 150,
            "green_score": 65,
            "streak_days": 3,
            "last_activity": datetime.now().date(),
            "co2_saved": 12.5,
            "clean_trips": 8,
            "created_at": datetime.now()
        }
        result = db.users.insert_one(user_data)
        user_id = result.inserted_id
        
        # Create default badges
        badges = [
            {"user_id": user_id, "badge_name": "Eco Starter", "badge_icon": "🌱", "earned_at": datetime.now()},
            {"user_id": user_id, "badge_name": "Conscious Citizen", "badge_icon": "🏅", "earned_at": datetime.now()}
        ]
        db.badges.insert_many(badges)
        
        user = db.users.find_one({"_id": user_id})
    
    # Convert ObjectId to string for JSON serialization
    user['id'] = str(user['_id'])
    del user['_id']
    
    return user

def analyze_location_patterns_ml(locations_data):
    """Use ML clustering to identify urban zone patterns"""
    if not locations_data or len(locations_data) < 3:
        return None
    
    coords = np.array([[loc['lat'], loc['lon']] for loc in locations_data])
    
    n_clusters = min(3, len(locations_data))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(coords)
    
    zone_types = ['Busy Zone', 'Moderate Zone', 'Calm Zone']
    
    for i, loc in enumerate(locations_data):
        loc['cluster'] = int(clusters[i])
        loc['zone_type'] = zone_types[clusters[i] % len(zone_types)]
    
    return locations_data

def generate_traffic_pattern(lat, lon):
    """Generate ML-based traffic pattern analysis"""
    hour = datetime.now().hour
    
    patterns = {
        'peak_morning': (7, 9),
        'peak_evening': (17, 20),
        'quiet': (22, 6)
    }
    
    if 7 <= hour <= 9:
        pattern = "Peak morning traffic - Busiest between 7-9 AM"
        traffic_level = random.randint(70, 95)
    elif 17 <= hour <= 20:
        pattern = "Peak evening rush - Busiest between 6-8 PM"
        traffic_level = random.randint(75, 100)
    elif 22 <= hour or hour <= 6:
        pattern = "Quiet zone - Perfect for evening walks"
        traffic_level = random.randint(10, 30)
    else:
        pattern = "Moderate traffic - Good time for errands"
        traffic_level = random.randint(40, 65)
    
    return {
        'pattern': pattern,
        'traffic_level': traffic_level,
        'busy_hours': '6-8 PM' if 17 <= hour <= 20 else '7-9 AM' if 7 <= hour <= 9 else 'Low traffic',
        'recommendations': []
    }

def get_tomtom_search(query, lat=None, lon=None):
    """Search POIs using TomTom Search API"""
    if not TOMTOM_API_KEY:
        return mock_tomtom_search(query, lat, lon)
    
    url = f"https://api.tomtom.com/search/2/search/{query}.json"
    params = {
        'key': TOMTOM_API_KEY,
        'limit': 10
    }
    if lat and lon:
        params['lat'] = lat
        params['lon'] = lon
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
    except Exception as e:
        print(f"TomTom API error: {e}")
    
    return mock_tomtom_search(query, lat, lon)

def mock_tomtom_search(query, lat=None, lon=None):
    """Mock TomTom search results for demo"""
    base_lat = lat or 18.5204
    base_lon = lon or 73.8567
    
    results = []
    poi_types = ['Restaurant', 'Park', 'Shopping Mall', 'Hospital', 'School']
    
    for i in range(5):
        offset_lat = random.uniform(-0.05, 0.05)
        offset_lon = random.uniform(-0.05, 0.05)
        
        results.append({
            'position': {
                'lat': base_lat + offset_lat,
                'lon': base_lon + offset_lon
            },
            'poi': {
                'name': f"{query} {poi_types[i % len(poi_types)]} {i+1}",
                'categories': [poi_types[i % len(poi_types)]]
            },
            'address': {
                'freeformAddress': f"Street {i+1}, Pune, India"
            }
        })
    
    return results

def get_tomtom_route(start_lat, start_lon, end_lat, end_lon, route_type='eco'):
    """Get route using TomTom Routing API"""
    if not TOMTOM_API_KEY:
        return mock_tomtom_route(start_lat, start_lon, end_lat, end_lon, route_type)
    
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
    params = {
        'key': TOMTOM_API_KEY,
        'routeType': 'eco' if route_type == 'eco' else 'fastest'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"TomTom Routing API error: {e}")
    
    return mock_tomtom_route(start_lat, start_lon, end_lat, end_lon, route_type)

def mock_tomtom_route(start_lat, start_lon, end_lat, end_lon, route_type):
    """Mock TomTom route for demo"""
    distance = geodesic((start_lat, start_lon), (end_lat, end_lon)).kilometers
    
    travel_time = int(distance * 4 * 60)
    if route_type == 'eco':
        travel_time = int(travel_time * 1.1)
    
    return {
        'routes': [{
            'summary': {
                'lengthInMeters': int(distance * 1000),
                'travelTimeInSeconds': travel_time,
                'trafficDelayInSeconds': random.randint(0, 300),
                'departureTime': datetime.now().isoformat(),
                'arrivalTime': (datetime.now() + timedelta(seconds=travel_time)).isoformat()
            },
            'legs': [{
                'points': [
                    {'latitude': start_lat, 'longitude': start_lon},
                    {'latitude': (start_lat + end_lat) / 2, 'longitude': (start_lon + end_lon) / 2},
                    {'latitude': end_lat, 'longitude': end_lon}
                ]
            }]
        }]
    }

def get_ai_insight(location_data, context='general'):
    """Generate AI-powered insights using OpenAI"""
    if not OPENAI_API_KEY:
        return generate_mock_insight(location_data, context)
    
    try:
        prompt = f"""Generate a one-line friendly insight about this location data:
        Traffic Level: {location_data.get('traffic_level', 50)}%
        AQI: {location_data.get('aqi', 75)}
        Time: {datetime.now().strftime('%H:%M')}
        Context: {context}
        
        Provide a helpful, conversational insight like "Traffic is moderate in your zone, AQI is healthy — best time for an evening walk!"
        """
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
    
    return generate_mock_insight(location_data, context)

def generate_mock_insight(location_data, context):
    """Generate mock AI insights"""
    traffic = location_data.get('traffic_level', 50)
    aqi = location_data.get('aqi', 75)
    hour = datetime.now().hour
    
    insights = [
        f"Traffic is {'light' if traffic < 40 else 'moderate' if traffic < 70 else 'heavy'} in your zone, AQI is {'healthy' if aqi < 100 else 'moderate'} — {'best time for an evening walk' if traffic < 40 else 'consider eco-friendly routes'}!",
        f"Your area is {'quiet' if traffic < 40 else 'moderately busy' if traffic < 70 else 'quite busy'} right now. Air quality is {'good' if aqi < 100 else 'fair'}. {'Perfect for outdoor activities' if traffic < 40 and aqi < 100 else 'Indoor activities recommended'}.",
        f"Current conditions: {traffic}% traffic, AQI {aqi}. {'Great conditions for a bike ride' if traffic < 50 and aqi < 100 else 'Consider using public transport'}!",
    ]
    
    return random.choice(insights)

def get_rule_based_response(message: str) -> str:
    """Generate a simple rule-based chatbot response when OpenAI is unavailable"""
    if not message:
        return "I'm GeoSense+, your eco-assistant! Ask me about clean routes, air quality, or earning eco-points."

    message_lower = message.lower()

    responses = [
        (
            ['route', 'walk', 'bike', 'path'],
            "I can guide you to cleaner routes! Try exploring eco-friendly paths during off-peak hours to save emissions."
        ),
        (
            ['eco', 'carbon', 'green score', 'points'],
            "Eco-points come from choosing sustainable travel. Every eco-route boosts your green score and saves CO₂!"
        ),
        (
            ['air', 'aqi', 'pollution', 'quality'],
            "Local AQI is usually best early mornings after rainfall. Consider parks or riverside areas for the cleanest air!"
        ),
        (
            ['traffic', 'congestion', 'rush'],
            "Traffic peaks around 8 AM and 6 PM. Shifting your commute by 20 minutes can lower delays and emissions."
        ),
        (
            ['mad', 'angry'],
            "I'm never mad—just motivated to help you find greener journeys!"
        ),
    ]

    for keywords, response in responses:
        if any(keyword in message_lower for keyword in keywords):
            return response

    return "I'm here to help with eco-routes, air quality insights, or your green score. How can I assist?"

@app.route('/')
def index():
    return render_template('index.html', tomtom_key=TOMTOM_API_KEY or '')

@app.route('/api/dashboard')
def dashboard_data():
    """Get dashboard data for current user"""
    user = get_or_create_user()
    
    badges = []
    if db:
        user_id = ObjectId(user['id']) if isinstance(user['id'], str) and len(user['id']) == 24 else user.get('_id')
        if user_id:
            try:
                badges_cursor = db.badges.find({"user_id": user_id}).sort("earned_at", -1)
                badges = []
                for badge in badges_cursor:
                    badge['id'] = str(badge['_id'])
                    del badge['_id']
                    badges.append(badge)
            except:
                pass
    
    location_data = {
        'aqi': random.randint(50, 120),
        'noise_level': random.randint(40, 80),
        'traffic_level': random.randint(30, 90)
    }
    
    insight = get_ai_insight(location_data, 'dashboard')
    
    return jsonify({
        'user': user,
        'badges': badges,
        'metrics': {
            'aqi': location_data['aqi'],
            'noise': location_data['noise_level'],
            'traffic': location_data['traffic_level'],
            'green_score': user['green_score']
        },
        'insight': insight,
        'streak': user['streak_days']
    })

@app.route('/api/location/analyze', methods=['POST'])
def analyze_location():
    """Analyze location using TomTom and ML"""
    data = request.json
    lat = data.get('lat', 18.5204)
    lon = data.get('lon', 73.8567)
    query = data.get('query', 'points of interest')
    
    pois = get_tomtom_search(query, lat, lon)
    
    locations_data = []
    for poi in pois[:5]:
        pos = poi.get('position', {})
        locations_data.append({
            'lat': pos.get('lat', lat),
            'lon': pos.get('lon', lon),
            'name': poi.get('poi', {}).get('name', 'Unknown'),
            'category': poi.get('poi', {}).get('categories', ['General'])[0] if poi.get('poi', {}).get('categories') else 'General'
        })
    
    analyzed = analyze_location_patterns_ml(locations_data)
    traffic_pattern = generate_traffic_pattern(lat, lon)
    
    location_data = {
        'aqi': random.randint(60, 110),
        'noise_level': random.randint(45, 85),
        'traffic_level': traffic_pattern['traffic_level']
    }
    
    insight = get_ai_insight(location_data, 'location_analysis')
    
    return jsonify({
        'locations': analyzed or locations_data,
        'traffic_pattern': traffic_pattern,
        'metrics': location_data,
        'insight': insight
    })

@app.route('/api/route/plan', methods=['POST'])
def plan_route():
    """Plan eco-friendly route using TomTom Routing API"""
    data = request.json
    start_lat = data.get('start_lat')
    start_lon = data.get('start_lon')
    end_lat = data.get('end_lat')
    end_lon = data.get('end_lon')
    route_type = data.get('route_type', 'eco')
    
    route_data = get_tomtom_route(start_lat, start_lon, end_lat, end_lon, route_type)
    
    if route_data and 'routes' in route_data and len(route_data['routes']) > 0:
        route = route_data['routes'][0]
        summary = route['summary']
        
        distance_km = summary['lengthInMeters'] / 1000
        eco_points = int(distance_km * 5) if route_type == 'eco' else int(distance_km * 2)
        co2_saved = round(distance_km * 0.12, 2) if route_type == 'eco' else 0
        
        user = get_or_create_user()
        
        if db:
            user_id = ObjectId(user['id']) if isinstance(user['id'], str) and len(user['id']) == 24 else user.get('_id')
            if user_id:
                db.users.update_one(
                    {"_id": user_id},
                    {
                        "$inc": {
                            "eco_points": eco_points,
                            "co2_saved": co2_saved,
                            "clean_trips": 1
                        }
                    }
                )
                
                # Save route
                db.user_routes.insert_one({
                    "user_id": user_id,
                    "start_location": f"{start_lat},{start_lon}",
                    "end_location": f"{end_lat},{end_lon}",
                    "route_type": route_type,
                    "eco_points_earned": eco_points,
                    "created_at": datetime.now()
                })
        
        return jsonify({
            'route': route,
            'eco_points_earned': eco_points,
            'co2_saved': co2_saved,
            'distance_km': round(distance_km, 2),
            'travel_time_min': summary['travelTimeInSeconds'] // 60,
            'route_type': route_type
        })
    
    return jsonify({'error': 'Could not calculate route'}), 400

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """AI chatbot for conversational queries"""
    data = request.json
    message = data.get('message', '')
    
    if not openai_client:
        return jsonify({'response': get_rule_based_response(message)})

    try:
        completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are GeoSense+, a helpful eco-assistant that helps users find clean routes, check air quality, and earn eco-points. Be friendly, factual, and concise.'
                },
                {'role': 'user', 'content': message or 'Hello!'}
            ],
            max_tokens=200,
            temperature=0.7
        )

        if completion and completion.choices:
            response_text = completion.choices[0].message.content.strip()
            if response_text:
                return jsonify({'response': response_text})

        print("Chatbot warning: OpenAI response missing choices or content")
    except Exception as e:
        print(f"Chatbot OpenAI error: {e}")

    return jsonify({'response': get_rule_based_response(message)})

@app.route('/api/community/posts')
def get_community_posts():
    """Get community posts"""
    if not db:
        # Fallback demo data
        return jsonify({
            'posts': [
                {
                    'id': '1',
                    'username': 'demo_user',
                    'title': 'Greenest Route of the Week',
                    'content': 'FC Road morning route has perfect AQI and low traffic!',
                    'location': 'FC Road, Pune',
                    'post_type': 'eco_route',
                    'upvotes': 25,
                    'created_at': datetime.now()
                }
            ]
        })
    
    posts_cursor = db.community_posts.find().sort("created_at", -1).limit(20)
    posts = []
    for post in posts_cursor:
        post['id'] = str(post['_id'])
        if 'user_id' in post and isinstance(post['user_id'], ObjectId):
            post['user_id'] = str(post['user_id'])
        del post['_id']
        posts.append(post)
    
    if not posts:
        # Seed demo posts
        demo_posts = [
            {"username": "demo_user", "title": "Greenest Route of the Week", "content": "FC Road morning route has perfect AQI and low traffic!", "location": "FC Road, Pune", "post_type": "eco_route", "upvotes": random.randint(5, 50)},
            {"username": "eco_warrior", "title": "Avoid FC Road at 6 PM", "content": "Heavy traffic and pollution during evening rush hour", "location": "FC Road, Pune", "post_type": "alert", "upvotes": random.randint(5, 50)},
            {"username": "green_citizen", "title": "Top Eco-Zone Discovery", "content": "Koregaon Park early morning is the best for walks!", "location": "Koregaon Park, Pune", "post_type": "eco_zone", "upvotes": random.randint(5, 50)}
        ]
        
        for post_data in demo_posts:
            post_data['created_at'] = datetime.now()
            db.community_posts.insert_one(post_data)
        
        # Fetch again
        posts_cursor = db.community_posts.find().sort("created_at", -1).limit(20)
        posts = []
        for post in posts_cursor:
            post['id'] = str(post['_id'])
            if 'user_id' in post and isinstance(post['user_id'], ObjectId):
                post['user_id'] = str(post['user_id'])
            del post['_id']
            posts.append(post)
    
    return jsonify({'posts': posts})

@app.route('/api/community/post', methods=['POST'])
def create_post():
    """Create community post"""
    data = request.json
    user = get_or_create_user()
    
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    user_id = ObjectId(user['id']) if isinstance(user['id'], str) and len(user['id']) == 24 else user.get('_id')
    
    post_data = {
        "user_id": user_id,
        "username": user['username'],
        "title": data.get('title'),
        "content": data.get('content'),
        "location": data.get('location'),
        "post_type": data.get('post_type', 'general'),
        "upvotes": 0,
        "created_at": datetime.now()
    }
    
    result = db.community_posts.insert_one(post_data)
    post = db.community_posts.find_one({"_id": result.inserted_id})
    
    post['id'] = str(post['_id'])
    post['user_id'] = str(post['user_id'])
    del post['_id']
    
    return jsonify({'post': post})

@app.route('/api/community/upvote/<post_id>', methods=['POST'])
def upvote_post(post_id):
    """Upvote a community post"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        post_object_id = ObjectId(post_id)
        result = db.community_posts.update_one(
            {"_id": post_object_id},
            {"$inc": {"upvotes": 1}}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/leaderboard')
def leaderboard():
    """Get leaderboard data"""
    if not db:
        # Fallback demo data
        return jsonify({
            'leaderboard': [
                {'username': 'demo_user', 'eco_points': 150, 'green_score': 65, 'co2_saved': 12.5, 'streak_days': 3}
            ]
        })
    
    leaders_cursor = db.users.find(
        {},
        {"username": 1, "eco_points": 1, "green_score": 1, "co2_saved": 1, "streak_days": 1}
    ).sort("eco_points", -1).limit(10)
    
    leaders = []
    for leader in leaders_cursor:
        leader['id'] = str(leader['_id'])
        del leader['_id']
        leaders.append(leader)
    
    return jsonify({'leaderboard': leaders})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
