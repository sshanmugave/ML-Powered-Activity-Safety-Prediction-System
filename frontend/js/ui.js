/**
 * SafeTravel - UI Rendering Module
 */

const UI = {
  /**
   * Render the main safety result
   */
  renderResult(data) {
    // Show result section
    show('#result-section');

    // Header info
    $('#result-place-name').textContent = `📍 ${data.place_name}`;
    $('#result-activity').innerHTML = `
      <span>${data.activity.icon}</span>
      <span>${data.activity.label}</span>
      <span style="margin:0 8px;color:var(--text-muted)">•</span>
      <span>${data.place_type.icon} ${data.place_type.label}</span>
      <span style="margin:0 8px;color:var(--text-muted)">•</span>
      <span>🕐 ${formatDateTime(data.datetime)}</span>
    `;

    // Medical condition info if not "none"
    if (data.medical_condition.key !== 'none') {
      $('#result-activity').innerHTML += `
        <span style="margin:0 8px;color:var(--text-muted)">•</span>
        <span>${data.medical_condition.icon} ${data.medical_condition.label}</span>
      `;
    }

    // Safety gauge
    const score = Math.round(data.prediction.score);
    const color = scoreToColor(score);
    const circumference = 2 * Math.PI * 95; // r=95

    const ring = $('#score-ring');
    ring.style.stroke = color;
    ring.style.strokeDasharray = circumference;
    // Animate from 0 to score
    ring.style.strokeDashoffset = circumference;
    requestAnimationFrame(() => {
      ring.style.strokeDashoffset = circumference - (score / 100) * circumference;
    });

    // Score number animation
    UI.animateNumber('#gauge-score', 0, score, 1200);
    
    $('#gauge-label').textContent = data.prediction.label_name;
    $('#gauge-label').style.color = color;
    $('#gauge-confidence').textContent = `ML Confidence: ${(data.prediction.confidence * 100).toFixed(1)}%`;

    // Status badge
    const badgeClass = labelToClass(data.prediction.label_name);
    const badge = $('#status-badge');
    badge.className = `status-badge ${badgeClass}`;
    $('#status-emoji').textContent = data.prediction.emoji;
    $('#status-text').textContent = data.prediction.label_name;

    // Status message
    $('#status-message').textContent = data.prediction.message;

    // Pollution details (O3 / NO2) if available
    if (data.o3 !== undefined || data.no2 !== undefined) {
      $('#o3-value').textContent = data.o3 ? `${data.o3.toFixed(1)} ppb` : 'N/A';
      $('#no2-value').textContent = data.no2 ? `${data.no2.toFixed(1)} ppb` : 'N/A';
      if (data.pollution_site) {
        $('#site-location').textContent = `Site ${data.pollution_site} · ${data.pollution_distance_km ?? ''} km`;
      }
    }

    // Factor cards
    UI.renderFactors(data.factors);

    // Health tips
    UI.renderTips(data.health_tips);

    // Scroll to results
    setTimeout(() => {
      $('#result-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
      initScrollAnimations();
    }, 300);
  },

  /**
   * Render factor breakdown cards
   */
  renderFactors(factors) {
    const grid = $('#factors-grid');
    
    const factorConfig = [
      { key: 'aqi', title: 'Air Quality', icon: '🌫️', cssClass: 'aqi', color: 'var(--color-aqi)' },
      { key: 'temperature', title: 'Temperature', icon: '🌡️', cssClass: 'temp', color: 'var(--color-temp)' },
      { key: 'weather', title: 'Weather', icon: '⛅', cssClass: 'weather', color: 'var(--color-weather)' },
      { key: 'uv', title: 'UV Index', icon: '☀️', cssClass: 'uv', color: 'var(--color-uv)' },
      { key: 'crowd', title: 'Crowd Level', icon: '👥', cssClass: 'crowd', color: 'var(--color-crowd)' }
    ];

    grid.innerHTML = factorConfig.map(fc => {
      const f = factors[fc.key];
      const fColor = scoreToColor(f.score);
      
      let displayValue = f.label;
      if (fc.key === 'aqi') {
        displayValue = `${f.label}`;
      }

      return `
        <div class="glass-card factor-card ${fc.cssClass} hover-lift">
          <div class="factor-icon">${fc.icon}</div>
          <div class="factor-title">${fc.title}</div>
          <div class="factor-value" style="color:${fColor}">${f.score}</div>
          <div class="factor-label">${displayValue}</div>
          ${fc.key === 'aqi' ? `<div class="factor-label" style="font-size:0.65rem;margin-top:2px">PM2.5: ${f.pm25}µg/m³</div>` : ''}
          <div class="factor-score-bar">
            <div class="factor-score-fill" style="width:${f.score}%;background:${fColor}"></div>
          </div>
        </div>
      `;
    }).join('');

    // Trigger stagger animation
    grid.classList.add('stagger-children');
    requestAnimationFrame(() => grid.classList.add('visible'));
  },

  /**
   * Render health tips
   */
  renderTips(tips) {
    const grid = $('#tips-grid');
    
    if (!tips || tips.length === 0) {
      hide('#tips-section');
      return;
    }
    
    show('#tips-section');

    const tipIcons = ['💡', '⚠️', '🩺', '🛡️', '💊', '🧴', '🥤', '👓'];
    
    grid.innerHTML = tips.map((tip, i) => `
      <div class="tip-card hover-lift">
        <span class="tip-icon">${tipIcons[i % tipIcons.length]}</span>
        <span class="tip-text">${tip}</span>
      </div>
    `).join('');
  },

  /**
   * Render activity comparison
   */
  renderComparison(comparisons) {
    const grid = $('#compare-grid');
    
    grid.innerHTML = comparisons.map(c => {
      const colorClass = labelToClass(c.label);
      const bgColorVar = `var(--color-${colorClass}-bg)`;
      const colorVar = `var(--color-${colorClass})`;

      return `
        <div class="compare-bar hover-lift">
          <div class="compare-emoji">${c.activity_icon}</div>
          <div class="compare-name">${c.activity_label}</div>
          <div class="compare-score" style="color:${colorVar}">${Math.round(c.score)}</div>
          <div class="compare-label-badge" style="background:${bgColorVar};color:${colorVar}">
            ${c.label}
          </div>
        </div>
      `;
    }).join('');
  },

  /**
   * Render model info modal
   */
  renderModelInfo(info) {
    const stats = $('#model-stats');
    const details = $('#model-details');

    if (!info.success && !info.models) {
      stats.innerHTML = '<p style="color:var(--text-tertiary)">Model metrics not available. Train the model first.</p>';
      return;
    }

    const bestModel = info.best_model || 'random_forest';
    const modelData = info.models?.[bestModel] || {};

    stats.innerHTML = `
      <div class="glass-card model-stat">
        <div class="stat-value">${((modelData.accuracy || 0) * 100).toFixed(1)}%</div>
        <div class="stat-label">Accuracy</div>
      </div>
      <div class="glass-card model-stat">
        <div class="stat-value">${((modelData.f1_score || 0) * 100).toFixed(1)}%</div>
        <div class="stat-label">F1 Score</div>
      </div>
      <div class="glass-card model-stat">
        <div class="stat-value">${((modelData.precision || 0) * 100).toFixed(1)}%</div>
        <div class="stat-label">Precision</div>
      </div>
      <div class="glass-card model-stat">
        <div class="stat-value">${((modelData.recall || 0) * 100).toFixed(1)}%</div>
        <div class="stat-label">Recall</div>
      </div>
    `;

    details.innerHTML = `
      <div class="glass-card" style="padding:20px">
        <h4 style="margin-bottom:12px">📋 Model Details</h4>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.875rem">
          <div><span style="color:var(--text-tertiary)">Best Model:</span></div>
          <div style="font-weight:600">${bestModel.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</div>
          <div><span style="color:var(--text-tertiary)">Features:</span></div>
          <div style="font-weight:600">${info.n_features || 28}</div>
          <div><span style="color:var(--text-tertiary)">Classes:</span></div>
          <div style="font-weight:600">${(info.classes || []).join(', ')}</div>
          <div><span style="color:var(--text-tertiary)">CV Accuracy:</span></div>
          <div style="font-weight:600">${((modelData.cv_mean || 0) * 100).toFixed(1)}% ± ${((modelData.cv_std || 0) * 100).toFixed(1)}%</div>
        </div>
      </div>
      ${info.models && Object.keys(info.models).length > 1 ? `
        <div class="glass-card" style="padding:20px;margin-top:12px;">
          <h4 style="margin-bottom:12px">🔄 Model Comparison</h4>
          <table style="width:100%;font-size:0.875rem;border-collapse:collapse;">
            <tr style="border-bottom:1px solid var(--border-color)">
              <th style="text-align:left;padding:8px;color:var(--text-tertiary)">Model</th>
              <th style="text-align:right;padding:8px;color:var(--text-tertiary)">Accuracy</th>
              <th style="text-align:right;padding:8px;color:var(--text-tertiary)">F1</th>
            </tr>
            ${Object.entries(info.models).map(([name, m]) => `
              <tr style="border-bottom:1px solid var(--border-color)">
                <td style="padding:8px;font-weight:${name === bestModel ? '700' : '400'}">${name === bestModel ? '🏆 ' : ''}${name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
                <td style="text-align:right;padding:8px">${(m.accuracy * 100).toFixed(1)}%</td>
                <td style="text-align:right;padding:8px">${(m.f1_score * 100).toFixed(1)}%</td>
              </tr>
            `).join('')}
          </table>
        </div>
      ` : ''}
    `;
  },

  /**
   * Animate a number from start to end
   */
  animateNumber(selector, start, end, duration = 1000) {
    const el = $(selector);
    if (!el) return;
    
    const startTime = performance.now();
    const range = end - start;

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + range * eased);
      
      el.textContent = current;
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    
    requestAnimationFrame(update);
  },

  /**
   * Show loading state
   */
  showLoading(text = 'Analyzing safety conditions...') {
    $('#loading-text').textContent = text;
    $('#loading-overlay').classList.add('active');
  },

  /**
   * Hide loading state
   */
  hideLoading() {
    $('#loading-overlay').classList.remove('active');
  }
};
