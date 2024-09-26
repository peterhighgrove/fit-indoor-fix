import os
import fitparse
#import pandas as pd

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
"""
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
"""
# ================================================================
def min2minSek_longStr (minutes):
    min = int(minutes)
    sec = int(round((minutes - min) * 60,0))
    min_str = str(min) + ':'
    if sec < 10: min_str += '0' + str(sec)
    else: min_str += str(sec)
    return (min_str)

# ================================================================
def min2minSek_shStr (minutes):
    min = int(minutes)
    sec = int(round((minutes - min) * 60,0))
    min_str = str(min)
    if sec == 0: min_str += ''
    elif sec < 10: min_str += ':0' + str(sec)
    else: min_str += ':' + str(sec)
    return (min_str)

# ================================================================
def sec2minSec_longStr (seconds):
    min = int(seconds / 60)
    sec = int(round((seconds / 60 - min) * 60,0))
    min_str = str(min)
    if sec < 10: min_str += ':0' + str(sec)
    else: min_str += ':' + str(sec)
    return (min_str)

# ================================================================
def sec2minSec_shStr (seconds):
    min = int(seconds / 60)
    sec = int(round((seconds / 60 - min) * 60,0))
    min_str = str(min)
    if sec == 0: min_str += ''
    elif sec < 10: min_str += ':0' + str(sec)
    else: min_str += ':' + str(sec)
    return (min_str)

# ================================================================
def m2km_0decStr (meters):
    kmStr = str(round(meters / 1000, 0))
    return (kmStr)

# ================================================================
def m2km_1decStr (meters):
    kmStr = str(round(meters / 1000, 1))
    return (kmStr)

# ================================================================
def m2km_2decStr (meters):
    kmStr = str(round(meters / 1000, 2))
    return (kmStr)

# ================================================================
def mps2kmph_0decStr (speed):
    kmphStr = str(round(speed * 3600 / 1000, 0))
    return (kmphStr)

# ================================================================
def mps2kmph_1decStr (speed):
    kmphStr = str(round(speed * 3600 / 1000, 1))
    return (kmphStr)

# ================================================================
def mps2kmph_2decStr (speed):
    kmphStr = str(round(speed * 3600 / 1000, 2))
    return (kmphStr)

# ================================================================

def extract_lapHRdata_from_fit(file_path):
    # Parse the FIT file
    fitfile = fitparse.FitFile(file_path)
    
    level = []
    HR = []
    timestamps = []
    
    lapHRtbl = []
    recordNo = 0
    lapNo = 0
    

    # Iterate over all messages of type "record"
    for record in fitfile.get_messages('record'):
        # Extract data fields
        for record_data in record:
            #if (recordNo / 300) == (int(recordNo/300)): print (record_data.name, record_data.value)
            if record_data.name == 'Level':
                # Append cadence value
                level.append(record_data.value)
            elif record_data.name == 'heart_rate':
                # Append timestamp value
                HR.append(record_data.value)
            elif record_data.name == 'timestamp':
                # Append timestamp value
                timestamps.append(record_data.value)

        if recordNo == 0 or level[recordNo] != level[recordNo - 1]: 
            
            if recordNo == 0:
                lapRecord = {
                    'lapHRstart': None,
                    'lapHRend': None
                }
                lapRecord['lapHRstart'] = HR[recordNo]
                startTime = (str(timestamps[recordNo]).replace(':','-').replace(' ','-'))
            if level[recordNo] != level[recordNo - 1]: 
                lapRecord['lapHRend'] = HR[recordNo - 1]
                lapHRtbl.append(lapRecord)
                lapNo += 1
                lapRecord = {
                    'lapHRstart': None,
                    'lapHRend': None
                }
                lapRecord['lapHRstart'] = HR[recordNo]
                print (lapNo, timestamps[recordNo], HR[recordNo-1], HR[recordNo])
            
        recordNo += 1

    lapRecord['lapHRend'] = HR[recordNo - 1]
    lapHRtbl.append(lapRecord)

    lapNo = 0
    for lapRecord in lapHRtbl:
        print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'])
        lapNo += 1
    
    return lapHRtbl, startTime

# ================================================================

def extract_lap_data_from_fit_and_add_from_txt(fit_file_path, lapHRtbl, lap_tbl_from_txt):
    # Parse the FIT file
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lap_tbl = []
    totTime = 0
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
            'lapHRstart': None,
            'lapHRend': None,
            'totDist': None,
            'lapDist': None,
            'avgSpeed': None,
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
        lap_info['lapHRstart'] = lapHRtbl[i]['lapHRstart']
        lap_info['lapHRend'] = lapHRtbl[i]['lapHRend']
        lap_info['lapTime2'] = lap_info['lapTime'] / 60                     # (min)
        lap_info['lapTime_str'] = min2minSek_longStr(lap_info['lapTime2'])                  # (m:ss)
        lap_info['totDist'] = lap_tbl_from_txt[i]['totDist']                               # (m)
        lap_info['lapDist'] = lap_tbl_from_txt[i]['lapDist']                           # (m)
        lap_info['avgSpeed'] = lap_info['lapDist'] / lap_info['lapTime']  # (m/s)
        lap_info['level'] = (lap_tbl_from_txt[i]['level']) 
        lap_info['stepLen'] = (round((lap_info['lapDist'] / 10) / (lap_info['avgCad'] * lap_info['lapTime'] / 60),2))  # step length acc to FFRT

        totTime += lap_info['lapTime']
        i += 1

        # Append the lap information to the list
        lap_tbl.append(lap_info)
        #print(lap_info)
        #wait = input("Press Enter to continue.")

    return lap_tbl, lap_info['totDist'], totTime

# ================================================================
"""
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
"""
# ================================================================
"""
def display_lap_table(lap_tbl):
    # Convert the lap data into a pandas DataFrame for better presentation
    df = pd.DataFrame(lap_tbl)
    df.index += 1  # Start index from 1 for lap numbers
    # Display the lap_tbl_from_txt
    print(df)
"""
# ================================================================

def save_lap_table_to_txt(outLapTxt_file_path, lap_tbl):
    
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lap_info in lap_tbl:
        if lap_info['wktStepType'] == 'active':
            lapTxtLine = 'lap' + str(lap_info['lapNo']) + ' lv' + str(lap_info['level']) +  ' '
            lapTxtLine += str(lap_info['lapHRstart']) + '+' + str(lap_info['lapHRend'] - lap_info['lapHRstart']) +  '->'
            lapTxtLine += str(lap_info['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lap_info['lapTime']) + 'min '
            lapTxtLine += str(lap_info['avgCad']) + 'rpm ' + m2km_1decStr(lap_info['lapDist']) + 'km '
            lapTxtLine += mps2kmph_1decStr(lap_info['avgSpeed']) + 'km/h' 
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lap_info in lap_tbl:
        if lap_info['wktStepType'] == 'rest':
            lapTxtLine = 'lap' + str(lap_info['lapNo']) + ' lv' + str(lap_info['level']) +  ' '
            lapTxtLine += str(lap_info['maxHR']) + 'maxHR'
            lapTxtLine += str(lap_info['lapHRend'] - lap_info['lapHRstart']) + '->' + str(lap_info['lapHRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lap_info['lapTime']) + 'min '
            lapTxtLine += str(lap_info['avgCad']) + 'rpm ' + m2km_1decStr(lap_info['lapDist']) + 'km '
            lapTxtLine += mps2kmph_1decStr(lap_info['avgSpeed']) + 'km/h' 
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('ALL lap data ')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('ALL lap data\n')
    outLapTxt_file.write ('-----------\n')

    lapTxtLine = 'lapNo;level;lapHRstart;lapHRend;maxHR;avgHR;lapTime;avgCad;lapDist;avgSpeed'
    print (lapTxtLine)
    outLapTxt_file.write (lapTxtLine + '\n')
    for lap_info in lap_tbl:
        lapTxtLine = str(lap_info['lapNo']) + ';' + str(lap_info['level']) + ';'
        lapTxtLine += str(lap_info['lapHRstart']) + ';' + str(lap_info['lapHRend']) +  ';'
        lapTxtLine += str(lap_info['maxHR']) + ';' + str(lap_info['avgHR']) + ';'
        lapTxtLine += str(lap_info['lapTime']) + ';'
        lapTxtLine += str(lap_info['avgCad']) + ';' + str(lap_info['lapDist']) + ';'
        lapTxtLine += str(lap_info['avgSpeed'])
        print (lapTxtLine)
        outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('LAP DISTANCES')
    print('-----------')

    for lap_info in lap_tbl:
            lapTxtLine = 'lap' + str(lap_info['lapNo']) +  ' '
            lapTxtLine += m2km_2decStr(lap_info['lapDist']) + 'km '
            lapTxtLine += str(lap_info['stepLen'])
            print (lapTxtLine)
    return

# ================================================================
# ================================================================

device = 'pc'
#device = 'm'

if device == 'm':
    pathPrefix = '/storage/emulated/0/'
    pathDL = 'download/'
else:
    pathPrefix = 'c:/users/peter/'
    pathDL = 'downloads/'

# ================================================================

lap_file_path = pathPrefix + 'documents/indoorBikeLapsLatest.txt'
file_exist = os.path.isfile(lap_file_path)
if not file_exist:
    print('---------------- Lap file does not exist!')
    exit()

# File path to your FIT file
fit_file_path = pathPrefix + pathDL + '17090763560_ACTIVITY.fit'
file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit file does not exist!')
    exit()

lapHRtbl, startTime = extract_lapHRdata_from_fit(fit_file_path)
lap_tbl_from_txt = extract_lap_data_from_txt(lap_file_path)

lap_tbl, totDist, totTime = extract_lap_data_from_fit_and_add_from_txt(fit_file_path, lapHRtbl, lap_tbl_from_txt)

# File path to your destination text file
outLapTxt_file_path = pathPrefix + 'documents/' + startTime + '-' + m2km_1decStr(totDist) + 'km-' + sec2minSec_shStr(totTime).replace(':','.') + 'min-LapTables.txt'

save_lap_table_to_txt(outLapTxt_file_path, lap_tbl)

"""
for lap_info in lap_tbl:
    print(lap_info)
"""