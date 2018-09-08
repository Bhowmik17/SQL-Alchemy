import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import numpy as np
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# create app
app = Flask(__name__)

################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    ### List all available api routes ###
        return(
            f"Welcome to the Hawaii Climate Analysis API! \n"
            f"Available routes: \n"
            f"/api/v1.0/precipitation \n"
            f"/api/v1.0/stations \n"
            f"/api/v1.0/tobs \n"
            f"/api/v1.0/temp/start/end \n"
        )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
        last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=last_year).all() #order_by(Measurement.date)
        precip = {}
        for row in precipitation:
            precip[row[0]] = row[1]
        return jsonify(precip)
    
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs = session.query(Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= last_year).all()
    temps = list(np.ravel(tobs))
    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def starts(start=None, end=None):
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        # TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
        results = session.query(*selection).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    # calculate TMIN`, `TAVG`, and `TMAX' for dates in between start and end
    results = session.query(*selection).filter(Measurement.date <= end).all()
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)
