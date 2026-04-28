"""
SafeTravel - Weather Service
OpenWeatherMap API integration for weather and air quality data.
"""

import requests
import time
from config import OPENWEATHER_API_KEY

# Simple in-memory cache
_cache = {}
CACHE_TTL = 600  # 10 minutes


def _get_cached(key):
    """Get cached value if still valid."""
    if key in _cache:
        val, ts = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return val
        del _cache[key]
    return None


def _set_cache(key, value):
    """Set cache value."""
    _cache[key] = (value, time.time())


def get_weather(lat, lon, api_key=None):
    """
    Fetch current weather data from OpenWeatherMap.
    
    Args:
        lat: latitude
        lon: longitude
        api_key: optional override for API key
    
    Returns:
        dict with weather data
    """
    key = api_key or OPENWEATHER_API_KEY
    cache_key = f"weather_{round(lat,2)}_{round(lon,2)}"
    
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        _set_cache(cache_key, data)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Weather API error: {e}")
        return _get_fallback_weather()


def get_air_quality(lat, lon, api_key=None):
    """
    Fetch current air quality data from OpenWeatherMap.
    
    Returns:
        dict with AQI and pollutant components
    """
    key = api_key or OPENWEATHER_API_KEY
    cache_key = f"aqi_{round(lat,2)}_{round(lon,2)}"
    
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        _set_cache(cache_key, data)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Air Quality API error: {e}")
        return _get_fallback_aqi()


def get_forecast(lat, lon, api_key=None):
    """
    Fetch 5-day/3-hour forecast from OpenWeatherMap.
    
    Returns:
        dict with forecast data
    """
    key = api_key or OPENWEATHER_API_KEY
    cache_key = f"forecast_{round(lat,2)}_{round(lon,2)}"
    
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        _set_cache(cache_key, data)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Forecast API error: {e}")
        return {'list': []}


def get_air_quality_forecast(lat, lon, api_key=None):
    """
    Fetch air quality forecast from OpenWeatherMap.
    
    Returns:
        dict with AQI forecast data
    """
    key = api_key or OPENWEATHER_API_KEY
    cache_key = f"aqi_forecast_{round(lat,2)}_{round(lon,2)}"
    
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://api.openweathermap.org/data/2.5/air_pollution/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        _set_cache(cache_key, data)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ AQI Forecast API error: {e}")
        return {'list': []}


def _get_fallback_weather():
    """Return fallback weather data when API fails."""
    return {
        'main': {'temp': 28, 'humidity': 55, 'feels_like': 30},
        'wind': {'speed': 3},
        'visibility': 8000,
        'clouds': {'all': 30},
        'weather': [{'id': 802, 'main': 'Clouds', 'description': 'scattered clouds', 'icon': '03d'}],
        '_fallback': True
    }


def _get_fallback_aqi():
    """Return fallback AQI data when API fails."""
    return {
        'list': [{
            'main': {'aqi': 2},
            'components': {
                'pm2_5': 18.0,
                'pm10': 25.0,
                'co': 250,
                'no2': 15,
                'o3': 55,
                'so2': 8,
                'nh3': 5,
                'no': 3
            }
        }],
        '_fallback': True
    }
