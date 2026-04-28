"""
Pollution Engine - Routes predictions to nearest site model

Loads per-site O3/NO2 models trained from SIH Data_SIH_2025 and exposes
a simple interface to predict pollutant concentrations for a given lat/lon
and feature dict.
"""
import os
import joblib
import numpy as np
from math import radians, cos, sin, asin, sqrt


class PollutionEngine:
    """Routes to nearest site and predicts O3/NO2"""
    SITE_COORDS = {
        1: (28.69536, 77.18168),
        2: (28.5718, 77.07125),
        3: (28.58278, 77.23441),
        4: (28.82286, 77.10197),
        5: (28.53077, 77.27123),
        6: (28.72954, 77.09601),
        7: (28.71052, 77.24951)
    }

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self._load_models()

    def _load_models(self):
        model_dir = os.path.join(os.path.dirname(__file__), 'models', 'pollution_models')
        for site in range(1, 8):
            site_dir = os.path.join(model_dir, f'site_{site}')
            if os.path.exists(site_dir):
                try:
                    o3_path = os.path.join(site_dir, 'o3_model.pkl')
                    no2_path = os.path.join(site_dir, 'no2_model.pkl')
                    scaler_path = os.path.join(site_dir, 'scaler.pkl')
                    if all(os.path.exists(p) for p in [o3_path, no2_path, scaler_path]):
                        self.models[site] = {
                            'o3': joblib.load(o3_path),
                            'no2': joblib.load(no2_path)
                        }
                        self.scalers[site] = joblib.load(scaler_path)
                        print(f"✅ Loaded pollution models for Site {site}")
                except Exception as e:
                    print(f"⚠️ Error loading Site {site}: {e}")

    def haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates (km)"""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c

    def find_nearest_site(self, lat, lon):
        min_dist = float('inf')
        nearest_site = 1
        for site, (site_lat, site_lon) in self.SITE_COORDS.items():
            dist = self.haversine(lat, lon, site_lat, site_lon)
            if dist < min_dist:
                min_dist = dist
                nearest_site = site
        return nearest_site, min_dist

    def predict_pollution(self, lat, lon, features_dict):
        """
        Predict O3/NO2 for given location.

        features_dict must provide the SIH-style inputs (best-effort):
        O3_forecast, NO2_forecast, T_forecast, q_forecast, u_forecast,
        v_forecast, w_forecast, NO2_satellite, HCHO_satellite, ratio_satellite
        """
        site, distance = self.find_nearest_site(lat, lon)
        if site not in self.models:
            return {
                'o3': None,
                'no2': None,
                'site': site,
                'distance_km': round(distance, 2),
                'error': 'Models not available for this site'
            }

        try:
            feature_cols = [
                'O3_forecast', 'NO2_forecast', 'T_forecast', 'q_forecast',
                'u_forecast', 'v_forecast', 'w_forecast',
                'NO2_satellite', 'HCHO_satellite', 'ratio_satellite'
            ]
            X = np.array([[features_dict.get(c, 0) for c in feature_cols]])
            X_scaled = self.scalers[site].transform(X)
            o3_pred = float(self.models[site]['o3'].predict(X_scaled)[0])
            no2_pred = float(self.models[site]['no2'].predict(X_scaled)[0])

            return {
                'o3': max(0, o3_pred),
                'no2': max(0, no2_pred),
                'site': site,
                'distance_km': round(distance, 2),
                'coords': self.SITE_COORDS[site]
            }
        except Exception as e:
            return {
                'o3': None,
                'no2': None,
                'site': site,
                'distance_km': round(distance, 2),
                'error': str(e)
            }
