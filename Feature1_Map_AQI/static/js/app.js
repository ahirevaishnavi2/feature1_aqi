let map;
let currentLat = 18.5204;
let currentLon = 73.8567;
let currentMode = "citizen";
let markers = [];
let trafficLayer;
let trafficIncidentsLayer;

// Initialize the application
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

function initializeApp() {
  // Set up navigation button click handlers
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const sectionName = this.getAttribute("data-section");
      if (sectionName) {
        showSection(sectionName);
      }
    });
  });

  // Set up quick action buttons
  document.querySelectorAll(".action-card[data-section]").forEach((card) => {
    card.addEventListener("click", function () {
      const sectionName = this.getAttribute("data-section");
      if (sectionName) {
        showSection(sectionName);
      }
    });
  });

  // Initialize dashboard
  loadDashboard();

  // Set random AI insight
  const insights = [
    "AI-powered urban intelligence at your fingertips 🧠",
    "Making cities greener, one route at a time 🌿",
    "Your personal eco-assistant for sustainable living 🌍",
  ];
  document.getElementById("main-insight").textContent =
    insights[Math.floor(Math.random() * insights.length)];
}

function showSection(sectionName) {
  console.log("Showing section:", sectionName);

  // Hide all sections
  document
    .querySelectorAll(".section")
    .forEach((s) => s.classList.remove("active"));

  // Remove active class from all nav buttons
  document
    .querySelectorAll(".nav-btn")
    .forEach((b) => b.classList.remove("active"));

  // Show the selected section
  const sectionElement = document.getElementById(`${sectionName}-section`);
  if (sectionElement) {
    sectionElement.classList.add("active");

    // Add active class to corresponding nav button
    document
      .querySelector(`[data-section="${sectionName}"]`)
      .classList.add("active");

    // Handle section-specific initialization
    if (sectionName === "map") {
      setTimeout(() => {
        initMap();
      }, 100);
    } else if (sectionName === "dashboard") {
      loadDashboard();
    } else if (sectionName === "community") {
      loadCommunityPosts();
      loadLeaderboard();
    }
  }
}

function initMap() {
  console.log("initMap called");

  if (typeof tt === "undefined") {
    console.error("TomTom SDK not loaded");
    setTimeout(initMap, 100);
    return;
  }

  const mapContainer = document.getElementById("map");
  if (!mapContainer) {
    console.error("Map container not found");
    return;
  }

  // Clear existing map if it exists
  if (map) {
    map.remove();
    map = null;
  }

  try {
    console.log("Initializing TomTom map...");
    map = tt.map({
      key: TOMTOM_API_KEY || "demo",
      container: "map",
      center: [currentLon, currentLat],
      zoom: 13,
      style: "tomtom://vector/1/basic-main",
    });

    // Add navigation control
    map.addControl(new tt.NavigationControl());

    map.on("load", function () {
      console.log("Map loaded successfully");

      // Initialize traffic layers
      trafficLayer = new tt.TrafficFlow({
        key: TOMTOM_API_KEY || "demo",
      });

      trafficIncidentsLayer = new tt.TrafficIncidents({
        key: TOMTOM_API_KEY || "demo",
      });

      // Add markers
      addMapMarkers();
      updateMapMode();

      // Ensure map is properly sized
      setTimeout(() => {
        if (map) {
          map.resize();
        }
      }, 300);
    });

    map.on("error", function (e) {
      console.error("Map error:", e);
    });
  } catch (error) {
    console.error("Error initializing map:", error);
  }
}

function addMapMarkers() {
  if (!map) return;

  // Clear existing markers
  markers.forEach((m) => m.remove());
  markers = [];

  const zones = [
    {
      lat: 18.5204,
      lon: 73.8567,
      type: "busy",
      name: "FC Road - High Traffic",
      aqi: 120,
      noise: 75,
    },
    {
      lat: 18.5314,
      lon: 73.8446,
      type: "calm",
      name: "Koregaon Park - Calm Zone",
      aqi: 65,
      noise: 45,
    },
    {
      lat: 18.5074,
      lon: 73.8077,
      type: "pollution",
      name: "Industrial Area - High Pollution",
      aqi: 150,
      noise: 80,
    },
    {
      lat: 18.5362,
      lon: 73.897,
      type: "calm",
      name: "Viman Nagar - Low Traffic",
      aqi: 70,
      noise: 50,
    },
  ];

  zones.forEach((zone) => {
    const icon =
      zone.type === "busy" ? "🚗" : zone.type === "calm" ? "🌿" : "😷";

    const el = document.createElement("div");
    el.className = "custom-marker";
    el.innerHTML = `<div style="font-size: 24px; cursor: pointer;">${icon}</div>`;

    const popup = new tt.Popup({ offset: 35 }).setHTML(
      `<div style="padding: 10px;">
                <strong>${zone.name}</strong><br>
                <small>Type: ${zone.type}</small><br>
                ${
                  currentMode === "expert"
                    ? `
                    <small>AQI: ${zone.aqi}</small><br>
                    <small>Noise: ${zone.noise} dB</small>
                `
                    : ""
                }
            </div>`
    );

    const marker = new tt.Marker({ element: el })
      .setLngLat([zone.lon, zone.lat])
      .setPopup(popup)
      .addTo(map);

    markers.push(marker);
  });
}

function updateMapMode() {
  if (!map) return;

  // Clear existing layers
  if (trafficLayer && map.getLayer("traffic-flow")) {
    map.removeLayer("traffic-flow");
    map.removeSource("traffic-flow");
  }

  if (trafficIncidentsLayer && map.getLayer("traffic-incidents")) {
    map.removeLayer("traffic-incidents");
    map.removeSource("traffic-incidents");
  }

  if (currentMode === "expert") {
    const trafficFlowCheckbox = document.querySelector(
      '#expert-legend input[data-layer="traffic-flow"]'
    );
    const trafficIncidentsCheckbox = document.querySelector(
      '#expert-legend input[data-layer="traffic-incidents"]'
    );
    const poiClustersCheckbox = document.querySelector(
      '#expert-legend input[data-layer="poi-clusters"]'
    );

    if (trafficFlowCheckbox && trafficFlowCheckbox.checked) {
      map.addLayer(trafficLayer);
    }

    if (trafficIncidentsCheckbox && trafficIncidentsCheckbox.checked) {
      map.addLayer(trafficIncidentsLayer);
    }

    if (poiClustersCheckbox && !poiClustersCheckbox.checked) {
      markers.forEach((m) => m.remove());
      markers = [];
    } else if (
      poiClustersCheckbox &&
      poiClustersCheckbox.checked &&
      markers.length === 0
    ) {
      addMapMarkers();
    }
  } else {
    // Citizen mode - show basic markers
    if (markers.length === 0) {
      addMapMarkers();
    }
  }
}

// Set up mode toggle buttons
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      document
        .querySelectorAll(".mode-btn")
        .forEach((b) => b.classList.remove("active"));
      this.classList.add("active");

      currentMode = this.dataset.mode;

      if (currentMode === "citizen") {
        document.getElementById("citizen-legend").style.display = "block";
        document.getElementById("expert-legend").style.display = "none";
      } else {
        document.getElementById("citizen-legend").style.display = "none";
        document.getElementById("expert-legend").style.display = "block";
      }

      updateMapMode();
    });
  });

  // Set up expert layer controls
  document
    .querySelectorAll('#expert-legend input[type="checkbox"]')
    .forEach((checkbox) => {
      checkbox.addEventListener("change", updateMapMode);
    });
});

function getCurrentLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        currentLat = position.coords.latitude;
        currentLon = position.coords.longitude;
        document.getElementById("location-input").value = `${currentLat.toFixed(
          4
        )}, ${currentLon.toFixed(4)}`;

        if (map) {
          map.setCenter([currentLon, currentLat]);
          map.setZoom(15);
        }
      },
      (error) => {
        alert("Unable to get your location. Using default location (Pune).");
      }
    );
  } else {
    alert("Geolocation is not supported by your browser.");
  }
}

async function analyzeLocation() {
  const input = document.getElementById("location-input").value;
  const resultsDiv = document.getElementById("analysis-results");
  const contentDiv = document.getElementById("analysis-content");

  if (!input.trim()) {
    alert("Please enter a location or use GPS");
    return;
  }

  // Show loading state
  contentDiv.innerHTML = "<p>Analyzing location...</p>";
  resultsDiv.style.display = "block";

  try {
    // Simulate API call with demo data
    setTimeout(() => {
      const demoData = {
        insight:
          "This area shows moderate traffic patterns with good air quality. Perfect for eco-friendly commuting! 🌿",
        metrics: {
          aqi: 65,
          noise_level: 45,
          traffic_level: 30,
        },
        traffic_pattern: {
          pattern:
            "Low congestion during peak hours, ideal for cycling and walking.",
        },
        locations: [
          {
            name: "Local Park",
            category: "Green Zone",
            zone_type: "calm",
            lat: currentLat + 0.001,
            lon: currentLon + 0.001,
          },
          {
            name: "Main Street",
            category: "Commercial",
            zone_type: "moderate",
            lat: currentLat - 0.001,
            lon: currentLon - 0.001,
          },
        ],
      };
      displayAnalysisResults(demoData);
    }, 1500);
  } catch (error) {
    console.error("Analysis error:", error);
    contentDiv.innerHTML = "<p>Error analyzing location. Please try again.</p>";
  }
}

function displayAnalysisResults(data) {
  const contentDiv = document.getElementById("analysis-content");

  let html = `
        <div class="ai-insight">${data.insight}</div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h4>Air Quality Index</h4>
                <p class="metric-value aqi">${data.metrics.aqi}</p>
            </div>
            <div class="metric-card">
                <h4>Noise Level</h4>
                <p class="metric-value noise">${data.metrics.noise_level} dB</p>
            </div>
            <div class="metric-card">
                <h4>Traffic Level</h4>
                <p class="metric-value traffic">${data.metrics.traffic_level}%</p>
            </div>
        </div>
        
        <h4>Traffic Pattern Analysis</h4>
        <p class="pattern-analysis">${data.traffic_pattern.pattern}</p>
        
        <h4>Nearby Points of Interest</h4>
        <div class="locations-list">
    `;

  data.locations.forEach((loc) => {
    html += `
            <div class="location-item">
                <strong>${loc.name}</strong><br>
                <small>${loc.category} | Zone Type: ${loc.zone_type}</small>
            </div>
        `;
  });

  html += "</div>";
  contentDiv.innerHTML = html;
}

async function loadDashboard() {
  try {
    // Simulate API call with demo data
    const demoData = {
      user: {
        green_score: 85,
        co2_saved: 24.5,
        clean_trips: 12,
        eco_points: 450,
      },
      metrics: {
        aqi: 65,
        noise: 42,
        traffic: 30,
      },
      streak: 7,
      insight: "Great job! You've saved 24.5kg CO₂ this month. 🌍",
      badges: [
        { badge_icon: "🌱", badge_name: "Eco Starter" },
        { badge_icon: "🚶", badge_name: "Walk Warrior" },
        { badge_icon: "⭐", badge_name: "Green Star" },
      ],
    };

    updateGauge("green-score", demoData.user.green_score, 100);
    updateGauge("aqi", demoData.metrics.aqi, 200);
    updateGauge("noise", demoData.metrics.noise, 100);
    updateGauge("traffic", demoData.metrics.traffic, 100);

    document.getElementById(
      "co2-saved"
    ).textContent = `${demoData.user.co2_saved} kg`;
    document.getElementById("clean-trips").textContent =
      demoData.user.clean_trips;
    document.getElementById(
      "eco-streak"
    ).textContent = `${demoData.streak} days`;
    document.getElementById("eco-points").textContent =
      demoData.user.eco_points;

    const badgesContainer = document.getElementById("badges-container");
    badgesContainer.innerHTML = demoData.badges
      .map(
        (badge) => `
                <div class="badge-item">
                    <div class="badge-icon">${badge.badge_icon}</div>
                    <div>${badge.badge_name}</div>
                </div>
            `
      )
      .join("");
  } catch (error) {
    console.error("Dashboard error:", error);
  }
}

function updateGauge(id, value, max) {
  const percentage = Math.min(value / max, 1);
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - percentage * circumference;

  const gauge = document.getElementById(`${id}-gauge`);
  const text = document.getElementById(`${id}-text`);

  if (gauge) {
    gauge.style.strokeDasharray = circumference;
    gauge.style.strokeDashoffset = offset;
  }
  if (text) {
    text.textContent = Math.round(value);
  }
}

function toggleChatbot() {
  const chatbot = document.getElementById("chatbot-window");
  chatbot.style.display = chatbot.style.display === "none" ? "flex" : "none";
}

async function sendChatMessage() {
  const input = document.getElementById("chatbot-input");
  const message = input.value.trim();

  if (!message) return;

  const messagesDiv = document.getElementById("chatbot-messages");

  // Add user message
  messagesDiv.innerHTML += `<div class="user-message">${message}</div>`;
  input.value = "";

  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  try {
    // Simulate bot response
    setTimeout(() => {
      const responses = [
        "I can help you find eco-friendly routes and analyze air quality in your area!",
        "Based on current traffic patterns, I recommend taking the bike path for your commute.",
        "Your carbon footprint is looking great this week! Keep up the good work. 🌿",
      ];
      const response = responses[Math.floor(Math.random() * responses.length)];

      messagesDiv.innerHTML += `<div class="bot-message">${response}</div>`;
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }, 1000);
  } catch (error) {
    console.error("Chatbot error:", error);
    messagesDiv.innerHTML += `<div class="bot-message">Sorry, I'm having trouble right now. Please try again!</div>`;
  }
}

function showRouteModal() {
  document.getElementById("route-modal").style.display = "block";
}

function closeRouteModal() {
  document.getElementById("route-modal").style.display = "none";
}

async function planRoute() {
  const startLoc = document.getElementById("start-location").value;
  const endLoc = document.getElementById("end-location").value;
  const routeType = document.querySelector(
    'input[name="route-type"]:checked'
  ).value;

  if (!endLoc) {
    alert("Please enter a destination");
    return;
  }

  const resultsDiv = document.getElementById("route-results");
  resultsDiv.innerHTML = "<p>Planning your route...</p>";

  try {
    // Simulate route planning
    setTimeout(() => {
      const demoRoute = {
        distance_km: 5.2,
        travel_time_min: 15,
        route_type: routeType,
        eco_points_earned: 25,
        co2_saved: 1.2,
      };

      resultsDiv.innerHTML = `
                <div class="route-success">
                    <h3>🎉 Route Planned Successfully!</h3>
                    <p><strong>Distance:</strong> ${
                      demoRoute.distance_km
                    } km</p>
                    <p><strong>Travel Time:</strong> ${
                      demoRoute.travel_time_min
                    } minutes</p>
                    <p><strong>Route Type:</strong> ${
                      demoRoute.route_type === "eco"
                        ? "Eco-Friendly 🌿"
                        : "Fastest ⚡"
                    }</p>
                    <p><strong>Eco Points Earned:</strong> +${
                      demoRoute.eco_points_earned
                    } points</p>
                    ${
                      demoRoute.co2_saved > 0
                        ? `<p><strong>CO₂ Saved:</strong> ${demoRoute.co2_saved} kg 🌍</p>`
                        : ""
                    }
                    <div class="eco-banner">
                        🏅 Great choice! You're making a positive impact!
                    </div>
                </div>
            `;

      // Show the route on map if available
      if (map) {
        showSection("map");
      }
    }, 2000);
  } catch (error) {
    console.error("Route planning error:", error);
    resultsDiv.innerHTML = "<p>Failed to plan route. Please try again.</p>";
  }
}

async function loadCommunityPosts() {
  try {
    // Simulate community posts
    const demoPosts = {
      posts: [
        {
          id: 1,
          title: "Great bike path discovered!",
          content:
            "Found an amazing new bike path that avoids all the traffic. Highly recommended!",
          location: "Downtown",
          username: "EcoRider",
          post_type: "eco_route",
          upvotes: 12,
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          title: "Air quality improving",
          content:
            "Noticed significant improvement in air quality near the park after the new green initiative.",
          location: "Central Park",
          username: "GreenObserver",
          post_type: "eco_zone",
          upvotes: 8,
          created_at: new Date().toISOString(),
        },
      ],
    };

    const feedDiv = document.getElementById("community-feed");
    feedDiv.innerHTML = demoPosts.posts
      .map(
        (post) => `
                <div class="post-item">
                    <div class="post-header">
                        <div class="post-title">${post.title}</div>
                        <span class="post-type-badge">${post.post_type.replace(
                          "_",
                          " "
                        )}</span>
                    </div>
                    <p>${post.content}</p>
                    <div class="post-meta">
                        📍 ${post.location} | 👤 ${post.username} | 
                        ${new Date(post.created_at).toLocaleDateString()}
                    </div>
                    <button class="upvote-btn" onclick="upvotePost(${post.id})">
                        👍 Upvote (${post.upvotes})
                    </button>
                </div>
            `
      )
      .join("");
  } catch (error) {
    console.error("Error loading posts:", error);
  }
}

async function loadLeaderboard() {
  try {
    // Simulate leaderboard data
    const demoLeaderboard = {
      leaderboard: [
        {
          username: "EcoChampion",
          eco_points: 1250,
          co2_saved: 45.2,
          green_score: 95,
          streak_days: 21,
        },
        {
          username: "GreenCommuter",
          eco_points: 980,
          co2_saved: 32.7,
          green_score: 88,
          streak_days: 14,
        },
        {
          username: "SustainableSarah",
          eco_points: 750,
          co2_saved: 28.1,
          green_score: 82,
          streak_days: 9,
        },
      ],
    };

    const leaderboardDiv = document.getElementById("leaderboard-list");
    leaderboardDiv.innerHTML = demoLeaderboard.leaderboard
      .map(
        (user, index) => `
                <div class="leaderboard-item">
                    <span class="rank">${
                      index === 0
                        ? "🥇"
                        : index === 1
                        ? "🥈"
                        : index === 2
                        ? "🥉"
                        : index + 1
                    }</span>
                    <div class="user-info">
                        <strong>${user.username}</strong><br>
                        <small>${user.eco_points} points | ${
          user.co2_saved
        } kg CO₂ saved</small>
                    </div>
                    <div class="user-stats">
                        <div>Green Score: ${user.green_score}</div>
                        <small>${user.streak_days} day streak</small>
                    </div>
                </div>
            `
      )
      .join("");
  } catch (error) {
    console.error("Error loading leaderboard:", error);
  }
}

function showPostModal() {
  document.getElementById("post-modal").style.display = "block";
}

function closePostModal() {
  document.getElementById("post-modal").style.display = "none";
}

async function submitPost() {
  const title = document.getElementById("post-title").value;
  const content = document.getElementById("post-content").value;
  const location = document.getElementById("post-location").value;
  const postType = document.getElementById("post-type").value;

  if (!title || !content || !location) {
    alert("Please fill in all fields");
    return;
  }

  try {
    // Simulate post submission
    console.log("Submitting post:", { title, content, location, postType });

    closePostModal();
    loadCommunityPosts();

    // Clear form
    document.getElementById("post-title").value = "";
    document.getElementById("post-content").value = "";
    document.getElementById("post-location").value = "";
  } catch (error) {
    console.error("Error creating post:", error);
    alert("Failed to create post. Please try again.");
  }
}

async function upvotePost(postId) {
  try {
    console.log("Upvoting post:", postId);
    // In a real app, this would make an API call
    loadCommunityPosts(); // Refresh to show updated counts
  } catch (error) {
    console.error("Error upvoting:", error);
  }
}

// Close modals when clicking outside
window.onclick = function (event) {
  const routeModal = document.getElementById("route-modal");
  const postModal = document.getElementById("post-modal");

  if (event.target === routeModal) {
    closeRouteModal();
  }
  if (event.target === postModal) {
    closePostModal();
  }
};
