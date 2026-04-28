# 🤝 Contributing to SafeTravel

Thank you for interest in contributing to **SafeTravel**! This document outlines guidelines and best practices for contributing.

## 📋 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Follow the project's coding standards
- Test your changes before submitting

## 🐛 Reporting Bugs

Found a bug? Please open an **Issue** on GitHub with:

1. **Title:** Clear, concise description
2. **Description:** What happened? Expected vs actual behavior
3. **Steps to reproduce:** Exact steps to trigger the bug
4. **Environment:** OS, Python version, Node.js version
5. **Error message:** Full error trace if applicable

**Example:**
```
Title: Search crashes on empty input
Description: When I click search with empty text, app crashes
Steps: 1. Load app 2. Leave search empty 3. Click search button
Environment: Windows 11, Python 3.11, Node 18
Error: ValueError: location cannot be None
```

## 💡 Feature Requests

Have an idea? Open an **Issue** with:

1. **What:** Feature description
2. **Why:** Problem it solves or value it adds
3. **How:** Suggested implementation (optional)
4. **Use case:** Real-world example

## 🔄 Pull Request Process

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/ML-Powered-Activity-Safety-Prediction-System.git
cd "ML-Powered-Activity-Safety-Prediction-System"
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/issue-description
```

### 3. Make Changes

- Follow coding standards
- Write clear commit messages
- Test thoroughly

### 4. Commit & Push

```bash
git add .
git commit -m "feat: Add descriptive commit message"
git push origin feature/your-feature-name
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
- `feat(backend): add email notifications`
- `fix(frontend): correct dark mode toggle`
- `docs: update installation guide`

### 5. Create Pull Request

1. Go to GitHub and create PR
2. Link related issues: `Fixes #123`
3. Describe changes clearly
4. Wait for review

### 6. Review & Merge

- Address feedback
- Rebase if needed
- Maintainers will merge when approved

---

## 📝 Coding Standards

### Python (Backend)

```python
# Follow PEP 8
# Use type hints when possible
def predict_safety(lat: float, lon: float) -> dict:
    """Predict safety level for location.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        dict: Prediction result with safety level
    """
    pass

# Use meaningful names
ACTIVITIES = {...}  # CONSTANT_NAMES
def calculate_score():  # function_names
    local_var = 0  # variable_names
```

### JavaScript (Frontend)

```javascript
// Use ES6+ syntax
// Clear function and variable names
const calculateSafetyScore = (factors) => {
  // Implementation
};

// Use const by default, let if reassignment needed
const API_ENDPOINT = 'http://localhost:5000';

// JSDoc for public functions
/**
 * Fetches prediction from API
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<Object>} Prediction result
 */
async function predictSafety(lat, lon) {
  // Implementation
}
```

### File Structure

```
backend/
├── app.py              # Main Flask app
├── config.py           # Configuration
├── safety_engine.py    # Core logic
├── pollution_engine.py # Pollution predictions
├── weather_service.py  # Weather API
└── tests/              # Unit tests

frontend/
├── index.html          # Main template
├── js/
│   ├── main.js         # Entry point
│   ├── api.js          # API client
│   └── utils.js        # Utilities
└── css/
    └── index.css       # Styles
```

---

## 🧪 Testing

### Backend Tests

```bash
python -m pytest backend/tests/
# or
python -m unittest discover backend/tests/
```

**Write tests for new features:**
```python
import unittest
from app import app

class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_predict_endpoint(self):
        response = self.app.post('/api/predict', json={
            'lat': 28.59, 'lon': 77.22,
            'activity': 'jogging', 'place_type': 'park'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('prediction', response.json)
```

### Frontend Tests (Optional)

```bash
npm test  # When testing framework added
```

---

## 📚 Documentation

### Update README.md when:
- Adding features
- Changing API endpoints
- Modifying setup process

### Add comments for:
- Complex algorithms
- Non-obvious logic
- External dependencies
- Configuration options

### Use docstrings:
```python
def engineer_features(weather, aqi, activity, **kwargs):
    """Engineer features for ML model.
    
    This function takes raw weather and AQI data and
    creates a feature vector suitable for model prediction.
    
    Args:
        weather (dict): Weather data from OpenWeatherMap
        aqi (dict): Air quality data
        activity (str): Activity type
        **kwargs: Additional parameters
    
    Returns:
        tuple: (features_array, factor_details_dict)
    
    Raises:
        ValueError: If required fields missing
    
    Example:
        >>> features, details = engineer_features(w, a, 'jogging')
    """
    pass
```

---

## 🎯 Areas for Contribution

### Backend (Python)
- [ ] Add more ML models
- [ ] Implement caching for API calls
- [ ] Add database integration
- [ ] Write unit tests
- [ ] Optimize model performance
- [ ] Add data validation

### Frontend (JavaScript)
- [ ] Add more chart types
- [ ] Improve UI/UX
- [ ] Add dark mode improvements
- [ ] Mobile responsiveness
- [ ] Accessibility features
- [ ] Browser compatibility

### Documentation
- [ ] Expand setup guide
- [ ] Add architecture diagrams
- [ ] Create video tutorials
- [ ] Improve code comments
- [ ] API documentation

### DevOps
- [ ] Docker containerization
- [ ] CI/CD pipelines
- [ ] Deployment automation
- [ ] Performance optimization

---

## ✅ Checklist Before Submitting PR

- [ ] Code follows project style
- [ ] Tests written and passing
- [ ] No hardcoded values
- [ ] Docstrings added
- [ ] README updated if needed
- [ ] No API keys or secrets committed
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] Related issues linked

---

## 📞 Questions?

- **Issues:** Ask in GitHub Issues
- **Discussions:** Use GitHub Discussions
- **Email:** maintainer@example.com

## 🙏 Thank You!

Your contributions make SafeTravel better for everyone! 🌟

---

**Happy contributing!** 🚀
