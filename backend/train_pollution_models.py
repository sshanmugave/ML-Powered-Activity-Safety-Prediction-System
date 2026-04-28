"""
SafeTravel - Pollution Model Training
Trains O3 and NO2 prediction models for each Delhi site using SIH data.
"""

import pandas as pd
import joblib
import os
import json
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# Paths
SIH_DATA_DIR = r'e:\KCT\ml project\iteration 2\SIH_Data_PS-10\Data_SIH_2025'
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
POLLUTION_MODEL_DIR = os.path.join(MODEL_DIR, 'pollution_models')

SITE_COORDS = {
    1: (28.69536, 77.18168),
    2: (28.5718, 77.07125),
    3: (28.58278, 77.23441),
    4: (28.82286, 77.10197),
    5: (28.53077, 77.27123),
    6: (28.72954, 77.09601),
    7: (28.71052, 77.24951)
}

os.makedirs(POLLUTION_MODEL_DIR, exist_ok=True)

FEATURE_COLS = [
    'O3_forecast', 'NO2_forecast', 'T_forecast', 'q_forecast',
    'u_forecast', 'v_forecast', 'w_forecast',
    'NO2_satellite', 'HCHO_satellite', 'ratio_satellite'
]

TARGET_O3 = 'O3_target'
TARGET_NO2 = 'NO2_target'


def load_sih_data():
    all_data = []
    for site in range(1, 8):
        train_file = os.path.join(SIH_DATA_DIR, f'site_{site}_train_data.csv')
        if os.path.exists(train_file):
            df = pd.read_csv(train_file)
            df['site'] = site
            all_data.append(df)
            print(f"✅ Loaded site {site}: {len(df)} samples")
    if not all_data:
        raise FileNotFoundError('No SIH training files found in expected folder')
    return pd.concat(all_data, ignore_index=True)


def prepare_features(data):
    data[FEATURE_COLS] = data[FEATURE_COLS].fillna(data[FEATURE_COLS].mean())
    data = data.dropna(subset=[TARGET_O3, TARGET_NO2])
    print(f"✅ Data prepared: {len(data)} samples with valid targets")
    return data


def train_site_models(data):
    metrics_all = {}
    for site in range(1, 8):
        print(f"\n🎯 Training models for Site {site}...")
        site_data = data[data['site'] == site].copy()
        if len(site_data) < 50:
            print(f"⚠️ Site {site}: Insufficient data ({len(site_data)} samples)")
            continue

        X = site_data[FEATURE_COLS].values
        y_o3 = site_data[TARGET_O3].values
        y_no2 = site_data[TARGET_NO2].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # O3
        o3_rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
        o3_xgb = XGBRegressor(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42)
        o3_rf.fit(X_scaled, y_o3)
        o3_xgb.fit(X_scaled, y_o3)

        o3_rf_r2 = r2_score(y_o3, o3_rf.predict(X_scaled))
        o3_xgb_r2 = r2_score(y_o3, o3_xgb.predict(X_scaled))
        o3_best = o3_xgb if o3_xgb_r2 > o3_rf_r2 else o3_rf

        # NO2
        no2_rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
        no2_xgb = XGBRegressor(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42)
        no2_rf.fit(X_scaled, y_no2)
        no2_xgb.fit(X_scaled, y_no2)

        no2_rf_r2 = r2_score(y_no2, no2_rf.predict(X_scaled))
        no2_xgb_r2 = r2_score(y_no2, no2_xgb.predict(X_scaled))
        no2_best = no2_xgb if no2_xgb_r2 > no2_rf_r2 else no2_rf

        site_dir = os.path.join(POLLUTION_MODEL_DIR, f'site_{site}')
        os.makedirs(site_dir, exist_ok=True)
        joblib.dump(o3_best, os.path.join(site_dir, 'o3_model.pkl'))
        joblib.dump(no2_best, os.path.join(site_dir, 'no2_model.pkl'))
        joblib.dump(scaler, os.path.join(site_dir, 'scaler.pkl'))

        metrics_all[site] = {
            'o3_r2': float(max(o3_rf_r2, o3_xgb_r2)),
            'no2_r2': float(max(no2_rf_r2, no2_xgb_r2)),
            'samples': len(site_data),
            'coords': SITE_COORDS[site]
        }

        print(f"  ✅ Models saved for Site {site}")

    metrics_file = os.path.join(POLLUTION_MODEL_DIR, 'pollution_metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump(metrics_all, f, indent=2)
    print(f"\n✅ All models trained. Metrics saved to {metrics_file}")
    return metrics_all


if __name__ == '__main__':
    print("\n🌍 SafeTravel - Pollution Model Trainer")
    data = load_sih_data()
    data = prepare_features(data)
    train_site_models(data)
