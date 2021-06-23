#You must change the value of all the following variables, depending on your setup

#identification keys to use with the AerisWeather API
#string variables
#you can retrieve these information on your member page on Aerisweather: https://www.aerisweather.com/account/member
CLIENT_ID = "384924U4HIRHSF9ZSFD27398364872646"
CLIENT_SECRET = "98U94U294KD93UJOIEZFN9283927398178"

#name of your dataset
#string variable
#example for a dataset named "processed_data.csv": DATAFILE = "processed_data.csv"
#for each participant, the dataset must contain the following information: participant identifier (no specific format), time at which the participant took the study (format must be "DD/MM/YYYY HH:MM"), exact location of the participant (format must be "latitude,longitude")
DATAFILE = "processed_data.csv"

#in your dataset, name of the column in which is referenced the participant ID of a given participant
#string variable
#example for a dataset in which the participant ID is referenced in the "participant_id" column: EXACT_LOCATION_COLUMN = "participant_id"
PARTICIPANT_ID_COLUMN = "participant_id"

#in your dataset, name of the column in which is referenced the timestamp of a given participant (time at which the participant took the study, with the following format: "DD/MM/YYYY HH:MM")
#string variable
#example for a dataset in which the timestamp is referenced in the "timestamp" column: EXACT_LOCATION_COLUMN = "timestamp"
TIMESTAMP_COLUMN = "timestamp"

#in your dataset, name of the column in which is referenced the exact location of a given participant, with the following format: "latitude,longitude"
#string variable
#example for a dataset in which the exact location is referenced in the "exact_location" column: EXACT_LOCATION_COLUMN = "exact_location"
EXACT_LOCATION_COLUMN = "exact_location"


#timezone of the time displayed on your computer
#numerical variable
#example for a computer in Paris: UTC_TIMEZONE = 2
#example for a computer in New-York: UTC_TIMEZONE = -4
#You are capped to a certain number of accesses to the API per day. If you happen to reach the daily limit, the script will be paused until midnight UTC.
UTC_TIMEZONE = 2


#year for which you want to collect yearly averages of the climate variables (leave unchanged if you don't want to collect yearly averages)
#string variable
#example: YEAR = "2020"
YEAR = "2020"


#variables of interest for the "yearly_averages" mode 
#all possible climate variables are displayed here:
#https://www.aerisweather.com/support/docs/api/reference/endpoints/observations-summary/
#if you want to collect climate variables different than those documented below, add/change the values in the following python list accordingly
#note that you must keep the default values if you want to run the "aerisweather_statscomputing.py" script.
SUMMARY_FOI = ["periods.summary.dateTimeISO",
                        "periods.summary.range.maxDateTimeISO",
                        "periods.summary.range.minDateTimeISO",
                        "periods.summary.temp.avgC",
                        "periods.summary.temp.count",
                        "periods.summary.dewpt.avgC",
                        "periods.summary.dewpt.count",
                        "periods.summary.rh.avg",
                        "periods.summary.rh.count",
                        "periods.summary.altimeter.avgMB",
                        "periods.summary.altimeter.count",
                        "periods.summary.pressure.avgMB",
                        "periods.summary.pressure.count",
                        "periods.summary.visibility.avgKM",
                        "periods.summary.visibility.count",
                        "periods.summary.wind.avgKPH",
                        "periods.summary.wind.count",
                        "periods.summary.sky.avg",
                        "periods.summary.sky.count",
                        "profile.elevM"]


#variables of interest for the "specified_date" mode
#if you want to collect other climate variables, check this link:
#https://www.aerisweather.com/support/docs/api/reference/endpoints/observations-archive/
#if you want to collect climate variables different than those documented below, add/change the values in the following python list accordingly
#note that you must keep the default values if you want to run the "aerisweather_statscomputing.py" script.
ARCHIVE_FOI = ["periods.ob.dateTimeISO",
                        "periods.ob.recDateTimeISO",
                        "periods.ob.tempC",
                        "periods.ob.dewpointC",
                        "periods.ob.humidity",
                        "periods.ob.pressureMB",
                        "periods.ob.altimeterMB",
                        "periods.ob.windSpeedKPH",
                        "periods.ob.visibilityKM",
                        "periods.ob.sky",
                        "periods.profile.elevM"]