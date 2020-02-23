# dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# batabase setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app
app = Flask(__name__)

# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
    f"Available routes:<br>"
    f"/api/v1.0/precipitation - Rain Level Observations Over Last Year<br>"
    f"/api/v1.0/stations - List of Weather Stations<br>"
    f"/api/v1.0/tobs - Temperature Observations Over Last Year<br>"
    f"/api/v1.0/<start> - Min/Average/Max Temperature Observations from Specified Start Date yyyy-mm-dd <br>"
    f"/api/v1.0/<start>/<end> - Min/Average/Max Temperature Observations between Two Specified Dates yyyy-mm-dd/yyyy-mm-dd")


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    prcp = [Measurement.date, Measurement.prcp]

    # Calculate the date 1 year ago from the last data point in the database
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc)[0]
    start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    year_prcp = session.query(*prcp).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date)

    # create dictionary for JSON
    precipitation = []
    for date, prcp in year_prcp:
        data = {}
        data['date'] = date
        data['prcp'] = prcp
        precipitation.append(data)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.name, Station.station, Station.elevation).all()
    session.close()

    #create dictionary for JSON
    station_list = []
    for result in stations:
        row = {}
        row['name'] = result[0]
        row['station'] = result[1]
        row['elevation'] = result[2]
        station_list.append(row)
    return jsonify(station_list)
    
    

@app.route("/api/v1.0/tobs")
def temperature_tobs():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    # end_date = session.query(Measurement.date).order_by(Measurement.date.desc)[0]
    # start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)

    year_station_temp = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").all()
    session.close()

    #use dictionary, create json
    tobs_list = []
    for result in year_station_temp:
        row = {}
        row["Date"] = result[0]
        row["Station"] = result[1]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    session = Session(engine)
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
        func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list = list(from_start)
    session.close()
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    session = Session(engine)  
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list = list(between_dates)
    session.close()
    return jsonify(between_dates_list)

if __name__ == "__main__":
    app.run(debug=True)
