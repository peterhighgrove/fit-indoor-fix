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
"""
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
"""
# ================================================================

def extract_lap_data_from_fit(fit_file_path):
    print('---extract_lap_data_from_fit')
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lapTable = []
    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        #print('\n',lap)
        
        # Dictionary to store lap information
        lapRecord = {
            'lapNo': None,
            'timeStart': None,
            'timeEnd': None,
            'dataRecordNoStart': None,
            'dataRecordNoEnd': None,
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
            'stepLen': None,
            'avgDragFactor': None
        }
        for lap_data_field in lap:
            #if lap_data_field.value != None:
                #print (lap_data_field.name, lap_data_field.value)
            if lap_data_field.name == 'message_index': lapRecord['lapNo'] = lap_data_field.value
            elif lap_data_field.name == 'total_timer_time': lapRecord['lapTime'] = int(round(lap_data_field.value,0))
            elif lap_data_field.name == 'start_time': lapRecord['timeStart'] = lap_data_field.value
            elif lap_data_field.name == 'intensity': lapRecord['wktStepType'] = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate': lapRecord['maxHR'] = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate': lapRecord['avgHR'] = lap_data_field.value
            #print (lap_data_field.name,lap_data_field.value)
        print('start:', lapRecord['timeStart'])
        lapTable.append(lapRecord)

    return lapTable

# ================================================================

def calc_timeStartEnd_in_lapTable(lapTable):
    totTime = 0
    i = 0
    for lapRecord in lapTable:
        lapRecord['timeEnd'] = lapRecord['timeStart'] + timedelta(seconds=lapRecord['lapTime'])
        if i > 0:
            lapTable[i-1]['timeEnd'] = lapRecord['timeStart'] + timedelta(seconds=-1)
        print('end:', lapRecord['timeEnd'])

        totTime += lapRecord['lapTime']
        i += 1

        # Append the lap information to the list

        #print(lapRecord)
        #wait = input("Press Enter to continue.")

    lapCountLapFit = len(lapTable)
    for lapRecord in lapTable:
        print(lapRecord['timeStart'], lapRecord['timeEnd'])
    return lapTable, totTime, lapCountLapFit

# ================================================================

def extract_recordData_from_fit(lapTable, fit_file_path):
    print('--extract_lapHRdata_from_fit')
    
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    recordDataTable = []
    # Iterate over all messages of type "record"
    for fit_record in fitfile.get_messages('record'):
        #if recordNo <10: print('\n',fit_record)
        # Extract data fields
        recordData = {
            'timestamp': None,
            'HR': None,
            'CIQlevel': None,
            'CIQtrainSess': None,
            'CIQdistance': None,
            'CIQspeed': None,
            'CIQstrokeLength': None,
            'CIQdragfactor': None,
            'lapNo': None
        }
        for fit_record_data in fit_record:
            #if (recordNo / 300) == (int(recordNo/300)): print (fit_record_data.name, fit_record_data.value)
            if fit_record_data.name == 'timestamp': recordData['timestamp'] = fit_record_data.value
            elif fit_record_data.name == 'heart_rate': recordData['HR'] = fit_record_data.value
            elif fit_record_data.name == 'Level': recordData['CIQlevel'] = fit_record_data.value
            elif fit_record_data.name == 'Training_session': recordData['CIQtrainSess'] = fit_record_data.value
            elif fit_record_data.name == 'Distance': recordData['CIQdistance'] = fit_record_data.value
            elif fit_record_data.name == 'Speed': recordData['CIQspeed'] = fit_record_data.value
            elif fit_record_data.name == 'StrokeLength': recordData['CIQstrokeLength'] = fit_record_data.value
            elif fit_record_data.name == 'DragFactor': recordData['CIQdragfactor'] = fit_record_data.value
            #print(fit_record_data)
            #if recordNo <10: print(fit_record_data.name, fit_record_data.value)
        recordDataTable.append(recordData)

    return recordDataTable

# ================================================================

def calc_lapHRstartEnd_from_recordDataTbl(recordDataTable, lapTable):
    lapHRtbl = []
    recordNo = 0
    lapNo = 0
    
    for recordData in recordDataTable:
        #if recordNo == 0 or (timestamp[recordNo] == lapTable[lapNo]['timeEnd']): 
        if recordNo == 0:
            lapRecord = {
                'lapHRstart': None,
                'lapHRend': None
            }
            lapRecord['lapHRstart'] = recordData['HR']
            print ('first rec: ', recordData['timestamp'])
            timeEnd = (str(recordData['timestamp']).replace(':','-').replace(' ','-'))
        
        if lapNo < (len(lapTable)-1) and recordData['timestamp'] == lapTable[lapNo]['timeEnd']: 
            lapRecord['lapHRend'] = recordDataTable[recordNo - 1]['HR']
            lapHRtbl.append(lapRecord)
            
            #if lapNo < len(lapTable) - 1:  
            lapNo += 1
            lapRecord = {
                'lapHRstart': None,
                'lapHRend': None
            }
            lapRecord['lapHRstart'] = recordData['HR']
            #print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
        recordNo += 1
        #print(recordNo, lapNo)
        #if recordNo == 970: exit()

    lapRecord['lapHRend'] = recordDataTable[recordNo - 1]['HR']
    #print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'], recordNo)
    lapHRtbl.append(lapRecord)

    """
    lapNo = 0
    for lapRecord in lapHRtbl:
        print (lapNo, lapRecord['lapHRstart'], lapRecord['lapHRend'])
        lapNo += 1
    #"""

    lapCountHRfit = len(lapHRtbl)
    print ('last rec: ', recordDataTable[recordNo - 1]['timestamp'])

    return lapTable, recordDataTable, timeEnd, lapCountHRfit

# ================================================================

#2def add_from_txt_and_fitHR(lapFitTable, lapHRtbl, lapFromTxtTbl):
def add_from_txt_and_fitHR(lapFitTable, lapHRtbl):
    print('----add_from_txt_and_fitHR')
    # Initialize lists to store lap data
    i = 0

    for lapRecord in lapFitTable:
        
        lapRecord['lapHRstart'] = lapHRtbl[i]['lapHRstart']
        lapRecord['lapHRend'] = lapHRtbl[i]['lapHRend']
        #2lapRecord['totDist'] = lapFromTxtTbl[i]['totDist']                               # (m)
        #2lapRecord['lapDist'] = lapFromTxtTbl[i]['lapDist']                           # (m)
        #2lapRecord['level'] = lapFromTxtTbl[i]['level'] 
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

    lapTxtLine = 'lapNo;level;lapHRstart;lapHRend;maxHR;avgHR;lapTime;avgCad;lapDist;totDist;wktStepType;avgSpeed'
    print (lapTxtLine)
    outLapTxt_file.write (lapTxtLine + '\n')
    for lapRecord in lapTable:
        lapTxtLine = str(lapRecord['lapNo']) + ';' + str(lapRecord['level']) + ';'
        lapTxtLine += str(lapRecord['lapHRstart']) + ';' + str(lapRecord['lapHRend']) +  ';'
        lapTxtLine += str(lapRecord['maxHR']) + ';' + str(lapRecord['avgHR']) + ';'
        lapTxtLine += str(lapRecord['lapTime']) + ';'
        lapTxtLine += str(lapRecord['avgCad']) + ';'
        lapTxtLine += str(lapRecord['lapDist']) + ';' + lapTxtLine + str(lapRecord['totDist']) + ';'
        lapTxtLine += str(lapRecord['wktStepType']) + ';'
        lapTxtLine += str(lapRecord['avgSpeed'])
        print (lapTxtLine)
        outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('LAP DISTANCES')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('LAP DISTANCES\n')
    outLapTxt_file.write ('-----------\n')

    for lapRecord in lapTable:
            lapTxtLine = 'lap' + str(lapRecord['lapNo']) +  ' '
            lapTxtLine += m2km_2decStr(lapRecord['lapDist']) + 'km '
            lapTxtLine += str(lapRecord['stepLen'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
    print('Totaldist: ' + m2km_2decStr(totDist) + ' km')
    outLapTxt_file.write ('Totaldist: ' + m2km_2decStr(totDist) + ' km' + '\n')
    
    return

# ================================================================
# ================================================================
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
"""#2
lap_txtFile_path = pathPrefix + 'documents/indoorBikeLapsLatest.txt'
file_exist = os.path.isfile(lap_txtFile_path)
if not file_exist:
    print('---------------- Lap txtFile does not exist!')
    exit()
"""
# File path to your FIT txtFile
fit_file_path = pathPrefix + pathDL + '2024-09-24-16-40-47-bike-indoorBike-0.0km-00-55-15tim-Epix Pro gen 2.fit'
file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit txtFile does not exist!')
    exit()

#lapFromTxtTbl, lapCountTxt = extract_lap_data_from_txt(lap_txtFile_path)
lapTable = extract_lap_data_from_fit(fit_file_path)
lapTable, totTime, lapCountLapFit = calc_timeStartEnd_in_lapTable(lapTable)
recordDataTable = extract_recordData_from_fit(lapTable, fit_file_path)
lapTable, recordDataTable, timeEnd, lapCountHRfit = calc_lapHRstartEnd_from_recordDataTbl(recordDataTable, lapTable)

#2print('lapCount in all files: ', lapCountTxt, lapCountHRfit, lapCountLapFit)
print('lapCount in all files: ', lapCountHRfit, lapCountLapFit)
#2if lapCountTxt != lapCountHRfit: exit()
#2if lapCountTxt != lapCountLapFit: exit()
if lapCountHRfit != lapCountLapFit: exit()
exit()
#2lapTable, totDist = add_from_txt_and_fitHR(lapFitTable, lapHRtbl, lapFromTxtTbl)
lapTable, totDist = add_from_txt_and_fitHR(lapFitTable, lapHRtbl)

# File path to your destination text txtFile
outLapTxt_file_path = pathPrefix + pathDL + timeEnd + '-' + m2km_1decStr(totDist) + 'km-' + sec2minSec_shStr(totTime).replace(':','.') + 'min-LapTables.txt'

saveLapTable_to_txt(outLapTxt_file_path, lapTable)

"""
for lapRecord in lapTable:
    print(lapRecord)
"""