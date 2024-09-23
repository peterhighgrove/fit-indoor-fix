﻿import os
import fitparse
import pandas as pd

# ================================================================

def extract_lap_data_from_txt(lap_file_path):

    # List to store the rows
    lap_tbl_from_txt = []

    # Open the text file
    with open(lap_file_path, 'r') as file:
        i = 0
        for line in file:
            lap_info_inTxt = {
                    'level': None,
                    'totDist': None,
                    'lapDist': None,
            }

            # Read each line and split into values based on delimiter
            lap_info_in_txt_line = (line.strip().split(' '))  # Adjust delimiter as needed
            lap_info_inTxt['level'] = int(lap_info_in_txt_line[0])
            lap_info_inTxt['totDist'] = 10 * int(lap_info_in_txt_line[1])

            if i == 0:
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'])
            else:
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'] - lap_tbl_from_txt[i-1]['totDist'])
            
            # print(lap_info_inTxt)
            lap_tbl_from_txt.append(lap_info_inTxt)
            i += 1

    return (lap_tbl_from_txt)

# ================================================================

def extract_lap_data_from_txt_list(lap_file_path):

    # List to store the rows
    lap_tbl_from_txt = []

    # Open the text file
    with open(lap_file_path, 'r') as file:
        # Read each line and split into values based on delimiter
        i = 0
        for line in file:
            lap_info_inTxt = (line.strip().split(' '))  # Adjust delimiter as needed
            lap_info_inTxt[0] = int(lap_info_inTxt[0])
            lap_info_inTxt[1] = 10 * int(lap_info_inTxt[1])
            lap_info_inTxt = [lap_info_inTxt[0], lap_info_inTxt[1]]
            if i == 0:
                lap_info_inTxt.append(lap_info_inTxt[1])
            else:
                lap_info_inTxt.append((lap_info_inTxt[1] - lap_tbl_from_txt[i-1][1]))
            
            # print(lap_info_inTxt)
            lap_tbl_from_txt.append(lap_info_inTxt)
            i += 1

    return (lap_tbl_from_txt)

# ================================================================

def min_sec_str (minutes):
    min = int(minutes)
    sec = int(round((minutes - min) * 60,0))
    min_str = str(min) + ':'
    if sec < 10: min_str += '0' + str(sec)
    else: min_str += str(sec)
    return (min_str)

# ================================================================

def extract_lap_data_from_fit_and_add_from_txt(fit_file_path, lap_tbl_from_txt):
    # Parse the FIT file
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lap_tbl = []
    i = 0
    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        
        # Dictionary to store lap information
        lap_info = {
            'lapNo': None,
            'wktStepType': None,
            'lapTime': None,
            'lapTime2': None,
            'lapTime_str': None,
            'avgCad': None,
            'maxHR': None,
            'avgHR': None,
            'totDist': None,
            'lapDist': None,
            'avgSpeed': None,
            'avgSpeed2': None,
            'avgPace': None,
            'level': None,
            'stepLen': None
        }
        for lap_data_field in lap:
            #if lap_data_field.value != None:
                #print (lap_data_field.name, lap_data_field.value)
            if lap_data_field.name == 'message_index':
                lap_info['lapNo'] = lap_data_field.value
            elif lap_data_field.name == 'intensity':
                lap_info['wktStepType'] = lap_data_field.value
            elif lap_data_field.name == 'total_timer_time':
                lap_info['lapTime'] = int(round(lap_data_field.value,0))
            elif lap_data_field.name == 'avg_cadence':
                lap_info['avgCad'] = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate':
                lap_info['maxHR'] = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate':
                lap_info['avgHR'] = lap_data_field.value
        lap_info['lapTime2'] = lap_info['lapTime'] / 60                     # (m)
        lap_info['lapTime_str'] = min_sec_str(lap_info['lapTime2'])                  # (m)
        lap_info['totDist'] = lap_tbl_from_txt[i]['totDist']                               # (m)
        lap_info['lapDist'] = lap_tbl_from_txt[i]['lapDist']                           # (m)
        lap_info['avgSpeed'] = (round(lap_info['lapDist'] / lap_info['lapTime'], 1))  # (m/s)
        lap_info['avgSpeed2'] = (round(lap_info['avgSpeed'] * 3600 / 1000, 1))            # (km/h)
        lap_info['avgPace'] = (round(60 / lap_info['avgSpeed2'], 2))            # (min/km)
        lap_info['level'] = (lap_tbl_from_txt[i]['level']) 
        lap_info['stepLen'] = (round((lap_info['lapDist'] / 10) / (lap_info['avgCad'] * lap_info['lapTime'] / 60),2))  # step length acc to FFRT

        i += 1

        # Append the lap information to the list
        lap_tbl.append(lap_info)
        #print(lap_info)
        #wait = input("Press Enter to continue.")

    return lap_tbl

# ================================================================

def extract_lap_data_from_fit_and_add_from_txt_list(fit_file_path, lap_tbl_from_txt):
    # Parse the FIT file
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lap_tbl = []
    i = 0
    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        
        lap_info = []
        for lap_data_field in lap:
            #if lap_data_field.value != None:
            #    print (lap_data_field.name, lap_data_field.value)
            if lap_data_field.name == 'message_index':
                lap_info_message_index = lap_data_field.value
            elif lap_data_field.name == 'intensity':
                lap_info_intensity = lap_data_field.value
            elif lap_data_field.name == 'total_timer_time':
                lap_info_total_timer_time = lap_data_field.value
            elif lap_data_field.name == 'avg_cadence':
                lap_info_avg_cadence = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate':
                lap_info_max_heart_rate = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate':
                lap_info_avg_heart_rate = lap_data_field.value
        lap_info.append(lap_info_message_index)                         # 0.
        lap_info.append(lap_info_intensity)                             # 1.
        lap_info.append(int(round(lap_info_total_timer_time,0)))        # 2.
        lap_info.append(lap_info_avg_cadence)                           # 3.
        lap_info.append(lap_info_max_heart_rate)                        # 4.
        lap_info.append(lap_info_avg_heart_rate)                        # 5.
        lap_info.append(lap_tbl_from_txt[i][1])                          # 6.total distance (m)
        lap_info.append(lap_tbl_from_txt[i][2])                          # 7.lap_distance (m)
        lap_info.append(round(lap_tbl_from_txt[i][2] / lap_info[2], 1))  # 8.avg_speed (m/s)
        lap_info.append(round(lap_info[8] * 3600 / 1000, 1))            # 9.avg_speed (km/h)
        lap_info.append(lap_tbl_from_txt[i][0])                          # 10.level
        lap_info.append(round((lap_info[7] / 10) / (lap_info[3] * lap_info[2] / 60),2))  # 11.step length

        i += 1

        # Append the lap information to the list
        lap_tbl.append(lap_info)
        #print(lap_info)
        #wait = input("Press Enter to continue.")

    return lap_tbl

# ================================================================

def display_lap_table(lap_tbl):
    # Convert the lap data into a pandas DataFrame for better presentation
    df = pd.DataFrame(lap_tbl)
    df.index += 1  # Start index from 1 for lap numbers
    # Display the lap_tbl_from_txt
    print(df)

# ================================================================

def save_lap_table_to_txt(outLapTxt_file_path, lap_tbl):
    
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    print('Active laps')
    print('-----------')
    for lap_info in lap_tbl:
        if lap_info['wktStepType'] == 'active':
            lapTxtLine = 'lap' + str(lap_info['lapNo']) + ' lv' + str(lap_info['level'])# + ' ' + lap_info['wktStepType']
            lapTxtLine += ' ' + str(lap_info['maxHR']) + 'maxHR ' + str(lap_info['lapTime_str']) + 'min'
            print (lapTxtLine)
    return

# ================================================================
# ================================================================

lap_file_path = '/storage/emulated/0/documents/indoorBikeLapsLatest.txt'
file_exist = os.path.isfile(lap_file_path)
if not file_exist:
    print('---------------- Lap file does not exist!')
    exit()

# File path to your FIT file
fit_file_path = '/storage/emulated/0/Download/17090763560_ACTIVITY.fit'
file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit file does not exist!')
    exit()

# File path to your destination text file
outLapTxt_file_path = '/storage/emulated/0/documents/latestActivityLapTables.txt'


lap_tbl_from_txt = extract_lap_data_from_txt(lap_file_path)


# ================================================================



lap_file_path = 'c:/users/peter/documents/indoorBikeLapsLatest.txt'
file_exist = os.path.isfile(lap_file_path)
if not file_exist:
    print('---------------- Lap file does not exist!')
    exit()

# File path to your FIT file
fit_file_path = 'c:/users/peter/documents/2024-09-14-09-46-48-indoorbike.fit'
file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit file does not exist!')
    exit()

# File path to your destination text file
outLapTxt_file_path = 'c:/users/peter/documents/latestActivityLapTables.txt'


lap_tbl_from_txt = extract_lap_data_from_txt(lap_file_path)


# Output the nested list
# print(lap_tbl_from_txt)

# Extract lap cadence data
lap_tbl = extract_lap_data_from_fit_and_add_from_txt(fit_file_path, lap_tbl_from_txt)

# Display the lap cadence data in a lap_tbl_from_txt
display_lap_table(lap_tbl)

save_lap_table_to_txt(outLapTxt_file_path, lap_tbl)

"""
for lap_info in lap_tbl:
    print(lap_info)
"""