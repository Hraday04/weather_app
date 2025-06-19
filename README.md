# WeatherScope - Modern Weather Forecasting App

A beautiful, responsive weather application built with Flask and vanilla JavaScript.

## Features

- 🌤️ Current weather conditions
- 📅 5-day weather forecast
- ⏰ 24-hour hourly forecast
- 📍 Location-based weather (GPS)
- 🎨 Modern, responsive design
- 🔄 Real-time data from OpenWeatherMap API

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your free API key:**
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up and get your free API key

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenWeatherMap API key
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   - Go to `http://localhost:5000`

## API Endpoints

- `GET /api/weather/current?location=city` - Current weather
- `GET /api/weather/forecast?location=city` - 5-day forecast
- `GET /api/weather/hourly?location=city` - Hourly forecast
- `GET /api/weather/coordinates?lat=X&lon=Y` - Weather by coordinates
- `GET /api/health` - Health check

## Tech Stack

- **Backend:** Flask, Python
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **API:** OpenWeatherMap
- **Styling:** Custom CSS with modern design

## Features

- Responsive design for all devices
- Smooth animations and transitions
- Geolocation support
- Error handling
- Loading states
- Weather icons
