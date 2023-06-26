# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def landing_page():
    # List all available api routes
    return (
        f"Available Routes:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/tobs<br/>"
        f"/api/start/<start_date><br/>"
        f"/api/start-end/<start_date><end_date>"
    )

@app.route('/api/precipitation')
def get_precipitation():
    # Query the maximum date in the Measurement table
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year ago from the most recent date
    last_year = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)

    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()

    # Create a dictionary with date as key and precipitation as value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route('/api/stations')
def get_stations():
    # Query all stations in the database
    stations = session.query(Station).all()

    session.close()

    # Create a list to hold station data
    station_data = []

    # Iterate through stations and extract relevant information
    for station in stations:
        station_info = {
            'id': station.id,
            'name': station.name,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'elevation': station.elevation
        }
        station_data.append(station_info)

    return jsonify(station_data)

@app.route('/api/tobs')
def get_tobs():
    # Query the maximum date in the Measurement table
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year ago from the current date
    last_year = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)

    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()

    # Query temperature observations (tobs) for the last year from the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= last_year).\
        all()

    session.close()

    # Create a list of dictionaries with date and temperature data
    tobs_data = [{'date': date, 'tobs': tobs} for date, tobs in results]

    return jsonify(tobs_data)

@app.route('/api/start/<start_date>')
def get_temperatures_start(start_date):
    # Convert start_date to a datetime object
    start_date = datetime.strptime(start_date, '%Y-%m-%d')

    # Query min, max, and average temperatures from start_date to the end of the dataset
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    # Extract the temperature values from the query results
    min_temp, max_temp, avg_temp = results[0]

    # Create a dictionary with the temperature data
    temperature_data = {
        'min_temp': min_temp,
        'max_temp': max_temp,
        'avg_temp': avg_temp
    }

    return jsonify(temperature_data)

@app.route('/api/start-end/<start_date>/<end_date>')
def get_temperatures_start_end(start_date, end_date):
    # Convert start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Query min, max, and average temperatures from start_date to end_date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    session.close()

    # Extract the temperature values from the query results
    min_temp, max_temp, avg_temp = results[0]

    # Create a dictionary with the temperature data
    temperature_data = {
        'min_temp': min_temp,
        'max_temp': max_temp,
        'avg_temp': avg_temp
    }

    return jsonify(temperature_data)

if __name__ == '__main__':
    app.run()

