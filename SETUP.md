# 📦 Installation & Setup Guide

Complete step-by-step instructions to get **SafeTravel** running on your machine.

## Prerequisites

Ensure you have the following installed:
- **Python 3.8 or higher** – [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** – [Download Node.js](https://nodejs.org/)
- **Git** – [Download Git](https://git-scm.com/)
- **OpenWeatherMap API Key** – [Get Free API Key](https://openweathermap.org/api)

Verify installations:
```bash
python --version
node --version
npm --version
git --version
```

---

## 🚀 Quick Setup (5 minutes)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sshanmugave/ML-Powered-Activity-Safety-Prediction-System.git
cd "ML-Powered-Activity-Safety-Prediction-System/iteration 2"
```

### 2️⃣ Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file and add your OpenWeatherMap API key
# (See .env.example for format)
```

**First time only – Train ML models:**
```bash
# Generate synthetic training dataset
python generate_dataset.py

# Train the safety prediction model
python train_model.py

# Train per-site pollution models (uses SIH_Data_PS-10 folder)
python train_pollution_models.py
```

**Start the backend server:**
```bash
python app.py
```

✅ Backend runs at `http://localhost:5000`

### 3️⃣ Frontend Setup

Open **another terminal** in the `frontend` folder:

```bash
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend runs at `http://localhost:3000`

### 4️⃣ Open the App

Visit **http://localhost:3000** in your web browser and start predicting! 🎉

---

## 📋 Detailed Setup

### Backend Configuration

#### 1. Create `.env` file

In the `backend/` directory, create a `.env` file with your configuration:

```env
OPENWEATHER_API_KEY=your_api_key_here
FLASK_ENV=development
```

**Get your free API key:**
1. Visit [https://openweathermap.org/api](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Paste it in the `.env` file

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- Flask – REST API framework
- scikit-learn, XGBoost – ML models
- pandas, numpy – Data processing
- requests – HTTP client
- matplotlib, seaborn – Visualization

#### 3. Train Models (First Time)

```bash
# Generate 12,000+ synthetic training samples
python generate_dataset.py

# Train safety prediction models (Random Forest + XGBoost)
python train_model.py

# Train per-site pollution models from SIH dataset
python train_pollution_models.py
```

**Output:**
- `models/safety_model_xgb.pkl` – Main safety predictor
- `models/safety_model_rf.pkl` – Backup Random Forest model
- `models/pollution_models/site_<1-7>/` – Per-site O3/NO2 models
- `models/model_metrics.json` – Training metrics

#### 4. Run Backend

```bash
python app.py
```

Expected output:
```
==================================================
  🌍 SafeTravel API Server
==================================================
  Model loaded: True
  Model type:   xgboost
  API Key:      Set
==================================================

 * Running on http://0.0.0.0:5000
```

---

### Frontend Configuration

#### 1. Install Dependencies

```bash
npm install
```

**Includes:**
- Vite – Fast development server
- Chart.js – Data visualizations

#### 2. Start Dev Server

```bash
npm run dev
```

Expected output:
```
VITE ready in 828 ms

  ➜  Local:   http://localhost:3000/
```

#### 3. Build for Production

```bash
npm run build
```

Output in `dist/` folder ready for deployment.

---

## 🔧 Troubleshooting

### Backend Issues

#### ❌ `ModuleNotFoundError: No module named 'flask'`

**Solution:** Install dependencies

```bash
pip install -r requirements.txt
```

#### ❌ `[Errno 48] Address already in use`

**Solution:** Port 5000 is already in use. Kill the process:

**Windows (PowerShell):**
```powershell
Get-Process -Name python | Stop-Process -Force
```

**macOS/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
```

Or change port in `backend/app.py`:
```python
app.run(debug=True, port=5001)  # Change from 5000 to 5001
```

#### ❌ `FileNotFoundError: No module named 'models'`

**Solution:** Models not trained yet. Run:

```bash
python generate_dataset.py
python train_model.py
```

#### ❌ `openweathermap.org: [Errno -2] Name or service not known`

**Solution:** Check internet connection or API key is valid

```bash
# Test API key
curl "https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid=YOUR_API_KEY"
```

---

### Frontend Issues

#### ❌ `npm: command not found`

**Solution:** Node.js not installed. [Download Node.js](https://nodejs.org/)

#### ❌ `EADDRINUSE: address already in use :::3000`

**Solution:** Port 3000 is in use. Kill process:

**Windows (PowerShell):**
```powershell
Get-Process -Name node | Stop-Process -Force
```

**macOS/Linux:**
```bash
lsof -ti:3000 | xargs kill -9
```

Or use different port:
```bash
# Edit vite.config.js
# server: { port: 3001 }
npm run dev
```

#### ❌ Blank page or `Cannot GET /`

**Solution:** Backend is not running. Ensure:

1. Backend terminal shows `Running on http://0.0.0.0:5000`
2. Frontend can reach backend at `http://localhost:5000/api/health`

Test in terminal:
```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{"status":"ok","model_loaded":true,"model_name":"xgboost",...}
```

---

## 🌐 Environment Variables

Create `.env` file in `backend/` folder:

```env
# OpenWeatherMap API Key (required)
OPENWEATHER_API_KEY=your_key_here

# Flask Configuration (optional)
FLASK_ENV=development
FLASK_DEBUG=True

# Database (if using in future)
# DATABASE_URL=sqlite:///safetravel.db
```

Load in `backend/config.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
```

---

## 🐳 Docker Setup (Optional)

### Build Docker Image

```bash
docker build -t safetravel:latest .
```

### Run Container

```bash
docker run -p 5000:5000 -p 3000:3000 \
  -e OPENWEATHER_API_KEY=your_key_here \
  safetravel:latest
```

---

## 📊 Data & Models

### Dataset Locations

- **Synthetic training data:** `backend/data/training_data.csv`
- **SIH dataset:** `SIH_Data_PS-10/Data_SIH_2025/`
- **Trained models:** `backend/models/`

### Training Pipeline

```
generate_dataset.py → training_data.csv → train_model.py → safety_model_xgb.pkl
                                                         → safety_model_rf.pkl
                                                         → model_metrics.json

train_pollution_models.py → SIH data → pollution_models/site_<1-7>/
                                    → o3_model.pkl
                                    → no2_model.pkl
                                    → scaler.pkl
```

---

## ✅ Verify Everything Works

### Backend Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "xgboost",
  "timestamp": "2024-12-15T10:30:00"
}
```

### Make a Test Prediction

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 28.59,
    "lon": 77.22,
    "activity": "jogging",
    "place_type": "park",
    "medical_condition": "none",
    "datetime": "2024-12-15T08:00:00",
    "place_name": "Lodhi Garden"
  }'
```

### Frontend Check

Open http://localhost:3000 and search for a location. You should see:
- ✅ Location search working
- ✅ Safety prediction loading
- ✅ Risk factors displaying
- ✅ Health tips showing

---

## 📦 Deployment

### Production Build (Frontend)

```bash
cd frontend
npm run build
# Output: dist/ folder (upload to Netlify, Vercel, or any static host)
```

### Production Deployment (Backend)

Use a production WSGI server like **Gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use **Heroku**, **AWS**, **Azure**, etc. See `DEPLOYMENT.md` for details.

---

## ❓ FAQ

**Q: Do I need the SIH dataset?**
A: No, the project works with synthetic data. SIH data is optional for enhanced pollution predictions.

**Q: Is the API key free?**
A: Yes, OpenWeatherMap offers 1,000 free API calls/day.

**Q: Can I use this offline?**
A: No, real-time weather and AQI data requires internet connectivity.

**Q: Can I modify the models?**
A: Yes, retrain anytime with `python train_model.py` or `python train_pollution_models.py`.

---

## 🎓 Next Steps

1. Explore the [API Documentation](../API.md)
2. Read [Architecture Guide](../ARCHITECTURE.md)
3. Check [Contributing Guidelines](../CONTRIBUTING.md)
4. Join our [Discord Community](#)

Happy predicting! 🌍✨
