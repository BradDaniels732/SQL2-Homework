import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    session = Session(engine)

    # Find the range of dates for the data
    date_string = session.query(func.min(Measurement.date)).all()[0][0]
    FIRST_DATE = dt.datetime.strptime(date_string, '%Y-%m-%d').date()

    date_string = session.query(func.max(Measurement.date)).all()[0][0]
    LAST_DATE = dt.datetime.strptime(date_string, '%Y-%m-%d').date()

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br/>"
        f"Please enter start_date and end_date as YYYY-MM-DD<br/>"
        f"<br/>"
        f"The dates must be between {FIRST_DATE} and {LAST_DATE}, inclusive, or else!!!"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation data"""
    """Seems weird to just get the date and precipitation, when there are multiple stations """
    """The instructions for this entire homework are not very clear"""
    """I will total the precipitation across all stations, and return that value """
    session = Session(engine)
    results = session.query(Measurement.date, func.sum(Measurement.prcp)).group_by(Measurement.date).all()

    # Create a dictionary 
    all_results = []
    for date, sum_1 in results:
        prcp_dict = {}
        prcp_dict[date] = sum_1
        all_results.append(prcp_dict)

    return jsonify(all_results)


@app.route("/api/v1.0/stations")
def stations():

    """ Return a list of all stations """
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()

    # Create a dictionary 
    all_results = []
    for station, station_name in results:
        dict_entry = {}
        dict_entry[station] = station_name
        all_results.append(dict_entry)

    return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def tobs():

    """ query for the dates and temp obs from a year from the last data point, and return a json """
    """ Well, not much instruction here, so I guess it's up to me.
        I'll take the average min, average and max across all the stations, and report one set of numbers per date"""
    session = Session(engine)

    """ Find the last date in the file, subtract 354 days, save both dates"""
    date_string = session.query(func.max(Measurement.date)).all()[0][0]
    LTM_end = dt.datetime.strptime(date_string, '%Y-%m-%d').date()

    # Set the start date to be 365 days earlier
    LTM_start = LTM_end - dt.timedelta(days=364)

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date>=LTM_start).filter(Measurement.date<=LTM_end)\
        .group_by(Measurement.date).all()

    # Create a dictionary 
    all_results = []
    for date, min_1, avg_1, max_1 in results:
        prcp_dict = {}
        prcp_dict[date] = (min_1, avg_1, max_1)
        all_results.append(prcp_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/<start_date>")
def one_date(start_date):
    """return a json with min, avg, max temps from the given date to the end of the data """
    """ Again, I'll take the average min, average and max across alll stations for the requested dates """
 
    session = Session(engine)

    # Find the range of dates for the data
    FIRST_DATE_STR = session.query(func.min(Measurement.date)).all()[0][0]
    LAST_DATE_STR = session.query(func.max(Measurement.date)).all()[0][0]

    if (start_date < FIRST_DATE_STR) or (start_date > LAST_DATE_STR):
        return (f"The start date must be between {FIRST_DATE_STR} and {LAST_DATE_STR}! Try again!")

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date>=start_date)\
        .group_by(Measurement.date).all()

    # Create a dictionary 
    all_results = []
    for date, min_1, avg_1, max_1 in results:
        prcp_dict = {}
        prcp_dict[date] = (min_1, avg_1, max_1)
        all_results.append(prcp_dict)

    return jsonify(all_results)


@app.route("/api/v1.0/<start_date>/<end_date>")
def two_dates(start_date, end_date):
    """return a json with min, avg, max temps between the two given dates """
    session = Session(engine)

    # Find the range of dates for the data
    FIRST_DATE_STR = session.query(func.min(Measurement.date)).all()[0][0]
    LAST_DATE_STR = session.query(func.max(Measurement.date)).all()[0][0]

    if (start_date < FIRST_DATE_STR) or (start_date > LAST_DATE_STR):
        return (f"The start date must be between {FIRST_DATE_STR} and {LAST_DATE_STR}! Try again!")

    if (end_date < FIRST_DATE_STR) or (end_date > LAST_DATE_STR):
        return (f"The end date must be between {FIRST_DATE_STR} and {LAST_DATE_STR}! Try again!")

    if (start_date > end_date):
        return (f"The start date of {start_date} must be on or after the end date of {end_date}! Try again!")


    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date>=start_date).filter(Measurement.date<=end_date)\
        .group_by(Measurement.date).all()

    # Create a dictionary 
    all_results = []
    for date, min_1, avg_1, max_1 in results:
        prcp_dict = {}
        prcp_dict[date] = (min_1, avg_1, max_1)
        all_results.append(prcp_dict)

    return jsonify(all_results)


if __name__ == '__main__':
    app.run(debug=True)
