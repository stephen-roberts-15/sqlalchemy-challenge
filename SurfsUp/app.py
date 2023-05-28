# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")





# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f'Welcome!'
        f"Available Routes: <br/>"
        f"Precipitation: /api/v1.0/precipitation <br/>"
        f"Stations: /api/v1.0/stations <br/>"
        f"Temperature for the previous year: /api/v1.0/tobs <br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"


    )
@app.route("/api/v1.0/precipitation")
def precipitation():
        #creating session for python to pull from database
        session = Session(engine)
        #determining the last measurment date in the dataset
        last_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
        date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

        #defining year from last as one year prior to the last measurment date for final year data
        year_from_last = date - dt.timedelta(days = 365)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_from_last).all()
        prcp_query = []
        session.close()

        #creating dictionary for row data to return query output
        for date, prcp in results: 
            prcp_dict = {}
            prcp_dict['precipitation'] = prcp 
            prcp_dict['date'] = date
            prcp_query.append(prcp_dict)
        return jsonify(prcp_query)
@app.route("/api/v1.0/stations")
def stations():
    #creating session for python to pull from database
    session = Session(engine)
    #querying all stations in database
    results = session.query(Station.station, Station.id).all()

    session.close()
    stations = []
    #creating dictionary for row data to return output
    for station, id in results:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        stations.append(stations_dict)
    return jsonify(stations)

    
@app.route("/api/v1.0/tobs")
def tobs():
    #creating session for python to pull from database
    session = Session(engine)

    #querying all tobs measurement data and filtering by most recent 1 year
    last_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
    date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    year_from_last = date - dt.timedelta(days = 365)
    tobs_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_from_last)
    session.close()
    tobs_list = []
    #creating dictionary for row data to return output
    for date, tobs in tobs_query:
        tobs_dict= {}
        tobs_dict["date"] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)
    return (
        jsonify(tobs_list)


    )
@app.route("/api/v1.0/<start>")
def start(start):

    #creating session link for python to access database
    session = Session(engine)
    #querying all tobs data after user defined start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    start_date_list = []
    #creatng dictionary for row data to return output
    for min, avg, max in results:
        start_date_tobs_dict = {}
        start_date_tobs_dict['min_temp'] = min
        start_date_tobs_dict['avg_temp'] = avg
        start_date_tobs_dict['max_temp'] = max
        start_date_list.append(start_date_tobs_dict)
    
    return jsonify(start_date_list)
    
    
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    #creating session for python to pull from database
    session = Session(engine)

    #querying all tobs data and filtering by user defined star and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
 
    start_end_tobs_list = []
    #creating dictionary for row data to return output
    for min, avg, max in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min_temp"] = min
        start_end_tobs_dict["avg_temp"] = avg
        start_end_tobs_dict["max_temp"] = max
        start_end_tobs_list.append(start_end_tobs_dict) 

    return jsonify(start_end_tobs_list)
    
if __name__ == "__main__": 

    app.run(debug = True)