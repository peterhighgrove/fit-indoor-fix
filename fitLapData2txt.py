import os
from datetime import datetime, time, timedelta
import fitparse

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

def extract_lap_data_from_txt(lap_txtFile_path):
    print('-extract_lap_data_from_txt')

    # List to store the rows
    lapFromTxtTbl = []

    # Open the text txtFile
    with open(lap_txtFile_path, 'r') as txtFile:
        i = 0
        for line in txtFile:
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
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'] - lapFromTxtTbl[i-1]['totDist'])
            
            # print(lap_info_inTxt)
            lapFromTxtTbl.append(lap_info_inTxt)
            i += 1
        lapCountTxt = len(lapFromTxtTbl)
    return (lapFromTxtTbl, lapCountTxt)

# ================================================================

def extract_lap_data_from_fit(fit_file_path):
    print('---extract_lap_data_from_fit')
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lapTable = []
    totTime = 0
    i = 0
    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        #print('\n',lap)
        
        # Dictionary to store lap information
        lapRecord = {
            'lapNo': None,
            'endTime': None,
            'wktStepType': None,
            'lapTime': None,
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
                lapRecord['lapNo'] = lap_data_field.value
            elif lap_data_field.name == 'total_timer_time':
                lapRecord['lapTime'] = int(round(lap_data_field.value,0))
            elif lap_data_field.name == 'start_time':
                lapRecord['endTime'] = lap_data_field.value
            elif lap_data_field.name == 'intensity':
                lapRecord['wktStepType'] = lap_data_field.value
            elif lap_data_field.name == 'avg_cadence':
                lapRecord['avgCad'] = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate':
                lapRecord['maxHR'] = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate':
                lapRecord['avgHR'] = lap_data_field.value
        print(lapRecord['endTime'])
        lapRecord['endTime'] = lapRecord['endTime'] + timedelta(seconds=lapRecord['lapTime'])
        print(lapRecord['endTime'])

        totTime += lapRecord['lapTime']
        i += 1

        # Append the lap information to the list
        lapTable.append(lapRecord)
        #print(lapRecord)
        #wait = input("Press Enter to continue.")

        lapCountLapFit = len(lapTable)

    return lapTable, totTime, lapCountLapFit

# ================================================================

def extract_lapHRdata_from_fit(fitFile_path, lapTable):
    print('--extract_lapHRdata_from_fit')
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fitFile_path)
    
    CIQlevel = []
    HR = []
    timestamps = []
    
    lapHRtbl = []
    recordNo = 0
    lapNo = 0
    

    # Iterate over all messages of type "record"
    for record in fitfile.get_messages('record'):
        #print('\n',record)
        # Extract data fields
        for record_data in record:
            #if (recordNo / 300) == (int(recordNo/300)): print (record_data.name, record_data.value)
            if record_data.name == 'Level':
                # Append cadence value
                CIQlevel.append(record_data.value)
            elif record_data.name == 'heart_rate':
                # Append timestamp value
                HR.append(record_data.value)
            elif record_data.name == 'timestamp':
                # Append timestamp value
                timestamps.append(record_data.value)
            #print(record_data)

        #if recordNo == 0 or (timestamps[recordNo] == lapTable[lapNo]['endTime']): 
            
        if recordNo == 0:
            lapRecord = {
                'lapHRstart': None,
                'lapHRend': None
            }
            lapRecord['lapHRstart'] = HR[recordNo]
            print (timestamps[recordNo])
            endTime = (str(timestamps[recordNo]).replace(':','-').replace(' ','-'))
        
        if lapNo < (len(lapTable)-1) and timestamps[recordNo] == lapTable[lapNo]['endTime']: 
            lapRecord['lapHRend'] = HR[recordNo - 1]
            print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
            lapHRtbl.append(lapRecord)
            print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
            
            #if lapNo < len(lapTable) - 1:  
            lapNo += 1
            print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
            lapRecord = {
                'lapHRstart': None,
                'lapHRend': None
            }
            lapRecord['lapHRstart'] = HR[recordNo]
            print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)

        recordNo += 1
        #print(recordNo, lapNo)
        #if recordNo == 970: exit()

    print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
    lapRecord['lapHRend'] = HR[recordNo - 1]
    print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
    lapHRtbl.append(lapRecord)

    #"""
    lapNo = 0
    for lapRecord in lapHRtbl:
        print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'])
        lapNo += 1
    #"""

    lapCountHRfit = len(lapHRtbl)

    return lapHRtbl, endTime, lapCountHRfit

# ================================================================

def add_from_txt_and_fitHR(lapFitTable, lapHRtbl, lapFromTxtTbl):
    print('----add_from_txt_and_fitHR')
    # Initialize lists to store lap data
    i = 0

    for lapRecord in lapFitTable:
        
        lapRecord['lapHRstart'] = lapHRtbl[i]['lapHRstart']
        lapRecord['lapHRend'] = lapHRtbl[i]['lapHRend']
        lapRecord['totDist'] = lapFromTxtTbl[i]['totDist']                               # (m)
        lapRecord['lapDist'] = lapFromTxtTbl[i]['lapDist']                           # (m)
        lapRecord['level'] = lapFromTxtTbl[i]['level'] 
        lapRecord['avgSpeed'] = lapRecord['lapDist'] / lapRecord['lapTime']  # (m/s)
        lapRecord['stepLen'] = (round((lapRecord['lapDist'] / 10) / (lapRecord['avgCad'] * lapRecord['lapTime'] / 60),2))  # step length acc to FFRT

        i += 1

        # Append the lap information to the list
        #print(lapRecord)
        #wait = input("Press Enter to continue.")
        #print(lapRecord['totDist'])

    return lapFitTable, lapRecord['totDist']

# ================================================================

def saveLapTable_to_txt(outLapTxt_file_path, lapTable):
    
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapRecord in lapTable:
        if lapRecord['wktStepType'] == 'active':
            lapTxtLine = 'lap' + str(lapRecord['lapNo']) + ' lv' + str(lapRecord['level']) +  ' '
            lapTxtLine += str(lapRecord['lapHRstart']) + '+' + str(lapRecord['lapHRend'] - lapRecord['lapHRstart']) +  '->'
            lapTxtLine += str(lapRecord['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapRecord['lapTime']) + 'min '
            lapTxtLine += str(lapRecord['avgCad']) + 'rpm ' + m2km_1decStr(lapRecord['lapDist']) + 'km '
            lapTxtLine += mps2kmph_1decStr(lapRecord['avgSpeed']) + 'km/h' 
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapRecord in lapTable:
        if lapRecord['wktStepType'] == 'rest':
            lapTxtLine = 'lap' + str(lapRecord['lapNo']) + ' lv' + str(lapRecord['level']) +  ' '
            lapTxtLine += str(lapRecord['maxHR']) + 'maxHR'
            lapTxtLine += str(lapRecord['lapHRend'] - lapRecord['lapHRstart']) + '->' + str(lapRecord['lapHRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapRecord['lapTime']) + 'min '
            lapTxtLine += str(lapRecord['avgCad']) + 'rpm ' + m2km_1decStr(lapRecord['lapDist']) + 'km'
            lapTxtLine += mps2kmph_1decStr(lapRecord['avgSpeed']) + 'km/h' 
            if (lapRecord['maxHR'] - lapRecord['lapHRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapRecord['maxHR'] - lapRecord['lapHRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('ALL lap data ')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('ALL lap data\n')
    outLapTxt_file.write ('-----------\n')

    lapTxtLine = 'lapNo;level;lapHRstart;lapHRend;maxHR;avgHR;lapTime;avgCad;lapDist;totDist;avgSpeed'
    print (lapTxtLine)
    outLapTxt_file.write (lapTxtLine + '\n')
    for lapRecord in lapTable:
        lapTxtLine = str(lapRecord['lapNo']) + ';' + str(lapRecord['level']) + ';'
        lapTxtLine += str(lapRecord['lapHRstart']) + ';' + str(lapRecord['lapHRend']) +  ';'
        lapTxtLine += str(lapRecord['maxHR']) + ';' + str(lapRecord['avgHR']) + ';'
        lapTxtLine += str(lapRecord['lapTime']) + ';'
        lapTxtLine += str(lapRecord['avgCad']) + ';'
        lapTxtLine += str(lapRecord['lapDist']) + ';' + lapTxtLine + str(lapRecord['totDist']) + ';'
        lapTxtLine += str(lapRecord['avgSpeed'])
        print (lapTxtLine)
        outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('LAP DISTANCES')
    print('-----------')

    for lapRecord in lapTable:
            lapTxtLine = 'lap' + str(lapRecord['lapNo']) +  ' '
            lapTxtLine += m2km_2decStr(lapRecord['lapDist']) + 'km '
            lapTxtLine += str(lapRecord['stepLen'])
            print (lapTxtLine)
    print('Totaldist: ' + m2km_2decStr(totDist) + ' km')
    
    return

# ================================================================
# ================================================================

#device = 'pc'
device = 'pc1drv'
#device = 'm'

if device == 'm':
    pathPrefix = '/storage/emulated/0/'
    pathDL = 'download/'
elif device == 'pc':
    pathPrefix = 'c:/users/peter/'
    pathDL = 'downloads/'
else:
    pathPrefix = 'C:/Users/peter/'
    pathDL = 'OneDrive/Dokument Peter OneDrive/Träning/ActivityFiles/Peter activities/'


# ================================================================

lap_txtFile_path = pathPrefix + 'documents/indoorBikeLapsLatest.txt'
file_exist = os.path.isfile(lap_txtFile_path)
if not file_exist:
    print('---------------- Lap txtFile does not exist!')
    exit()

# File path to your FIT txtFile
fit_file_path = pathPrefix + pathDL + '2024-09-21-10-52-11-bike-indoorBike-0.0km-01-10-09tim-Epix Pro gen 2.fit'
file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit txtFile does not exist!')
    exit()

lapFromTxtTbl, lapCountTxt = extract_lap_data_from_txt(lap_txtFile_path)
lapFitTable, totTime, lapCountLapFit = extract_lap_data_from_fit(fit_file_path)
lapHRtbl, endTime, lapCountHRfit = extract_lapHRdata_from_fit(fit_file_path, lapFitTable)

print('lapCount in all files: ', lapCountTxt, lapCountHRfit, lapCountLapFit)
if lapCountTxt != lapCountHRfit: exit()
if lapCountTxt != lapCountLapFit: exit()
if lapCountHRfit != lapCountLapFit: exit()

lapTable, totDist = add_from_txt_and_fitHR(lapFitTable, lapHRtbl, lapFromTxtTbl)

# File path to your destination text txtFile
outLapTxt_file_path = pathPrefix + pathDL + endTime + '-' + m2km_1decStr(totDist) + 'km-' + sec2minSec_shStr(totTime).replace(':','.') + 'min-LapTables.txt'

saveLapTable_to_txt(outLapTxt_file_path, lapTable)

"""
for lapRecord in lapTable:
    print(lapRecord)
"""