"""
SafeTravel - Safety Engine
Feature engineering and ML model prediction interface.
"""

import numpy as np
import joblib
import os
import math
from datetime import datetime

from config import (
    ACTIVITIES, PLACE_TYPES, MEDICAL_CONDITIONS,
    FEATURE_NAMES, SAFETY_LABELS, HEALTH_TIPS,
    RF_MODEL_PATH, XGB_MODEL_PATH, SCALER_PATH, METRICS_PATH,
    get_weather_category
)


class SafetyEngine:
    """ML-powered safety prediction engine."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_name = "random_forest"
        self._load_models()
    
    def _load_models(self):
        """Load trained models and scaler."""
        try:
            if os.path.exists(RF_MODEL_PATH):
                self.model = joblib.load(RF_MODEL_PATH)
                self.model_name = "random_forest"
                print("✅ Loaded Random Forest model")
            
            # Try XGBoost (if it's better)
            if os.path.exists(METRICS_PATH):
                import json
                with open(METRICS_PATH) as f:
                    metrics = json.load(f)
                if metrics.get('best_model') == 'xgboost' and os.path.exists(XGB_MODEL_PATH):
                    self.model = joblib.load(XGB_MODEL_PATH)
                    self.model_name = "xgboost"
                    print("✅ Loaded XGBoost model (best)")
            
            if os.path.exists(SCALER_PATH):
                self.scaler = joblib.load(SCALER_PATH)
                print("✅ Loaded feature scaler")
            
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            self.model = None
            self.scaler = None
    
    def estimate_uv(self, hour, month, latitude, cloud_cover_pct):
        """Estimate UV index from location, time, and cloud cover."""
        if hour < 6 or hour > 19:
            return 0.0
        
        solar_factor = max(0, math.sin(math.pi * (hour - 6) / 13))
        seasonal = 1.0 + 0.3 * math.sin(2 * math.pi * (month - 3) / 12)
        lat_factor = 1.0 + 0.2 * (30 - min(latitude, 40)) / 30
        cloud_factor = 1.0 - (cloud_cover_pct / 100) * 0.6
        
        uv = 12 * solar_factor * seasonal * lat_factor * cloud_factor
        return round(max(0, min(uv, 14)), 1)
    
    def estimate_crowd(self, hour, day_of_week, place_type, is_weekend):
        """Estimate crowd level (0-1)."""
        base = PLACE_TYPES.get(place_type, PLACE_TYPES["other"])["crowd_base"]
        
        if 6 <= hour <= 8:
            time_factor = 0.4
        elif 9 <= hour <= 11:
            time_factor = 0.7
        elif 12 <= hour <= 14:
            time_factor = 0.6
        elif 15 <= hour <= 18:
            time_factor = 0.9
        elif 19 <= hour <= 21:
            time_factor = 0.8
        else:
            time_factor = 0.2
        
        weekend_mult = 1.4 if is_weekend else 1.0
        
        if place_type == "temple" and day_of_week in [1, 4, 5]:
            weekend_mult *= 1.2
        if place_type == "market" and 17 <= hour <= 21:
            time_factor = 1.0
        
        return round(min(base * time_factor * weekend_mult, 1.0), 2)
    
    def engineer_features(self, weather_data, aqi_data, activity_key, place_type,
                          medical_key, target_datetime, latitude=25.0):
        """
        Transform raw API data into model features.
        
        Args:
            weather_data: dict from OpenWeatherMap weather API
            aqi_data: dict from OpenWeatherMap air pollution API
            activity_key: str key from ACTIVITIES
            place_type: str key from PLACE_TYPES
            medical_key: str key from MEDICAL_CONDITIONS
            target_datetime: datetime object
            latitude: float
        
        Returns:
            numpy array of features in correct order
        """
        activity = ACTIVITIES.get(activity_key, ACTIVITIES["sightseeing"])
        medical = MEDICAL_CONDITIONS.get(medical_key, MEDICAL_CONDITIONS["none"])
        
        # Extract weather data
        temp = weather_data.get('main', {}).get('temp', 25)
        humidity = weather_data.get('main', {}).get('humidity', 50)
        wind_speed = weather_data.get('wind', {}).get('speed', 2)
        visibility = weather_data.get('visibility', 10000)
        clouds = weather_data.get('clouds', {}).get('all', 0)
        
        # Weather category
        weather_id = weather_data.get('weather', [{}])[0].get('id', 800)
        weather_cat = get_weather_category(weather_id)
        weather_encode_map = {
            "clear": 0, "clouds": 1, "rain_light": 2,
            "rain_heavy": 3, "storm": 4, "snow": 5, "fog": 6
        }
        weather_encoded = weather_encode_map.get(weather_cat, 0)
        
        # AQI data
        aqi_val = aqi_data.get('list', [{}])[0].get('main', {}).get('aqi', 2)
        components = aqi_data.get('list', [{}])[0].get('components', {})
        pm25 = components.get('pm2_5', 20)
        pm10 = components.get('pm10', 30)
        
        # Time features
        hour = target_datetime.hour
        day_of_week = target_datetime.weekday()
        month = target_datetime.month
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Derived features
        uv_estimate = self.estimate_uv(hour, month, latitude, clouds)
        crowd_estimate = self.estimate_crowd(hour, day_of_week, place_type, is_weekend)
        
        # Activity encoding
        activity_keys = list(ACTIVITIES.keys())
        activity_encoded = activity_keys.index(activity_key) if activity_key in activity_keys else 0
        
        # Place encoding
        place_keys = list(PLACE_TYPES.keys())
        place_encoded = place_keys.index(place_type) if place_type in place_keys else 12
        
        # Build feature vector in exact order
        features = np.array([
            temp,                               # temperature
            humidity,                            # humidity
            wind_speed,                          # wind_speed
            visibility,                          # visibility
            weather_encoded,                     # weather_encoded
            aqi_val,                            # aqi
            pm25,                               # pm25
            pm10,                               # pm10
            uv_estimate,                        # uv_estimate
            hour,                               # hour_of_day
            day_of_week,                        # day_of_week
            month,                              # month
            is_weekend,                         # is_weekend
            activity_encoded,                   # activity_encoded
            place_encoded,                      # place_encoded
            1 if activity["is_outdoor"] else 0, # is_outdoor
            activity["exertion_level"],         # exertion_level
            activity["pollution_sensitivity"],  # pollution_sensitivity
            activity["weather_sensitivity"],    # weather_sensitivity
            activity["crowd_sensitivity"],      # crowd_sensitivity
            activity["uv_sensitivity"],         # uv_sensitivity
            activity["heat_sensitivity"],       # heat_sensitivity
            crowd_estimate,                     # crowd_estimate
            medical["aqi_multiplier"],          # medical_aqi_multiplier
            medical["heat_multiplier"],         # medical_heat_multiplier
            medical["uv_multiplier"],           # medical_uv_multiplier
            medical["humidity_multiplier"],     # medical_humidity_multiplier
            medical["exertion_multiplier"],     # medical_exertion_multiplier
        ]).reshape(1, -1)
        
        # Additional info for response
        factor_details = {
            'temperature': temp,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'visibility': visibility,
            'weather_category': weather_cat,
            'weather_description': weather_data.get('weather', [{}])[0].get('description', 'N/A'),
            'weather_icon': weather_data.get('weather', [{}])[0].get('icon', '01d'),
            'aqi': aqi_val,
            'pm25': pm25,
            'pm10': pm10,
            'uv_estimate': uv_estimate,
            'crowd_estimate': crowd_estimate,
            'hour': hour,
            'clouds': clouds
        }
        
        return features, factor_details
    
    def predict(self, features):
        """
        Run ML model prediction.
        
        Args:
            features: numpy array of shape (1, n_features)
        
        Returns:
            dict with prediction, confidence, probabilities
        """
        if self.model is None:
            return {
                'label': 2,
                'label_name': 'Moderate',
                'confidence': 0.5,
                'probabilities': [0.1, 0.2, 0.4, 0.3],
                'score': 60,
                'model_loaded': False
            }
        
        # Scale features
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features)
        else:
            features_scaled = features
        
        # Predict
        prediction = int(self.model.predict(features_scaled)[0])
        probabilities = self.model.predict_proba(features_scaled)[0].tolist()
        confidence = max(probabilities)
        
        # Convert to safety score (0-100)
        # Weighted average of class probabilities
        score = (
            probabilities[0] * 10 +   # Unsafe → 10
            probabilities[1] * 35 +   # Risky → 35
            probabilities[2] * 65 +   # Moderate → 65
            probabilities[3] * 95     # Safe → 95
        )
        
        return {
            'label': prediction,
            'label_name': SAFETY_LABELS[prediction]['label'],
            'color': SAFETY_LABELS[prediction]['color'],
            'emoji': SAFETY_LABELS[prediction]['emoji'],
            'message': SAFETY_LABELS[prediction]['message'],
            'confidence': round(confidence, 3),
            'probabilities': {
                'unsafe': round(probabilities[0], 3),
                'risky': round(probabilities[1], 3),
                'moderate': round(probabilities[2], 3),
                'safe': round(probabilities[3], 3)
            },
            'score': round(score, 1),
            'model_name': self.model_name,
            'model_loaded': True
        }
    
    def generate_health_tips(self, factor_details, activity_key, medical_key):
        """Generate contextual health tips based on conditions."""
        tips = []
        
        aqi = factor_details['aqi']
        temp = factor_details['temperature']
        weather = factor_details['weather_category']
        uv = factor_details['uv_estimate']
        crowd = factor_details['crowd_estimate']
        humidity = factor_details['humidity']
        visibility = factor_details.get('visibility', 10000)
        
        # AQI tips
        if aqi >= 3:
            tips.extend(HEALTH_TIPS['high_aqi'][:2])
        
        # Temperature tips
        if temp > 35:
            tips.extend(HEALTH_TIPS['high_temp'][:2])
        elif temp < 10:
            tips.extend(HEALTH_TIPS['low_temp'][:2])
        
        # UV tips
        if uv > 5:
            tips.extend(HEALTH_TIPS['high_uv'][:2])
        
        # Weather tips
        if weather in ['rain_light', 'rain_heavy']:
            tips.extend(HEALTH_TIPS['rain'][:2])
        elif weather == 'storm':
            tips.extend(HEALTH_TIPS['storm'][:2])
        elif weather == 'fog':
            tips.extend(HEALTH_TIPS['fog'][:2])
        
        # Crowd tips
        if crowd > 0.7:
            tips.extend(HEALTH_TIPS['high_crowd'][:2])
        
        # Humidity tips
        if humidity > 80:
            tips.extend(HEALTH_TIPS['high_humidity'][:2])
        
        # Medical condition tips
        medical = MEDICAL_CONDITIONS.get(medical_key, MEDICAL_CONDITIONS["none"])
        if medical_key != "none" and medical.get('tips'):
            tips.extend(medical['tips'][:3])
        
        # Deduplicate and limit
        seen = set()
        unique_tips = []
        for tip in tips:
            if tip not in seen:
                seen.add(tip)
                unique_tips.append(tip)
        
        return unique_tips[:8]  # Max 8 tips
    
    def get_factor_scores(self, factor_details):
        """Calculate individual factor scores for the UI breakdown."""
        scores = {}
        
        # AQI score (1=best, 5=worst)
        aqi = factor_details['aqi']
        aqi_scores = {1: 95, 2: 75, 3: 50, 4: 25, 5: 5}
        scores['aqi'] = {
            'score': aqi_scores.get(aqi, 50),
            'value': aqi,
            'label': ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'][aqi - 1],
            'pm25': round(factor_details['pm25'], 1),
            'pm10': round(factor_details['pm10'], 1)
        }
        
        # Temperature score
        temp = factor_details['temperature']
        if 20 <= temp <= 30:
            temp_score = 95
        elif 15 <= temp < 20 or 30 < temp <= 35:
            temp_score = 70
        elif 10 <= temp < 15 or 35 < temp <= 40:
            temp_score = 45
        elif 5 <= temp < 10 or 40 < temp <= 45:
            temp_score = 20
        else:
            temp_score = 5
        scores['temperature'] = {
            'score': temp_score,
            'value': round(temp, 1),
            'label': f"{round(temp, 1)}°C"
        }
        
        # Weather score
        weather_scores = {
            'clear': 95, 'clouds': 80, 'rain_light': 50,
            'rain_heavy': 20, 'storm': 5, 'snow': 30, 'fog': 40
        }
        weather = factor_details['weather_category']
        scores['weather'] = {
            'score': weather_scores.get(weather, 60),
            'value': weather,
            'label': factor_details.get('weather_description', weather).title(),
            'icon': factor_details.get('weather_icon', '01d')
        }
        
        # UV score
        uv = factor_details['uv_estimate']
        if uv <= 2:
            uv_score = 95
        elif uv <= 5:
            uv_score = 70
        elif uv <= 7:
            uv_score = 45
        elif uv <= 10:
            uv_score = 20
        else:
            uv_score = 5
        scores['uv'] = {
            'score': uv_score,
            'value': round(uv, 1),
            'label': ['Low', 'Moderate', 'High', 'Very High', 'Extreme'][
                min(4, int(uv / 3))
            ]
        }
        
        # Crowd score
        crowd = factor_details['crowd_estimate']
        crowd_score = max(5, int(100 - crowd * 90))
        scores['crowd'] = {
            'score': crowd_score,
            'value': round(crowd, 2),
            'label': ['Empty', 'Low', 'Moderate', 'Crowded', 'Very Crowded'][
                min(4, int(crowd * 4.9))
            ]
        }
        
        return scores
