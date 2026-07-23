# 🌱 Green Google Maps – AI-Based Eco Route Optimizer

An intelligent route optimization system that uses **Machine Learning and Maps APIs** to suggest fuel-efficient and eco-friendly routes. The project combines a trained Random Forest model with TomTom APIs to estimate vehicle efficiency and provide smarter navigation decisions.

## 🚀 Features

- 🚗 Vehicle type and fuel type selection
- 📍 Source and destination location input
- 🌍 Real-time geocoding using TomTom Geocoding API
- 🛣️ Route generation using TomTom Routing API
- 🤖 Machine Learning-based fuel efficiency prediction
- 🌱 Focus on reducing fuel consumption and carbon emissions
- 📊 Interactive Streamlit web application

## 🧠 Machine Learning Model

The project uses a **Random Forest Regression model** to predict vehicle efficiency based on:

- Vehicle Type
- Fuel Type
- Other vehicle-related parameters

Categorical features are processed using encoders before being passed into the trained model.

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Scikit-learn**
- **Pandas**
- **NumPy**
- **TomTom Maps API**
- **Joblib**

## 📂 Project Structure

```
GreenGoogleMaps/
│
├── app.py                  # Streamlit application
├── model/
│   └── random_forest.pkl   # Trained ML model
│
├── encoders/
│   ├── vehicle_encoder.pkl
│   └── fuel_encoder.pkl
│
├── utils/
│   └── helper functions
│
├── dataset/
│   └── vehicle dataset
│
├── requirements.txt
└── README.md
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/GreenGoogleMaps.git
```

Navigate to the project folder:

```bash
cd GreenGoogleMaps
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔑 API Configuration

This project requires a **TomTom API Key**.

Add your API key inside your configuration file or environment variable:

```
TOMTOM_API_KEY = "your_api_key"
```

## ▶️ Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The application will open in your browser.

## 📊 Workflow

1. User enters source and destination locations.
2. TomTom Geocoding API converts locations into coordinates.
3. TomTom Routing API generates possible routes.
4. Vehicle and fuel details are processed.
5. ML model predicts fuel efficiency.
6. The system provides an eco-friendly route recommendation.

## 🔮 Future Improvements

- Add live traffic data integration
- Improve fuel consumption prediction accuracy
- Add carbon emission calculations
- Compare multiple routes based on environmental impact
- Deploy with cloud infrastructure

## 👨‍💻 Author
**Suresh Chaudhary**

B.Tech IT | Data Science & Machine Learning Enthusiast

**Suresh Chaudhary**

B.Tech IT | Data Science & Machine Learning Enthusiast
