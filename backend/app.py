"""
SafeTravel - Flask REST API Server
Serves ML model predictions and weather data to the frontend.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

from config import (
    ACTIVITIES, PLACE_TYPES, MEDICAL_CONDITIONS,
    SAFETY_LABELS, METRICS_PATH, OPENWEATHER_API_KEY
)
from safety_engine import SafetyEngine
from weather_service import get_weather, get_air_quality
from best_time import get_best_times, compare_activities
from pollution_engine import PollutionEngine

app = Flask(__name__)
CORS(app)

# Initialize safety engine
engine = SafetyEngine()
# Initialize pollution engine (loads per-site models if present)
pollution_engine = PollutionEngine()


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check."""
    return jsonify({
        'status': 'ok',
        'model_loaded': engine.model is not None,
        'model_name': engine.model_name,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/predict', methods=['POST'])
def predict_safety():
    """
    Main prediction endpoint.
    
    Expects JSON body:
    {
        "lat": 28.59,
        "lon": 77.22,
        "activity": "jogging",
        "place_type": "park",
        "medical_condition": "none",
        "datetime": "2024-12-15T08:00:00",
        "place_name": "Lodhi Garden"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))
        activity_key = data.get('activity', 'sightseeing')
        place_type = data.get('place_type', 'other')
        medical_key = data.get('medical_condition', 'none')
        datetime_str = data.get('datetime', datetime.now().isoformat())
        place_name = data.get('place_name', 'Unknown Place')
        api_key = data.get('api_key', OPENWEATHER_API_KEY)
        
        # Validate inputs
        if activity_key not in ACTIVITIES:
            activity_key = 'sightseeing'
        if place_type not in PLACE_TYPES:
            place_type = 'other'
        if medical_key not in MEDICAL_CONDITIONS:
            medical_key = 'none'
        
        # Parse datetime
        try:
            target_dt = datetime.fromisoformat(datetime_str)
        except ValueError:
            target_dt = datetime.now()
        
        # Fetch real-time data
        weather_data = get_weather(lat, lon, api_key)
        aqi_data = get_air_quality(lat, lon, api_key)
        
        # Engineer features
        features, factor_details = engine.engineer_features(
            weather_data, aqi_data, activity_key, place_type,
            medical_key, target_dt, latitude=lat
        )

        # Try to enhance pollution info with SIH-trained models (if available)
        try:
            # Build best-effort SIH-style feature dict from available API data
            components = aqi_data.get('list', [{}])[0].get('components', {}) if aqi_data else {}
            sih_features = {
                'O3_forecast': components.get('o3', 0),
                'NO2_forecast': components.get('no2', 0),
                'T_forecast': factor_details.get('temperature', 0),
                'q_forecast': factor_details.get('humidity', 0),
                'u_forecast': 0.0,
                'v_forecast': 0.0,
                'w_forecast': 0.0,
                'NO2_satellite': 0.0,
                'HCHO_satellite': 0.0,
                'ratio_satellite': 0.0
            }

            pollution_result = pollution_engine.predict_pollution(lat, lon, sih_features)
            # If we have predictions, override the aqi used by the safety engine
            if pollution_result.get('o3') is not None and pollution_result.get('no2') is not None:
                # Simple AQI sub-index: convert O3/NO2 to an approximate AQI
                def _sub_aqi(value, breakpoints):
                    for (c_low, c_high, i_low, i_high) in breakpoints:
                        if value <= c_high:
                            return i_low + (i_high - i_low) * ((value - c_low) / (c_high - c_low))
                    return 500.0

                # Breakpoints (ppb) approximate
                o3_bp = [
                    (0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300),(201,1000,301,500)
                ]
                no2_bp = [
                    (0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,10000,301,500)
                ]

                o3_val = pollution_result['o3']
                no2_val = pollution_result['no2']
                aqi_o3 = _sub_aqi(o3_val, o3_bp)
                aqi_no2 = _sub_aqi(no2_val, no2_bp)
                computed_aqi_value = int(max(aqi_o3, aqi_no2))

                # Map 0-500 AQI value to OpenWeather-like index (1-5)
                def _aqi_to_index(val):
                    if val <= 50:
                        return 1
                    elif val <= 100:
                        return 2
                    elif val <= 150:
                        return 3
                    elif val <= 200:
                        return 4
                    else:
                        return 5

                aqi_index = _aqi_to_index(computed_aqi_value)

                # Update features array (AQI index expected at index 5)
                try:
                    features[0][5] = aqi_index
                except Exception:
                    pass

                factor_details['aqi'] = aqi_index
                factor_details['aqi_value'] = computed_aqi_value
                factor_details['o3'] = o3_val
                factor_details['no2'] = no2_val
                factor_details['pollution_site'] = pollution_result.get('site')
                factor_details['pollution_distance_km'] = pollution_result.get('distance_km')
        except Exception as e:
            print(f"⚠️ Pollution prediction skipped: {e}")
        
        # ML Prediction
        prediction = engine.predict(features)
        
        # Factor breakdown scores
        factor_scores = engine.get_factor_scores(factor_details)
        
        # Health tips
        health_tips = engine.generate_health_tips(factor_details, activity_key, medical_key)
        
        # Build response
        response = {
            'success': True,
            'place_name': place_name,
            'activity': {
                'key': activity_key,
                'label': ACTIVITIES[activity_key]['label'],
                'icon': ACTIVITIES[activity_key]['icon']
            },
            'place_type': {
                'key': place_type,
                'label': PLACE_TYPES[place_type]['label'],
                'icon': PLACE_TYPES[place_type]['icon']
            },
            'medical_condition': {
                'key': medical_key,
                'label': MEDICAL_CONDITIONS[medical_key]['label'],
                'icon': MEDICAL_CONDITIONS[medical_key]['icon']
            },
            'datetime': target_dt.isoformat(),
            'prediction': prediction,
            'factors': factor_scores,
            'o3': factor_details.get('o3'),
            'no2': factor_details.get('no2'),
            'pollution_site': factor_details.get('pollution_site'),
            'pollution_distance_km': factor_details.get('pollution_distance_km'),
            'raw_weather': {
                'temperature': factor_details['temperature'],
                'humidity': factor_details['humidity'],
                'wind_speed': factor_details['wind_speed'],
                'visibility': factor_details['visibility'],
                'weather': factor_details['weather_description'],
                'weather_icon': factor_details['weather_icon'],
                'clouds': factor_details['clouds']
            },
            'health_tips': health_tips,
            'is_fallback': weather_data.get('_fallback', False)
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/best-time', methods=['POST'])
def best_time():
    """
    Get best times to visit.
    
    Expects JSON body with same fields as /api/predict, plus optional 'date'.
    """
    try:
        data = request.get_json()
        
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))
        activity_key = data.get('activity', 'sightseeing')
        place_type = data.get('place_type', 'other')
        medical_key = data.get('medical_condition', 'none')
        target_date = data.get('date', None)
        api_key = data.get('api_key', OPENWEATHER_API_KEY)
        
        result = get_best_times(
            lat, lon, activity_key, place_type, medical_key,
            target_date, api_key
        )
        
        return jsonify({'success': True, **result})
    
    except Exception as e:
        print(f"❌ Best time error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/compare-activities', methods=['POST'])
def compare():
    """
    Compare safety of different activities at same place.
    
    Expects JSON body with lat, lon, place_type, medical_condition, datetime.
    Optional: activities (list of activity keys)
    """
    try:
        data = request.get_json()
        
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))
        place_type = data.get('place_type', 'other')
        medical_key = data.get('medical_condition', 'none')
        datetime_str = data.get('datetime', datetime.now().isoformat())
        activities = data.get('activities', None)
        api_key = data.get('api_key', OPENWEATHER_API_KEY)
        
        try:
            target_dt = datetime.fromisoformat(datetime_str)
        except ValueError:
            target_dt = datetime.now()
        
        results = compare_activities(
            lat, lon, place_type, medical_key,
            target_dt, activities, api_key
        )
        
        return jsonify({'success': True, 'comparisons': results})
    
    except Exception as e:
        print(f"❌ Compare error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/activities', methods=['GET'])
def list_activities():
    """List all supported activities."""
    activities = []
    for key, val in ACTIVITIES.items():
        activities.append({
            'key': key,
            'label': val['label'],
            'icon': val['icon'],
            'description': val['description'],
            'is_outdoor': val['is_outdoor']
        })
    return jsonify({'activities': activities})


@app.route('/api/place-types', methods=['GET'])
def list_place_types():
    """List all supported place types."""
    types = []
    for key, val in PLACE_TYPES.items():
        types.append({
            'key': key,
            'label': val['label'],
            'icon': val['icon']
        })
    return jsonify({'place_types': types})


@app.route('/api/medical-conditions', methods=['GET'])
def list_medical_conditions():
    """List all supported medical conditions."""
    conditions = []
    for key, val in MEDICAL_CONDITIONS.items():
        conditions.append({
            'key': key,
            'label': val['label'],
            'icon': val['icon'],
            'tips': val.get('tips', [])
        })
    return jsonify({'medical_conditions': conditions})


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model training metrics and info."""
    try:
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH) as f:
                metrics = json.load(f)
            return jsonify({'success': True, **metrics})
        else:
            return jsonify({
                'success': False,
                'message': 'Model metrics not found. Train the model first.'
            })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/predict-pollution', methods=['POST'])
def predict_pollution():
    """Direct pollution prediction endpoint using SIH-trained models."""
    try:
        data = request.get_json() or {}
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))

        features = {
            'O3_forecast': float(data.get('O3_forecast', data.get('o3_forecast', 0) or 0)),
            'NO2_forecast': float(data.get('NO2_forecast', data.get('no2_forecast', 0) or 0)),
            'T_forecast': float(data.get('T_forecast', data.get('temperature', 0) or 0)),
            'q_forecast': float(data.get('q_forecast', data.get('humidity', 0) or 0)),
            'u_forecast': float(data.get('u_forecast', 0) or 0),
            'v_forecast': float(data.get('v_forecast', 0) or 0),
            'w_forecast': float(data.get('w_forecast', 0) or 0),
            'NO2_satellite': float(data.get('NO2_satellite', 0) or 0),
            'HCHO_satellite': float(data.get('HCHO_satellite', 0) or 0),
            'ratio_satellite': float(data.get('ratio_satellite', 0) or 0)
        }

        result = pollution_engine.predict_pollution(lat, lon, features)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  🌍 SafeTravel API Server")
    print("=" * 50)
    print(f"  Model loaded: {engine.model is not None}")
    print(f"  Model type:   {engine.model_name}")
    print(f"  API Key:      {'Set' if OPENWEATHER_API_KEY else 'Not set'}")
    print("=" * 50 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
