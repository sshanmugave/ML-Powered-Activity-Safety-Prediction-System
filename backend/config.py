"""
SafeTravel - Configuration & Constants
"""

import os

# ─── API Keys ───────────────────────────────────────────────
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "121ce07e8b925ab65aba5b6b5e8fb078")

# ─── Model Paths ────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

RF_MODEL_PATH = os.path.join(MODEL_DIR, "safety_model_rf.pkl")
XGB_MODEL_PATH = os.path.join(MODEL_DIR, "safety_model_xgb.pkl")
ENCODERS_PATH = os.path.join(MODEL_DIR, "label_encoders.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.json")

TRAINING_DATA_PATH = os.path.join(DATA_DIR, "training_data.csv")
FEATURE_IMPORTANCE_PATH = os.path.join(DATA_DIR, "feature_importance.png")
CONFUSION_MATRIX_PATH = os.path.join(DATA_DIR, "confusion_matrix.png")

# ─── Activities ─────────────────────────────────────────────
ACTIVITIES = {
    "jogging": {
        "label": "Jogging / Running",
        "icon": "🏃",
        "is_outdoor": True,
        "exertion_level": 0.9,       # high breathing = very sensitive to AQI
        "pollution_sensitivity": 0.95,
        "weather_sensitivity": 0.8,
        "crowd_sensitivity": 0.3,
        "uv_sensitivity": 0.7,
        "heat_sensitivity": 0.9,
        "description": "Running or jogging in open air"
    },
    "family_outing": {
        "label": "Family Outing",
        "icon": "👨‍👩‍👧‍👦",
        "is_outdoor": True,
        "exertion_level": 0.3,
        "pollution_sensitivity": 0.7,
        "weather_sensitivity": 0.85,
        "crowd_sensitivity": 0.6,
        "uv_sensitivity": 0.6,
        "heat_sensitivity": 0.7,
        "description": "Casual outing with family members"
    },
    "temple_visit": {
        "label": "Temple / Worship",
        "icon": "🛕",
        "is_outdoor": False,
        "exertion_level": 0.2,
        "pollution_sensitivity": 0.4,
        "weather_sensitivity": 0.6,
        "crowd_sensitivity": 0.8,
        "uv_sensitivity": 0.3,
        "heat_sensitivity": 0.5,
        "description": "Visiting a temple or place of worship"
    },
    "photography": {
        "label": "Photography",
        "icon": "📸",
        "is_outdoor": True,
        "exertion_level": 0.2,
        "pollution_sensitivity": 0.3,
        "weather_sensitivity": 0.7,
        "crowd_sensitivity": 0.5,
        "uv_sensitivity": 0.5,
        "heat_sensitivity": 0.4,
        "description": "Outdoor photography or sightseeing with camera"
    },
    "cycling": {
        "label": "Cycling",
        "icon": "🚴",
        "is_outdoor": True,
        "exertion_level": 0.85,
        "pollution_sensitivity": 0.9,
        "weather_sensitivity": 0.85,
        "crowd_sensitivity": 0.4,
        "uv_sensitivity": 0.7,
        "heat_sensitivity": 0.85,
        "description": "Cycling outdoors"
    },
    "picnic": {
        "label": "Picnic",
        "icon": "🧺",
        "is_outdoor": True,
        "exertion_level": 0.1,
        "pollution_sensitivity": 0.6,
        "weather_sensitivity": 0.95,
        "crowd_sensitivity": 0.5,
        "uv_sensitivity": 0.7,
        "heat_sensitivity": 0.7,
        "description": "Outdoor picnic at a park or garden"
    },
    "water_sport": {
        "label": "Water Sport / Swimming",
        "icon": "🏊",
        "is_outdoor": True,
        "exertion_level": 0.7,
        "pollution_sensitivity": 0.4,
        "weather_sensitivity": 0.9,
        "crowd_sensitivity": 0.3,
        "uv_sensitivity": 0.85,
        "heat_sensitivity": 0.3,
        "description": "Swimming, boating, or water sports"
    },
    "shopping": {
        "label": "Shopping / Market Visit",
        "icon": "🛍️",
        "is_outdoor": False,
        "exertion_level": 0.2,
        "pollution_sensitivity": 0.3,
        "weather_sensitivity": 0.4,
        "crowd_sensitivity": 0.9,
        "uv_sensitivity": 0.2,
        "heat_sensitivity": 0.4,
        "description": "Visiting markets or shopping areas"
    },
    "sightseeing": {
        "label": "Sightseeing / Tourism",
        "icon": "🏛️",
        "is_outdoor": True,
        "exertion_level": 0.4,
        "pollution_sensitivity": 0.5,
        "weather_sensitivity": 0.7,
        "crowd_sensitivity": 0.6,
        "uv_sensitivity": 0.6,
        "heat_sensitivity": 0.6,
        "description": "Visiting monuments, landmarks, or tourist spots"
    },
    "trekking": {
        "label": "Trekking / Hiking",
        "icon": "🥾",
        "is_outdoor": True,
        "exertion_level": 0.95,
        "pollution_sensitivity": 0.8,
        "weather_sensitivity": 0.9,
        "crowd_sensitivity": 0.2,
        "uv_sensitivity": 0.8,
        "heat_sensitivity": 0.95,
        "description": "Hiking or trekking on trails"
    }
}

# ─── Place Types ────────────────────────────────────────────
PLACE_TYPES = {
    "park": {"label": "Park / Garden", "icon": "🌳", "outdoor_factor": 1.0, "crowd_base": 0.5},
    "lake": {"label": "Lake / Water Body", "icon": "🏞️", "outdoor_factor": 1.0, "crowd_base": 0.4},
    "temple": {"label": "Temple / Religious", "icon": "🛕", "outdoor_factor": 0.5, "crowd_base": 0.7},
    "market": {"label": "Market / Bazaar", "icon": "🏪", "outdoor_factor": 0.6, "crowd_base": 0.8},
    "beach": {"label": "Beach", "icon": "🏖️", "outdoor_factor": 1.0, "crowd_base": 0.5},
    "hill": {"label": "Hill / Mountain", "icon": "⛰️", "outdoor_factor": 1.0, "crowd_base": 0.2},
    "monument": {"label": "Monument / Heritage", "icon": "🏛️", "outdoor_factor": 0.8, "crowd_base": 0.6},
    "mall": {"label": "Mall / Shopping Center", "icon": "🏬", "outdoor_factor": 0.1, "crowd_base": 0.7},
    "garden": {"label": "Botanical Garden", "icon": "🌺", "outdoor_factor": 0.9, "crowd_base": 0.4},
    "riverside": {"label": "Riverside / Ghat", "icon": "🌊", "outdoor_factor": 1.0, "crowd_base": 0.5},
    "zoo": {"label": "Zoo / Wildlife Park", "icon": "🦁", "outdoor_factor": 0.9, "crowd_base": 0.5},
    "stadium": {"label": "Stadium / Sports Ground", "icon": "🏟️", "outdoor_factor": 0.8, "crowd_base": 0.4},
    "other": {"label": "Other", "icon": "📍", "outdoor_factor": 0.7, "crowd_base": 0.5}
}

# ─── Medical Conditions ────────────────────────────────────
MEDICAL_CONDITIONS = {
    "none": {
        "label": "No Medical Conditions",
        "icon": "💪",
        "aqi_multiplier": 1.0,
        "heat_multiplier": 1.0,
        "uv_multiplier": 1.0,
        "humidity_multiplier": 1.0,
        "exertion_multiplier": 1.0,
        "tips": []
    },
    "asthma": {
        "label": "Asthma",
        "icon": "🫁",
        "aqi_multiplier": 2.5,       # very sensitive to AQI
        "heat_multiplier": 1.3,
        "uv_multiplier": 1.0,
        "humidity_multiplier": 1.5,
        "exertion_multiplier": 1.8,
        "tips": [
            "Always carry your inhaler",
            "Avoid areas with heavy traffic or industrial emissions",
            "Prefer early morning hours when air is cleanest",
            "Wear a proper N95/N99 mask if AQI is moderate or above",
            "Stay hydrated to keep airways moist"
        ]
    },
    "heart_disease": {
        "label": "Heart Disease",
        "icon": "❤️‍🩹",
        "aqi_multiplier": 1.8,
        "heat_multiplier": 2.0,      # very sensitive to heat
        "uv_multiplier": 1.2,
        "humidity_multiplier": 1.6,
        "exertion_multiplier": 2.0,
        "tips": [
            "Avoid strenuous activities in extreme temperatures",
            "Carry prescribed medication at all times",
            "Take frequent rest breaks",
            "Avoid midday heat (11 AM - 3 PM)",
            "Keep emergency contact numbers handy"
        ]
    },
    "allergies": {
        "label": "Allergies (Pollen/Dust)",
        "icon": "🤧",
        "aqi_multiplier": 1.8,
        "heat_multiplier": 1.0,
        "uv_multiplier": 1.0,
        "humidity_multiplier": 1.3,
        "exertion_multiplier": 1.3,
        "tips": [
            "Take antihistamines before going outdoors",
            "Wear sunglasses to protect eyes from pollen",
            "Avoid parks/gardens during high pollen seasons (Feb-Apr, Sep-Nov)",
            "Shower after returning from outdoor activities",
            "Check pollen count if available for your area"
        ]
    },
    "skin_sensitivity": {
        "label": "Skin Sensitivity / Dermatitis",
        "icon": "🧴",
        "aqi_multiplier": 1.1,
        "heat_multiplier": 1.4,
        "uv_multiplier": 2.5,        # very sensitive to UV
        "humidity_multiplier": 1.3,
        "exertion_multiplier": 1.0,
        "tips": [
            "Apply SPF 50+ sunscreen 30 minutes before going out",
            "Wear long sleeves and a wide-brimmed hat",
            "Avoid direct sun exposure between 10 AM - 4 PM",
            "Carry an umbrella for shade",
            "Reapply sunscreen every 2 hours"
        ]
    },
    "elderly": {
        "label": "Elderly (60+ years)",
        "icon": "👴",
        "aqi_multiplier": 1.6,
        "heat_multiplier": 1.8,
        "uv_multiplier": 1.4,
        "humidity_multiplier": 1.5,
        "exertion_multiplier": 1.7,
        "tips": [
            "Avoid extreme temperatures (both hot and cold)",
            "Stay well-hydrated throughout the visit",
            "Choose shaded paths and rest frequently",
            "Wear comfortable, non-slip footwear",
            "Avoid crowded places during peak hours"
        ]
    },
    "pregnancy": {
        "label": "Pregnancy",
        "icon": "🤰",
        "aqi_multiplier": 2.0,
        "heat_multiplier": 1.8,
        "uv_multiplier": 1.3,
        "humidity_multiplier": 1.5,
        "exertion_multiplier": 2.0,
        "tips": [
            "Avoid high-pollution areas completely",
            "Stay hydrated and carry snacks",
            "Avoid standing for long periods",
            "Choose cool, shaded, and well-ventilated places",
            "Avoid overcrowded places"
        ]
    },
    "respiratory": {
        "label": "Respiratory Issues (COPD/Bronchitis)",
        "icon": "😮‍💨",
        "aqi_multiplier": 2.8,
        "heat_multiplier": 1.4,
        "uv_multiplier": 1.0,
        "humidity_multiplier": 1.6,
        "exertion_multiplier": 2.2,
        "tips": [
            "Wear N95/N99 mask at all times outdoors",
            "Avoid smoky areas, construction zones, and traffic",
            "Carry prescribed bronchodilator/inhaler",
            "Check real-time AQI before stepping out",
            "Prefer indoor or well-ventilated activities"
        ]
    },
    "diabetes": {
        "label": "Diabetes",
        "icon": "💉",
        "aqi_multiplier": 1.2,
        "heat_multiplier": 1.6,
        "uv_multiplier": 1.1,
        "humidity_multiplier": 1.3,
        "exertion_multiplier": 1.4,
        "tips": [
            "Carry glucose tablets or sugary snacks",
            "Stay hydrated to avoid dehydration",
            "Wear comfortable footwear to prevent foot injuries",
            "Monitor blood sugar more frequently during outings",
            "Avoid extreme heat—it can affect insulin absorption"
        ]
    }
}

# ─── Safety Labels ──────────────────────────────────────────
SAFETY_LABELS = {
    0: {"label": "Unsafe", "color": "#ef4444", "emoji": "🔴", "message": "Not recommended to visit now"},
    1: {"label": "Risky", "color": "#f97316", "emoji": "🟠", "message": "Visit with high caution"},
    2: {"label": "Moderate", "color": "#eab308", "emoji": "🟡", "message": "Visit with some precautions"},
    3: {"label": "Safe", "color": "#22c55e", "emoji": "🟢", "message": "Great time to visit!"}
}

# ─── Health Tips by Factor ──────────────────────────────────
HEALTH_TIPS = {
    "high_aqi": [
        "Wear an N95 mask to filter pollutants",
        "Avoid prolonged outdoor exposure",
        "Keep windows closed when back indoors",
        "Stay hydrated to help flush toxins"
    ],
    "high_temp": [
        "Carry plenty of water and stay hydrated",
        "Wear light, breathable cotton clothing",
        "Apply sunscreen (SPF 30+) before going out",
        "Take breaks in shaded areas every 20-30 minutes"
    ],
    "low_temp": [
        "Dress in warm layers",
        "Carry a hot beverage if possible",
        "Protect extremities (gloves, warm socks, ear covers)",
        "Avoid prolonged exposure to cold winds"
    ],
    "high_uv": [
        "Apply SPF 50+ sunscreen, reapply every 2 hours",
        "Wear UV-protective sunglasses",
        "Use an umbrella or hat for shade",
        "Avoid direct sun between 10 AM - 4 PM"
    ],
    "rain": [
        "Carry a waterproof jacket or umbrella",
        "Wear non-slip footwear",
        "Be cautious of slippery surfaces",
        "Watch out for waterlogging in low areas"
    ],
    "storm": [
        "Seek immediate indoor shelter",
        "Stay away from trees and tall structures",
        "Avoid water bodies during thunderstorms",
        "Do not use umbrellas with metal tips"
    ],
    "high_crowd": [
        "Visit during off-peak hours for a better experience",
        "Keep valuables secure in crowded areas",
        "Maintain hydration in crowded, hot conditions",
        "Have a meeting point plan if visiting with a group"
    ],
    "high_humidity": [
        "Wear moisture-wicking fabrics",
        "Stay hydrated—you lose more fluids in humid conditions",
        "Take frequent breaks to cool down",
        "Carry a small towel or handkerchief"
    ],
    "fog": [
        "Drive carefully with fog lights on if traveling",
        "Wear bright or reflective clothing",
        "Be extra cautious near water bodies",
        "Visibility may be poor—stay on marked paths"
    ]
}

# ─── Weather Code Mapping ───────────────────────────────────
WEATHER_CATEGORIES = {
    "clear": [800],
    "clouds": [801, 802, 803, 804],
    "rain_light": [300, 301, 310, 311, 500, 501],
    "rain_heavy": [302, 312, 313, 314, 321, 502, 503, 504, 511, 520, 521, 522, 531],
    "storm": [200, 201, 202, 210, 211, 212, 221, 230, 231, 232],
    "snow": [600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622],
    "fog": [701, 711, 721, 731, 741, 751, 761, 762, 771, 781]
}

def get_weather_category(weather_id):
    """Map OpenWeatherMap weather ID to our category."""
    for category, ids in WEATHER_CATEGORIES.items():
        if weather_id in ids:
            return category
    return "clear"

# ─── Feature Names (for model) ──────────────────────────────
FEATURE_NAMES = [
    'temperature', 'humidity', 'wind_speed', 'visibility',
    'weather_encoded', 'aqi', 'pm25', 'pm10',
    'uv_estimate', 'hour_of_day', 'day_of_week', 'month',
    'is_weekend', 'activity_encoded', 'place_encoded',
    'is_outdoor', 'exertion_level',
    'pollution_sensitivity', 'weather_sensitivity',
    'crowd_sensitivity', 'uv_sensitivity', 'heat_sensitivity',
    'crowd_estimate',
    'medical_aqi_multiplier', 'medical_heat_multiplier',
    'medical_uv_multiplier', 'medical_humidity_multiplier',
    'medical_exertion_multiplier'
]
