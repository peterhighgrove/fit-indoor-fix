import os
import sys
from datetime import datetime, time, timedelta
import fitparse
from zipfile import ZipFile
import pathlib

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
    if meters == 0:
        kmStr ='-'
    else:
        kmStr = str(round(meters / 1000, 0))
    return (kmStr)

# ================================================================
def m2km_1decStr (meters):
    if meters == 0:
        kmStr ='-'
    else:
        kmStr = str(round(meters / 1000, 1))
    return (kmStr)

# ================================================================
def m2km_2decStr (meters):
    if meters == 0:
        kmStr ='-'
    else:
        kmStr = str(round(meters / 1000, 2))
    return (kmStr)

# ================================================================
def mps2minpkm_Str (speed):
    if speed == 0 or speed == None:
        minpkmStr = '-'
    else:
        minpkmStr = sec2minSec_longStr(1/(speed / 1000))
    return (minpkmStr)

# ================================================================
def mps2minp500m_Str (speed):
    if speed == 0 or speed == None:
        minp500mStr = '-'
    else:
        minp500mStr = sec2minSec_longStr(1/(speed / 1000)/2)
    return (minp500mStr)

# ================================================================
def mps2kmph_0decStr (speed):
    kmphStr = str(round(speed * 3600 / 1000, 0))
    return (kmphStr)

# ================================================================
def mps2kmph_1decStr (speed):
    if speed == 0 or speed == None:
        kmphStr = '-'
    else:
        kmphStr = str(round(speed * 3600 / 1000, 1))
    return (kmphStr)

# ================================================================
def mps2kmph_2decStr (speed):
    if speed == 0 or speed == None:
        kmphStr = '-'
    else:
        kmphStr = str(round(speed * 3600 / 1000, 2))
    return (kmphStr)

# ================================================================
# ================================================================
# ================================================================

def extract_lap_data_from_txt(lap_txtFile_path):
    print('-extract_lap_data_from_txt')

    # List to store the rows
    lapFromTxtTbl = []

    # Open the text txtFile
    with open(lap_txtFile_path, 'r') as txtFile:
        lapIx = 0
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

            if lapIx == 0:
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'])
            else:
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'] - lapFromTxtTbl[lapIx-1]['totDist'])
            
            # print(lap_info_inTxt)
            lapFromTxtTbl.append(lap_info_inTxt)
            lapIx += 1
        lapCountTxt = len(lapFromTxtTbl)
    return (lapFromTxtTbl, lapCountTxt)

# ================================================================

def extract_record_data_from_C2fit(fit_file_path):
    print('--extract_RECORD_data_from_C2fit', datetime.now())
    
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    recordTable = []
    recordIx = 0
    # Iterate over all messages of type "record"
    for fit_record in fitfile.get_messages('record'):
        #if recordIx <10: print('\n',fit_record)
        # Extract data fields
        recordData = {
            'timestamp': None,
            'HR': None,
            'distance': None,
            'cadence': None,
            'speed': None,
            'power': None
        }
        for fit_record_data in fit_record:
            #if (recordIx / 300) == (int(recordIx/300)): print (fit_record_data.name, fit_record_data.value)
            if fit_record_data.name == 'timestamp': recordData['timestamp'] = fit_record_data.value
            elif fit_record_data.name == 'heart_rate': recordData['HR'] = fit_record_data.value
            elif fit_record_data.name == 'distance': recordData['distance'] = fit_record_data.value
            elif fit_record_data.name == 'cadence': recordData['cadence'] = fit_record_data.value
            elif fit_record_data.name == 'speed': recordData['speed'] = fit_record_data.value
            elif fit_record_data.name == 'power': recordData['power'] = fit_record_data.value
            #if recordIx <10: print(fit_record_data)
            #if recordIx <10: print(fit_record_data.name, fit_record_data.value)
        recordTable.append(recordData)
        if recordIx == 0: timeFirstRecord = recordData['timestamp']
        recordIx += 1
        timeLastRecord = recordData['timestamp']
    
    # FIX Cadence = 0 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['cadence'] == 0 or recordTable[recordIx]['cadence'] == None) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['cadence']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['cadence'] = firstValue
    
    # FIX Power = 0 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['power'] == 0 or recordTable[recordIx]['power'] == None) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['power']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['power'] = firstValue
    
    # Check for bad data, HIGH cadence
    for recordIx in range(len(recordTable)):
        if recordTable[recordIx]['cadence'] > 65:
            print('HIGH cadence: ', recordTable[recordIx-1]['cadence'], '->', recordTable[recordIx]['cadence'], ' @', recordIx)
            recordTable[recordIx]['cadence'] = recordTable[recordIx-1]['cadence']


    print('C2record times from ' + str(timeFirstRecord) + ' to ' + str(timeLastRecord))
    print('C2Activity time: ' + str(timeLastRecord - timeFirstRecord))
    print('C2record no from 0 to ' + str(recordIx - 1),'\n')
    
    return recordTable, timeFirstRecord, timeLastRecord

# ================================================================

def extract_record_data_from_fit(fit_file_path):
    print('--extract_RECORD_data_from_fit', datetime.now())
    
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    recordTable = []
    recordIx = 0
   
    # Iterate over all messages of type "record"
    for fit_record in fitfile.get_messages('record'):
        #if recordIx <10: print('\n',fit_record)
        # Extract data fields
        recordData = {
            'timestamp': None,
            'HR': None,
            'distance': None,
            'speed': None,
            'cadence': None,
            'power': None,
            'CIQlevel': None,
            'CIQtrainSess': None,
            'CIQstrokeLen': None,
            'CIQdragfactor': None,
            'C2speed':None,
            'C2distance':None,
            'C2HR':None,
            'lapNo': None
        }
        for fit_record_data in fit_record:
            if fit_record_data.name == 'timestamp': recordData['timestamp'] = fit_record_data.value
            elif fit_record_data.name == 'heart_rate': recordData['HR'] = fit_record_data.value
            elif fit_record_data.name == 'Level': recordData['CIQlevel'] = fit_record_data.value
            elif fit_record_data.name == 'Training_session': recordData['CIQtrainSess'] = fit_record_data.value
            elif fit_record_data.name == 'Distance': recordData['distance'] = fit_record_data.value         # distance from C2 SkiErg CIQ distance
            elif fit_record_data.name == 'distance': 
                if recordData['distance'] == 0 or recordData['distance'] == None: recordData['distance'] = fit_record_data.value         # native distance
            elif fit_record_data.name == 'Speed': recordData['speed'] = fit_record_data.value               # speed from C2 SkiErg CIQ speed
            elif fit_record_data.name == 'enhanced_speed': 
                if recordData['speed'] == 0 or recordData['speed'] == None: recordData['speed'] = fit_record_data.value      # native Speed
            elif fit_record_data.name == 'cadence': recordData['cadence'] = fit_record_data.value
            elif fit_record_data.name == 'power': recordData['power'] = fit_record_data.value
            elif fit_record_data.name == 'StrokeLength': recordData['CIQstrokeLen'] = fit_record_data.value
            elif fit_record_data.name == 'DragFactor': recordData['CIQdragfactor'] = fit_record_data.value
            #print(fit_record_data)
            #if recordIx <10: print(fit_record_data.name, fit_record_data.value)
        #if recordIx <10: print(recordData['distance'])
        recordTable.append(recordData)
        if recordIx == 0: timeFirstRecord = recordData['timestamp']
        recordIx += 1

    timeLastRecord = recordData['timestamp']
    totalTime = (timeLastRecord - timeFirstRecord).total_seconds()
    print('record times from ' + str(timeFirstRecord) + ' to ' + str(timeLastRecord))
    print('Activity time: ' + str(timeLastRecord - timeFirstRecord) + ' ' + str(totalTime) + 'sec')
    print('record no from 0 to ' + str(recordIx - 1),'\n')
    
    #for recordIx in range(0, 16):
    #    print (recordTable[recordIx]['distance'])

    # Smoothing distance records if 2 following record are the same, then calc avg for the one before and after the 2
    for recordIx in range(2, len(recordTable)-1):
        if recordTable[recordIx]['distance'] == recordTable[recordIx-1]['distance']:
            newDistStep = ((recordTable[recordIx+1]['distance'] - recordTable[recordIx-2]['distance']) / 3)
            recordTable[recordIx-1]['distance'] = recordTable[recordIx-2]['distance'] + newDistStep
            recordTable[recordIx]['distance'] = recordTable[recordIx-2]['distance'] + newDistStep * 2
  
    #for recordIx in range(40):
        #print (recordTable[recordIx]['distance'], recordTable[recordIx]['C2distance'], recordTable[recordIx]['speed'], recordTable[recordIx]['C2speed'], recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])
        #print (recordTable[recordIx]['speed'], recordTable[recordIx]['CIQstrokeLen'], recordTable[recordIx]['CIQdragfactor'])
    #print('\n----------------\n')
    
    # FIX speed = 0 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['speed'] == 0 or recordTable[recordIx]['speed'] == None) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['speed']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['speed'] = firstValue
    
    # FIX CIQstrokeLen = 0 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['CIQstrokeLen'] == 0 or recordTable[recordIx]['CIQstrokeLen'] == None) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['CIQstrokeLen']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['CIQstrokeLen'] = firstValue
    
    # FIX CIQdragfactor = 1 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['CIQdragfactor'] == 1 or recordTable[recordIx]['CIQdragfactor'] == None) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['CIQdragfactor']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['CIQdragfactor'] = firstValue
    
    #for recordIx in range(40):
        #print (recordTable[recordIx]['distance'], recordTable[recordIx]['C2distance'], recordTable[recordIx]['speed'], recordTable[recordIx]['C2speed'], recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])
        #print (recordTable[recordIx]['speed'], recordTable[recordIx]['CIQstrokeLen'], recordTable[recordIx]['CIQdragfactor'])
    
    #exit()

    return recordTable, timeFirstRecord, timeLastRecord

# ================================================================

def extract_lap_data_from_fit(fit_file_path, startWithWktStep):
    print('--extract_LAP_data_from_fit', datetime.now())
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lapTable = []
    # Iterate over all messages of type "lap"
    LapIx = 0
    for lap in fitfile.get_messages('lap'):
        #print('\n',lap)
        lapData = {
            'lapNo': None,
            'timeStart': None,
            'timeEnd': None,
            'recordNoStart': None,
            'recordNoEnd': None,
            'wktStepType': None,
            'lapTime': None,
            'avgCad': None,
            'maxCad': None,
            'avgPower': None,
            'maxPower': None,
            'avgHR': None,
            'maxHR': None,
            'HRstart': None,
            'HRend': None,
            'totDist': None,
            'lapDist': None,
            'avgSpeed': None,       # Native avgSpeed data or Calculated based on dist/time
            'avgSpeed2': None,      # Calculated based on avg of all speed record data
            'level': None,
            'stepLen': None,
            'avgStrokeLen': None,
            'avgDragFactor': None
        }
        for lap_data_field in lap:
            if lap_data_field.name == 'message_index': lapData['lapNo'] = lap_data_field.value + 1
            elif lap_data_field.name == 'total_timer_time': 
                lapData['lapTime'] = int(round(lap_data_field.value,0))
            elif lap_data_field.name == 'total_distance': lapData['lapDist'] = lap_data_field.value
            elif lap_data_field.name == 'start_time': lapData['timeStart'] = lap_data_field.value
            elif lap_data_field.name == 'intensity': lapData['wktStepType'] = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate': lapData['avgHR'] = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate': lapData['maxHR'] = lap_data_field.value
            elif lap_data_field.name == 'enhanced_avg_speed': lapData['avgSpeed'] = lap_data_field.value
            elif lap_data_field.name == 'enhanced_max_speed': lapData['maxSpeed'] = lap_data_field.value
            elif lap_data_field.name == 'avg_cadence': lapData['avgCad'] = lap_data_field.value
            elif lap_data_field.name == 'max_cadence': lapData['maxCad'] = lap_data_field.value
            elif lap_data_field.name == 'avg_power': lapData['avgPower'] = lap_data_field.value
            elif lap_data_field.name == 'max_power': lapData['maxPower'] = lap_data_field.value
            #if LapIx <10: print (LapIx, lap_data_field.name, lap_data_field.value)

        LapIx += 1
        #print('start:', lapData['timeStart'])
        lapTable.append(lapData)

    # FIX for non workout lap data, every other lap rest
    if (lapTable[0]['wktStepType'] == 'active' and lapTable[1]['wktStepType'] == 'active') or lapTable[0]['wktStepType'] == 5:
        print('======= NO WORKOUT STEPS, using: ' + startWithWktStep)
        if startWithWktStep == 'WarmupThenActive':
            wktStepType = 'rest'
        else:
            wktStepType = 'active'
        for lap in lapTable:
            lap['wktStepType'] = wktStepType
            if wktStepType == 'active': 
                wktStepType = 'rest'
            else:
                wktStepType = 'active'
        lapTable[0]['wktStepType'] = 'warmup'
        lapTable[len(lapTable) - 1]['wktStepType'] = 'cooldown'

    lapCountFit = len(lapTable)

    return lapTable, lapCountFit

# ================================================================

def merge_C2records_with_recordTable(recordTable, C2recordTable):
    print('---merge_C2records_with_recordTable', datetime.now())
    recordIx = 0
    C2recordIx = 0

    for recordData in recordTable:
        if C2recordTable[C2recordIx]['distance'] <= recordData['distance']:
            recordData['cadence'] = C2recordTable[C2recordIx]['cadence']
            recordData['power'] = C2recordTable[C2recordIx]['power']
            recordData['C2speed'] = C2recordTable[C2recordIx]['speed']
            recordData['C2distance'] = C2recordTable[C2recordIx]['distance']
            recordData['C2HR'] = C2recordTable[C2recordIx]['HR']
            C2recordIx += 1
        recordIx += 1
    
    #for recordIx in range(40):
        #print (recordTable[recordIx]['distance'], recordTable[recordIx]['C2distance'], recordTable[recordIx]['speed'], recordTable[recordIx]['C2speed'], recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])
        #print (recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])
    #print('\n----------------\n')
    
    # FIX empty/None cadence and power records. Fill with last. Merge creates this due to not all seconds from Conccept2
    for recordIx in range(len(recordTable)):
        if recordTable[recordIx]['cadence'] == None:
            recordTable[recordIx]['cadence'] = recordTable[recordIx-1]['cadence']
        if recordTable[recordIx]['power'] == None:
            recordTable[recordIx]['power'] = recordTable[recordIx-1]['power']

    #for recordIx in range(40):
        #print (recordTable[recordIx]['distance'], recordTable[recordIx]['C2distance'], recordTable[recordIx]['speed'], recordTable[recordIx]['C2speed'], recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])
        #print (recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])

    return recordTable

# ================================================================

def merge_lapData_from_txt(lapTable, lapFromTxtTbl):
    print('----merge_lapData_from_txt', datetime.now())
    # Initialize lists to store lap data
    lapIx = 0

    for lapData in lapTable:
        
        lapData['totDist'] = lapFromTxtTbl[lapIx]['totDist']                               # (m)
        lapData['lapDist'] = lapFromTxtTbl[lapIx]['lapDist']                           # (m)
        lapData['level'] = lapFromTxtTbl[lapIx]['level'] 
        #lapData['avgSpeed'] = lapData['lapDist'] / lapData['lapTime']  # (m/s)
        #lapData['stepLen'] = (round((lapData['lapDist'] / 10) / (lapData['avgCad'] * lapData['lapTime'] / 60),2))  # step length acc to FFRT

        lapIx += 1

        # Append the lap information to the list
        #print(lapData)
        #wait = input("Press Enter to continue.")
        #print(lapData['totDist'])

    return lapTable, lapData['totDist']

# ================================================================

def calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord):
    print('---calc_lapTimeEnd_in_lapTable', datetime.now())
    lapIx = 0
    lapNo = lapIx+1
    for lapData in lapTable:
        if lapIx > 0:
            lapTable[lapIx-1]['timeEnd'] = lapData['timeStart'] + timedelta(seconds=-1)
        lapIx += 1
        lapNo = lapIx+1

    lapData['timeEnd'] = timeLastRecord
    
    totTimeSumLapTime = 0
    for lapData in lapTable:
        #print(lapData['lapTime'], (lapData['timeEnd']-lapData['timeStart']).total_seconds()+1)
        if lapData['lapTime'] == 0 or lapData['lapTime'] == None:
            lapData['lapTime'] = (lapData['timeEnd']-lapData['timeStart']).total_seconds()+1
        totTimeSumLapTime += lapData['lapTime']

    return lapTable, totTimeSumLapTime

# ================================================================

def calc_lapData_from_recordTable(recordTable, lapTable):
    print('---calc_lapData_from_recordTable', datetime.now())
    recordIx = 0
    lapIx = 0
    lapNo = lapIx+1
    speedLapSum = 0
    cadLapSum = 0
    powerLapSum = 0
    CIQstrokeLengthLapSum = 0
    CIQdragfactorLapSum = 0

    for recordData in recordTable:
        if recordData['speed'] == None: recordData['speed'] = 0
        if recordData['cadence'] == None: recordData['cadence'] = 0
        if recordData['power'] == None: recordData['power'] = 0
        if recordData['CIQstrokeLen'] == None: recordData['CIQstrokeLen'] = 0
        if recordData['CIQdragfactor'] == None: recordData['CIQdragfactor'] = 0
        speedLapSum += recordData['speed']
        cadLapSum += recordData['cadence']
        powerLapSum += recordData['power']
        CIQstrokeLengthLapSum += recordData['CIQstrokeLen']
        CIQdragfactorLapSum += recordData['CIQdragfactor']
        recordData['lapNo'] = lapNo

        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeStart']:
            lapTable[lapIx]['HRstart'] = recordTable[recordIx]['HR']
            lapTable[lapIx]['recordNoStart'] = recordIx
        
        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeEnd']:
            lapTable[lapIx]['HRend'] = recordTable[recordIx]['HR']
            lapTable[lapIx]['recordNoEnd'] = recordIx
            if lapTable[lapIx]['lapDist'] == None or lapTable[lapIx]['lapDist'] == 0:
                if lapIx == 0:
                    lapTable[lapIx]['lapDist'] = recordData['distance']
                else:
                    lapTable[lapIx]['lapDist'] = recordData['distance'] - lapTable[lapIx - 1]['totDist']
            if lapTable[lapIx]['totDist'] in [0, None]:
                lapTable[lapIx]['totDist'] = recordData['distance']
            if lapTable[lapIx]['avgSpeed'] in [0, None]:
                lapTable[lapIx]['avgSpeed'] = lapTable[lapIx]['lapDist'] / lapTable[lapIx]['lapTime']
            if lapTable[lapIx]['avgSpeed2'] in [0, None]:
                lapTable[lapIx]['avgSpeed2'] = speedLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            if lapTable[lapIx]['avgCad'] in [0, None]:
                lapTable[lapIx]['avgCad'] = cadLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            if lapTable[lapIx]['avgPower'] in [0, None]:
                lapTable[lapIx]['avgPower'] = powerLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['avgStrokeLen'] = CIQstrokeLengthLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['avgDragFactor'] = CIQdragfactorLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['stepLen'] = (round((lapTable[lapIx]['lapDist'] / 10) / (lapTable[lapIx]['avgCad'] * lapTable[lapIx]['lapTime'] / 60),2))  # step length acc to FFRT
            speedLapSum = 0
            cadLapSum = 0
            powerLapSum = 0
            CIQstrokeLengthLapSum = 0
            CIQdragfactorLapSum = 0
            lapIx += 1
            lapNo = lapIx+1
        
        recordIx += 1
        
        
    #print ("lapNo, lapData['lapDist'], lapData['totDist'], lapData['avgStrokeLen'], lapData['lapTime'], '=', lapData['avgCad'], lapData['HRstart'], lapData['HRend'], lapData['avgSpeed'], lapData['avgDragFactor'], lapData['stepLen']")
    #print(lapIx)
    #for lapData in lapTable:
        #print (lapNo, lapData['lapDist'], lapData['totDist'], lapData['avgStrokeLen'], lapData['lapTime'], '=', lapData['avgCad'], lapData['HRstart'], lapData['HRend'], lapData['avgSpeed'], lapData['avgDragFactor'], lapData['stepLen'])

    totDist = lapTable[lapIx-1]['totDist']
    #print ('last rec: ', recordTable[recordIx - 1]['timestamp'])

    return lapTable, recordTable, totDist

# ================================================================

def calc_avg_in_lapTable(lapTable):
    print('---calc_avg_in_lapTable', datetime.now())
    lapIx = 0
    lapNo = lapIx+1
    activeTime = 0
    restTime = 0
    sumSpeedActive = 0
    sumCadActive = 0
    sumPowerActive = 0
    sumSpeedRest = 0
    sumCadRest = 0
    sumPowerRest = 0
    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            activeTime += lapData['lapTime']
            sumSpeedActive += lapData['avgSpeed'] * lapData['lapTime']
            sumCadActive += lapData['avgCad'] * lapData['lapTime']
            sumPowerActive += lapData['avgPower'] * lapData['lapTime']
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            restTime += lapData['lapTime']
            sumSpeedRest += lapData['avgSpeed'] * lapData['lapTime']
            sumCadRest += lapData['avgCad'] * lapData['lapTime']
            sumPowerRest += lapData['avgPower'] * lapData['lapTime']
    avgSpeedActive = sumSpeedActive / activeTime
    avgCadActive = sumCadActive / activeTime
    avgPowerActive = sumPowerActive / activeTime
    avgSpeedRest = sumSpeedRest / restTime
    avgCadRest  = sumCadRest / restTime
    avgPowerRest  = sumPowerRest / restTime
    return avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest


# ================================================================

def saveSpinBikeLapTable_to_txt():
    print('----saveSpinBikeLapTable_to_txt', datetime.now())
    
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fit_file_path)
    outLapTxt_file.write ('Src: ' + fit_file_path +'\n')

    # ACTIVE LAPS 
    print('-----------')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            # Create 
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) +  '->'
            lapTxtLine += str(lapData['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            if lapData['avgCad'] != 0: lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'rpm '
            if lapData['avgSpeed'] != 0: lapTxtLine += mps2kmph_1decStr(lapData['avgSpeed']) + 'km/h ' 
            if lapData['avgPower'] != 0: lapTxtLine += str(int(round(lapData['avgPower'],1))) + 'W ' 
            if lapData['lapDist'] != 0: lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km'
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
            
    # Avg data for ACTIVE LAPS
    avgLine = ''
    if lapData['avgCad'] != 0:avgLine += 'avgCad: ' + str(round(avgCadActive,1)) + 'rpm '
    if lapData['avgSpeed'] != 0: avgLine += 'avgSpeed: ' + mps2kmph_1decStr(avgSpeedActive) + 'km/h '
    if lapData['lapDist'] != 0: avgLine += 'avgPower: ' + str(round(avgPowerActive,1)) + 'W'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')
    
    # REST LAPS
    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) + '->'
            lapTxtLine += str(lapData['HRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            if lapData['avgCad'] != 0: lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'rpm '
            if lapData['avgSpeed'] != 0: lapTxtLine += mps2kmph_1decStr(lapData['avgSpeed']) + 'km/h ' 
            if lapData['avgPower'] != 0: lapTxtLine += str(int(round(lapData['avgPower'],1))) + 'W ' 
            if lapData['lapDist'] != 0: lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km'
            if (lapData['maxHR'] - lapData['HRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapData['maxHR'] - lapData['HRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    # Avg data for REST LAPS
    avgLine = ''
    if lapData['avgCad'] != 0: avgLine += 'avgCad: ' + str(round(avgCadRest,1)) + 'rpm '
    if lapData['avgSpeed'] != 0: avgLine += 'avgSpeed: ' + mps2kmph_1decStr(avgSpeedRest) + 'km/h '
    if lapData['avgPower'] != 0: avgLine += 'avgPower: ' + str(round(avgPowerRest,1)) + 'W'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')
   
    return

# ================================================================

def saveGymBikeLapTable_to_txt():
    print('----saveGymBikeLapTable_to_txt', datetime.now())
    
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fit_file_path)
    outLapTxt_file.write ('Src: ' + fit_file_path +'\n')
    print('Src: ' + lap_txtFile_path)
    outLapTxt_file.write ('Src: ' + lap_txtFile_path + '\n')

    # ACTIVE LAPS 
    print('-----------')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            # Create 
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += 'lv' + str(lapData['level']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) +  '->'
            lapTxtLine += str(lapData['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'rpm '
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += mps2kmph_1decStr(lapData['avgSpeed']) + 'km/h' 
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
            
    # Avg data for ACTIVE LAPS
    avgLine = 'avgSpeed: ' + mps2kmph_1decStr(avgSpeedActive) + 'km/h, avgCad: ' + str(round(avgCadActive,1)) + 'rpm'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')

# REST LAPS
    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += 'lv' + str(lapData['level']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) + '->'
            lapTxtLine += str(lapData['HRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'rpm '
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += mps2kmph_1decStr(lapData['avgSpeed']) + 'km/h' 
            if (lapData['maxHR'] - lapData['HRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapData['maxHR'] - lapData['HRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    # Avg data for REST LAPS
    avgLine = 'avgSpeed: ' + mps2kmph_1decStr(avgSpeedRest) + 'km/h, avgCad: ' + str(round(avgCadRest,1)) + 'rpm'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')

    # LAP DISTANCES to be used if script need to be run again
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('Original lap data from text file written during indoor activity\n')
    outLapTxt_file.write ('-----------\n')

    lapTxtLine = 'level totDist'
    outLapTxt_file.write (lapTxtLine + '\n')
    for lapData in lapTable:
        lapTxtLine = ''
        lapTxtLine += str(lapData['level'])
        lapTxtLine += ' '
        lapTxtLine += str(lapData['totDist'])
        outLapTxt_file.write (lapTxtLine + '\n')

    # LAP DISTANCES to be used in FFRT when calculating indoor activities like 'indoor bike' or elliptical/cross trainer
    print('-----------')
    print('LAP DISTANCES to be used in FFRT when calculating indoor activities like indoor bike or elliptical/cross trainer')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('LAP DISTANCES to be used in FFRT when calculating indoor activities like indoor bike or elliptical/cross trainer\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
            lapTxtLine = 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += m2km_2decStr(lapData['lapDist']) + 'km '
            lapTxtLine += str(lapData['stepLen'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
    print('Totaldist: ' + m2km_2decStr(totDist) + ' km')
    outLapTxt_file.write ('Totaldist: ' + m2km_2decStr(totDist) + ' km' + '\n')
    
    return

# ================================================================

def saveCTLapTable_to_txt():
    print('----saveCTLapTable_to_txt', datetime.now())
    
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fit_file_path)
    outLapTxt_file.write ('Src: ' + fit_file_path +'\n')
    print('Src: ' + lap_txtFile_path)
    outLapTxt_file.write ('Src: ' + lap_txtFile_path + '\n')

    # ACTIVE LAPS 
    print('-----------')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            # Create 
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += 'lv' + str(lapData['level']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) +  '->'
            lapTxtLine += str(lapData['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'rpm '
            lapTxtLine += mps2minpkm_Str(lapData['avgSpeed']) + 'min/km ' 
            lapTxtLine += mps2kmph_1decStr(lapData['avgSpeed']) + 'km/h' 
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
            
    # Avg data for ACTIVE LAPS
    avgLine = ''
    avgLine += 'avgCad: ' + str(round(avgCadActive,1)) + 'rpm, '
    avgLine += 'avgPace: ' + mps2minpkm_Str(avgSpeedActive) + 'min/km, '
    avgLine += 'avgSpeed: ' + mps2kmph_1decStr(avgSpeedActive) + 'km/h'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')
    
    # REST LAPS
    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += 'lv' + str(lapData['level']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) + '->'
            lapTxtLine += str(lapData['HRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'rpm '
            lapTxtLine += mps2minpkm_Str(lapData['avgSpeed']) + 'min/km ' 
            lapTxtLine += mps2kmph_1decStr(lapData['avgSpeed']) + 'km/h' 
            if (lapData['maxHR'] - lapData['HRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapData['maxHR'] - lapData['HRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    # Avg data for REST LAPS
    avgLine += 'avgCad: ' + str(round(avgCadRest,1)) + 'rpm, '
    avgLine = 'avgPace: ' + mps2minpkm_Str(avgSpeedRest) + 'min/km, '
    avgLine += 'avgSpeed: ' + mps2kmph_1decStr(avgSpeedRest) + 'km/h'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')

    # LAP DISTANCES to be used if script need to be run again
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('Original lap data from text file written during indoor activity\n')
    outLapTxt_file.write ('-----------\n')

    lapTxtLine = 'level totDist'
    outLapTxt_file.write (lapTxtLine + '\n')
    for lapData in lapTable:
        lapTxtLine = ''
        lapTxtLine += str(lapData['level'])
        lapTxtLine += ' '
        lapTxtLine += str(int(lapData['totDist']/10))
        outLapTxt_file.write (lapTxtLine + '\n')

    # LAP DISTANCES to be used in FFRT when calculating indoor activities like 'indoor bike' or elliptical/cross trainer
    print('-----------')
    print('LAP DISTANCES to be used in FFRT when calculating indoor activities like indoor bike or elliptical/cross trainer')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('LAP DISTANCES to be used in FFRT when calculating indoor activities like indoor bike or elliptical/cross trainer\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
            lapTxtLine = 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += m2km_2decStr(lapData['lapDist']) + 'km '
            lapTxtLine += str(lapData['stepLen'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
    print('Totaldist: ' + m2km_2decStr(totDist) + ' km')
    outLapTxt_file.write ('Totaldist: ' + m2km_2decStr(totDist) + ' km' + '\n')
    
    return

# ================================================================

def saveSkiErgLapTable_to_txt():
    print('----saveSkiErgLapTable_to_txt', datetime.now())
    
    # CSV file with to be used to merge data in FFRT (developer tab, open in xl, paste data from csv, reimport xl)
    outNewDistTxt_file = open(outnewDistTxt_file_path, 'w')
    outNewDistTxt_file.write('distance;cadence;power\n')
    for record in recordTable:
        outNewDistTxt_file.write(str(record['distance']/1000).replace('.',',') + ';' + str(record['cadence']).replace('.',',') + ';' + str(record['power']).replace('.',',') + '\n')
        
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outnewDistTxt_file_path +'\n')
    print('Dest: ' + outnewDistTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fit_file_path)
    outLapTxt_file.write ('Src: ' + fit_file_path +'\n')
    print('Src: ' + C2fit_file_path)
    outLapTxt_file.write ('Src: ' + C2fit_file_path + '\n')

    # ACTIVE LAPS 
    print('-----------')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            # Create 
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += 'df' + str(int(round(lapData['avgDragFactor'],0))) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) +  '->'
            lapTxtLine += str(lapData['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'spm '
            lapTxtLine += mps2minp500m_Str(lapData['lapDist']/lapData['lapTime']) + 'min/500m ' 
            lapTxtLine += str(int(round(lapData['avgPower'],1))) + 'W ' 
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
            
    # Avg data for ACTIVE LAPS
    avgLine = ''
    avgLine += 'avgCad: ' + str(round(avgCadActive,1)) + 'spm '
    avgLine += 'avgPace: ' + mps2minp500m_Str(avgSpeedActive) + 'min/500m '
    avgLine += 'avgPower: ' + str(round(avgPowerActive,1)) + 'W '
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')
    
    # REST LAPS
    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) + ' '
            lapTxtLine += 'df' + str(int(round(lapData['avgDragFactor'],0))) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) + '->'
            lapTxtLine += str(lapData['HRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'spm '
            lapTxtLine += mps2minp500m_Str(lapData['avgSpeed']) + 'min/500m ' 
            lapTxtLine += str(int(round(lapData['avgPower'],1))) + 'W ' 
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            if (lapData['maxHR'] - lapData['HRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapData['maxHR'] - lapData['HRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    # Avg data for REST LAPS
    avgLine = ''
    avgLine += 'avgCad: ' + str(round(avgCadRest,1)) + 'spm '
    avgLine += 'avgPace: ' + mps2minp500m_Str(avgSpeedRest) + 'min/500m '
    avgLine += 'avgPower: ' + str(round(avgPowerRest,1)) + 'W '
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')

    # Create speed comparation between diff lap starts for SkiErg - written only to terminal
    print('-----------')
    print('Speed compare with diff lap start points')
    print('-----------')
    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            speedLine = ''
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-4]['distance']-recordTable[lapData['recordNoStart']-4]['distance'])/lapData['lapTime']) + '-4 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-3]['distance']-recordTable[lapData['recordNoStart']-3]['distance'])/lapData['lapTime']) + '-3 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-2]['distance']-recordTable[lapData['recordNoStart']-2]['distance'])/lapData['lapTime']) + '-2 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-1]['distance']-recordTable[lapData['recordNoStart']-1]['distance'])/lapData['lapTime']) + '-1 '
            speedLine += mps2minp500m_Str( lapData['lapDist']/lapData['lapTime']) + '-0 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']+1]['distance']-recordTable[lapData['recordNoStart']+1]['distance'])/lapData['lapTime']) + '+1 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']+2]['distance']-recordTable[lapData['recordNoStart']+2]['distance'])/lapData['lapTime']) + '+2 '
            print(speedLine)
   
    return

# ================================================================

def saveRunLapTable_to_txt():
    print('----saveSpinBikeLapTable_to_txt', datetime.now())
    
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTimeSumLapTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fit_file_path)
    outLapTxt_file.write ('Src: ' + fit_file_path +'\n')

    # ACTIVE LAPS 
    print('-----------')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            # Create 
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) +  '->'
            lapTxtLine += str(lapData['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad']*2,0))) + 'spm '
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += mps2minpkm_Str(lapData['avgSpeed']) + 'min/km ' 
            lapTxtLine += str(int(round(lapData['avgPower'],1))) + 'W' 
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
            
    # Avg data for ACTIVE LAPS
    avgLine = 'avgPace: ' + mps2minpkm_Str(avgSpeedActive) + 'min/km, avgCad: ' + str(round(avgCadActive*2,1)) + 'spm, avgPower: ' + str(round(avgPowerActive,1)) + 'W'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')
    
    # REST LAPS
    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            lapTxtLine = ''
            lapTxtLine += 'lap' + str(lapData['lapNo']) +  ' '
            lapTxtLine += str(lapData['HRstart'])
            if lapData['HRend'] >= lapData['HRstart']: lapTxtLine += '+'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) + '->'
            lapTxtLine += str(lapData['HRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad']*2,0))) + 'spm '
            lapTxtLine += m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += mps2minpkm_Str(lapData['avgSpeed']) + 'min/km ' 
            lapTxtLine += str(int(round(lapData['avgPower'],1))) + 'W' 
            if (lapData['maxHR'] - lapData['HRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapData['maxHR'] - lapData['HRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')

    # Avg data for REST LAPS
    avgLine = 'avgPace: ' + mps2minpkm_Str(avgSpeedRest) + 'min/km, avgCad: ' + str(round(avgCadRest*2,1)) + 'spm, avgPower: ' + str(round(avgPowerRest,1)) + 'W'
    print (avgLine)
    outLapTxt_file.write (avgLine + '\n')
   
    return

# ================================================================
# ================================================================
# ================================================================
# ================================================================

noArgs = len(sys.argv)
print(noArgs, sys.argv)
if noArgs <= 1:
    #activityType = 'spinbike'
    #activityType = 'gymbike'
    #activityType = 'ct'
    activityType = 'skierg'
    #activityType = 'run'
else:
    activityType = sys.argv[1]

activityType = activityType.lower()
if activityType in ['spinbike','gymbike','ct','skierg','run']:
    print('Using activityType: ' + activityType)
else:
    print('---------------Wrong activityType!')
    exit()

test = 0                # 0 if NO TEST
startWithWktStep = 'WarmupThenActive'    # If no workout steps in file, then start with this, can be "WarmupThenActive" OR "WarmupAndRest"

device = 'pc'
#device = 'pc1drv'
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

# File path to your FIT txtFile
if noArgs > 2:
    fit_file_path = pathPrefix + pathDL + sys.argv[2]
elif test == 0:
    fit_file_path = pathPrefix + pathDL + '17090763560.zip'
else:
    if activityType == 'spinbike':
        fit_file_path = pathPrefix + pathDL + 'TESTfiles/2024-09-26-14-27-04-spinbike-18.4km-40.04min-analyzed.fit'
    elif activityType == 'gymbike':
        fit_file_path = pathPrefix + pathDL + 'TESTfiles/2024-09-14-07-46-48-gymbike-31.2km-60.43min-analyzed.fit'
    elif activityType == 'skierg':
        fit_file_path = pathPrefix + pathDL + 'TESTfiles/2024-09-30-14-48-09-skierg-11.0km-61.05min-analyzed.fit'
    elif activityType == 'run':
        fit_file_path = pathPrefix + pathDL + 'TESTfiles/2024-08-02-15-27-43-run-5.4km-61.23min-analyzed.fit'

fileName = pathlib.Path(fit_file_path).stem
ext = pathlib.Path(fit_file_path).suffix
if ext =='.zip':
    zip_file_path = fit_file_path
    file_exist = os.path.isfile(zip_file_path)
    if not file_exist:
        print('---------------- ZIP File does not exist!')
        exit()
    zip = ZipFile(zip_file_path)
    zip.extractall(pathPrefix + pathDL)
    zip.close()
    fit_file_path = pathPrefix + pathDL + fileName + '_ACTIVITY.fit'

file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit File does not exist!')
    exit()

if activityType == 'skierg':
    if noArgs > 3:
        C2fit_file_path = pathPrefix + pathDL + sys.argv[3]
    elif test == 0:
        C2fit_file_path = pathPrefix + pathDL + '240927-concept2-logbook-workout-92357194.fit'
    else:
        C2fit_file_path = pathPrefix + pathDL + 'TESTfiles/testSkiErgConcept2File.fit'
    file_exist = os.path.isfile(C2fit_file_path)
    if not file_exist:
        print('---------------- C2Fit txtFile does not exist!')
        exit()

if activityType == 'gymbike' or activityType == 'ct':
    if test == 0:
        lap_txtFile_path = pathPrefix + 'documents/indoorBikeLapsLatest.txt'
    else:
        lap_txtFile_path = 'c:/Users/peter/OneDrive/Dokument Peter OneDrive/Träning/ActivityFiles/Peter activities/TESTfiles/testManualLaps.txt'
    print(lap_txtFile_path)
    file_exist = os.path.isfile(lap_txtFile_path)
    if not file_exist:
        print('---------------- Lap txtFile does not exist! ', lap_txtFile_path)
        exit()

# ================================================================

if activityType == 'gymbike' or activityType == 'ct':
    lapFromTxtTbl, lapCountTxt = extract_lap_data_from_txt(lap_txtFile_path)

if activityType == 'skierg':
    C2recordTable, C2timeFirstRecord, C2timeLastRecord = extract_record_data_from_C2fit(C2fit_file_path)

recordTable, timeFirstRecord, timeLastRecord = extract_record_data_from_fit(fit_file_path)
lapTable, lapCountFit = extract_lap_data_from_fit(fit_file_path, startWithWktStep)

if activityType == 'gymbike' or activityType == 'ct':
    print('lapCount in TXT and FIT files: ', lapCountTxt, lapCountFit)
    if lapCountTxt != lapCountFit: exit()

if activityType == 'skierg':
    recordTable = merge_C2records_with_recordTable(recordTable, C2recordTable)

lapTable, totTimeSumLapTime = calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord)

if activityType == 'gymbike' or activityType == 'ct':
    lapTable, totDist = merge_lapData_from_txt(lapTable, lapFromTxtTbl)

lapTable, recordTable, totDist = calc_lapData_from_recordTable(recordTable, lapTable)
avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest = calc_avg_in_lapTable(lapTable)

if activityType == 'skierg':
    print('date from C2 and watch file: ', C2timeFirstRecord, timeFirstRecord)
    if C2timeFirstRecord.date() != timeFirstRecord.date(): exit()

out_baseFileName = str(timeFirstRecord).replace(':','-').replace(' ','-') + '-' + activityType + '-' + m2km_1decStr(totDist) + 'km-' + sec2minSec_shStr(totTimeSumLapTime).replace(':','.')

if test == 0:
    # File path to your destination text txtFile
    outLapTxt_file_path = pathPrefix + pathDL + out_baseFileName + 'min-LapTables.txt'
    # File path to your destination text txtFile
    outnewDistTxt_file_path = pathPrefix + pathDL + out_baseFileName + 'min-newDistCadPower.csv'
else:
    # File path to your destination text txtFile
    outLapTxt_file_path = pathPrefix + pathDL + 'TESTfiles/' + out_baseFileName + 'min-LapTables.txt'
    # File path to your destination text txtFile
    outnewDistTxt_file_path = pathPrefix + pathDL + 'TESTfiles/' + out_baseFileName + 'min-newDistCadPower.csv'

if test != 0:
    print('================ TEST =================')
if activityType == 'spinbike':
    saveSpinBikeLapTable_to_txt()
if activityType == 'gymbike':
    saveGymBikeLapTable_to_txt()
if activityType == 'ct':
    saveCTLapTable_to_txt()
if activityType == 'skierg':
    saveSkiErgLapTable_to_txt()
if activityType == 'run':
    saveRunLapTable_to_txt()

if test == 0:
    newFitFileName = pathPrefix + pathDL + out_baseFileName + 'min-analyzed.fit'
else:
    newFitFileName = pathPrefix + pathDL + 'TESTfiles/' + out_baseFileName + 'min-analyzed.fit'

if fit_file_path != newFitFileName:
    if os.path.exists(newFitFileName):
        os.remove(newFitFileName)
    os.rename(fit_file_path, newFitFileName)
    if ext == '.zip':
        os.remove(zip_file_path)

print('-----THE END', datetime.now())
if test != 0:
    print('================ TEST END =================')
