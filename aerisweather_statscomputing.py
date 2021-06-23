import os
import json
import pandas
from statistics import *
from aerisweather_functions import *
from aerisweather_keys import *

mode = input("Which type of data do you want to run the script on? (yearly_averages/specified_date) ")

path = "results\\"

dataframe = pandas.read_csv(filepath_or_buffer=DATAFILE,
                                                sep=";",
                                                dtype=object,
                                                usecols=[PARTICIPANT_ID_COLUMN, TIMESTAMP_COLUMN, EXACT_LOCATION_COLUMN],
                                                encoding='utf8',
                                                engine="c")

#dictionary used to retrieve climate data for the "timestamps" data
variables_timestamps = ["tempC",
                        "dewpointC",
                        "humidity",
                        "pressureMB",
                        "altimeterMB",
                        "windSpeedKPH",
                        "visibilityKM",
                        "sky"]

if mode == "yearly_averages":
    with open("analytic_data_averages_{}.csv".format(YEAR), "w") as opening:
        opening.write("year;exact_location;geo_coordinates;climate_variable;n_observations;year_min;year_max;year_mean;year_median;year_sd_sample;year_sd_population")

    #list of unique locations
    unique_locations = list(dict.fromkeys(dataframe[EXACT_LOCATION_COLUMN].tolist()))
    unique_locations = [value for value in unique_locations if value != ""]
    unique_locations = [value for value in unique_locations if str(value) != "nan"]

    #for each location
    for location in unique_locations:

        geo_coordinates = location

        variables, temp_deviation = variables_average_gen()
        path_of_interest = os.getcwd() + "\\" + path

        #for each file associated to the location
        for file in os.listdir(path_of_interest):
            if location not in file and "averages" not in file:
                continue
            with open("{}\\{}".format(path_of_interest, file)) as json_file:
                json_data = json.load(json_file)
            
            if json_data["error"] != None and json_data["error"]["code"] == "warn_no_data":
                continue
            
            #for each datapoint in the file
            for i, timestamp in enumerate(json_data["response"][0]["periods"]):
                for variable in variables.keys():
                    if variable == "elevM":
                        if type(json_data["response"][0]["profile"][variable]) is int or type(json_data["response"][0]["profile"][variable]) is float:
                            variables[variable][1].append(json_data["response"][0]["profile"][variable])
                    else:
                        if type(json_data["response"][0]["periods"][i]["summary"][variable][variables[variable][0]]) is int or type(json_data["response"][0]["periods"][i]["summary"][variable][variables[variable][0]]) is float:
                            variables[variable][1].append(json_data["response"][0]["periods"][i]["summary"][variable][variables[variable][0]])
                            if variable == "temp":
                                deviation = json_data["response"][0]["periods"][i]["summary"][variable][variables[variable][0]] - 22
                                if deviation < 0:
                                    temp_deviation["temp_deviation_22_negative"][1].append(deviation)
                                elif deviation > 0:
                                    temp_deviation["temp_deviation_22_positive"][1].append(deviation)
                                temp_deviation["temp_deviation_22_absolute"][1].append(abs(deviation))

        for variable in variables.keys():
            merged_values = compute_stats(variables[variable][1])
            results = "\n{};{};{};{};{}".format(YEAR, location, geo_coordinates, variable, merged_values)
            with open("analytic_data_averages_{}.csv".format(YEAR), "a") as opening:
                opening.write(results)

        for variable in temp_deviation.keys():
            merged_values = compute_stats(temp_deviation[variable][1])
            results = "\n{};{};{};{};{}".format(YEAR, location, geo_coordinates, variable, merged_values)
            with open("analytic_data_averages_{}.csv".format(YEAR), "a") as opening:
                opening.write(results)


elif mode == "specified_date":
    with open("analytic_data_specified_date.csv", "w") as opening:
        opening.write("id;timing;climate_variable;n_observations;period_min;period_max;period_mean;period_median;period_sd_sample;period_sd_population")

    #list of unique ids
    unique_ids = list(dict.fromkeys(dataframe[PARTICIPANT_ID_COLUMN].tolist()))
    unique_ids = [value for value in unique_ids if value != ""]
    unique_ids = [value for value in unique_ids if str(value) != "nan"]

    #for each unique id
    for id in unique_ids:

        variables_1location_ontime, variables_1location_p24h, variables_1location_p48h, temp_deviation_1location_ontime, temp_deviation_1location_p24h, temp_deviation_1location_p48h = variables_timestamps_gen()
    
        id_df = dataframe.loc[dataframe[PARTICIPANT_ID_COLUMN] == id]

        #here we determine whether the .json files contain data
        for timing in ["ontime", "day-1", "day-2"]:
            file_of_interest = os.getcwd() + "\\" + path + "\\specified_date_{}_{}.json".format(timing, id)
            with open(file_of_interest) as json_file:
                json_data = json.load(json_file)
            if json_data["error"] != None and json_data["error"]["code"] == "warn_no_data":
                timing_success = False
                continue
            else:
                timing_success = True
                break
        
        #if no .json file contains data, we can skip to the next participant
        if timing_success is False:
            for i in [[variables_1location_ontime, "ontime"], [temp_deviation_1location_ontime, "ontime"], [variables_1location_p24h, "p24h"], [temp_deviation_1location_p24h, "p24h"], [variables_1location_p48h, "p48h"], [temp_deviation_1location_p48h, "p48h"]]:
                for variable in i[0]:
                    merged_values = compute_stats(i[0][variable])
                    with open("analytic_data_specified_date.csv", "a") as opening:
                        opening.write("\n{};{};{};{}".format(id, i[1], variable, merged_values))
            continue
        
        ontime, p24h, p48h = ["ontime"], ["day-1"], ["day-2"]

        #here we retrieve the data for "ontime" (day of data collection)
        for timing in ontime:
            file_of_interest = os.getcwd() + "\\" + path + "\\specified_date_{}_{}.json".format(timing, id)
            with open(file_of_interest) as json_file:
                json_data = json.load(json_file)
            if json_data["error"] != None and json_data["error"]["code"] == "warn_no_data":
                pass
            else:
                variables_1location_ontime, temp_deviation_1location_ontime = data_pulling_timestamps(json_data, variables_timestamps, variables_1location_ontime, temp_deviation_1location_ontime)
        
        #here we retrieve the data for "p24h" (1 day before the day of data collection)
        for timing in p24h:
            file_of_interest = os.getcwd() + "\\" + path + "\\specified_date_{}_{}.json".format(timing, id)
            with open(file_of_interest) as json_file:
                json_data = json.load(json_file)
            if json_data["error"] != None and json_data["error"]["code"] == "warn_no_data":
                pass
            else:
                variables_1location_p24h, temp_deviation_1location_p24h = data_pulling_timestamps(json_data, variables_timestamps, variables_1location_p24h, temp_deviation_1location_p24h)

                #here we retrieve the data for "p48h" (2 days before the day of data collection)
                for timing in p48h:
                    file_of_interest_2 = os.getcwd() + "\\" + path + "\\specified_date_{}_{}.json".format(timing, id)
                    with open(file_of_interest_2) as json_file_2:
                        json_data_2 = json.load(json_file_2)
                    if json_data_2["error"] != None and json_data_2["error"]["code"] == "warn_no_data":
                        pass
                    else:
                        variables_1location_p48h, temp_deviation_1location_p48h = data_pulling_timestamps(json_data, variables_timestamps, variables_1location_p48h, temp_deviation_1location_p48h)

                        variables_1location_p48h, temp_deviation_1location_p48h = data_pulling_timestamps(json_data_2, variables_timestamps, variables_1location_p48h, temp_deviation_1location_p48h)

        #stats computing (for "ontime", "p24h", "p48h")
        for i in [[variables_1location_ontime, "ontime"], [temp_deviation_1location_ontime, "ontime"], [variables_1location_p24h, "p24h"], [temp_deviation_1location_p24h, "p24h"], [variables_1location_p48h, "p48h"], [temp_deviation_1location_p48h, "p48h"]]:
            for variable in i[0]:
                merged_values = compute_stats(i[0][variable])
                with open("analytic_data_specified_date.csv", "a") as opening:
                    opening.write("\n{};{};{};{}".format(id, i[1], variable, merged_values))

print("Statistics successfully computed. Press any key to quit.")
os.system("pause")
quit()