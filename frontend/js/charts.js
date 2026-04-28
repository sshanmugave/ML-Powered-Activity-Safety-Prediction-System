/**
 * SafeTravel - Chart.js Visualizations
 */

const Charts = {
  timelineChart: null,

  /**
   * Create the 24-hour safety timeline chart
   */
  renderTimeline(hourlyData) {
    const ctx = document.getElementById('timeline-chart');
    if (!ctx) return;

    // Destroy previous
    if (Charts.timelineChart) {
      Charts.timelineChart.destroy();
    }

    const labels = hourlyData.map(h => formatTime(h.hour));
    const scores = hourlyData.map(h => h.score);
    const colors = scores.map(s => scoreToHex(s));
    
    // Create gradient areas
    const bgColors = scores.map(s => {
      if (s >= 75) return 'rgba(34, 197, 94, 0.15)';
      if (s >= 55) return 'rgba(234, 179, 8, 0.15)';
      if (s >= 35) return 'rgba(249, 115, 22, 0.15)';
      return 'rgba(239, 68, 68, 0.15)';
    });

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    const textColor = isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)';

    Charts.timelineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Safety Score',
          data: scores,
          borderColor: function(context) {
            const idx = context.dataIndex;
            return colors[idx] || '#7c3aed';
          },
          backgroundColor: function(context) {
            const chart = context.chart;
            const {ctx: c, chartArea} = chart;
            if (!chartArea) return 'rgba(124, 58, 237, 0.1)';
            
            const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            gradient.addColorStop(0, 'rgba(124, 58, 237, 0.2)');
            gradient.addColorStop(1, 'rgba(124, 58, 237, 0.01)');
            return gradient;
          },
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: colors,
          pointBorderColor: colors,
          pointBorderWidth: 2,
          borderWidth: 2.5,
          segment: {
            borderColor: function(context) {
              const score = context.p1.parsed.y;
              return scoreToHex(score);
            }
          }
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: isDark ? 'rgba(20,20,35,0.95)' : 'rgba(255,255,255,0.95)',
            titleColor: isDark ? '#fff' : '#000',
            bodyColor: isDark ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.7)',
            borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
              title: function(items) {
                return `🕐 ${items[0].label}`;
              },
              label: function(item) {
                const score = item.raw;
                const hourData = hourlyData[item.dataIndex];
                let status = score >= 75 ? '🟢 Safe' : score >= 55 ? '🟡 Moderate' : score >= 35 ? '🟠 Risky' : '🔴 Unsafe';
                return [
                  `Score: ${Math.round(score)}/100 (${status})`,
                  `🌡️ ${hourData.temperature}°C • 🌫️ AQI ${hourData.aqi}`,
                  `☀️ UV ${hourData.uv} • ${hourData.weather}`
                ];
              }
            }
          },
          // Draw threshold zones
          annotation: undefined
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              font: { family: 'Inter', size: 11 },
              callback: v => v + '%'
            }
          },
          x: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              font: { family: 'Inter', size: 10 },
              maxTicksLimit: 12
            }
          }
        }
      }
    });
  },

  /**
   * Update chart theme when toggling dark/light
   */
  updateTheme() {
    // Re-render if data exists by triggering a resize
    if (Charts.timelineChart) {
      Charts.timelineChart.update();
    }
  }
};
