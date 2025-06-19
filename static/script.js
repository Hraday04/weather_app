// Weather App JavaScript
let currentLocation = '';
let currentTab = 'current';

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Add enter key listener to search input
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchWeather();
        }
    });
    
    // Default location search
    searchWeather('Ahmedabad');
});

// Search weather by location
function searchWeather(location = null) {
    const searchInput = document.getElementById('searchInput');
    const query = location || searchInput.value.trim();
    
    if (!query) {
        showError('Please enter a location');
        return;
    }
    
    currentLocation = query;
    loadWeatherData();
}

// Get current location
function getCurrentLocation() {
    if (navigator.geolocation) {
        showLoading();
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                currentLocation = `${lat},${lon}`;
                loadWeatherData();
            },
            function(error) {
                console.error('Geolocation error:', error);
                showError('Unable to get your location. Please enter a city name.');
            }
        );
    } else {
        showError('Geolocation is not supported by this browser.');
    }
}

// Load weather data based on current tab
function loadWeatherData() {
    switch(currentTab) {
        case 'current':
            loadCurrentWeather();
            break;
        case 'forecast':
            loadForecast();
            break;
        case 'hourly':
            loadHourlyForecast();
            break;
    }
}

// Load current weather
function loadCurrentWeather() {
    showLoading();
    
    fetch(`/api/weather/current?location=${encodeURIComponent(currentLocation)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayCurrentWeather(data);
        })
        .catch(error => {
            console.error('Error fetching current weather:', error);
            showError('Unable to fetch weather data. Please try again.');
        });
}

// Load 5-day forecast
function loadForecast() {
    showLoading();
    
    fetch(`/api/weather/forecast?location=${encodeURIComponent(currentLocation)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayForecast(data);
        })
        .catch(error => {
            console.error('Error fetching forecast:', error);
            showError('Unable to fetch forecast data. Please try again.');
        });
}

// Load hourly forecast
function loadHourlyForecast() {
    showLoading();
    
    fetch(`/api/weather/hourly?location=${encodeURIComponent(currentLocation)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayHourlyForecast(data);
        })
        .catch(error => {
            console.error('Error fetching hourly forecast:', error);
            showError('Unable to fetch hourly forecast data. Please try again.');
        });
}

// Display current weather
function displayCurrentWeather(data) {
    const container = document.getElementById('weatherContainer');
    const current = data.current;
    const location = data.location;
    
    container.innerHTML = `
        <div class="weather-card">
            <div class="current-weather">
                <div class="weather-main">
                    <div class="weather-icon">
                        ${getWeatherIcon(current.icon)}
                    </div>
                    <div class="temperature">${current.temp}°C</div>
                    <div class="description">${current.description}</div>
                    <div class="location">${location.name}, ${location.country}</div>
                </div>
                <div class="weather-details">
                    <div class="detail-item">
                        <div class="detail-label">Feels Like</div>
                        <div class="detail-value">${current.feels_like}°C</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Humidity</div>
                        <div class="detail-value">${current.humidity}%</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Wind Speed</div>
                        <div class="detail-value">${current.wind_speed} m/s</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Pressure</div>
                        <div class="detail-value">${current.pressure} hPa</div>
                    </div>
                </div>
                <div class="additional-details">
                    <div class="detail-item">
                        <div class="detail-label">Min Temp</div>
                        <div class="detail-value">${current.temp_min}°C</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Max Temp</div>
                        <div class="detail-value">${current.temp_max}°C</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Visibility</div>
                        <div class="detail-value">${current.visibility} km</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Sunrise</div>
                        <div class="detail-value">${current.sunrise}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Sunset</div>
                        <div class="detail-value">${current.sunset}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Wind Direction</div>
                        <div class="detail-value">${current.wind_deg}°</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Display 5-day forecast
function displayForecast(data) {
    const container = document.getElementById('weatherContainer');
    
    const forecastItems = data.list.map(item => `
        <div class="forecast-item">
            <div class="forecast-day">${item.day}</div>
            <div class="forecast-icon">
                ${getWeatherIcon(item.icon)}
            </div>
            <div class="forecast-temp">
                <span class="temp-high">${item.temp_max}°</span>
                <span class="temp-low">${item.temp_min}°</span>
            </div>
            <div class="description">${item.description}</div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div class="weather-card">
            <div class="forecast-title">5-Day Forecast for ${data.city}, ${data.country}</div>
            <div class="forecast-grid">
                ${forecastItems}
            </div>
        </div>
    `;
}

// Display hourly forecast
function displayHourlyForecast(data) {
    const container = document.getElementById('weatherContainer');
    
    const hourlyItems = data.hourly.map(item => `
        <div class="forecast-item">
            <div class="forecast-day">${item.time}</div>
            <div class="forecast-icon">
                ${getWeatherIcon(item.icon)}
            </div>
            <div class="forecast-temp">
                <span class="temp-high">${item.temp}°C</span>
            </div>
            <div class="description">${item.description}</div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div class="weather-card">
            <div class="forecast-title">24-Hour Forecast for ${data.city}, ${data.country}</div>
            <div class="forecast-grid">
                ${hourlyItems}
            </div>
        </div>
    `;
}

// Switch tabs
function switchTab(tabName) {
    // Update active tab
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    
    currentTab = tabName;
    
    if (currentLocation) {
        loadWeatherData();
    }
}

// Show loading state
function showLoading() {
    const container = document.getElementById('weatherContainer');
    container.innerHTML = `
        <div class="weather-card">
            <div class="loading">
                <div class="loader"></div>
                <p>Loading weather data...</p>
            </div>
        </div>
    `;
}

// Show error message
function showError(message) {
    const container = document.getElementById('weatherContainer');
    container.innerHTML = `
        <div class="weather-card">
            <div class="error">
                <h3>⚠️ Error</h3>
                <p>${message}</p>
            </div>
        </div>
    `;
}

// Get weather icon
function getWeatherIcon(iconCode) {
    const iconMap = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '☁️',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️',
        '10d': '🌦️', '10n': '🌧️',
        '11d': '⛈️', '11n': '⛈️',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫️'
    };
    
    return iconMap[iconCode] || '🌤️';
}

// Utility function to format time
function formatTime(timestamp) {
    return new Date(timestamp * 1000).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add animation delays to forecast items
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    });
    
    // Observe forecast items for animation
    setTimeout(() => {
        document.querySelectorAll('.forecast-item').forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = 'all 0.5s ease';
            observer.observe(item);
        });
    }, 100);
});
