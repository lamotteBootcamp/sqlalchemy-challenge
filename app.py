from flask import Flask, jsonify

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, desc

# Database startup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect the existing database into a new model
Base = automap_base()

#reflect the tables
# Base.prepare(engine, reflect = True)
Base.prepare(autoload_with = engine)
#Save Reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask Route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create our link from Python to the DB
    session = Session(engine)

    # Querying the last 12 months of precipitation data
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= dt.date(2016, 8, 23)).\
    filter(Measurement.date <= dt.date(2017, 8, 23)).order_by(Measurement.date).all()
    
    session.close()

    # Convert list of tuples into normal list
    prcp_data = []
    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data) 

#New Route - Returns JSON of stations
@app.route("/api/v1.0/stations")
def stations():
#Creating session link
    session = Session(engine)

#Query all stations
    all_stations = session.query(Station.station, Station.name).all()


    session.close()
#Creating a list and return a JSON response
    station_list = list(np.ravel(all_stations))

    return jsonify(station_list) 

#New Route - Returns JSON of Tobs, identifying most active station for the past year, and returns JSON
@app.route("/api/v1.0/tobs")
def tobs():
#Creating session link
    session = Session(engine)

#Query dates and temp observations for the previous year, and finding station with highest activity
    station_activity = session.query(Station.station, func.count(Measurement.station)).filter(Measurement.station == Station.station).group_by(Station.station).\
    order_by(func.count(Station.station).desc()).all()
#Close session
    session.close()

#Create list and return JSON response
    highest_activity = list(np.ravel(station_activity))

    return jsonify(highest_activity)


@app.route("/api/v1.0/start/<start>")
@app.route("/api/v1.0/start_end/<start>/<end>")
def start_end(start, end = "2017-08-23"):
    # Create session link 
    session = Session(engine)

    # Query minimum temp, average temp, and maximum temp for specified start or start-end range
    station_activity = session.query(Station.station, func.count(Measurement.station)).filter(Measurement.station == Station.station).group_by(Station.station).\
    order_by(func.count(Station.station).desc()).all()
    most_id = station_activity[0][0]
    most_active = session.query(Measurement.station, func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.station == most_id).all()

    # Close session
    session.close()

    # Create list and return JSON response
    start_result = list(np.ravel(most_active))
    return jsonify(start_result)
    
    

if __name__ == '__main__':
    app.run(debug=True)