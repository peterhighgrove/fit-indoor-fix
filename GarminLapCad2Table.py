import os
import fitparse
import pandas as pd

def extract_lap_data_from_txt(lap_file_path):

    # List to store the rows
    lap_data_from_txt = []

    # Open the text file
    with open(lap_file_path, 'r') as file:
        # Read each line and split into values based on delimiter
        i = 0
        for line in file:
            lap_info_in_txt = (line.strip().split(' '))  # Adjust delimiter as needed
            lap_info_in_txt[0] = int(lap_info_in_txt[0])
            lap_info_in_txt[1] = 10 * int(lap_info_in_txt[1])
            lap_info_in_txt = [lap_info_in_txt[0], lap_info_in_txt[1]]
            if i == 0:
                lap_info_in_txt.append(lap_info_in_txt[1])
            else:
                lap_info_in_txt.append((lap_info_in_txt[1] - lap_data_from_txt[i-1][1]))
            
            # print(lap_info_in_txt)
            lap_data_from_txt.append(lap_info_in_txt)
            i += 1

    return (lap_data_from_txt)

def extract_lap_data_from_fit_and_add_from_txt(fit_file_path, lap_data_in_txt):
    # Parse the FIT file
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lap_data = []
    i = 0
    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        # Dictionary to store lap information
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
        
        """
        1.message_index
        2.intensity
        3.laptime (total_timer_time) (sec)
        4.avg_cadence
        5.max_heart_rate
        6.avg_heart_rate
        7.total distance (m)
        8.lap_distance (m)
        9.avg_speed (m/S)
        10.level
        """
        lap_info.append(lap_info_message_index)                         # 0.
        lap_info.append(lap_info_intensity)                             # 1.
        lap_info.append(int(round(lap_info_total_timer_time,0)))        # 2.
        lap_info.append(lap_info_avg_cadence)                           # 3.
        lap_info.append(lap_info_max_heart_rate)                        # 4.
        lap_info.append(lap_info_avg_heart_rate)                        # 5.
        lap_info.append(lap_data_in_txt[i][1])                          # 6.total distance (m)
        lap_info.append(lap_data_in_txt[i][2])                          # 7.lap_distance (m)
        lap_info.append(round(lap_data_in_txt[i][2] / lap_info[2], 1))  # 8.avg_speed (m/s)
        lap_info.append(round(lap_info[8] * 3600 / 1000, 1)) # 9.avg_speed (km/h)
        lap_info.append(lap_data_in_txt[i][0])                          # 10.level
        lap_info.append(round((lap_info[7] / 10) / (lap_info[3] * lap_info[2] / 60),2))  # 11.step length

        i += 1

        # Append the lap information to the list
        lap_data.append(lap_info)
        #print(lap_info)
        #wait = input("Press Enter to continue.")

    return lap_data

def display_lap_table(lap_data):
    # Convert the lap data into a pandas DataFrame for better presentation
    df = pd.DataFrame(lap_data)
    df.index += 1  # Start index from 1 for lap numbers
    # Display the lap_data_from_txt
    print(df)

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

lap_data_from_txt = extract_lap_data_from_txt(lap_file_path)

# Output the nested list
# print(lap_data_from_txt)

# Extract lap cadence data
lap_data = extract_lap_data_from_fit_and_add_from_txt(fit_file_path, lap_data_from_txt)

# Display the lap cadence data in a lap_data_from_txt
display_lap_table(lap_data)
"""
for lap_info in lap_data:
    print(lap_info)
"""