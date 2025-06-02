import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

class WeatherDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        
    def get_current_weather(self, city):
        """Fetch current weather data"""
        url = f"{self.base_url}weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current weather: {e}")
            return None
    
    def get_forecast(self, city):
        """Fetch 5-day weather forecast"""
        url = f"{self.base_url}forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def create_temperature_gauge(self, temp, ax):
        """Create a temperature gauge visualization"""
        # Create semicircle gauge
        theta = np.linspace(0, np.pi, 100)
        r = 1
        
        # Temperature ranges and colors
        temp_ranges = [(-20, 0, 'blue'), (0, 15, 'lightblue'), 
                      (15, 25, 'green'), (25, 35, 'orange'), (35, 50, 'red')]
        
        for i, (min_temp, max_temp, color) in enumerate(temp_ranges):
            start_angle = np.pi * (min_temp + 20) / 70
            end_angle = np.pi * (max_temp + 20) / 70
            theta_range = np.linspace(start_angle, end_angle, 50)
            ax.fill_between(theta_range, 0.8, 1, color=color, alpha=0.7)
        
        # Current temperature indicator
        temp_angle = np.pi * (temp + 20) / 70
        needle_x = [0, 0.9 * np.cos(temp_angle)]
        needle_y = [0, 0.9 * np.sin(temp_angle)]
        ax.plot(needle_x, needle_y, 'k-', linewidth=3)
        ax.plot(0, 0, 'ko', markersize=8)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'Temperature: {temp}°C', fontsize=14, fontweight='bold')
    
    def create_weather_icon(self, weather_main, ax):
        """Create weather icon based on condition"""
        ax.clear()
        
        weather_icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️'
        }
        
        icon = weather_icons.get(weather_main, '🌤️')
        ax.text(0.5, 0.5, icon, fontsize=60, ha='center', va='center', transform=ax.transAxes)
        ax.set_title(f'Condition: {weather_main}', fontsize=14, fontweight='bold')
        ax.axis('off')
    
    def create_circular_gauge(self, value, max_value, label, unit, ax, color='blue'):
        """Create a circular gauge for humidity, pressure, etc."""
        # Create circle
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False, linewidth=8, color='lightgray')
        ax.add_patch(circle)
        
        # Create value arc
        theta = 2 * np.pi * (value / max_value)
        arc_angles = np.linspace(0, theta, 100)
        x = 0.5 + 0.4 * np.cos(arc_angles - np.pi/2)
        y = 0.5 + 0.4 * np.sin(arc_angles - np.pi/2)
        
        for i in range(len(x)-1):
            ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color=color, linewidth=8)
        
        # Add text
        ax.text(0.5, 0.5, f'{value}{unit}', ha='center', va='center', 
                fontsize=16, fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.3, label, ha='center', va='center', 
                fontsize=12, transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
    
    def create_wind_compass(self, wind_speed, wind_direction, ax):
        """Create wind direction compass"""
        # Draw compass circle
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False, linewidth=2, color='black')
        ax.add_patch(circle)
        
        # Add compass directions
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        
        for direction, angle in zip(directions, angles):
            rad = np.radians(angle - 90)  # Adjust for matplotlib coordinates
            x = 0.5 + 0.45 * np.cos(rad)
            y = 0.5 + 0.45 * np.sin(rad)
            ax.text(x, y, direction, ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Draw wind direction arrow
        if wind_direction is not None:
            wind_rad = np.radians(wind_direction - 90)
            arrow_length = 0.3
            x_end = 0.5 + arrow_length * np.cos(wind_rad)
            y_end = 0.5 + arrow_length * np.sin(wind_rad)
            
            ax.annotate('', xy=(x_end, y_end), xytext=(0.5, 0.5),
                       arrowprops=dict(arrowstyle='->', lw=3, color='red'))
        
        ax.text(0.5, 0.1, f'Wind Speed: {wind_speed} m/s', ha='center', va='center', 
                fontsize=12, fontweight='bold', transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Wind Direction', fontsize=14, fontweight='bold')
    
    def create_forecast_chart(self, forecast_data, ax):
        """Create 5-day forecast chart"""
        if not forecast_data:
            return
            
        # Extract daily data (one entry per day at noon)
        daily_data = []
        for item in forecast_data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            if dt.hour == 12:  # Get noon data for each day
                daily_data.append({
                    'date': dt.strftime('%m/%d'),
                    'temp': item['main']['temp'],
                    'weather': item['weather'][0]['main']
                })
        
        if len(daily_data) < 5:
            # If we don't have enough noon data, take first 5 entries
            daily_data = []
            for i in range(0, min(40, len(forecast_data['list'])), 8):  # Every 8th entry (24 hours)
                item = forecast_data['list'][i]
                dt = datetime.fromtimestamp(item['dt'])
                daily_data.append({
                    'date': dt.strftime('%m/%d'),
                    'temp': item['main']['temp'],
                    'weather': item['weather'][0]['main']
                })
        
        dates = [item['date'] for item in daily_data[:5]]
        temps = [item['temp'] for item in daily_data[:5]]
        
        # Create bar chart
        bars = ax.bar(dates, temps, color=['skyblue' if t > 20 else 'lightcoral' if t < 10 else 'lightgreen' for t in temps])
        
        # Add temperature labels on bars
        for bar, temp in zip(bars, temps):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{temp:.1f}°C', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('5-Day Temperature Forecast', fontsize=14, fontweight='bold')
        ax.set_ylabel('Temperature (°C)')
        ax.grid(True, alpha=0.3)
    
    def create_dashboard(self, city):
        """Create comprehensive weather dashboard"""
        # Fetch data
        current_weather = self.get_current_weather(city)
        forecast_data = self.get_forecast(city)
        
        if not current_weather:
            print(f"Could not fetch weather data for {city}")
            return
        
        # Set up the dashboard
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle(f'Weather Dashboard - {city.title()}', fontsize=20, fontweight='bold')
        
        # Create subplots
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Current temperature gauge
        ax1 = fig.add_subplot(gs[0, 0])
        self.create_temperature_gauge(current_weather['main']['temp'], ax1)
        
        # Weather icon
        ax2 = fig.add_subplot(gs[0, 1])
        self.create_weather_icon(current_weather['weather'][0]['main'], ax2)
        
        # Humidity gauge
        ax3 = fig.add_subplot(gs[0, 2])
        self.create_circular_gauge(current_weather['main']['humidity'], 100, 
                                 'Humidity', '%', ax3, 'green')
        
        # Pressure gauge
        ax4 = fig.add_subplot(gs[0, 3])
        pressure = current_weather['main']['pressure']
        self.create_circular_gauge(pressure, 1200, 'Pressure', ' hPa', ax4, 'purple')
        
        # Wind compass
        ax5 = fig.add_subplot(gs[1, :2])
        wind_speed = current_weather.get('wind', {}).get('speed', 0)
        wind_direction = current_weather.get('wind', {}).get('deg', None)
        self.create_wind_compass(wind_speed, wind_direction, ax5)
        
        # Current weather details
        ax6 = fig.add_subplot(gs[1, 2:])
        ax6.axis('off')
        
        # Weather details text
        details = [
            f"Temperature: {current_weather['main']['temp']:.1f}°C",
            f"Feels like: {current_weather['main']['feels_like']:.1f}°C",
            f"Description: {current_weather['weather'][0]['description'].title()}",
            f"Humidity: {current_weather['main']['humidity']}%",
            f"Pressure: {current_weather['main']['pressure']} hPa",
            f"Visibility: {current_weather.get('visibility', 'N/A')} m",
            f"UV Index: Not available in free API"
        ]
        
        for i, detail in enumerate(details):
            ax6.text(0.1, 0.9 - i*0.12, detail, fontsize=12, transform=ax6.transAxes)
        
        ax6.set_title('Current Weather Details', fontsize=14, fontweight='bold')
        
        # 5-day forecast
        ax7 = fig.add_subplot(gs[2, :])
        self.create_forecast_chart(forecast_data, ax7)
        
        plt.tight_layout()
        plt.show()
        
        return fig

def main():
    # Get API key and city from user
    print("Weather Dashboard Creator")
    print("=" * 30)
    
    api_key = input("Enter your OpenWeatherMap API key: ").strip()
    if not api_key:
        print("API key is required!")
        return
    
    city = input("Enter city name: ").strip()
    if not city:
        print("City name is required!")
        return
    
    # Create dashboard
    dashboard = WeatherDashboard(api_key)
    fig = dashboard.create_dashboard(city)
    
    if fig:
        # Save the dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_dashboard_{city}_{timestamp}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nDashboard saved as: {filename}")

if __name__ == "__main__":
    main()
