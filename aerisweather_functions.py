import datetime
from statistics import *
from aerisweather_keys import *


#returns a list that contains the beginning date and ending date of each month of the year of interest in the following format: 
#[[start_january,end_january], [...], [start_december,end_december]]
def compute_year_months(year):
    year = int(year)
    months_list = []
    for i in range(1, 12):
        month_start = datetime.date(year, i, 1)
        month_end = datetime.date(year, i+1, 1) - datetime.timedelta(days=1)
        months_list.append([str(month_start), str(month_end)])
    
    months_list.append(["{}-12-01".format(year), "{}-12-31".format(year)])
    
    return months_list


#returns a timestamp that is [delay] prior or subsequent to the input timestamp
def timestamp_computing(timestamp, delay, sign):

    if sign == "plus":
        timestamp = datetime.date(int(timestamp[:4]), int(timestamp[5:7]), int(timestamp[8:10])) + datetime.timedelta(delay)
    elif sign == "minus":
        timestamp = datetime.date(int(timestamp[:4]), int(timestamp[5:7]), int(timestamp[8:10])) - datetime.timedelta(delay)
    
    if len(str(timestamp.day)) == 1:
        day = "0{}".format(str(timestamp.day))
    else:
        day = str(timestamp.day)
    
    if len(str(timestamp.month)) == 1:
        month = "0{}".format(str(timestamp.month))
    else:
        month = str(timestamp.month)

    timestamp = "{}-{}-{}".format(timestamp.year, month, day)

    return timestamp


#creates the different "failed_accesses" and "warning_accesses" files, if they aren't already created
def files_init(year):

    try:
        with open("specified_date_failed_accesses.csv", "r") as opening:
            pass
    except:
        with open("specified_date_failed_accesses.csv", "w") as opening:
            opening.write("id;location;geo_coordinates;delay;timestamp;fields;error_code;error_description")

    try:
        with open("specified_date_warning_accesses.csv", "r") as opening:
            pass
    except:
        with open("specified_date_warning_accesses.csv", "w") as opening:
            opening.write("id;location;geo_coordinates;delay;timestamp;fields;error_code;error_description")

    try:
        with open("averages_{}_failed_accesses.csv".format(year), "r") as opening:
            pass
    except:
        with open("averages_{}_failed_accesses.csv".format(year), "w") as opening:
            opening.write("country;location;geo_coordinates;t1;t2;fields;error_code;error_description")

    try:
        with open("averages_{}_warning_accesses.csv".format(year), "r") as opening:
            pass
    except:
        with open("averages_{}_warning_accesses.csv".format(year), "w") as opening:
            opening.write("country;location;geo_coordinates;t1;t2;fields;error_code;error_description")


#returns dictionaries used to compute stats for the "specified date" data
def variables_timestamps_gen():
    variables_ontime = {"tempC": [],
                            "dewpointC": [],
                            "humidity": [],
                            "altimeterMB": [],
                            "pressureMB": [],
                            "visibilityKM": [],
                            "windSpeedKPH": [],
                            "sky": [],
                            "elevM": []}

    variables_p24h = {"tempC": [],
                            "dewpointC": [],
                            "humidity": [],
                            "altimeterMB": [],
                            "pressureMB": [],
                            "visibilityKM": [],
                            "windSpeedKPH": [],
                            "sky": [],
                            "elevM": []}

    variables_p48h = {"tempC": [],
                            "dewpointC": [],
                            "humidity": [],
                            "altimeterMB": [],
                            "pressureMB": [],
                            "visibilityKM": [],
                            "windSpeedKPH": [],
                            "sky": [],
                            "elevM": []}

    temp_deviation_ontime = {"temp_deviation_22_absolute": [],
        "temp_deviation_22_positive": [],
        "temp_deviation_22_negative": []}

    temp_deviation_p24h = {"temp_deviation_22_absolute": [],
            "temp_deviation_22_positive": [],
            "temp_deviation_22_negative": []}

    temp_deviation_p48h = {"temp_deviation_22_absolute": [],
            "temp_deviation_22_positive": [],
            "temp_deviation_22_negative": []}
    
    return variables_ontime, variables_p24h, variables_p48h, temp_deviation_ontime, temp_deviation_p24h, temp_deviation_p48h


#returns dictionaries used to compute stats for the "year averages" data
def variables_average_gen():
    variables = {"temp": ["avgC", []],
                    "dewpt": ["avgC", []],
                    "rh": ["avg", []],
                    "altimeter": ["avgMB", []],
                    "pressure": ["avgMB", []],
                    "visibility": ["avgKM", []],
                    "wind": ["avgKPH", []],
                    "sky": ["avg", []],
                    "elevM": ["elevM", []]}

    temp_deviation = {"temp_deviation_22_absolute": ["temp_deviation_22_absolute", []],
                            "temp_deviation_22_positive": ["temp_deviation_22_positive", []],
                            "temp_deviation_22_negative": ["temp_deviation_22_negative", []]}
    
    return variables, temp_deviation


#returns stats of the input climate variable 
def compute_stats(parameter_values):

    n_obs = str(len(parameter_values))
    parameter_values = sorted(parameter_values)

    if n_obs == "0":
        merged_values = "0;NA;NA;NA;NA;NA;NA"
    elif n_obs == "1":
        mean_ = str(mean(parameter_values))
        median_ = str(median(parameter_values))
        max_ = parameter_values[0]
        min_ = parameter_values[0]
        merged_values = "1;{};{};{};{};NA;NA".format(min_, max_, mean_, median_)
    else:
        mean_ = str(mean(parameter_values))
        median_ = str(median(parameter_values))
        max_ = parameter_values[len(parameter_values) - 1]
        min_ = parameter_values[0]
        sd_s = str(stdev(parameter_values))
        sd_p = str(pstdev(parameter_values))
        merged_values = "{};{};{};{};{};{};{}".format(n_obs, min_, max_, mean_, median_, sd_s, sd_p)

    return merged_values


#retrieves the climate data for the variables of interest in the AerisWeather .json files, for the "specified date" data
def data_pulling_timestamps(json_data, variables, variables_1location, temp_deviation_1location):
    for i, timestamp in enumerate(json_data["response"]["periods"]):
        for variable in variables:
            if type(json_data["response"]["periods"][i]["ob"][variable]) is int or type(json_data["response"]["periods"][i]["ob"][variable]) is float:
                variables_1location[variable].append(json_data["response"]["periods"][i]["ob"][variable])
                if variable == "tempC":
                    deviation = json_data["response"]["periods"][i]["ob"][variable] - 22
                    if deviation < 0:
                        temp_deviation_1location["temp_deviation_22_negative"].append(deviation)
                    elif deviation > 0:
                        temp_deviation_1location["temp_deviation_22_positive"].append(deviation)
                    temp_deviation_1location["temp_deviation_22_absolute"].append(abs(deviation))
    
    return variables_1location, temp_deviation_1location