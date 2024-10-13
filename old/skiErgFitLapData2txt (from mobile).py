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
def mps2minpkm_Str (speed):
    minpkmStr = sec2minSec_longStr(1/(speed / 1000))
    return (minpkmStr)

# ================================================================
def mps2minp500m_Str (speed):
    minp500mStr = sec2minSec_longStr(1/(speed / 1000)/2)
    return (minp500mStr)

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
"""
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
    print('C2record times from ' + str(timeFirstRecord) + ' to ' + str(timeLastRecord))
    print('C2record no from 0 to ' + str(recordIx - 1))
    
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
            #if (recordIx / 300) == (int(recordIx/300)): print (fit_record_data.name, fit_record_data.value)
            if fit_record_data.name == 'timestamp': recordData['timestamp'] = fit_record_data.value
            elif fit_record_data.name == 'heart_rate': recordData['HR'] = fit_record_data.value
            elif fit_record_data.name == 'Level': recordData['CIQlevel'] = fit_record_data.value
            elif fit_record_data.name == 'Training_session': recordData['CIQtrainSess'] = fit_record_data.value
            elif fit_record_data.name == 'Distance': recordData['distance'] = fit_record_data.value
            elif fit_record_data.name == 'Speed': recordData['speed'] = fit_record_data.value
            elif fit_record_data.name == 'StrokeLength': recordData['CIQstrokeLen'] = fit_record_data.value
            elif fit_record_data.name == 'DragFactor': recordData['CIQdragfactor'] = fit_record_data.value
            #print(fit_record_data)
            #if recordIx <10: print(fit_record_data.name, fit_record_data.value)
        recordTable.append(recordData)
        if recordIx == 0: timeFirstRecord = recordData['timestamp']
        recordIx += 1
    timeLastRecord = recordData['timestamp']
    print('record times from ' + str(timeFirstRecord) + ' to ' + str(timeLastRecord))
    print('record no from 0 to ' + str(recordIx - 1))
    
    #for recordIx in range(0, 16):
    #    print (recordTable[recordIx]['distance'])

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
    while recordTable[recordIx]['speed'] == 0 or recordTable[recordIx]['speed'] == None:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['speed']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['speed'] = firstValue
    
    # FIX CIQstrokeLen = 0 in BEGINNING
    recordIx = 0
    while recordTable[recordIx]['CIQstrokeLen'] == 0 or recordTable[recordIx]['CIQstrokeLen'] == None:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['CIQstrokeLen']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['CIQstrokeLen'] = firstValue
    
    # FIX CIQdragfactor = 1 in BEGINNING
    recordIx = 0
    while recordTable[recordIx]['CIQdragfactor'] == 1 or recordTable[recordIx]['CIQdragfactor'] == None:
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

def extract_lap_data_from_fit(fit_file_path):
    print('--extract_LAP_data_from_fit', datetime.now())
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fit_file_path)
    
    # Initialize lists to store lap data
    lapTable = []
    # Iterate over all messages of type "lap"
    for lap in fitfile.get_messages('lap'):
        #print('\n',lap)
        
        # Dictionary to store lap information
        lapData = {
            'lapNo': None,
            'timeStart': None,
            'timeEnd': None,
            'recordNoStart': None,
            'recordNoEnd': None,
            'wktStepType': None,
            'lapTime': None,
            'avgCad': None,
            'maxHR': None,
            'avgHR': None,
            'HRstart': None,
            'HRend': None,
            'totDist': None,
            'lapDist': None,
            'avgSpeed': None,      # avg calc from dist and time
            'avgSpeed2': None,    # avg calc from values
            'level': None,
            'stepLen': None,
            'avgStrokeLen': None,
            'avgDragFactor': None
        }
        for lap_data_field in lap:
            #if lap_data_field.value != None:
                #print (lap_data_field.name, lap_data_field.value)
            if lap_data_field.name == 'message_index': lapData['lapNo'] = lap_data_field.value
            elif lap_data_field.name == 'total_timer_time': lapData['lapTime'] = int(round(lap_data_field.value,0))
            elif lap_data_field.name == 'start_time': lapData['timeStart'] = lap_data_field.value
            elif lap_data_field.name == 'intensity': lapData['wktStepType'] = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate': lapData['maxHR'] = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate': lapData['avgHR'] = lap_data_field.value
            #print (lap_data_field.name,lap_data_field.value)
        #print('start:', lapData['timeStart'])
        lapTable.append(lapData)

    return lapTable

# ================================================================

def merge_C2records_with_recordTble(recordTable, C2recordTable):
    print('---merge_C2records_with_recordTble', datetime.now())
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
        
    # FIX Cadence = 0 in BEGINNING
    recordIx = 0
    while recordTable[recordIx]['cadence'] == 0 or recordTable[recordIx]['cadence'] == None:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['cadence']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['cadence'] = firstValue
    
    # FIX Power = 0 in BEGINNING
    recordIx = 0
    while recordTable[recordIx]['power'] == 0 or recordTable[recordIx]['power'] == None:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['power']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['power'] = firstValue
    
    # FIX None values and Cadence High
    for recordIx in range(len(recordTable)):
        if recordTable[recordIx]['cadence'] == None:
            recordTable[recordIx]['cadence'] = recordTable[recordIx-1]['cadence']
        if recordTable[recordIx]['cadence'] > 70:
            print('HIGH cadence: ', recordTable[recordIx-1]['cadence'], '->', recordTable[recordIx]['cadence'], ' @', recordIx)
            recordTable[recordIx]['cadence'] = recordTable[recordIx-1]['cadence']
        if recordTable[recordIx]['power'] == None:
            recordTable[recordIx]['power'] = recordTable[recordIx-1]['power']

    #for recordIx in range(40):
        #print (recordTable[recordIx]['distance'], recordTable[recordIx]['C2distance'], recordTable[recordIx]['speed'], recordTable[recordIx]['C2speed'], recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])
        #print (recordTable[recordIx]['cadence'], recordTable[recordIx]['power'])

    return recordTable

# ================================================================

def calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord):
    print('---calc_lapTimeEnd_in_lapTable', datetime.now())
    totTimeSumLapTime = 0
    lapIx = 0
    lapNo = lapIx+1
    for lapData in lapTable:
        if lapIx > 0:
            lapTable[lapIx-1]['timeEnd'] = lapData['timeStart'] + timedelta(seconds=-1)
        totTimeSumLapTime += lapData['lapTime']
        lapIx += 1
        lapNo = lapIx+1

        #print(lapData)
        #wait = input("Press Enter to continue.")
    lapData['timeEnd'] = timeLastRecord
    lapCountLapFit = len(lapTable)
    
    """
    for lapData in lapTable:
        print(lapData['timeStart'], lapData['timeEnd'])
    return lapTable, totTimeSumLapTime, lapCountLapFit
    #"""
    return lapTable, totTimeSumLapTime, lapCountLapFit

# ================================================================

def calc_lapData_from_recordDataTbl(recordTable, lapTable):
    print('---calc_lapData_from_recordDataTbl', datetime.now())
    recordIx = 0
    lapIx = 0
    lapNo = lapIx+1
    speedLapSum = 0
    cadLapSum = 0
    CIQstrokeLengthLapSum = 0
    CIQdragfactorLapSum = 0

    for recordData in recordTable:
        speedLapSum += recordData ['speed']
        cadLapSum += recordData ['cadence']
        CIQstrokeLengthLapSum += recordData['CIQstrokeLen']
        CIQdragfactorLapSum += recordData['CIQdragfactor']
        recordData['lapNo'] = lapNo

        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeStart']:
            lapTable[lapIx]['HRstart'] = recordTable[recordIx]['HR']
            lapTable[lapIx]['recordNoStart'] = recordIx
        
        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeEnd']:
            lapTable[lapIx]['HRend'] = recordTable[recordIx]['HR']
            lapTable[lapIx]['recordNoEnd'] = recordIx
            lapTable[lapIx]['avgSpeed2'] = speedLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['avgCad'] = cadLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['avgStrokeLen'] = CIQstrokeLengthLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['avgDragFactor'] = CIQdragfactorLapSum / (lapTable[lapIx]['recordNoEnd'] - lapTable[lapIx]['recordNoStart'])
            lapTable[lapIx]['totDist'] = recordData['distance']
            if lapIx == 0:
                lapTable[lapIx]['lapDist'] = recordData['distance']
            else:
                lapTable[lapIx]['lapDist'] = recordData['distance'] - lapTable[lapIx - 1]['totDist']
            lapTable[lapIx]['stepLen'] = (round((lapTable[lapIx]['lapDist'] / 10) / (lapTable[lapIx]['avgCad'] * lapTable[lapIx]['lapTime'] / 60),2))  # step length acc to FFRT
            speedLapSum = 0
            cadLapSum = 0
            CIQstrokeLengthLapSum = 0
            CIQdragfactorLapSum = 0
            lapIx += 1
            lapNo = lapIx+1
        
        recordIx += 1
        
        
    """
    lapNo = 0
    for lapData in lapTable:
        print (lapNo, lapData['lapDist'], lapData['avgStrokeLen'], lapData['lapTime'], '=', lapData['avgCad'], lapData['HRstart'], lapData['HRend'], lapData['avgSpeed'], lapData['avgDragFactor'], lapData['stepLen'])
        lapNo += 1
    #"""
    totDist = recordData['distance']
    lapCountHRfit = len(lapTable)
    #print ('last rec: ', recordTable[recordIx - 1]['timestamp'])

    return lapTable, recordTable, totDist, lapCountHRfit

# ================================================================

def calc_avg_in_lapTable(lapTable):
    print('---calc_avg_in_lapTable', datetime.now())
    lapIx = 0
    lapNo = lapIx+1
    activeTime = 0
    restTime = 0
    sumSpeedActive = 0
    sumCadActive = 0
    sumSpeedRest = 0
    sumCadRest = 0
    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            activeTime += lapData['lapTime']
            sumSpeedActive += lapData['avgSpeed'] * lapData['lapTime']
            sumCadActive += lapData['avgCad'] * lapData['lapTime']
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            restTime += lapData['lapTime']
            sumSpeedRest += lapData['avgSpeed'] * lapData['lapTime']
            sumCadRest += lapData['avgCad'] * lapData['lapTime']
    avgSpeedActive = sumSpeedActive / activeTime
    avgCadActive = sumCadActive / activeTime
    avgSpeedRest = sumSpeedRest / restTime
    avgCadRest  = sumCadRest / restTime
    return avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest 


# ================================================================

#2def add_from_txt_and_fitHR(lapFitTable, lapHRtbl, lapFromTxtTbl):
def add_from_txt_and_fitHR(lapFitTable, lapHRtbl):
    print('----add_from_txt_and_fitHR', datetime.now())
    # Initialize lists to store lap data
    lapIx = 0

    for lapData in lapFitTable:
        
        lapData['HRstart'] = lapHRtbl[lapIx]['HRstart']
        lapData['HRend'] = lapHRtbl[lapIx]['HRend']
        #2lapRecord['totDist'] = lapFromTxtTbl[lapIx]['totDist']                               # (m)
        #2lapRecord['lapDist'] = lapFromTxtTbl[lapIx]['lapDist']                           # (m)
        #2lapRecord['level'] = lapFromTxtTbl[lapIx]['level'] 
        lapData['avgSpeed'] = lapData['lapDist'] / lapData['lapTime']  # (m/s)
        lapData['stepLen'] = (round((lapData['lapDist'] / 10) / (lapData['avgCad'] * lapData['lapTime'] / 60),2))  # step length acc to FFRT

        lapIx += 1

        # Append the lap information to the list
        #print(lapData)
        #wait = input("Press Enter to continue.")
        #print(lapData['totDist'])

    return lapFitTable, lapData['totDist']

# ================================================================

def saveLapTable_to_txt(outLapTxt_file_path, lapTable, recordTable):
    print('----saveLapTable_to_txt', datetime.now())
    
    outNewDistTxt_file = open(outnewDistTxt_file_path, 'w')
    outNewDistTxt_file.write('distance;cadence;power\n')
    for record in recordTable:
        outNewDistTxt_file.write(str(record['distance']/1000).replace('.',',') + ';' + str(record['cadence']).replace('.',',') + ';' + str(record['power']).replace('.',',') + '\n')
        
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    print('-----------')
    print('Active laps')
    print('-----------')
    outLapTxt_file.write ('Active laps\n')
    outLapTxt_file.write ('-----------\n')

    speedComp = []
    
    for lapData in lapTable:
        if lapData['wktStepType'] == 'active':
            lapTxtLine = 'lap' + str(lapData['lapNo']) + ' df' + str(int(round(lapData['avgDragFactor'],0))) +  ' '
            lapTxtLine += str(lapData['HRstart']) + '+' + str(lapData['HRend'] - lapData['HRstart']) +  '->'
            lapTxtLine += str(lapData['maxHR']) + 'maxHR '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'spm ' + m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += mps2minp500m_Str(lapData['lapDist']/lapData['lapTime']) + 'min/500m' 
            print (lapTxtLine)
            
            speedLine = ''
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-4]['distance']-recordTable[lapData['recordNoStart']-4]['distance'])/lapData['lapTime']) + '-4 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-3]['distance']-recordTable[lapData['recordNoStart']-3]['distance'])/lapData['lapTime']) + '-3 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-2]['distance']-recordTable[lapData['recordNoStart']-2]['distance'])/lapData['lapTime']) + '-2 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']-1]['distance']-recordTable[lapData['recordNoStart']-1]['distance'])/lapData['lapTime']) + '-1 '
            speedLine += mps2minp500m_Str( lapData['lapDist']/lapData['lapTime']) + '-0 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']+1]['distance']-recordTable[lapData['recordNoStart']+1]['distance'])/lapData['lapTime']) + '+1 '
            speedLine += mps2minp500m_Str( (recordTable[lapData['recordNoEnd']+2]['distance']-recordTable[lapData['recordNoStart']+2]['distance'])/lapData['lapTime']) + '+2 '
            speedComp.append(speedLine)
            
            outLapTxt_file.write (lapTxtLine + '\n')
            
            
    print ('avgSpeed: ', mps2minp500m_Str(avgSpeedActive), 'min/500m, avgCad: ', str(round(avgCadActive,1)), 'spm')
    outLapTxt_file.write ('avgSpeed: ' + mps2minp500m_Str(avgSpeedActive) +  'min/500m, avgCad: '+  str(round(avgCadActive,1)) + 'spm' + '\n')
    
    for speedLine in speedComp:
        print(speedLine)

    print('-----------')
    print('REST laps')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('REST laps\n')
    outLapTxt_file.write ('-----------\n')

    for lapData in lapTable:
        if lapData['wktStepType'] == 'rest' or lapData['wktStepType'] == 'recover':
            lapTxtLine = 'lap' + str(lapData['lapNo']) + ' df' + str(int(round(lapData['avgDragFactor'],0))) +  ' '
            lapTxtLine += str(lapData['maxHR']) + 'maxHR'
            lapTxtLine += str(lapData['HRend'] - lapData['HRstart']) + '->' + str(lapData['HRend']) +  ' '
            lapTxtLine += sec2minSec_shStr(lapData['lapTime']) + 'min '
            lapTxtLine += str(int(round(lapData['avgCad'],0))) + 'spm ' + m2km_1decStr(lapData['lapDist']) + 'km '
            lapTxtLine += mps2minp500m_Str(lapData['lapDist']/lapData['lapTime']) + 'min/500m' 
            if (lapData['maxHR'] - lapData['HRstart']) != 0:
                lapTxtLine += ' HRtop' + str(lapData['maxHR'] - lapData['HRstart'])
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
    print ('avgSpeed: ', mps2minp500m_Str(avgSpeedRest), 'min/500m, avgCad: ', str(round(avgCadRest,1)), 'spm')
    outLapTxt_file.write ('avgSpeed: ' + mps2minp500m_Str(avgSpeedRest) +  'min/500m, avgCad: '+  str(round(avgCadRest,1)) + 'spm' + '\n')

    print('-----------')
    print('ALL lap data ')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('ALL lap data\n')
    outLapTxt_file.write ('-----------\n')

    lapTxtLine = 'lapNo;level;HRstart;HRend;maxHR;avgHR;lapTime;avgCad;lapDist;totDist;wktStepType;avgSpeed'
    print (lapTxtLine)
    outLapTxt_file.write (lapTxtLine + '\n')
    for lapData in lapTable:
        lapTxtLine = str(lapData['lapNo']) + ';' + str(lapData['avgDragFactor']) + ';'
        lapTxtLine += str(lapData['HRstart']) + ';' + str(lapData['HRend']) +  ';'
        lapTxtLine += str(lapData['maxHR']) + ';' + str(lapData['avgHR']) + ';'
        lapTxtLine += str(lapData['lapTime']) + ';'
        lapTxtLine += str(lapData['avgCad']) + ';'
        lapTxtLine += str(lapData['lapDist']) + ';' + lapTxtLine + str(lapData['totDist']) + ';'
        lapTxtLine += str(lapData['wktStepType']) + ';'
        lapTxtLine += str(lapData['avgSpeed'])
        print (lapTxtLine)
        outLapTxt_file.write (lapTxtLine + '\n')

    print('-----------')
    print('LAP DISTANCES')
    print('-----------')
    outLapTxt_file.write ('-----------\n')
    outLapTxt_file.write ('LAP DISTANCES\n')
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
# ================================================================
# ================================================================
# ================================================================

#device = 'pc'
#device = 'pc1drv'
device = 'm'

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
C2fit_file_path = pathPrefix + pathDL + 'concept2-logbook-workout-92447795.fit'
file_exist = os.path.isfile(C2fit_file_path)
if not file_exist:
    print('---------------- C2Fit txtFile does not exist!')
    exit()

fit_file_path = pathPrefix + pathDL + '17168349018_ACTIVITY.fit'
file_exist = os.path.isfile(fit_file_path)
if not file_exist:
    print('---------------- Fit txtFile does not exist!')
    exit()

#lapFromTxtTbl, lapCountTxt = extract_lap_data_from_txt(lap_txtFile_path)
C2recordTable, C2timeFirstRecord, C2timeLastRecord = extract_record_data_from_C2fit(C2fit_file_path)
recordTable, timeFirstRecord, timeLastRecord = extract_record_data_from_fit(fit_file_path)
lapTable = extract_lap_data_from_fit(fit_file_path)
recordTable = merge_C2records_with_recordTble(recordTable, C2recordTable)
lapTable, totTimeSumLapTime, lapCountLapFit = calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord)
lapTable, recordTable, totDist, lapCountHRfit = calc_lapData_from_recordDataTbl(recordTable, lapTable)
avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest = calc_avg_in_lapTable(lapTable)

#2print('lapCount in all files: ', lapCountTxt, lapCountHRfit, lapCountLapFit)
print('lapCount in all files: ', lapCountHRfit, lapCountLapFit)
#2if lapCountTxt != lapCountHRfit: exit()
#2if lapCountTxt != lapCountLapFit: exit()
if lapCountHRfit != lapCountLapFit: exit()

#2lapTable, totDist = add_from_txt_and_fitHR(lapFitTable, lapHRtbl, lapFromTxtTbl)
#lapTable, totDist = add_from_txt_and_fitHR(lapFitTable, lapTable)

# File path to your destination text txtFile
outLapTxt_file_path = pathPrefix + pathDL + str(timeFirstRecord).replace(':','-').replace(' ','-') + '-' + m2km_1decStr(totDist) + 'km-' + sec2minSec_shStr(totTimeSumLapTime).replace(':','.') + 'min-LapTables.txt'

# File path to your destination text txtFile
outnewDistTxt_file_path = pathPrefix + pathDL + str(timeFirstRecord).replace(':','-').replace(' ','-') + '-' + m2km_1decStr(totDist) + 'km-' + sec2minSec_shStr(totTimeSumLapTime).replace(':','.') + 'min-newDistCadPower.csv'

saveLapTable_to_txt(outLapTxt_file_path, lapTable, recordTable)

print('-----THE END', datetime.now())
