"""
SafeTravel - ML Model Training Script
Trains Random Forest + XGBoost classifiers for safety prediction.
Generates evaluation metrics, feature importance, and confusion matrix plots.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score
)

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("⚠️ XGBoost not installed. Using Random Forest only.")

import joblib
from config import (
    FEATURE_NAMES, MODEL_DIR, DATA_DIR,
    RF_MODEL_PATH, XGB_MODEL_PATH, SCALER_PATH,
    METRICS_PATH, FEATURE_IMPORTANCE_PATH, CONFUSION_MATRIX_PATH,
    TRAINING_DATA_PATH
)

warnings.filterwarnings('ignore')


def load_data():
    """Load training data."""
    print("📂 Loading training data...")
    df = pd.read_csv(TRAINING_DATA_PATH)
    
    X = df[FEATURE_NAMES].values
    y = df['safety_label'].values
    
    print(f"   Features: {X.shape[1]}, Samples: {X.shape[0]}")
    print(f"   Classes: {np.unique(y)}")
    return X, y, df


def train_models(X, y):
    """Train Random Forest and XGBoost models."""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    models = {}
    
    # ─── Random Forest ──────────────────────────────
    print("\n🌲 Training Random Forest Classifier...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf.fit(X_train_scaled, y_train)
    
    rf_pred = rf.predict(X_test_scaled)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_f1 = f1_score(y_test, rf_pred, average='weighted')
    
    # Cross-validation
    rf_cv = cross_val_score(rf, X_train_scaled, y_train, cv=5, scoring='accuracy')
    
    print(f"   Accuracy: {rf_accuracy:.4f}")
    print(f"   F1 Score: {rf_f1:.4f}")
    print(f"   CV Accuracy: {rf_cv.mean():.4f} ± {rf_cv.std():.4f}")
    
    results['random_forest'] = {
        'accuracy': round(rf_accuracy, 4),
        'f1_score': round(rf_f1, 4),
        'cv_mean': round(rf_cv.mean(), 4),
        'cv_std': round(rf_cv.std(), 4),
        'precision': round(precision_score(y_test, rf_pred, average='weighted'), 4),
        'recall': round(recall_score(y_test, rf_pred, average='weighted'), 4)
    }
    models['random_forest'] = (rf, rf_pred)
    
    # ─── XGBoost ────────────────────────────────────
    if HAS_XGBOOST:
        print("\n🚀 Training XGBoost Classifier...")
        xgb = XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss',
            n_jobs=-1
        )
        xgb.fit(X_train_scaled, y_train)
        
        xgb_pred = xgb.predict(X_test_scaled)
        xgb_accuracy = accuracy_score(y_test, xgb_pred)
        xgb_f1 = f1_score(y_test, xgb_pred, average='weighted')
        
        xgb_cv = cross_val_score(xgb, X_train_scaled, y_train, cv=5, scoring='accuracy')
        
        print(f"   Accuracy: {xgb_accuracy:.4f}")
        print(f"   F1 Score: {xgb_f1:.4f}")
        print(f"   CV Accuracy: {xgb_cv.mean():.4f} ± {xgb_cv.std():.4f}")
        
        results['xgboost'] = {
            'accuracy': round(xgb_accuracy, 4),
            'f1_score': round(xgb_f1, 4),
            'cv_mean': round(xgb_cv.mean(), 4),
            'cv_std': round(xgb_cv.std(), 4),
            'precision': round(precision_score(y_test, xgb_pred, average='weighted'), 4),
            'recall': round(recall_score(y_test, xgb_pred, average='weighted'), 4)
        }
        models['xgboost'] = (xgb, xgb_pred)
    
    # ─── Select best model ──────────────────────────
    best_name = max(results, key=lambda k: results[k]['accuracy'])
    best_model = models[best_name][0]
    best_pred = models[best_name][1]
    
    print(f"\n🏆 Best Model: {best_name} (Accuracy: {results[best_name]['accuracy']:.4f})")
    
    return {
        'rf': rf, 
        'xgb': models.get('xgboost', (None, None))[0],
        'scaler': scaler,
        'best_name': best_name,
        'best_model': best_model,
        'results': results,
        'y_test': y_test,
        'best_pred': best_pred,
        'X_test': X_test_scaled
    }


def save_models(training_result):
    """Save trained models and artifacts."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save Random Forest
    joblib.dump(training_result['rf'], RF_MODEL_PATH)
    print(f"💾 Saved RF model to {RF_MODEL_PATH}")
    
    # Save XGBoost
    if training_result['xgb'] is not None:
        joblib.dump(training_result['xgb'], XGB_MODEL_PATH)
        print(f"💾 Saved XGBoost model to {XGB_MODEL_PATH}")
    
    # Save Scaler
    joblib.dump(training_result['scaler'], SCALER_PATH)
    print(f"💾 Saved scaler to {SCALER_PATH}")
    
    # Save metrics
    metrics = {
        'best_model': training_result['best_name'],
        'models': training_result['results'],
        'feature_names': FEATURE_NAMES,
        'n_features': len(FEATURE_NAMES),
        'classes': ['Unsafe', 'Risky', 'Moderate', 'Safe']
    }
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"💾 Saved metrics to {METRICS_PATH}")


def plot_feature_importance(model, model_name):
    """Plot and save feature importance chart."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(14, 8))
    plt.title(f'Feature Importance - {model_name}', fontsize=16, fontweight='bold')
    
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(FEATURE_NAMES)))
    
    bars = plt.barh(
        range(len(FEATURE_NAMES)),
        importances[indices],
        color=colors[indices],
        edgecolor='white',
        linewidth=0.5
    )
    
    plt.yticks(range(len(FEATURE_NAMES)), [FEATURE_NAMES[i] for i in indices], fontsize=10)
    plt.xlabel('Importance', fontsize=12)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 Saved feature importance to {FEATURE_IMPORTANCE_PATH}")


def plot_confusion_matrix(y_test, y_pred, model_name):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_test, y_pred)
    labels = ['Unsafe', 'Risky', 'Moderate', 'Safe']
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=labels, yticklabels=labels,
        linewidths=1, linecolor='white'
    )
    plt.title(f'Confusion Matrix - {model_name}', fontsize=16, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 Saved confusion matrix to {CONFUSION_MATRIX_PATH}")


def print_classification_report(y_test, y_pred):
    """Print detailed classification report."""
    labels = ['Unsafe', 'Risky', 'Moderate', 'Safe']
    print("\n📋 Classification Report:")
    print("=" * 60)
    report = classification_report(y_test, y_pred, target_names=labels)
    print(report)


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("  🚀 SafeTravel ML Model Training Pipeline")
    print("=" * 60)
    
    # Check if training data exists
    if not os.path.exists(TRAINING_DATA_PATH):
        print("\n⚠️ Training data not found. Generating dataset first...")
        from generate_dataset import generate_dataset
        generate_dataset(12000)
    
    # Load data
    X, y, df = load_data()
    
    # Train models
    result = train_models(X, y)
    
    # Save everything
    save_models(result)
    
    # Plots
    best_model = result['best_model']
    best_name = result['best_name']
    
    plot_feature_importance(best_model, best_name.replace('_', ' ').title())
    plot_confusion_matrix(result['y_test'], result['best_pred'], best_name.replace('_', ' ').title())
    
    # Detailed report
    print_classification_report(result['y_test'], result['best_pred'])
    
    print("\n" + "=" * 60)
    print("  ✅ Training Complete!")
    print("=" * 60)
    print(f"\n  Best Model: {best_name}")
    print(f"  Accuracy:   {result['results'][best_name]['accuracy']:.4f}")
    print(f"  F1 Score:   {result['results'][best_name]['f1_score']:.4f}")
    print(f"  Files saved in: {MODEL_DIR}")
    print()


if __name__ == "__main__":
    main()
