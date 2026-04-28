/**
 * SafeTravel - Main Application Entry Point
 */

(function() {
  'use strict';

  // ─── State ───
  let selectedActivity = 'jogging';
  let selectedMedical = 'none';
  let lastPredictionParams = null;

  // ─── Initialize ───
  async function init() {
    console.log('🌍 SafeTravel initializing...');
    
    // Set default datetime to now
    const dtInput = $('#datetime-input');
    dtInput.value = getNowDatetimeLocal();

    // Initialize Lucide icons
    if (window.lucide) {
      lucide.createIcons();
    }

    // Setup event listeners
    setupEventListeners();
    
    // Init scroll animations
    initScrollAnimations();

    // Apply saved theme
    const savedTheme = loadFromStorage('theme', 'dark');
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Check backend health
    checkBackendHealth();

    console.log('✅ SafeTravel ready!');
  }

  // ─── Event Listeners ───
  function setupEventListeners() {
    // Place search
    const placeInput = $('#place-input');
    const searchResults = $('#search-results');
    
    placeInput.addEventListener('input', debounce(async (e) => {
      const query = e.target.value.trim();
      if (query.length < 3) {
        hide(searchResults);
        return;
      }
      
      const results = await Search.searchPlaces(query);
      Search.renderResults(results, searchResults);
    }, 400));

    // Hide search results on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-wrapper')) {
        hide(searchResults);
      }
    });

    // Activity selection
    $$('.activity-card').forEach(card => {
      card.addEventListener('click', () => {
        $$('.activity-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        selectedActivity = card.dataset.activity;
      });
    });

    // Medical condition selection
    $$('.medical-card').forEach(card => {
      card.addEventListener('click', () => {
        $$('.medical-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        selectedMedical = card.dataset.medical;
      });
    });

    // Predict button
    $('#btn-predict').addEventListener('click', handlePredict);

    // Theme toggle
    $('#theme-toggle').addEventListener('click', toggleTheme);

    // Model info
    $('#btn-model-info').addEventListener('click', showModelInfo);
    $('#footer-model-link').addEventListener('click', (e) => {
      e.preventDefault();
      showModelInfo();
    });

    // Close model modal
    $('#close-model-modal').addEventListener('click', () => {
      $('#model-modal').classList.remove('active');
    });
    
    $('#model-modal').addEventListener('click', (e) => {
      if (e.target === $('#model-modal')) {
        $('#model-modal').classList.remove('active');
      }
    });

    // Enable predict when place input has value
    placeInput.addEventListener('input', () => {
      // Allow manual coordinates or re-enable after place selection
      if (Search.selectedPlace) {
        $('#btn-predict').disabled = false;
      }
    });
  }

  // ─── Main Prediction ───
  async function handlePredict() {
    if (!Search.selectedPlace) {
      showToast('Please search and select a place first', 'error');
      return;
    }

    const place = Search.selectedPlace;
    const datetime = $('#datetime-input').value;
    const placeType = $('#place-type-select').value;

    if (!datetime) {
      showToast('Please select a date and time', 'error');
      return;
    }

    const params = {
      lat: place.lat,
      lon: place.lon,
      activity: selectedActivity,
      place_type: placeType,
      medical_condition: selectedMedical,
      datetime: datetime,
      place_name: place.name
    };

    lastPredictionParams = params;

    UI.showLoading('🤖 ML Model is analyzing safety...');

    try {
      // Run prediction, best time, and comparison in parallel
      const [predResult, bestTimeResult, compareResult] = await Promise.all([
        Api.predict(params),
        Api.getBestTime(params).catch(e => ({ success: false })),
        Api.compareActivities({
          lat: place.lat,
          lon: place.lon,
          place_type: placeType,
          medical_condition: selectedMedical,
          datetime: datetime
        }).catch(e => ({ success: false }))
      ]);

      UI.hideLoading();

      if (!predResult.success) {
        showToast('Prediction failed: ' + (predResult.error || 'Unknown error'), 'error');
        return;
      }

      // Render main result
      UI.renderResult(predResult);

      // Render timeline chart
      if (bestTimeResult.success && bestTimeResult.hourly) {
        show('#chart-section');
        Charts.renderTimeline(bestTimeResult.hourly);

        // Show best window info
        if (bestTimeResult.best_windows && bestTimeResult.best_windows.length > 0) {
          const bestW = bestTimeResult.best_windows[0];
          const bestHr = bestTimeResult.best_hour;
          if (predResult.prediction.label !== 3) {
            const msg = `💡 Best time: ${bestW.start_label} - ${bestW.end_label} (Score: ${bestW.avg_score})`;
            showToast(msg, 'success', 6000);
          }
        }
      }

      // Render activity comparison
      if (compareResult.success && compareResult.comparisons) {
        show('#compare-section');
        UI.renderComparison(compareResult.comparisons);
      }

      // Save to recent searches
      saveRecentSearch(params, predResult.prediction);

    } catch (error) {
      UI.hideLoading();
      console.error('Prediction error:', error);
      showToast('Error: ' + error.message + '. Make sure the backend server is running.', 'error', 6000);
    }
  }

  // ─── Theme Toggle ───
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    saveToStorage('theme', next);
    updateThemeIcon(next);
    Charts.updateTheme();
  }

  function updateThemeIcon(theme) {
    const btn = $('#theme-toggle');
    btn.innerHTML = theme === 'dark' 
      ? '<i data-lucide="sun" style="width:18px;height:18px"></i>'
      : '<i data-lucide="moon" style="width:18px;height:18px"></i>';
    if (window.lucide) lucide.createIcons();
  }

  // ─── Model Info ───
  async function showModelInfo() {
    const modal = $('#model-modal');
    modal.classList.add('active');
    
    try {
      const info = await Api.getModelInfo();
      UI.renderModelInfo(info);
    } catch (e) {
      UI.renderModelInfo({ success: false });
    }
  }

  // ─── Backend Health Check ───
  async function checkBackendHealth() {
    try {
      const health = await Api.healthCheck();
      if (health.status === 'ok') {
        console.log('✅ Backend connected. Model loaded:', health.model_loaded);
        if (!health.model_loaded) {
          showToast('⚠️ ML model not loaded. Please train the model first (python train_model.py)', 'error', 8000);
        }
      } else {
        showBackendWarning();
      }
    } catch (e) {
      showBackendWarning();
    }
  }

  function showBackendWarning() {
    showToast('⚠️ Backend not running. Start it with: cd backend && python app.py', 'error', 10000);
  }

  // ─── Recent Searches ───
  function saveRecentSearch(params, prediction) {
    const recents = loadFromStorage('recent_searches', []);
    recents.unshift({
      place: params.place_name,
      activity: params.activity,
      score: prediction.score,
      label: prediction.label_name,
      time: new Date().toISOString()
    });
    // Keep last 10
    saveToStorage('recent_searches', recents.slice(0, 10));
  }

  // ─── Start ───
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
