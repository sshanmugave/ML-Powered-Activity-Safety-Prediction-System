# 🔌 SafeTravel API Documentation

Complete reference for all SafeTravel REST API endpoints.

**Base URL:** `http://localhost:5000` (development)

## 📋 Table of Contents
- [Health Check](#health-check)
- [Safety Prediction](#safety-prediction)
- [Best Time Recommendations](#best-time-recommendations)
- [Activity Comparison](#activity-comparison)
- [Data Reference](#data-reference)
- [Error Handling](#error-handling)

---

## Health Check

### `GET /api/health`

Check if API is running and models are loaded.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "xgboost",
  "timestamp": "2024-12-15T10:30:00"
}
```

**Status Codes:**
- `200` – Server healthy, models loaded
- `500` – Server error

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

## Safety Prediction

### `POST /api/predict`

Get safety prediction for a location and activity.

**Request Body:**
```json
{
  "lat": 28.59,
  "lon": 77.22,
  "activity": "jogging",
  "place_type": "park",
  "medical_condition": "none",
  "datetime": "2024-12-15T08:00:00",
  "place_name": "Lodhi Garden",
  "api_key": "your_openweather_api_key"
}
```

**Parameters:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `lat` | float | ✅ | Latitude | 28.59 |
| `lon` | float | ✅ | Longitude | 77.22 |
| `activity` | string | ✅ | Activity type | "jogging" |
| `place_type` | string | ✅ | Place category | "park" |
| `medical_condition` | string | ✅ | Health condition | "none" |
| `datetime` | ISO string | ✅ | Visit time | "2024-12-15T08:00:00" |
| `place_name` | string | ❌ | Location name | "Lodhi Garden" |
| `api_key` | string | ❌ | OpenWeatherMap key | (uses env if omitted) |

**Response:**
```json
{
  "success": true,
  "place_name": "Lodhi Garden",
  "activity": {
    "key": "jogging",
    "label": "Jogging",
    "icon": "🏃"
  },
  "place_type": {
    "key": "park",
    "label": "Park",
    "icon": "🌳"
  },
  "medical_condition": {
    "key": "none",
    "label": "None",
    "icon": "✅"
  },
  "datetime": "2024-12-15T08:00:00",
  "prediction": 78,
  "factors": {
    "aqi": 2,
    "temperature": 28,
    "weather": 1,
    "uv_index": 2,
    "crowd_level": 2
  },
  "o3": 42.5,
  "no2": 35.2,
  "pollution_site": 1,
  "pollution_distance_km": 2.15,
  "raw_weather": {
    "temperature": 28,
    "humidity": 65,
    "wind_speed": 3.5,
    "visibility": 10000,
    "weather": "Partly cloudy",
    "weather_icon": "02d",
    "clouds": 30
  },
  "health_tips": [
    "Stay hydrated in warm weather",
    "Use sunscreen with SPF 30+"
  ],
  "is_fallback": false
}
```

**Safety Score:**
- **75-100** 🟢 Safe – Great time to visit
- **55-74** 🟡 Moderate – Visit with precautions
- **35-54** 🟠 Risky – Consider alternatives
- **0-34** 🔴 Unsafe – Not recommended

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 28.59,
    "lon": 77.22,
    "activity": "jogging",
    "place_type": "park",
    "medical_condition": "asthma",
    "datetime": "2024-12-15T08:00:00",
    "place_name": "Lodhi Garden"
  }'
```

**Valid Activity Values:**
`jogging`, `family_outing`, `temple_visit`, `photography`, `cycling`, `picnic`, `water_sport`, `shopping`, `sightseeing`, `trekking`

**Valid Place Types:**
`park`, `temple`, `lake`, `mall`, `beach`, `garden`, `market`, `museum`, `cafe`, `other`

**Valid Medical Conditions:**
`none`, `asthma`, `heart_disease`, `allergies`, `skin_sensitivity`, `elderly`, `pregnancy`, `respiratory_issues`, `diabetes`

---

## Best Time Recommendations

### `POST /api/best-time`

Get 24-hour timeline of safe times to visit.

**Request Body:**
```json
{
  "lat": 28.59,
  "lon": 77.22,
  "activity": "jogging",
  "place_type": "park",
  "medical_condition": "none",
  "date": "2024-12-15",
  "api_key": "your_openweather_api_key"
}
```

**Response:**
```json
{
  "success": true,
  "place": "Lodhi Garden",
  "activity": "jogging",
  "date": "2024-12-15",
  "hours": [
    {
      "hour": 6,
      "score": 85,
      "level": "Safe",
      "icon": "🟢",
      "reason": "Cool morning, low traffic"
    },
    {
      "hour": 7,
      "score": 82,
      "level": "Safe",
      "icon": "🟢",
      "reason": "Good conditions persist"
    },
    {
      "hour": 12,
      "score": 45,
      "level": "Risky",
      "icon": "🟠",
      "reason": "High heat, increased pollution"
    },
    {
      "hour": 18,
      "score": 72,
      "level": "Moderate",
      "icon": "🟡",
      "reason": "Evening traffic pollution"
    }
  ],
  "best_hours": [6, 7, 8, 19, 20],
  "worst_hours": [12, 13, 14, 15]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/best-time \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 28.59,
    "lon": 77.22,
    "activity": "jogging",
    "place_type": "park",
    "medical_condition": "none",
    "date": "2024-12-15"
  }'
```

---

## Activity Comparison

### `POST /api/compare-activities`

Compare safety scores of multiple activities at same location.

**Request Body:**
```json
{
  "lat": 28.59,
  "lon": 77.22,
  "place_type": "park",
  "medical_condition": "none",
  "datetime": "2024-12-15T08:00:00",
  "activities": ["jogging", "cycling", "picnic"],
  "api_key": "your_openweather_api_key"
}
```

**Response:**
```json
{
  "success": true,
  "place": "Lodhi Garden",
  "datetime": "2024-12-15T08:00:00",
  "comparisons": [
    {
      "activity": "jogging",
      "score": 78,
      "level": "Safe",
      "reason": "Good for cardio activity"
    },
    {
      "activity": "cycling",
      "score": 82,
      "level": "Safe",
      "reason": "Excellent conditions for cycling"
    },
    {
      "activity": "picnic",
      "score": 85,
      "level": "Safe",
      "reason": "Perfect weather for outdoor dining"
    }
  ],
  "ranked": [
    {"activity": "picnic", "score": 85},
    {"activity": "cycling", "score": 82},
    {"activity": "jogging", "score": 78}
  ]
}
```

---

## Data Reference

### `GET /api/activities`

List all supported activities.

**Response:**
```json
{
  "activities": [
    {
      "key": "jogging",
      "label": "Jogging",
      "icon": "🏃",
      "description": "Running/jogging activity",
      "is_outdoor": true
    },
    ...
  ]
}
```

### `GET /api/place-types`

List all place types.

**Response:**
```json
{
  "place_types": [
    {
      "key": "park",
      "label": "Park",
      "icon": "🌳"
    },
    ...
  ]
}
```

### `GET /api/medical-conditions`

List medical conditions with health tips.

**Response:**
```json
{
  "medical_conditions": [
    {
      "key": "asthma",
      "label": "Asthma",
      "icon": "🫁",
      "tips": ["Avoid high pollution areas", "Carry inhaler"]
    },
    ...
  ]
}
```

### `GET /api/model-info`

Get model training metrics.

**Response:**
```json
{
  "success": true,
  "accuracy": 0.852,
  "f1_score": 0.850,
  "cv_accuracy": 0.836,
  "model_type": "xgboost",
  "training_samples": 12000,
  "feature_count": 28,
  "pollution_models": {
    "1": {
      "o3_r2": 0.78,
      "no2_r2": 0.82,
      "samples": 1500,
      "coords": [28.69536, 77.18168]
    }
  }
}
```

---

## Pollution Prediction

### `POST /api/predict-pollution`

Direct pollution level prediction using SIH-trained models.

**Request Body:**
```json
{
  "lat": 28.69536,
  "lon": 77.18168,
  "O3_forecast": 50,
  "NO2_forecast": 60,
  "T_forecast": 28,
  "q_forecast": 65,
  "u_forecast": 1.2,
  "v_forecast": 0.8,
  "w_forecast": 0.0,
  "NO2_satellite": 0.0,
  "HCHO_satellite": 0.0,
  "ratio_satellite": 0.0
}
```

**Response:**
```json
{
  "success": true,
  "o3": 42.5,
  "no2": 35.2,
  "site": 1,
  "distance_km": 2.15,
  "coords": [28.69536, 77.18168]
}
```

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Reason | Solution |
|------|--------|----------|
| 400 | Invalid request data | Check JSON format and required fields |
| 401 | API key invalid | Verify OpenWeatherMap API key |
| 404 | Endpoint not found | Check URL spelling |
| 500 | Server error | Check server logs |
| 503 | Service unavailable | Check API rate limits |

### Example Error

**Request (missing required field):**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 28.59,
    "lon": 77.22
  }'
```

**Response:**
```json
{
  "success": false,
  "error": "Invalid request: Missing required field 'activity'"
}
```

---

## Rate Limiting

- No rate limits on local development
- Production: Check OpenWeatherMap API plan limits
- Recommended: Implement client-side caching

---

## CORS Headers

**Allowed Origins (configurable in `config.py`):**
- `http://localhost:3000` (development)
- `http://localhost:5173` (Vite dev)
- `https://yourdomain.com` (production)

**Allowed Methods:** GET, POST, OPTIONS

**Allowed Headers:** Content-Type, Authorization

---

## Best Practices

1. **Cache responses** – Same location shouldn't be requested twice in short time
2. **Handle errors gracefully** – Always check `success` field
3. **Use appropriate datetime** – ISO 8601 format required
4. **Validate inputs** – Check activity/place_type validity before sending
5. **Set timeouts** – API calls should timeout after 30 seconds

---

## Example Integration (JavaScript)

```javascript
async function predictSafety(lat, lon, activity, placeType, medicalCondition) {
  try {
    const response = await fetch('http://localhost:5000/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat,
        lon,
        activity,
        place_type: placeType,
        medical_condition: medicalCondition,
        datetime: new Date().toISOString()
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    if (!data.success) throw new Error(data.error);

    console.log(`Safety Score: ${data.prediction}`);
    return data;
  } catch (error) {
    console.error('Prediction failed:', error);
    return null;
  }
}
```

---

## Support

- 📧 Email: support@safetravel.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📖 Docs: Full documentation in README.md

---

**Last Updated:** December 2024
**API Version:** 1.0
