import requests
import schedule
import time
import sqlite3
import matplotlib.pyplot as plt
import datetime
import json

# Configuration settings
CONFIG = {
    "api_key": "346cde4f7e64bc99acb9b9abb7b7841a",
    "city": "Delhi",
    "temp_threshold": 35,  # Temperature threshold in Celsius
    "consecutive_updates": 2,  # Number of consecutive updates to trigger alert
    "update_interval_minutes": 5,  # Interval in minutes to fetch weather data
    "daily_summary_time": "23:59"  # Time to calculate daily summary
}

consecutive_high_temps = 0

def create_db():
    """Create a SQLite database to store weather data."""
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather
                 (city TEXT, main TEXT, temp REAL, feels_like REAL, dt INTEGER)''')
    conn.commit()
    conn.close()

def fetch_weather_data(city):
    """Fetch weather data from OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={CONFIG['api_key']}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        return {
            'main': data['weather'][0]['main'],
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'dt': data['dt']
        }
    else:
        print("Error fetching data:", data)
        return None

def insert_weather_data(city, main, temp, feels_like, dt):
    """Insert weather data into the database."""
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO weather (city, main, temp, feels_like, dt) VALUES (?, ?, ?, ?, ?)",
              (city, main, temp, feels_like, dt))
    conn.commit()
    conn.close()

def check_alert_conditions(temp):
    """Check if current temperature exceeds the threshold for consecutive updates."""
    global consecutive_high_temps

    if temp > CONFIG['temp_threshold']:
        consecutive_high_temps += 1
        if consecutive_high_temps >= CONFIG['consecutive_updates']:
            print(f"ALERT! Temperature has exceeded {CONFIG['temp_threshold']}°C for {CONFIG['consecutive_updates']} consecutive updates.")
            # Here, you can add email or SMS alert triggers if required.
    else:
        consecutive_high_temps = 0  # Reset counter if temperature is within threshold

def job():
    """Job to fetch weather data and insert into the database."""
    weather_data = fetch_weather_data(CONFIG['city'])
    if weather_data:
        insert_weather_data(CONFIG['city'], weather_data['main'], weather_data['temp'], weather_data['feels_like'], weather_data['dt'])
        print(weather_data)
        check_alert_conditions(weather_data['temp'])

def calculate_daily_summary():
    """Calculate and print the daily summary for stored weather data."""
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT date(datetime(dt, 'unixepoch')), 
               AVG(temp), 
               MAX(temp), 
               MIN(temp), 
               main 
        FROM weather 
        GROUP BY date(datetime(dt, 'unixepoch'))
    ''')
    
    rows = c.fetchall()
    if rows:
        for row in rows:
            date, avg_temp, max_temp, min_temp, dominant_condition = row
            print(f"Date: {date}")
            print(f"Average Temperature: {avg_temp:.2f} °C")
            print(f"Maximum Temperature: {max_temp:.2f} °C")
            print(f"Minimum Temperature: {min_temp:.2f} °C")
            print(f"Dominant Weather Condition: {dominant_condition}")
            print("-" * 40)
    else:
        print("No data available.")
    
    conn.close()

def plot_daily_temperature_trends(date):
    """Plot daily temperature trends for a specific date from the database."""
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    
    formatted_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    
    c.execute('''
        SELECT datetime(dt, 'unixepoch'), temp 
        FROM weather 
        WHERE date(datetime(dt, 'unixepoch')) = ?
    ''', (formatted_date,))
    
    rows = c.fetchall()
    if rows:
        times = [datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in rows]
        temperatures = [row[1] for row in rows]
        
        plt.figure(figsize=(10, 5))
        plt.plot(times, temperatures, marker='o')
        plt.title(f'Temperature Trends on {formatted_date}')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("No data available for the specified date.")
    
    conn.close()

def plot_historical_daily_summary():
    """Plot historical daily summaries for temperature data."""
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT date(datetime(dt, 'unixepoch')), 
               AVG(temp), 
               MAX(temp), 
               MIN(temp) 
        FROM weather 
        GROUP BY date(datetime(dt, 'unixepoch'))
    ''')
    
    rows = c.fetchall()
    if rows:
        dates = [datetime.datetime.strptime(row[0], "%Y-%m-%d").date() for row in rows]
        avg_temps = [row[1] for row in rows]
        max_temps = [row[2] for row in rows]
        min_temps = [row[3] for row in rows]
        
        plt.figure(figsize=(10, 5))
        plt.plot(dates, avg_temps, label='Average Temperature (°C)', marker='o')
        plt.plot(dates, max_temps, label='Maximum Temperature (°C)', marker='^')
        plt.plot(dates, min_temps, label='Minimum Temperature (°C)', marker='v')
        
        plt.title('Historical Daily Temperature Summary')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.legend(loc='best')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("No data available for historical summary.")
    
    conn.close()

# Save the configuration in JSON format
with open('config.json', 'w') as config_file:
    json.dump(CONFIG, config_file)

# Create database and table
create_db()

# Schedule the job to run every 5 minutes (or as per the configuration)
schedule.every(CONFIG['update_interval_minutes']).minutes.do(job)

# Schedule daily summary at the specified time
schedule.every().day.at(CONFIG['daily_summary_time']).do(calculate_daily_summary)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
