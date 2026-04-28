/**
 * SafeTravel - Utility Functions
 */

// ─── Debounce ───
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// ─── Date/Time Helpers ───
function formatDateTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short',
    hour: 'numeric', minute: '2-digit', hour12: true
  });
}

function formatTime(hour) {
  if (hour === 0) return '12 AM';
  if (hour === 12) return '12 PM';
  return hour < 12 ? `${hour} AM` : `${hour - 12} PM`;
}

function getNowDatetimeLocal() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

// ─── Color Helpers ───
function scoreToColor(score) {
  if (score >= 75) return 'var(--color-safe)';
  if (score >= 55) return 'var(--color-moderate)';
  if (score >= 35) return 'var(--color-risky)';
  return 'var(--color-unsafe)';
}

function scoreToHex(score) {
  if (score >= 75) return '#22c55e';
  if (score >= 55) return '#eab308';
  if (score >= 35) return '#f97316';
  return '#ef4444';
}

function scoreToClass(score) {
  if (score >= 75) return 'safe';
  if (score >= 55) return 'moderate';
  if (score >= 35) return 'risky';
  return 'unsafe';
}

function labelToClass(label) {
  return label.toLowerCase();
}

// ─── DOM Helpers ───
function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
}

function show(el) {
  if (typeof el === 'string') el = $(el);
  if (el) el.classList.remove('hidden');
}

function hide(el) {
  if (typeof el === 'string') el = $(el);
  if (el) el.classList.add('hidden');
}

// ─── Toast Notifications ───
function showToast(message, type = 'info', duration = 4000) {
  const container = $('#toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(50px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─── LocalStorage ───
function saveToStorage(key, value) {
  try {
    localStorage.setItem(`safetravel_${key}`, JSON.stringify(value));
  } catch (e) {
    console.warn('LocalStorage save failed:', e);
  }
}

function loadFromStorage(key, defaultValue = null) {
  try {
    const raw = localStorage.getItem(`safetravel_${key}`);
    return raw ? JSON.parse(raw) : defaultValue;
  } catch (e) {
    return defaultValue;
  }
}

// ─── Scroll Animation Observer ───
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  $$('.animate-on-scroll, .stagger-children').forEach(el => observer.observe(el));
}
