import os
import requests
import json
import pandas
import datetime
import pause
from threading import Thread, RLock
from statistics import *
from aerisweather_functions import *
from aerisweather_keys import *

#this script allows you to collect climate data using the AerisWeather API

if UTC_TIMEZONE <= 0:
    UTC_TIMEZONE = 0

try:
    files_init(YEAR)
except:
    try:
        files_init()
    except:
        pass

lock_pull, lock_failed, lock_warning = RLock(), RLock(), RLock()

dataframe = pandas.read_csv(filepath_or_buffer=DATAFILE,
                                                sep=";",
                                                dtype=object,
                                                usecols=[PARTICIPANT_ID_COLUMN, TIMESTAMP_COLUMN, EXACT_LOCATION_COLUMN],
                                                encoding='utf8',
                                                engine="c")

#list of unique locations
unique_locations = list(dict.fromkeys(dataframe[EXACT_LOCATION_COLUMN].tolist()))
unique_locations = [value for value in unique_locations if value != ""]
unique_locations = [value for value in unique_locations if str(value) != "nan"]

#list of unique participant ids
unique_ids = list(dict.fromkeys(dataframe[PARTICIPANT_ID_COLUMN].tolist()))
unique_ids = [value for value in unique_ids if value != ""]
unique_ids = [value for value in unique_ids if str(value) != "nan"]

months_list = compute_year_months(YEAR)

mode = input("Which type of data do you want to collect? (yearly_averages/specified_date) ")

class aerisweather_instance_year(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        #for each location
        while len(unique_locations) != 0:
            with lock_pull:
                location = unique_locations.pop(0)
            
            #The two lines below may seem redundant. That's because I initially wrote the script slightly differently. I changed it to make it easier to use for someone who doesn't program.
            coordinates = location 
            locations = {location: coordinates}
            
            #string in which are stored the AerisWeather parameter of interest for the API requests
            fields = ""
            for field in SUMMARY_FOI:
                fields += "{},".format(field)
            fields = fields[:-1]

            #for each location in the locations list
            for location in locations:
                for i, ts in enumerate(months_list):
                    
                    #start timestamp
                    t1 = ts[0]
                    #end timestamp
                    t2 = ts[1]

                    url = "https://api.aerisapi.com/observations/summary/{}?from={}&to={}&plimit=31&fields={}&client_id={}&client_secret={}".format(locations[location], t1, t2, fields, CLIENT_ID, CLIENT_SECRET)

                    try:
                        r = requests.get(url=url)
                        data_json = json.loads(r.content)
                    except:
                        with lock_failed:
                            with open("averages_{}_failed.csv".format(YEAR), "a") as opening:
                                opening.write("\n{};{};{};{};{};{};;".format(location, location, locations[location], t1, t2, fields))
                        continue
                        
                    if data_json["success"] is True:
                        with open("results/averages_{}_{}_{}_to_{}.json".format(YEAR, location, t1, t2), "w") as opening:
                            opening.write(str(r.content)[2:-1])
                        if data_json["error"] != None:
                            code = data_json["error"]["code"]
                            description = data_json["error"]["description"]
                            with lock_warning:
                                with open("averages_{}_warning.csv".format(YEAR), "a") as opening:
                                    opening.write("\n{};{};{};{};{};{};{};{}".format(location, location, locations[location], t1, t2, fields, code, description))
                    else:
                        code = data_json["error"]["code"]
                        description = data_json["error"]["description"]
                        with lock_failed:
                            with open("averages_{}_failed.csv".format(YEAR), "a") as opening:
                                opening.write("\n{};{};{};{};{};{};{};{}".format(location, location, locations[location], t1, t2, fields, code, description))
                        if code == "maxhits_daily":
                            #the script is paused till midnight UTC (2AM France time for the computer on which the script ran)
                            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                            pause.until(datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 2, 0, 30))

            print("location {} completed. {} locations left".format(location, str(len(unique_locations))))            
            
        print("Data succesfully pulled from AerisWeather. Press any key to quit.")
        os.system("pause")
        quit()


class aerisweather_instance_timestamp(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        #for each unique id
        while len(unique_ids) != 0:
            with lock_pull:
                id = unique_ids.pop(0)

            id_df = dataframe.loc[dataframe[PARTICIPANT_ID_COLUMN] == id]      

            #location of the participant      
            location = id_df[EXACT_LOCATION_COLUMN][list(id_df[EXACT_LOCATION_COLUMN].index)[0]]

            timestamp_ontime = id_df[TIMESTAMP_COLUMN][list(id_df[TIMESTAMP_COLUMN].index)[0]][:10]
            timestamp_ontime = "{}-{}-{}".format(timestamp_ontime[-4:], timestamp_ontime[3:5], timestamp_ontime[:2])
            timestamp_dm1 = timestamp_computing(timestamp_ontime, 1, "minus")
            timestamp_dm2 = timestamp_computing(timestamp_ontime, 2, "minus")


            #The two lines below may seem redundant. That's because I initially wrote the script slightly differently. I changed it a little bit to make it easier to use for someone who doesn't program.
            coordinates = location
            locations = {location: coordinates}

            #dictionary in which are stored the timestamps of interest
            timestamps = {"ontime": timestamp_ontime,
                            "day-1": timestamp_dm1,
                            "day-2": timestamp_dm2}

            #string in which are stored the AerisWeather parameter of interest for the API requests
            fields = ""
            for field in ARCHIVE_FOI:
                fields += "{},".format(field)
            fields = fields[:-1]

            #not necessary given that the participant is linked to a single location
            for location in locations.keys():

                #for each timestamp of interest
                for timestamp in timestamps.keys():
                    url = "https://api.aerisapi.com/observations/archive/{}?from={}&fields={}&client_id={}&client_secret={}".format(locations[location], timestamps[timestamp], fields, CLIENT_ID, CLIENT_SECRET)

                    try:
                        r = requests.get(url=url)
                        data_json = json.loads(r.content)
                    except:
                        with lock_failed:
                            with open("specified_date_failed.csv", "a") as opening:
                                opening.write("\n{};{};{};{};{};{};;".format(id, location, locations[location], timestamp, timestamps[timestamp], fields))
                        continue
                        
                    if data_json["success"] is True:
                        with open("results/specified_date_{}_{}.json".format(timestamp, id), "w") as opening:
                            opening.write(str(r.content)[2:-1])
                        if data_json["error"] != None:
                            code = data_json["error"]["code"]
                            description = data_json["error"]["description"]
                            with lock_warning:
                                with open("specified_date_warning.csv", "a") as opening:
                                    opening.write("\n{};{};{};{};{};{};{};{}".format(id, location, locations[location], timestamp, timestamps[timestamp], fields, code, description))
                    else:
                        code = data_json["error"]["code"]
                        description = data_json["error"]["description"]
                        with lock_failed:
                            with open("specified_date_failed.csv", "a") as opening:
                                opening.write("\n{};{};{};{};{};{};{};{}".format(id, location, locations[location], timestamp, timestamps[timestamp], fields, code, description))
                        if code == "maxhits_daily":
                            #the script is paused till midnight UTC
                            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                            pause.until(datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, UTC_TIMEZONE, 0, 30))
                            #besoin de changer cette valeur
            
            print("Participant {} completed. {} participants left".format(id, str(len(unique_ids))))      

        print("Data succesfully pulled from AerisWeather. Press any key to quit.")
        os.system("pause")
        quit()


while 1:
    try:
        threads_number = int(input("Number of threads? (1-10) "))
        if 1 <= threads_number <= 10:
            break
    except:
        pass

for i in range(1, threads_number+1, 1):
    if mode == "specified_date":
        aerisweather_instance_timestamp().start()
    elif mode == "yearly_averages":
        aerisweather_instance_year().start()
