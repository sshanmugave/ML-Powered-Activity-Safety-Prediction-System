# 🌍 SafeTravel – ML-Powered Activity Safety Prediction System

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Node.js](https://img.shields.io/badge/Node.js-16+-green)
![License](https://img.shields.io/badge/License-MIT-blue)
![Contributors](https://img.shields.io/badge/Contributors-Welcome-orange)

> 🤖 **Intelligent web application** that predicts whether it's **safe to visit any place** for a specific **activity** at a given **time**, using real-time **weather**, **pollution data**, and a trained **Machine Learning model**.

**[Quick Start](#-quick-start) • [Features](#-features) • [Setup Guide](./SETUP.md) • [API Docs](./API.md) • [Contributing](./CONTRIBUTING.md)**

---

## ✨ Features

### 🎯 Core Capabilities
- 🔍 **Any-Place Search** – Find any location using OpenStreetMap Nominatim geocoding
- 🏃 **10 Activities** – Jogging, Family Outing, Temple Visit, Photography, Cycling, Picnic, Water Sport, Shopping, Sightseeing, Trekking
- 🤖 **ML Safety Prediction** – XGBoost + Random Forest models predict safety level in real-time
- 🩺 **Medical Profiles** – Personalized predictions for 9 health conditions
- 📊 **Risk Factor Breakdown** – Visual charts for AQI, Temperature, Weather, UV Index, Crowd Level
- 💡 **Context-Aware Health Tips** – Actionable advice based on conditions and medical profile
- ⏰ **24-Hour Best Time Finder** – Discover optimal visiting windows throughout the day
- 🔄 **Activity Comparison** – Compare safety scores of all 10 activities at once
- 📱 **Dark/Light Theme** – Beautiful glassmorphism UI with full responsiveness
- 🌡️ **Real-Time Data** – Live weather + air quality from OpenWeatherMap

### 🧠 ML & Data
- **Accuracy:** 85.2% (XGBoost) with cross-validation: 83.6% ± 0.8%
- **Features:** 28 engineered features including medical condition multipliers
- **Models:** Per-site O3/NO2 predictions trained on SIH Data_SIH_2025 dataset
- **Data:** 12,000+ synthetic training samples + real SIH data integration
- **Scalability:** Handles all activities, place types, weather conditions, medical profiles

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python 3.8+, Flask | REST API server |
| **ML Models** | scikit-learn, XGBoost | Safety & pollution predictions |
| **Frontend** | HTML5, CSS3, JavaScript | Modern responsive UI |
| **Bundler** | Vite | Lightning-fast development |
| **Charts** | Chart.js | Interactive visualizations |
| **Geocoding** | Nominatim (OpenStreetMap) | Location search |
| **Weather API** | OpenWeatherMap | Real-time weather & AQI |
| **Data Processing** | pandas, numpy | Feature engineering |
| **Serialization** | joblib | Model persistence |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher – [Download](https://www.python.org/downloads/)
- Node.js 16 or higher – [Download](https://nodejs.org/)
- OpenWeatherMap API key (free) – [Get Key](https://openweathermap.org/api)

### 1. Clone & Setup (5 minutes)

```bash
# Clone repository
git clone https://github.com/sshanmugave/ML-Powered-Activity-Safety-Prediction-System.git
cd "ML-Powered-Activity-Safety-Prediction-System/iteration 2"

# Backend setup
cd backend
pip install -r requirements.txt

# Create .env file and add API key
echo 'OPENWEATHER_API_KEY=your_key_here' > .env

# Train models (first time only)
python generate_dataset.py
python train_model.py
python train_pollution_models.py

# Start backend
python app.py
```

### 2. Start Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

### 3. Open App

Visit **http://localhost:3000** 🎉

---

## 📊 Model Performance

| Metric | Random Forest | **XGBoost** |
|--------|---|---|
| Accuracy | 80.9% | **85.2%** ⭐ |
| F1 Score | 80.8% | **85.0%** |
| CV Accuracy | 79.5% ± 1.0% | **83.6% ± 0.8%** |

### Safety Classifications
- 🟢 **Safe** (75-100) – Great time to visit
- 🟡 **Moderate** (55-74) – Visit with precautions
- 🟠 **Risky** (35-54) – Consider alternatives
- 🔴 **Unsafe** (0-34) – Not recommended

---

## 📁 Project Structure

```
iteration 2/
├── 📄 README.md                    # This file
├── 📄 SETUP.md                     # Detailed installation guide
├── 📄 API.md                       # API reference documentation
├── 📄 CONTRIBUTING.md              # Contributing guidelines
├── 📄 LICENSE                      # MIT License
│
├── backend/                        # Python Flask API
│   ├── app.py                      # Main Flask application
│   ├── config.py                   # Configuration & constants
│   ├── safety_engine.py            # ML feature engineering & prediction
│   ├── pollution_engine.py         # Per-site O3/NO2 model routing
│   ├── weather_service.py          # OpenWeatherMap integration
│   ├── best_time.py                # 24-hour recommendations
│   ├── generate_dataset.py         # Synthetic data generation
│   ├── train_model.py              # Main model training
│   ├── train_pollution_models.py   # SIH data → per-site models
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── models/                     # Saved ML artifacts
│   │   ├── safety_model_xgb.pkl    # Main safety predictor
│   │   ├── safety_model_rf.pkl     # Backup Random Forest
│   │   ├── scaler.pkl              # Feature scaler
│   │   ├── model_metrics.json      # Training metrics
│   │   └── pollution_models/       # Per-site models
│   │       ├── site_1/
│   │       ├── site_2/
│   │       └── ... site_7/
│   └── data/                       # Data & visualizations
│       ├── training_data.csv       # Generated synthetic data
│       ├── feature_importance.png
│       └── confusion_matrix.png
│
├── frontend/                       # Vite + Vanilla JS
│   ├── index.html                  # Main page
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite configuration
│   ├── js/
│   │   ├── main.js                 # App entry point
│   │   ├── api.js                  # Backend API client
│   │   ├── search.js               # Nominatim place search
│   │   ├── ui.js                   # UI rendering engine
│   │   ├── charts.js               # Chart.js visualizations
│   │   └── utils.js                # Helper utilities
│   └── css/
│       ├── index.css               # Design system
│       ├── components.css          # Component styles
│       └── animations.css          # Animations & transitions
│
└── SIH_Data_PS-10/                 # SIH Dataset (optional)
    └── Data_SIH_2025/
        ├── site_1_train_data.csv
        ├── site_2_train_data.csv
        └── ... site_7_train_data.csv
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check & model status |
| POST | `/api/predict` | Main safety prediction |
| POST | `/api/best-time` | 24-hour best times timeline |
| POST | `/api/compare-activities` | Compare activities at location |
| POST | `/api/predict-pollution` | Direct O3/NO2 predictions |
| GET | `/api/activities` | List all activities |
| GET | `/api/place-types` | List all place types |
| GET | `/api/medical-conditions` | List medical conditions |
| GET | `/api/model-info` | Training metrics |

📖 **Full API documentation:** See [API.md](./API.md)

---

## 📝 Example Request

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

**Response:**
```json
{
  "success": true,
  "prediction": 78,
  "place_name": "Lodhi Garden",
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
  "raw_weather": {
    "temperature": 28,
    "humidity": 65,
    "wind_speed": 3.5,
    "visibility": 10000
  },
  "health_tips": [
    "Stay hydrated in warm weather",
    "Use sunscreen with SPF 30+"
  ]
}
```

---

## 🎓 How It Works

### 1. Feature Engineering
- Weather data (temperature, humidity, wind, visibility)
- Air quality metrics (AQI, O3, NO2)
- Time features (hour, day of week, month)
- UV index estimation (calculated from lat/lon/time/clouds)
- Activity properties (exertion level, pollution sensitivity)
- Medical condition multipliers (personalization)

### 2. ML Prediction Pipeline
```
Input Data
    ↓
Feature Engineering
    ↓
Feature Scaling (StandardScaler)
    ↓
XGBoost Model (85.2% accuracy)
    ↓
Safety Score (0-100)
    ↓
Classification (Safe/Moderate/Risky/Unsafe)
```

### 3. Pollution Modeling
Per-site O3/NO2 models trained on SIH data:
- **Site 1-7:** Individual RandomForest/XGBoost models
- **Routing:** Haversine distance to nearest site
- **Integration:** O3/NO2 → AQI → Safety Score

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Error: Address already in use
# Solution: Kill existing process
Get-Process -Name python | Stop-Process -Force  # Windows
lsof -ti:5000 | xargs kill -9                    # macOS/Linux
```

### API Key Not Working
```bash
# Verify your OpenWeatherMap API key
curl "https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid=YOUR_KEY"
```

### Frontend Can't Connect to Backend
```bash
# Test backend is running
curl http://localhost:5000/api/health

# Check CORS is enabled in Flask
# Should see "status": "ok"
```

📖 **Full troubleshooting guide:** See [SETUP.md](./SETUP.md#-troubleshooting)

---

## 📦 Installation Details

### Requirements
- **Python:** 3.8, 3.9, 3.10, 3.11
- **Node.js:** 16, 18, 20
- **Disk Space:** 500 MB (including models)
- **RAM:** 2 GB minimum
- **Internet:** Required for weather data

### Python Dependencies
```
Flask 2.3+, scikit-learn 1.3+, XGBoost 2.0+, pandas 2.0+,
numpy 1.24+, joblib 1.3+, requests 2.31+, matplotlib 3.7+, seaborn 0.12+
```

### Node.js Dependencies
```
Vite 5.0+, Chart.js 4.4+
```

---

## 🚀 Deployment

### Production Build
```bash
# Backend: Use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Frontend: Build static files
npm run build  # Output: dist/
```

### Cloud Deployment
- **Backend:** Heroku, AWS Lambda, Azure App Service, Google Cloud Run
- **Frontend:** Netlify, Vercel, GitHub Pages, AWS S3 + CloudFront
- **Database:** PostgreSQL, MongoDB (for future features)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Code style guidelines
- Pull request process
- Testing requirements
- Areas for contribution

**Quick contribution:**
```bash
git checkout -b feature/your-feature
# Make changes
git commit -am 'feat: Add your feature'
git push origin feature/your-feature
# Create Pull Request on GitHub
```

---

## 📚 Documentation

- **[Setup Guide](./SETUP.md)** – Step-by-step installation
- **[API Reference](./API.md)** – Complete endpoint documentation
- **[Contributing](./CONTRIBUTING.md)** – How to contribute code
- **[Troubleshooting](./SETUP.md#-troubleshooting)** – Common issues & fixes

---

## 🎯 Roadmap

### v1.0 (Current) ✅
- [x] ML safety prediction model
- [x] Real-time weather integration
- [x] SIH-based pollution models
- [x] Dark/Light theme UI
- [x] Activity comparison

### v1.1 (Planned) 🔜
- [ ] Historical data tracking
- [ ] User authentication
- [ ] Saved favorites
- [ ] Mobile app (React Native)
- [ ] Push notifications

### v2.0 (Future) 🚀
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] IoT sensor integration
- [ ] Crowdsourced safety reports
- [ ] Multi-language support
- [ ] Offline mode

---

## 📊 Statistics

- **Activities:** 10+ types
- **Places:** 10+ categories
- **Medical Conditions:** 9 profiles
- **Training Data:** 12,000+ samples
- **Features:** 28 engineered features
- **Model Accuracy:** 85.2%
- **Response Time:** <500ms
- **API Endpoints:** 9 public endpoints

---

## 📄 License

MIT License – Free to use, modify, and distribute. See [LICENSE](./LICENSE)

---

## 👥 Team & Credits

**Developed by:** ML & SafeTravel Contributors

**Data Source:** SIH_Data_PS-10, OpenWeatherMap

**Inspired by:** Environmental health research, urban mobility studies

---

## 🙏 Acknowledgments

- OpenWeatherMap for real-time weather data
- OpenStreetMap Nominatim for geocoding
- scikit-learn and XGBoost communities
- All contributors and users

---

## 📞 Support & Contact

- 🐛 **Report Bugs:** [GitHub Issues](https://github.com/sshanmugave/ML-Powered-Activity-Safety-Prediction-System/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/sshanmugave/ML-Powered-Activity-Safety-Prediction-System/discussions)
- 📧 **Email:** sshanmugave@example.com
- 🌐 **Website:** Coming soon

---

## ⭐ Show Your Support

If you find SafeTravel useful, please star this repository! ⭐

```bash
# Clone and support development
git clone https://github.com/sshanmugave/ML-Powered-Activity-Safety-Prediction-System.git
```

---

## 📋 Checklist for New Users

- [ ] Installed Python 3.8+
- [ ] Installed Node.js 16+
- [ ] Got OpenWeatherMap API key
- [ ] Cloned repository
- [ ] Installed backend dependencies
- [ ] Created `.env` file with API key
- [ ] Trained models
- [ ] Started backend server
- [ ] Started frontend server
- [ ] Opened http://localhost:3000
- [ ] Tested a prediction

---

**Made with ❤️ for safer travel. Happy predicting!** 🌍✨

**Last Updated:** December 2024 | **Version:** 1.0.0
