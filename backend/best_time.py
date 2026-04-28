"""
SafeTravel - Best Time Recommendation Engine
Finds optimal visiting windows by running ML predictions across 24 hours.
"""

from datetime import datetime, timedelta
from safety_engine import SafetyEngine
from weather_service import get_forecast, get_air_quality_forecast
from config import ACTIVITIES, PLACE_TYPES, MEDICAL_CONDITIONS


def get_best_times(lat, lon, activity_key, place_type, medical_key, 
                   target_date=None, api_key=None):
    """
    Find the best times to visit by predicting safety for each hour.
    
    Args:
        lat, lon: coordinates
        activity_key: activity type key
        place_type: place type key
        medical_key: medical condition key
        target_date: date string (YYYY-MM-DD) or None for today
        api_key: optional OpenWeatherMap API key
    
    Returns:
        dict with hourly predictions and best time windows
    """
    engine = SafetyEngine()
    
    # Get forecast data
    forecast_data = get_forecast(lat, lon, api_key)
    aqi_forecast = get_air_quality_forecast(lat, lon, api_key)
    
    if not target_date:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    target_dt = datetime.strptime(target_date, '%Y-%m-%d')
    
    # Build hourly predictions
    hourly = []
    forecast_list = forecast_data.get('list', [])
    aqi_list = aqi_forecast.get('list', [])
    
    for hour in range(24):
        current_dt = target_dt.replace(hour=hour, minute=0, second=0)
        
        # Find closest forecast entry
        weather_entry = _find_closest_forecast(forecast_list, current_dt)
        aqi_entry = _find_closest_aqi(aqi_list, current_dt)
        
        if weather_entry and aqi_entry:
            # Build weather data format matching API response
            weather_data = {
                'main': weather_entry.get('main', {'temp': 25, 'humidity': 50}),
                'wind': weather_entry.get('wind', {'speed': 2}),
                'visibility': weather_entry.get('visibility', 10000),
                'clouds': weather_entry.get('clouds', {'all': 30}),
                'weather': weather_entry.get('weather', [{'id': 800, 'description': 'clear sky', 'icon': '01d'}])
            }
            
            aqi_data = {
                'list': [aqi_entry]
            }
        else:
            # Use current weather as approximation with time adjustments
            from weather_service import get_weather, get_air_quality
            weather_data = get_weather(lat, lon, api_key)
            aqi_data = get_air_quality(lat, lon, api_key)
            
            # Adjust temperature for time of day
            base_temp = weather_data.get('main', {}).get('temp', 25)
            if 0 <= hour <= 5:
                weather_data['main']['temp'] = base_temp - 4
            elif 12 <= hour <= 15:
                weather_data['main']['temp'] = base_temp + 3
            elif 19 <= hour <= 23:
                weather_data['main']['temp'] = base_temp - 2
        
        # Get prediction
        features, factor_details = engine.engineer_features(
            weather_data, aqi_data, activity_key, place_type,
            medical_key, current_dt, latitude=lat
        )
        
        prediction = engine.predict(features)
        factor_scores = engine.get_factor_scores(factor_details)
        
        hourly.append({
            'hour': hour,
            'time_label': current_dt.strftime('%I %p'),
            'score': prediction['score'],
            'label': prediction['label_name'],
            'label_code': prediction['label'],
            'confidence': prediction['confidence'],
            'temperature': factor_details['temperature'],
            'weather': factor_details.get('weather_description', 'N/A'),
            'aqi': factor_details['aqi'],
            'uv': factor_details['uv_estimate']
        })
    
    # Find best time windows
    best_windows = _find_best_windows(hourly)
    
    # Find the single best hour
    best_hour = max(hourly, key=lambda x: x['score'])
    
    # Find worst hours to avoid
    worst_hours = sorted(hourly, key=lambda x: x['score'])[:3]
    
    return {
        'hourly': hourly,
        'best_windows': best_windows,
        'best_hour': best_hour,
        'worst_hours': worst_hours,
        'date': target_date,
        'activity': ACTIVITIES.get(activity_key, {}).get('label', activity_key),
        'place_type': PLACE_TYPES.get(place_type, {}).get('label', place_type)
    }


def _find_closest_forecast(forecast_list, target_dt):
    """Find the forecast entry closest to target datetime."""
    if not forecast_list:
        return None
    
    closest = None
    min_diff = float('inf')
    
    for entry in forecast_list:
        entry_dt = datetime.fromtimestamp(entry.get('dt', 0))
        diff = abs((entry_dt - target_dt).total_seconds())
        if diff < min_diff:
            min_diff = diff
            closest = entry
    
    # Only use if within 3 hours
    if min_diff > 10800:
        return None
    
    return closest


def _find_closest_aqi(aqi_list, target_dt):
    """Find the AQI entry closest to target datetime."""
    if not aqi_list:
        return None
    
    closest = None
    min_diff = float('inf')
    
    for entry in aqi_list:
        entry_dt = datetime.fromtimestamp(entry.get('dt', 0))
        diff = abs((entry_dt - target_dt).total_seconds())
        if diff < min_diff:
            min_diff = diff
            closest = entry
    
    if min_diff > 10800:
        return None
    
    return closest


def _find_best_windows(hourly):
    """
    Find contiguous time windows where safety is good.
    Returns list of windows with start, end, avg score.
    """
    windows = []
    current_window = None
    
    for entry in hourly:
        if entry['score'] >= 65:  # Moderate or better
            if current_window is None:
                current_window = {
                    'start_hour': entry['hour'],
                    'end_hour': entry['hour'],
                    'scores': [entry['score']],
                    'start_label': entry['time_label'],
                    'end_label': entry['time_label']
                }
            else:
                current_window['end_hour'] = entry['hour']
                current_window['scores'].append(entry['score'])
                current_window['end_label'] = entry['time_label']
        else:
            if current_window is not None:
                current_window['avg_score'] = round(
                    sum(current_window['scores']) / len(current_window['scores']), 1
                )
                current_window['duration'] = len(current_window['scores'])
                del current_window['scores']
                windows.append(current_window)
                current_window = None
    
    # Don't forget the last window
    if current_window is not None:
        current_window['avg_score'] = round(
            sum(current_window['scores']) / len(current_window['scores']), 1
        )
        current_window['duration'] = len(current_window['scores'])
        del current_window['scores']
        windows.append(current_window)
    
    # Sort by average score (best first)
    windows.sort(key=lambda w: w['avg_score'], reverse=True)
    
    return windows[:5]  # Top 5 windows


def compare_activities(lat, lon, place_type, medical_key, 
                       target_datetime, activities_to_compare=None, api_key=None):
    """
    Compare safety scores for different activities at the same place and time.
    
    Args:
        activities_to_compare: list of activity keys, or None for all
    
    Returns:
        list of {activity, score, label, ...} sorted by score
    """
    from weather_service import get_weather, get_air_quality
    
    engine = SafetyEngine()
    
    if activities_to_compare is None:
        activities_to_compare = list(ACTIVITIES.keys())
    
    weather_data = get_weather(lat, lon, api_key)
    aqi_data = get_air_quality(lat, lon, api_key)
    
    if isinstance(target_datetime, str):
        target_datetime = datetime.fromisoformat(target_datetime)
    
    results = []
    for act_key in activities_to_compare:
        if act_key not in ACTIVITIES:
            continue
        
        features, factor_details = engine.engineer_features(
            weather_data, aqi_data, act_key, place_type,
            medical_key, target_datetime, latitude=lat
        )
        
        prediction = engine.predict(features)
        
        results.append({
            'activity_key': act_key,
            'activity_label': ACTIVITIES[act_key]['label'],
            'activity_icon': ACTIVITIES[act_key]['icon'],
            'score': prediction['score'],
            'label': prediction['label_name'],
            'label_code': prediction['label'],
            'color': prediction['color'],
            'confidence': prediction['confidence']
        })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
