"""
SafeTravel - Synthetic Training Data Generator
Generates 10,000+ realistic samples for the ML safety prediction model.
Includes medical condition features for personalized recommendations.
"""

import numpy as np
import pandas as pd
import os
import random
from config import (
    ACTIVITIES, PLACE_TYPES, MEDICAL_CONDITIONS,
    FEATURE_NAMES, DATA_DIR
)

random.seed(42)
np.random.seed(42)

# ─── Weather encoding mapping ──────────────────────────────
WEATHER_ENCODE = {
    "clear": 0, "clouds": 1, "rain_light": 2,
    "rain_heavy": 3, "storm": 4, "snow": 5, "fog": 6
}

ACTIVITY_ENCODE = {k: i for i, k in enumerate(ACTIVITIES.keys())}
PLACE_ENCODE = {k: i for i, k in enumerate(PLACE_TYPES.keys())}
MEDICAL_ENCODE = {k: i for i, k in enumerate(MEDICAL_CONDITIONS.keys())}


def estimate_uv(hour, month, latitude=25.0, cloud_factor=1.0):
    """Estimate UV index based on hour, month, latitude, and clouds."""
    if hour < 6 or hour > 19:
        return 0.0
    
    # Solar angle factor (peaks at noon)
    solar_factor = max(0, np.sin(np.pi * (hour - 6) / 13))
    
    # Seasonal factor (higher in summer months in India)
    seasonal = 1.0 + 0.3 * np.sin(2 * np.pi * (month - 3) / 12)
    
    # Latitude factor (lower latitudes = higher UV in India range)
    lat_factor = 1.0 + 0.2 * (30 - latitude) / 30
    
    uv = 12 * solar_factor * seasonal * lat_factor * cloud_factor
    return round(max(0, min(uv, 14)), 1)


def estimate_crowd(hour, day_of_week, place_type, is_weekend):
    """Estimate crowd level (0-1) based on time, day, and place type."""
    base = PLACE_TYPES[place_type]["crowd_base"]
    
    # Time-based crowd pattern
    if 6 <= hour <= 8:
        time_factor = 0.4  # early morning - less crowd
    elif 9 <= hour <= 11:
        time_factor = 0.7
    elif 12 <= hour <= 14:
        time_factor = 0.6  # lunch time - slightly less
    elif 15 <= hour <= 18:
        time_factor = 0.9  # afternoon peak
    elif 19 <= hour <= 21:
        time_factor = 0.8  # evening
    else:
        time_factor = 0.2  # night - very less
    
    # Weekend multiplier
    weekend_mult = 1.4 if is_weekend else 1.0
    
    # Temple gets extra crowded on certain days
    if place_type == "temple" and day_of_week in [1, 4, 5]:  # Tue, Fri, Sat
        weekend_mult *= 1.2
    
    # Market gets crowded in evening
    if place_type == "market" and 17 <= hour <= 21:
        time_factor = 1.0
    
    crowd = base * time_factor * weekend_mult
    return round(min(crowd, 1.0), 2)


def calculate_safety_label(row):
    """
    Calculate safety label based on domain knowledge rules.
    Returns 0 (Unsafe), 1 (Risky), 2 (Moderate), 3 (Safe)
    """
    score = 100.0  # Start with perfect score
    
    temp = row['temperature']
    humidity = row['humidity']
    wind = row['wind_speed']
    visibility = row['visibility']
    weather = row['weather_encoded']
    aqi = row['aqi']
    pm25 = row['pm25']
    uv = row['uv_estimate']
    hour = row['hour_of_day']
    crowd = row['crowd_estimate']
    is_outdoor = row['is_outdoor']
    exertion = row['exertion_level']
    
    # Medical multipliers
    med_aqi = row['medical_aqi_multiplier']
    med_heat = row['medical_heat_multiplier']
    med_uv = row['medical_uv_multiplier']
    med_humidity = row['medical_humidity_multiplier']
    med_exertion = row['medical_exertion_multiplier']
    
    poll_sens = row['pollution_sensitivity']
    weather_sens = row['weather_sensitivity']
    crowd_sens = row['crowd_sensitivity']
    uv_sens = row['uv_sensitivity']
    heat_sens = row['heat_sensitivity']
    
    # ── AQI penalty (with medical multiplier) ──
    aqi_penalty = 0
    if aqi == 1:
        aqi_penalty = 0
    elif aqi == 2:
        aqi_penalty = 10
    elif aqi == 3:
        aqi_penalty = 25
    elif aqi == 4:
        aqi_penalty = 45
    elif aqi == 5:
        aqi_penalty = 70
    
    # PM2.5 additional penalty
    if pm25 > 100:
        aqi_penalty += 10
    if pm25 > 200:
        aqi_penalty += 15
    
    score -= aqi_penalty * poll_sens * med_aqi * (1 + exertion * 0.3)
    
    # ── Temperature penalty (with medical multiplier) ──
    temp_penalty = 0
    if temp > 42:
        temp_penalty = 50
    elif temp > 38:
        temp_penalty = 35
    elif temp > 35:
        temp_penalty = 20
    elif temp > 32:
        temp_penalty = 10
    elif 20 <= temp <= 30:
        temp_penalty = 0
    elif 15 <= temp < 20:
        temp_penalty = 5
    elif 10 <= temp < 15:
        temp_penalty = 10
    elif temp < 5:
        temp_penalty = 30
    elif temp < 10:
        temp_penalty = 15
    
    score -= temp_penalty * heat_sens * med_heat * (1 + exertion * 0.2)
    
    # ── Weather penalty ──
    weather_penalty = 0
    if weather == WEATHER_ENCODE["clear"]:
        weather_penalty = 0
    elif weather == WEATHER_ENCODE["clouds"]:
        weather_penalty = 2
    elif weather == WEATHER_ENCODE["rain_light"]:
        weather_penalty = 15
    elif weather == WEATHER_ENCODE["rain_heavy"]:
        weather_penalty = 40
    elif weather == WEATHER_ENCODE["storm"]:
        weather_penalty = 70
    elif weather == WEATHER_ENCODE["snow"]:
        weather_penalty = 30
    elif weather == WEATHER_ENCODE["fog"]:
        weather_penalty = 20
    
    score -= weather_penalty * weather_sens
    
    # Outdoor activities affected more
    if is_outdoor and weather in [WEATHER_ENCODE["rain_heavy"], WEATHER_ENCODE["storm"]]:
        score -= 15
    
    # ── UV penalty (with medical multiplier) ──
    uv_penalty = 0
    if uv > 10:
        uv_penalty = 35
    elif uv > 7:
        uv_penalty = 20
    elif uv > 5:
        uv_penalty = 10
    elif uv > 3:
        uv_penalty = 5
    
    score -= uv_penalty * uv_sens * med_uv
    
    # ── Crowd penalty ──
    crowd_penalty = crowd * 25  # 0 to 25 points
    score -= crowd_penalty * crowd_sens
    
    # ── Humidity penalty (with medical multiplier) ──
    if humidity > 85:
        score -= 10 * med_humidity
    elif humidity > 75:
        score -= 5 * med_humidity
    
    # ── Visibility penalty ──
    if visibility < 500:
        score -= 15
    elif visibility < 1000:
        score -= 8
    elif visibility < 2000:
        score -= 3
    
    # ── Wind speed penalty ──
    if wind > 15:
        score -= 15
    elif wind > 10:
        score -= 8
    elif wind > 7:
        score -= 3
    
    # ── Night penalty for certain activities ──
    if (hour < 5 or hour > 22) and is_outdoor:
        score -= 10
    
    # ── High exertion + medical condition combo ──
    if exertion > 0.7 and med_exertion > 1.5:
        score -= 10 * exertion * (med_exertion - 1)
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Convert to label
    if score >= 75:
        return 3  # Safe
    elif score >= 55:
        return 2  # Moderate
    elif score >= 35:
        return 1  # Risky
    else:
        return 0  # Unsafe


def generate_single_sample():
    """Generate a single training sample with realistic values."""
    
    # Random selections
    activity_key = random.choice(list(ACTIVITIES.keys()))
    place_key = random.choice(list(PLACE_TYPES.keys()))
    medical_key = random.choice(list(MEDICAL_CONDITIONS.keys()))
    
    activity = ACTIVITIES[activity_key]
    place = PLACE_TYPES[place_key]
    medical = MEDICAL_CONDITIONS[medical_key]
    
    # Time
    hour = random.randint(0, 23)
    day_of_week = random.randint(0, 6)
    month = random.randint(1, 12)
    is_weekend = 1 if day_of_week >= 5 else 0
    
    # Weather (seasonal bias)
    if month in [6, 7, 8, 9]:  # Monsoon
        weather_probs = [0.1, 0.2, 0.3, 0.2, 0.1, 0.0, 0.1]
    elif month in [11, 12, 1, 2]:  # Winter
        weather_probs = [0.3, 0.3, 0.05, 0.02, 0.01, 0.02, 0.3]
    else:  # Summer
        weather_probs = [0.5, 0.3, 0.05, 0.05, 0.05, 0.0, 0.05]
    
    weather_cat = np.random.choice(list(WEATHER_ENCODE.keys()), p=weather_probs)
    weather_encoded = WEATHER_ENCODE[weather_cat]
    
    # Temperature (seasonal)
    if month in [4, 5, 6]:  # Hot summer
        temp_base = random.gauss(38, 5)
    elif month in [7, 8, 9]:  # Monsoon
        temp_base = random.gauss(30, 4)
    elif month in [11, 12, 1, 2]:  # Winter
        temp_base = random.gauss(18, 6)
    else:  # Spring/Autumn
        temp_base = random.gauss(28, 5)
    
    # Diurnal variation
    if 0 <= hour <= 5:
        temp_base -= random.uniform(3, 7)
    elif 6 <= hour <= 9:
        temp_base -= random.uniform(1, 4)
    elif 12 <= hour <= 15:
        temp_base += random.uniform(2, 5)
    elif 19 <= hour <= 23:
        temp_base -= random.uniform(1, 3)
    
    temperature = round(max(-5, min(50, temp_base)), 1)
    
    # Humidity
    if weather_cat in ["rain_light", "rain_heavy", "storm"]:
        humidity = round(random.uniform(70, 98), 1)
    elif weather_cat == "fog":
        humidity = round(random.uniform(80, 100), 1)
    elif month in [7, 8, 9]:
        humidity = round(random.uniform(60, 95), 1)
    else:
        humidity = round(random.uniform(20, 75), 1)
    
    # Wind speed (m/s)
    if weather_cat == "storm":
        wind_speed = round(random.uniform(8, 25), 1)
    elif weather_cat in ["rain_heavy"]:
        wind_speed = round(random.uniform(3, 12), 1)
    else:
        wind_speed = round(random.uniform(0.5, 8), 1)
    
    # Visibility (meters)
    if weather_cat == "fog":
        visibility = round(random.uniform(50, 1500), 0)
    elif weather_cat in ["rain_heavy", "storm"]:
        visibility = round(random.uniform(500, 4000), 0)
    elif weather_cat == "rain_light":
        visibility = round(random.uniform(2000, 8000), 0)
    else:
        visibility = round(random.uniform(5000, 10000), 0)
    
    # AQI (1-5 scale, biased by season and time)
    if month in [11, 12, 1]:  # Winter = worst AQI in India
        aqi_probs = [0.05, 0.15, 0.3, 0.3, 0.2]
    elif month in [6, 7, 8, 9]:  # Monsoon = better AQI
        aqi_probs = [0.4, 0.3, 0.2, 0.08, 0.02]
    else:
        aqi_probs = [0.2, 0.3, 0.3, 0.15, 0.05]
    
    aqi = np.random.choice([1, 2, 3, 4, 5], p=aqi_probs)
    
    # PM2.5 based on AQI
    pm25_ranges = {1: (0, 12), 2: (12, 35), 3: (35, 55), 4: (55, 150), 5: (150, 500)}
    pm25 = round(random.uniform(*pm25_ranges[aqi]), 1)
    
    # PM10
    pm10 = round(pm25 * random.uniform(1.2, 2.5), 1)
    
    # UV estimate
    cloud_factor = 1.0 if weather_cat == "clear" else (0.7 if weather_cat == "clouds" else 0.3)
    uv_estimate = estimate_uv(hour, month, latitude=random.uniform(8, 35), cloud_factor=cloud_factor)
    
    # Crowd estimate
    crowd_estimate = estimate_crowd(hour, day_of_week, place_key, is_weekend)
    
    # Build sample
    sample = {
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'visibility': visibility,
        'weather_encoded': weather_encoded,
        'aqi': aqi,
        'pm25': pm25,
        'pm10': pm10,
        'uv_estimate': uv_estimate,
        'hour_of_day': hour,
        'day_of_week': day_of_week,
        'month': month,
        'is_weekend': is_weekend,
        'activity_encoded': ACTIVITY_ENCODE[activity_key],
        'place_encoded': PLACE_ENCODE[place_key],
        'is_outdoor': 1 if activity["is_outdoor"] else 0,
        'exertion_level': activity["exertion_level"],
        'pollution_sensitivity': activity["pollution_sensitivity"],
        'weather_sensitivity': activity["weather_sensitivity"],
        'crowd_sensitivity': activity["crowd_sensitivity"],
        'uv_sensitivity': activity["uv_sensitivity"],
        'heat_sensitivity': activity["heat_sensitivity"],
        'crowd_estimate': crowd_estimate,
        'medical_aqi_multiplier': medical["aqi_multiplier"],
        'medical_heat_multiplier': medical["heat_multiplier"],
        'medical_uv_multiplier': medical["uv_multiplier"],
        'medical_humidity_multiplier': medical["humidity_multiplier"],
        'medical_exertion_multiplier': medical["exertion_multiplier"],
        # Metadata (not features, for analysis)
        'activity_name': activity_key,
        'place_name': place_key,
        'medical_condition': medical_key
    }
    
    # Calculate safety label
    sample['safety_label'] = calculate_safety_label(sample)
    
    return sample


def generate_dataset(n_samples=12000):
    """Generate the full training dataset."""
    print(f"🔄 Generating {n_samples} training samples...")
    
    samples = []
    for i in range(n_samples):
        samples.append(generate_single_sample())
        if (i + 1) % 2000 == 0:
            print(f"   Generated {i + 1}/{n_samples} samples...")
    
    df = pd.DataFrame(samples)
    
    # Print class distribution
    print("\n📊 Class Distribution:")
    dist = df['safety_label'].value_counts().sort_index()
    labels = {0: "Unsafe", 1: "Risky", 2: "Moderate", 3: "Safe"}
    for label, count in dist.items():
        pct = count / len(df) * 100
        print(f"   {labels[label]}: {count} samples ({pct:.1f}%)")
    
    # Balance check - if too imbalanced, generate more of minority classes
    min_count = dist.min()
    max_count = dist.max()
    if max_count / min_count > 3:
        print("\n⚖️ Dataset is imbalanced. Generating additional samples for minority classes...")
        target_per_class = int(max_count * 0.8)
        
        for label in range(4):
            current_count = dist.get(label, 0)
            if current_count < target_per_class:
                needed = target_per_class - current_count
                extra = []
                attempts = 0
                while len(extra) < needed and attempts < needed * 20:
                    s = generate_single_sample()
                    if s['safety_label'] == label:
                        extra.append(s)
                    attempts += 1
                
                if extra:
                    df = pd.concat([df, pd.DataFrame(extra)], ignore_index=True)
                    print(f"   Added {len(extra)} samples for class '{labels[label]}'")
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\n✅ Final dataset size: {len(df)} samples")
    
    # Final distribution
    print("\n📊 Final Class Distribution:")
    dist = df['safety_label'].value_counts().sort_index()
    for label, count in dist.items():
        pct = count / len(df) * 100
        print(f"   {labels[label]}: {count} samples ({pct:.1f}%)")
    
    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(os.path.join(DATA_DIR, "training_data.csv"), index=False)
    print(f"\n💾 Saved to {os.path.join(DATA_DIR, 'training_data.csv')}")
    
    return df


if __name__ == "__main__":
    df = generate_dataset(12000)
    print("\n📋 Sample rows:")
    print(df[['activity_name', 'place_name', 'medical_condition', 'temperature', 
               'aqi', 'weather_encoded', 'hour_of_day', 'safety_label']].head(10))
