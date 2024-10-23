# Real-Time Weather Monitoring System

## Overview
This project is a Real-Time Data Processing System for monitoring weather conditions using the OpenWeatherMap API. It retrieves and analyzes weather data for selected metropolitan cities in India, calculates daily summaries, triggers alerts based on temperature thresholds, and provides visualizations of temperature trends.

## Features
- **Real-Time Weather Data Retrieval**: Fetches weather data for selected cities every few minutes.
- **Daily Weather Summaries**: Calculates average, maximum, minimum temperatures, and dominant weather conditions daily.
- **Alerting System**: Triggers alerts when temperature exceeds user-defined thresholds.
- **Data Visualization**: Provides visual representations of daily temperature trends and historical summaries.
- **Configurable Settings**: Users can easily modify key parameters like city name and temperature thresholds through a configuration file.

## Technologies Used
- Python
- SQLite for database management
- Requests library for API calls
- Matplotlib for data visualization
- Schedule for task scheduling

## Setup Instructions

### Prerequisites
- Python 3.x installed on your machine.
- Required Python packages. You can install them using pip:

```bash
pip install requests matplotlib schedule

