import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://mlops-backend-j5im.onrender.com'
    : 'http://localhost:8000')

const FEATURE_FIELDS = [
  { name: 'MedInc', label: 'Median Income (tens of thousands)', placeholder: 'e.g. 8.3252', step: '0.0001' },
  { name: 'HouseAge', label: 'House Age (years)', placeholder: 'e.g. 41', step: '1' },
  { name: 'AveRooms', label: 'Average Rooms', placeholder: 'e.g. 6.98', step: '0.01' },
  { name: 'AveBedrms', label: 'Average Bedrooms', placeholder: 'e.g. 1.02', step: '0.01' },
  { name: 'Population', label: 'Population', placeholder: 'e.g. 322', step: '1' },
  { name: 'AveOccup', label: 'Average Occupancy', placeholder: 'e.g. 2.55', step: '0.01' },
  { name: 'Latitude', label: 'Latitude', placeholder: 'e.g. 37.88', step: '0.01' },
  { name: 'Longitude', label: 'Longitude', placeholder: 'e.g. -122.23', step: '0.01' },
]

function App() {
  const [formValues, setFormValues] = useState({
    MedInc: '', HouseAge: '', AveRooms: '', AveBedrms: '',
    Population: '', AveOccup: '', Latitude: '', Longitude: '',
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (name, value) => {
    setFormValues((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)

    const payload = {}
    for (const [key, val] of Object.entries(formValues)) {
      payload[key] = parseFloat(val)
    }

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error (${response.status})`)
      }
      const data = await response.json()
      setResult(data.prediction)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-container">
      <h1>California Housing Price Predictor</h1>
      <p className="subtitle">Enter housing features to predict the median house value</p>

      <form onSubmit={handleSubmit} className="prediction-form">
        <div className="form-grid">
          {FEATURE_FIELDS.map(({ name, label, placeholder, step }) => (
            <div key={name} className="form-field">
              <label htmlFor={name}>{label}</label>
              <input
                id={name}
                type="number"
                step={step}
                placeholder={placeholder}
                value={formValues[name]}
                onChange={(e) => handleChange(name, e.target.value)}
                required
              />
            </div>
          ))}
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Predicting…' : 'Predict'}
        </button>
      </form>

      {result !== null && (
        <div className="result-card success">
          <strong>Predicted Median House Value:</strong> ${(result * 100000).toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </div>
      )}

      {error && (
        <div className="result-card error">
          <strong>Error:</strong> {error}
        </div>
      )}
    </main>
  )
}

export default App
