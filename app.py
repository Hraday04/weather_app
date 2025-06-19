from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '872c70dc0e781baeeedab7c584da265e')
BASE_URL = 'https://api.openweathermap.org/data/2.5'

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = BASE_URL
    
    def get_current_weather(self, location):
        """Get current weather data for a location"""
        try:
            if self._is_coordinates(location):
                lat, lon = location.split(',')
                url = f"{self.base_url}/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            else:
                url = f"{self.base_url}/weather?q={location}&appid={self.api_key}&units=metric"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_current_weather(data)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return None
    
    def get_forecast(self, location):
        """Get 5-day weather forecast"""
        try:
            if self._is_coordinates(location):
                lat, lon = location.split(',')
                url = f"{self.base_url}/forecast?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            else:
                url = f"{self.base_url}/forecast?q={location}&appid={self.api_key}&units=metric"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_forecast(data)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            return None
    
    def get_hourly_forecast(self, location):
        """Get hourly forecast (using 5-day forecast data filtered for next 24 hours)"""
        try:
            forecast_data = self.get_forecast(location)
            if not forecast_data:
                return None
            
            # Filter for next 24 hours
            current_time = datetime.now()
            next_24_hours = current_time + timedelta(hours=24)
            
            hourly_data = []
            for item in forecast_data['list'][:8]:  # Take first 8 entries (24 hours)
                hourly_data.append({
                    'dt': item['dt'],
                    'time': item['time'],
                    'temp': item['temp'],
                    'weather': item['weather'],
                    'description': item['description'],
                    'icon': item['icon']
                })
            
            return {
                'city': forecast_data['city'],
                'country': forecast_data['country'],
                'hourly': hourly_data
            }
        
        except Exception as e:
            logger.error(f"Error processing hourly forecast: {e}")
            return None
    
    def get_weather_by_coordinates(self, lat, lon):
        """Get weather data by latitude and longitude"""
        location = f"{lat},{lon}"
        return self.get_current_weather(location)
    
    def _is_coordinates(self, location):
        """Check if location string contains coordinates"""
        try:
            parts = location.split(',')
            if len(parts) == 2:
                float(parts[0])
                float(parts[1])
                return True
        except:
            pass
        return False
    
    def _format_current_weather(self, data):
        """Format current weather data"""
        return {
            'location': {
                'name': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            },
            'current': {
                'temp': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'temp_min': round(data['main']['temp_min'], 1),
                'temp_max': round(data['main']['temp_max'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'uv_index': data.get('uvi', 0),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_forecast(self, data):
        """Format 5-day forecast data"""
        daily_forecasts = {}
        
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            date_str = date.strftime('%Y-%m-%d')
            
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    'date': date_str,
                    'day': date.strftime('%A'),
                    'temps': [],
                    'weather_conditions': [],
                    'dt': item['dt'],
                    'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                }
            
            daily_forecasts[date_str]['temps'].append({
                'temp': item['main']['temp'],
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max']
            })
            
            daily_forecasts[date_str]['weather_conditions'].append({
                'main': item['weather'][0]['main'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon']
            })
        
        # Process daily summaries
        forecast_list = []
        for date_str, day_data in list(daily_forecasts.items())[:5]:  # Only 5 days
            temps = [t['temp'] for t in day_data['temps']]
            temp_mins = [t['temp_min'] for t in day_data['temps']]
            temp_maxs = [t['temp_max'] for t in day_data['temps']]
            
            # Get most common weather condition
            weather_counts = {}
            for condition in day_data['weather_conditions']:
                main = condition['main']
                if main in weather_counts:
                    weather_counts[main] += 1
                else:
                    weather_counts[main] = 1
            
            most_common_weather = max(weather_counts, key=weather_counts.get)
            weather_info = next(w for w in day_data['weather_conditions'] if w['main'] == most_common_weather)
            
            forecast_list.append({
                'dt': day_data['dt'],
                'time': day_data['time'],
                'date': day_data['date'],
                'day': day_data['day'],
                'temp': round(sum(temps) / len(temps), 1),
                'temp_min': round(min(temp_mins), 1),
                'temp_max': round(max(temp_maxs), 1),
                'weather': weather_info['main'],
                'description': weather_info['description'],
                'icon': weather_info['icon']
            })
        
        return {
            'city': data['city']['name'],
            'country': data['city']['country'],
            'list': forecast_list
        }

# Initialize weather service
weather_service = WeatherService(OPENWEATHER_API_KEY)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/weather/current')
def get_current_weather():
    """API endpoint for current weather"""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400
    
    weather_data = weather_service.get_current_weather(location)
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'Unable to fetch weather data'}), 500

@app.route('/api/weather/forecast')
def get_forecast():
    """API endpoint for 5-day forecast"""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400
    
    forecast_data = weather_service.get_forecast(location)
    if forecast_data:
        return jsonify(forecast_data)
    else:
        return jsonify({'error': 'Unable to fetch forecast data'}), 500

@app.route('/api/weather/hourly')
def get_hourly_forecast():
    """API endpoint for hourly forecast"""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400
    
    hourly_data = weather_service.get_hourly_forecast(location)
    if hourly_data:
        return jsonify(hourly_data)
    else:
        return jsonify({'error': 'Unable to fetch hourly forecast data'}), 500

@app.route('/api/weather/coordinates')
def get_weather_by_coordinates():
    """API endpoint for weather by coordinates"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude parameters are required'}), 400
    
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({'error': 'Invalid latitude or longitude values'}), 400
    
    weather_data = weather_service.get_weather_by_coordinates(lat, lon)
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'Unable to fetch weather data'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if API key is configured
    if OPENWEATHER_API_KEY == 'your_api_key_here':
        print("⚠️  WARNING: OpenWeatherMap API key not configured!")
        print("   Set the OPENWEATHER_API_KEY environment variable or update the code.")
        print("   Get your free API key from: https://openweathermap.org/api")
    
    print("🌤️  Weather App Starting...")
    print(f"🔗  Access the app at: http://localhost:5600")
    print(f"📊  API Health Check: http://localhost:5600/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5600)
