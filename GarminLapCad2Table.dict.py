import os
import fitparse
import pandas as pd
import csv

def extract_lap_cadence(file_path):
    # Parse the FIT file
    fitfile = fitparse.FitFile(file_path)
    
    # Initialize lists to store lap data
    lap_data = []

    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        # Dictionary to store lap information
        lap_info = {
            'lap_number': None,
            'start_time': None,
            'end_time': None,
            'avg_cadence': None
        }
        
        for lap_data_field in lap:
            #if lap_data_field.value != None:
                #print (lap_data_field.name, lap_data_field.value)
            if lap_data_field.name == 'start_time':
                lap_info['start_time'] = lap_data_field.value
            elif lap_data_field.name == 'timestamp':
                lap_info['end_time'] = lap_data_field.value
            elif lap_data_field.name == 'avg_cadence':
                lap_info['avg_cadence'] = lap_data_field.value
            elif lap_data_field.name == 'lap_number':
                lap_info['lap_number'] = lap_data_field.value

        # Append the lap information to the list
        lap_data.append(lap_info)
        #print(lap_info)
        #wait = input("Press Enter to continue.")

    return lap_data

def display_lap_cadence_lap_data_from_text_file(lap_data):
    # Convert the lap data into a pandas DataFrame for better presentation
    df = pd.DataFrame(lap_data)
    df.index += 1  # Start index from 1 for lap numbers
    # Display the lap_data_from_txt
    print(df)

# File path to your FIT file
fit_file_path = 'c:/users/peter/documents/2024-09-14-09-46-48-indoorbike.fit'
#check_file = os.path.isfile(fit_file_path)
#print(check_file)
#wait = input("Press Enter to continue.")

# Extract lap cadence data
lap_data = extract_lap_cadence(fit_file_path)

# Display the lap cadence data in a lap_data_from_txt
#display_lap_cadence_lap_data_from_text_file(lap_data)

for lap_info in lap_data:
    lap_info['level'] = 12

#for lap_info in lap_data:
    #print(lap_info)

print (lap_data[2])

lap_file_path = 'c:/users/peter/documents/indoorBikeLapsLatest.txt'
check_file = os.path.isfile(lap_file_path)
print('lap file exist: ', check_file)
#wait = input("Press Enter to continue.")

# List to store the rows
lap_data_from_txt = []

# Open the text file
with open(lap_file_path, 'r') as file:
    # Read each line and split into values based on delimiter
    for line in file:
        lap_info_in_txt = (line.strip().split(' '))  # Adjust delimiter as needed
        lap_info_in_txt[0] = int(lap_info_in_txt[0])
        lap_info_in_txt[1] = int(lap_info_in_txt[1])
        lap_info_in_txt = [lap_info_in_txt[0], lap_info_in_txt[1]]
        lap_data_from_txt.append(lap_info_in_txt)

# Output the nested list
print(lap_data_from_txt)