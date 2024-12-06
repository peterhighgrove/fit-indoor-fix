import os
import sys
from datetime import datetime, time, timedelta
import pytz
import fitparse
from zipfile import ZipFile
from pathlib import Path 
import filecmp

# ================================================================
def min2minSek_longStr (minutes):
    min = int(minutes)
    sec = int(round((minutes - min) * 60,0))
    if sec == 60:
        min += 1
        sec = 0
    min_str = str(min) + ':'
    if sec < 10: min_str += '0' + str(sec)
    else: min_str += str(sec)
    return (min_str)

# ================================================================
def min2minSek_shStr (minutes):
    min = int(minutes)
    sec = int(round((minutes - min) * 60,0))
    if sec == 60:
        min += 1
        sec = 0
    min_str = str(min)
    if sec == 0: min_str += ''
    elif sec < 10: min_str += ':0' + str(sec)
    else: min_str += ':' + str(sec)
    return (min_str)

# ================================================================
def sec2minSec_longStr (seconds):
    min = int(seconds / 60)
    sec = int(round((seconds / 60 - min) * 60,0))
    if sec == 60:
        min += 1
        sec = 0
    min_str = str(min)
    if sec < 10: min_str += ':0' + str(sec)
    else: min_str += ':' + str(sec)
    return (min_str)

# ================================================================
def sec2minSec_shStr (seconds):
    min = int(seconds / 60)
    sec = int(round((seconds / 60 - min) * 60,0))
    if sec == 60:
        min += 1
        sec = 0
    min_str = str(min)
    if sec == 0: min_str += ''
    elif sec < 10: min_str += ':0' + str(sec)
    else: min_str += ':' + str(sec)
    return (min_str)

# ================================================================
def m2km_0decStr (meters):
    if meters in [0, None]:
        kmStr ='-'
    else:
        kmStr = str(round(meters / 1000, 0))
    return (kmStr)

# ================================================================
def m2km_1decStr (meters):
    if meters in [0, None]:
        kmStr ='-'
    else:
        kmStr = str(round(meters / 1000, 1))
    return (kmStr)

# ================================================================
def m2km_2decStr (meters):
    if meters in [0, None]:
        kmStr ='-'
    else:
        kmStr = str(round(meters / 1000, 2))
    return (kmStr)

# ================================================================
def mps2minpkm_Str (speed):
    if speed in [0, None]:
        minpkmStr = '-'
    else:
        minpkmStr = sec2minSec_longStr(1/(speed / 1000))
    return (minpkmStr)

# ================================================================
def mps2minp500m_Str (speed):
    if speed in [0, None]:
        minp500mStr = '-'
    else:
        minp500mStr = sec2minSec_longStr(1/(speed / 1000)/2)
    return (minp500mStr)

# ================================================================
def mps2kmph_0decStr (speed):
    if speed in [0, None]:
        kmphStr = '-'
    else:
        kmphStr = str(round(speed * 3600 / 1000, 0))
    return (kmphStr)

# ================================================================
def mps2kmph_1decStr (speed):
    if speed in [0, None]:
        kmphStr = '-'
    else:
        kmphStr = str(round(speed * 3600 / 1000, 1))
    return (kmphStr)

# ================================================================
def mps2kmph_2decStr (speed):
    if speed in [0, None]:
        kmphStr = '-'
    else:
        kmphStr = str(round(speed * 3600 / 1000, 2))
    return (kmphStr)

# ================================================================
def mps2kmph_alldecStr (speed):
    if speed in [0, None]:
        kmphStr = '0'
    else:
        kmphStr = str(speed * 3600 / 1000)
    return (kmphStr)

# ================================================================
# ================================================================
# ================================================================

def extract_session_data_from_fit(fitFile_path_name, fileInfo):
    if not doRename:
        print('--extract_SESSION_data_from_fit', datetime.now())
    
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fitFile_path_name)
    recordTable = []
    recordIx = 0
    # Iterate over all messages of type "record"
    for fit_record in fitfile.get_messages('device_info'):
        #if recordIx <10: print('\n',fit_record)
        # Extract data fields
        recordData = {
            'garminProd': None,
            'manufacturer': None,
            'SWver': None,
        }
        for fit_record_data in fit_record:
            if fit_record_data.name == 'garmin_product': recordData['garminProd'] = fit_record_data.value
            elif fit_record_data.name == 'manufacturer': recordData['manufacturer'] = fit_record_data.value
            elif fit_record_data.name == 'software_version': recordData['SWver'] = fit_record_data.value
            #if recordIx <10: print(fit_record_data)
            #if recordIx <10: print(fit_record_data.name, fit_record_data.value)
        recordTable.append(recordData)
        recordIx += 1
    garminProd = recordTable[0]['garminProd']
    manufacturer = recordTable[0]['manufacturer']
    SWver = recordTable[0]['SWver']
    #print(len(recordTable))
    
    if garminProd in ['', 0, None]: 
        if not manufacturer in ['', 0, None]: product = manufacturer
    elif garminProd == 4314: product = 'epix2pro'
    elif garminProd == 4257: product = 'fr265'
    elif garminProd == 4130: product = 'HRMpro'
    else: product = ''

    recordTable = []
    recordIx = 0
    startTime = None
    totDist = None
    avgSpeed = None
    noLaps = None
    totTime = None
    sport = ''
    subSport = ''
    actName = ''
    for fit_record in fitfile.get_messages('session'):
        #if recordIx <10: print('\n',fit_record)
        # Extract data fields

        for fit_record_data in fit_record:
            if fit_record_data.name == 'Distance' and totDist in [0, None]: totDist = fit_record_data.value
            elif fit_record_data.name == 'Speed' and avgSpeed in [0, None]: avgSpeed = fit_record_data.value
            elif fit_record_data.name == 'enhanced_avg_speed' and avgSpeed in [0, None]: avgSpeed = fit_record_data.value
            elif fit_record_data.name == 'num_laps': noLaps = fit_record_data.value
            elif fit_record_data.name == 'sport': sport = fit_record_data.value
            elif fit_record_data.name == 'start_time': 
                startTime = fit_record_data.value
                startTime = pytz.utc.localize(startTime).astimezone(timeZone)
            elif fit_record_data.name == 'sub_sport': subSport = fit_record_data.value
            elif fit_record_data.name == 'total_timer_time': totTime = fit_record_data.value
            elif fit_record_data.name == 'total_distance' and totDist in [0, None]: totDist = fit_record_data.value
            elif fit_record_data.name == 'unknown_110': actName = fit_record_data.value
            #if recordIx <10: print(fit_record_data)
            #if recordIx <10: print(fit_record_data.name, fit_record_data.value)
        recordTable.append(recordData)
        recordIx += 1
    #print(len(recordTable))
    
    recordTable = []
    recordIx = 0
    wktName = ''
    for fit_record in fitfile.get_messages('workout'):
        #if recordIx <10: print('\n',fit_record)
        # Extract data fields

        for fit_record_data in fit_record:
            if fit_record_data.name == 'wkt_name': wktName = fit_record_data.value
            #if recordIx <10: print(fit_record_data)
            #if activityType == 'info': print(fit_record_data.name, fit_record_data.value)
        recordTable.append(recordData)
        recordIx += 1
    actNameOrg = actName
    actName = actName.replace(' (bike)','')
    if actName == 'Cykel inne' and totDist > 0:
        actName = actName.replace('Cykel inne','SpinBike')
    else:
        actName = actName.replace('Cykel inne','GymBike')

    actName = actName.replace('spinbike','SBike')
    actName = actName.replace('SpinBike','SBike')
    actName = actName.replace('Spin','SpinBike')
    actName = actName.replace('SBike','SpinBike')

    if actName.find('Ellipt') >= 0: actName = 'Elliptical'
    actName = actName.replace('Elliptical','CT')
    actName = actName.replace('Ellipt','Elliptical')
    actName = actName.replace('ellipt','Elliptical')
    actName = actName.replace('CT','Elliptical')
    actName = actName.replace('ct','Elliptical')
    if actName == '':
        if subSport == 'indoor_cycling': actName = 'GymSpinBike'
        elif subSport == 'elliptical': actName = 'Elliptical'
        elif subSport in ['indoor_rowing', 'indoor_skiing']: actName = 'SkiErg'
        else: actName = sport + '_' + subSport

    #wktName = wktName.replace('×','x').replace('(','_').replace(')','_').replace(' ','_')
    actName = actName.replace(' ','_')

    wktNameOrg = wktName
    wktName = wktName.replace(' (bike)','')
    wktName = wktName.replace('/','!')
    wktName = wktName.replace(' ','_')
    
    infoLine = '---------------\nACTIVITY FILE INFO before\n---------------\n'
    infoLine += 'StartTime: ' + str(startTime) + ' DST: ' + str(startTime.dst()) + '\n'
    infoLine += 'Prod: ' + product + ' v' + str(SWver) + ', ProdNo: ' + str(garminProd) + ', Manuf: ' + manufacturer + '\n'
    infoLine += 'WatchActivity: ' + actNameOrg + '->' + actName + ', Sport: ' + sport + ', subSport: ' + subSport + '\n'
    infoLine += 'WktName: ' + wktNameOrg + '->' + wktName + ', no of Laps: ' + str(noLaps) + '\n'
    infoLine += sec2minSec_longStr(totTime) + 'min, '
    infoLine += m2km_1decStr(totDist) + 'km, ' + mps2kmph_1decStr(avgSpeed) + 'km/h\n'
    infoLine += '----------------\n'
    print(infoLine)

    fileInfo += infoLine

    if activityType == 'info':

        print('\nLAPS\n-----------')
        lapTable = []
        # Iterate over all messages of type "lap"
        LapIx = 0
        for lap in fitfile.get_messages('lap'):
            #if LapIx <10: print('\n',lap)
            lapData = {
                'lapNo': None,
                'timeStart': None,
                'timeEnd': None,
                'recordIxStart': None,
                'recordIxEnd': None,
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
                'avgDragFactor': None,
                'wktStepIx': None
                }
            for lap_data_field in lap:
                if lap_data_field.name == 'avg_cadence': lapData['avgCad'] = lap_data_field.value
                elif lap_data_field.name == 'avg_heart_rate': lapData['avgHR'] = lap_data_field.value
                elif lap_data_field.name == 'avg_power': lapData['avgPower'] = lap_data_field.value
                elif lap_data_field.name == 'enhanced_avg_speed': lapData['avgSpeed'] = lap_data_field.value
                elif lap_data_field.name == 'enhanced_max_speed': lapData['maxSpeed'] = lap_data_field.value
                elif lap_data_field.name == 'intensity': lapData['wktStepType'] = lap_data_field.value
                elif lap_data_field.name == 'max_cadence': lapData['maxCad'] = lap_data_field.value
                elif lap_data_field.name == 'max_heart_rate': lapData['maxHR'] = lap_data_field.value
                elif lap_data_field.name == 'max_power': lapData['maxPower'] = lap_data_field.value
                elif lap_data_field.name == 'message_index': lapData['lapNo'] = lap_data_field.value + 1
                elif lap_data_field.name == 'start_time': 
                    lapData['timeStart'] = lap_data_field.value# + timedelta(hours=TZhours)
                    lapData['timeStart'] = pytz.utc.localize(lapData['timeStart']).astimezone(timeZone)
                elif lap_data_field.name == 'total_timer_time': lapData['lapTime'] = int(round(lap_data_field.value,0))
                elif lap_data_field.name == 'total_distance': lapData['lapDist'] = lap_data_field.value
                elif lap_data_field.name == 'wkt_step_index': lapData['wktStepIx'] = lap_data_field.value
                #if LapIx <10: print (LapIx, lap_data_field.name, lap_data_field.value)
            #print('---------------wktStep:',LapIx, lapData['wktStepType'])
            if lapData['wktStepType'] == 4: lapData['wktStepType'] = 'recover'
            if lapData['wktStepType'] == 5: lapData['wktStepType'] = 'active' # according to SDK, 5=interval
            LapIx += 1
            #print('start:', lapData['timeStart'])
            lapTable.append(lapData)

            printLine = ''
            printLine += str(lapData['lapNo'])
            printLine += ', '
            printLine += sec2minSec_shStr(lapData['lapTime'])
            printLine += 'min, '
            printLine += str(lapData['avgCad'])
            printLine += 'rpm, wktStepType: '
            printLine += str(lapData['wktStepType'])
            printLine += ', wktStepIx: '
            printLine += str(lapData['wktStepIx'])
            print(printLine)

        recordTable = []
        recordIx = 0

        print('\nWORKOUT STEPS\n-----------')
        for fit_record in fitfile.get_messages('workout_step'):
            #if recordIx <10: print('\n',fit_record)
            # Extract data fields
            recordData = {
                'targetHRhigh': None,
                'targetHRlow': None,
                'gotoStep': None,
                'durTime': None,
                'durType': None,
                'stepType': None,
                'stepIx': None,
                'notes': None,
                'repeatCount': None,
                'target_type': None
                }
            for fit_record_data in fit_record:
                if fit_record_data.name == 'custom_target_heart_rate_high': recordData['targetHRhigh'] = fit_record_data.value
                if fit_record_data.name == 'custom_target_heart_rate_low': recordData['targetHRlow'] = fit_record_data.value
                if fit_record_data.name == 'duration_step': recordData['gotoStep'] = fit_record_data.value
                if fit_record_data.name == 'duration_time': recordData['durTime'] = fit_record_data.value
                if fit_record_data.name == 'duration_type': recordData['durType'] = fit_record_data.value
                if fit_record_data.name == 'intensity': recordData['stepType'] = fit_record_data.value
                if fit_record_data.name == 'message_index': recordData['stepIx'] = fit_record_data.value
                if fit_record_data.name == 'notes': recordData['notes'] = fit_record_data.value
                if fit_record_data.name == 'repeat_steps': recordData['repeatCount'] = fit_record_data.value
                if fit_record_data.name == 'target_type': recordData['targetType'] = fit_record_data.value
                #if recordIx <10: print(fit_record_data)
                #if recordIx < 10: print(fit_record_data.name, fit_record_data.value)
            if recordData['stepType'] == 4: recordData['stepType'] = 'recover'
            if recordData['stepType'] == 5: recordData['stepType'] = 'active' # according to SDK, 5=interval
            recordTable.append(recordData)
            recordIx += 1
            
            printLine = ''
            printLine += str(recordData['stepIx'])
            if recordData['durType'] == 'repeat_until_steps_cmplt':
                printLine += 'x --> goto step '
                printLine += str(recordData['gotoStep'])
                printLine += ', '
                printLine += str(recordData['repeatCount'])
                printLine += 'x'
            else:
                if recordData['stepType'] != None:
                    printLine += ', '
                    printLine += str(recordData['stepType'])
                printLine += ', '
                printLine += str(recordData['durType'])
                if recordData['durTime'] != None:
                    printLine += ', '
                    printLine += str(int(recordData['durTime']))
                    printLine += 'sek'
                if recordData['targetType'] != None:
                    printLine += ', target: '
                    printLine += str(recordData['targetType'])
                if recordData['targetHRlow'] != None:
                    printLine += ', '
                    printLine += str(recordData['targetHRlow'])
                if recordData['targetHRhigh'] != None:
                    printLine += '->'
                    printLine += str(recordData['targetHRhigh'])

            print(printLine)
    
    return product, SWver, totDist, avgSpeed, noLaps, sport, startTime, subSport, totTime, actName, wktName, fileInfo

# ================================================================

def extract_lap_data_from_txt(manualLapsFileName):
    print('-extract_lap_data_from_txt')

    # List to store the rows
    lapFromTxtTbl = []

    # Open the text txtFile
    with open(manualLapsFileName, 'r') as txtFile:
        lapIx = 0
        for line in txtFile:
            lap_info_inTxt = {
                    'level': None,
                    'totDist': None,
                    'lapDist': None,
            }

            # Read each line and split into values based on delimiter
            lap_info_in_txt_line = (line.strip().split(' '))  # Adjust delimiter as needed
            lap_info_inTxt['level'] = lap_info_in_txt_line[0]
            lap_info_inTxt['totDist'] = 10 * int(lap_info_in_txt_line[1])

            if lapIx == 0:
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'])
            else:
                lap_info_inTxt['lapDist'] = (lap_info_inTxt['totDist'] - lapFromTxtTbl[lapIx-1]['totDist'])
            
            # print(lap_info_inTxt)
            lapFromTxtTbl.append(lap_info_inTxt)
            lapIx += 1
        lapCountTxt = len(lapFromTxtTbl)

    return (lapFromTxtTbl, lapCountTxt, lap_info_inTxt['totDist'])

# ================================================================

def extract_record_data_from_C2fit(fitFile_path_name):
    print('--extract_RECORD_data_from_C2fit', datetime.now())
    
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fitFile_path_name)
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
            if fit_record_data.name == 'timestamp': 
                recordData['timestamp'] = fit_record_data.value# + timedelta(hours=TZhours)
                recordData['timestamp'] = pytz.utc.localize(recordData['timestamp']).astimezone(timeZone)
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
        totDist = recordData['distance']
    
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
    
    return recordTable, timeFirstRecord, timeLastRecord, totDist

# ================================================================

def extract_record_data_from_fit(fitFile_path_name):
    print('--extract_RECORD_data_from_fit', datetime.now())
    
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fitFile_path_name)
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
            if fit_record_data.name == 'cadence': recordData['cadence'] = fit_record_data.value
            elif fit_record_data.name == 'Distance' and recordData['distance'] in [0, None]: recordData['distance'] = fit_record_data.value                                 # distance from C2 SkiErg CIQ distance
            elif fit_record_data.name == 'distance' and recordData['distance'] in [0, None]: recordData['distance'] = fit_record_data.value         # native distance
            elif fit_record_data.name == 'DragFactor': recordData['CIQdragfactor'] = fit_record_data.value
            elif fit_record_data.name == 'enhanced_speed' and  recordData['speed'] in [0, None]: recordData['speed'] = fit_record_data.value      # native Speed
            elif fit_record_data.name == 'heart_rate': recordData['HR'] = fit_record_data.value
            elif fit_record_data.name == 'Level' and recordData['CIQlevel'] in [0, None]: recordData['CIQlevel'] = fit_record_data.value
            elif fit_record_data.name == 'power': recordData['power'] = fit_record_data.value
            elif fit_record_data.name == 'Speed' and  recordData['speed'] in [0, None]: recordData['speed'] = fit_record_data.value                                       # speed from C2 SkiErg CIQ speed
            elif fit_record_data.name == 'StrokeLength': recordData['CIQstrokeLen'] = fit_record_data.value
            elif fit_record_data.name == 'timestamp': 
                recordData['timestamp'] = fit_record_data.value# + timedelta(hours=TZhours)
                recordData['timestamp'] = pytz.utc.localize(recordData['timestamp']).astimezone(timeZone)
            elif fit_record_data.name == 'Training_session': recordData['CIQtrainSess'] = fit_record_data.value
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
    while (recordTable[recordIx]['speed'] in [0, None]) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['speed']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['speed'] = firstValue
    
    # FIX CIQstrokeLen = 0 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['CIQstrokeLen'] in [0, None]) and recordIx < len(recordTable) - 1:
        recordIx += 1
    endZeroValueIx = recordIx
    firstValue = recordTable[endZeroValueIx]['CIQstrokeLen']
    for recordIx in range(endZeroValueIx, -1, -1):
        recordTable[recordIx]['CIQstrokeLen'] = firstValue
    
    # FIX CIQdragfactor = 1 in BEGINNING
    recordIx = 0
    while (recordTable[recordIx]['CIQdragfactor'] in [1, None]) and recordIx < len(recordTable) - 1:
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

def extract_lap_data_from_fit(fitFile_path_name, startWithWktStep):
    print('--extract_LAP_data_from_fit', datetime.now())
    # Parse the FIT txtFile
    fitfile = fitparse.FitFile(fitFile_path_name)
    
    # Initialize lists to store lap data
    lapTable = []
    # Iterate over all messages of type "lap"
    LapIx = 0
    for lap in fitfile.get_messages('lap'):
        #if LapIx <10: print('\n',lap)
        lapData = {
            'lapNo': None,
            'timeStart': None,
            'timeEnd': None,
            'recordIxStart': None,
            'recordIxEnd': None,
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
            if lap_data_field.name == 'avg_cadence': lapData['avgCad'] = lap_data_field.value
            elif lap_data_field.name == 'avg_heart_rate': lapData['avgHR'] = lap_data_field.value
            elif lap_data_field.name == 'avg_power': lapData['avgPower'] = lap_data_field.value
            elif lap_data_field.name == 'enhanced_avg_speed': lapData['avgSpeed'] = lap_data_field.value
            elif lap_data_field.name == 'enhanced_max_speed': lapData['maxSpeed'] = lap_data_field.value
            elif lap_data_field.name == 'intensity': lapData['wktStepType'] = lap_data_field.value
            elif lap_data_field.name == 'max_cadence': lapData['maxCad'] = lap_data_field.value
            elif lap_data_field.name == 'max_heart_rate': lapData['maxHR'] = lap_data_field.value
            elif lap_data_field.name == 'max_power': lapData['maxPower'] = lap_data_field.value
            elif lap_data_field.name == 'message_index': lapData['lapNo'] = lap_data_field.value + 1
            elif lap_data_field.name == 'start_time': 
                lapData['timeStart'] = lap_data_field.value# + timedelta(hours=TZhours)
                lapData['timeStart'] = pytz.utc.localize(lapData['timeStart']).astimezone(timeZone)
            elif lap_data_field.name == 'total_timer_time': lapData['lapTime'] = int(round(lap_data_field.value,0))
            elif lap_data_field.name == 'total_distance': lapData['lapDist'] = lap_data_field.value
            #if LapIx <10: print (LapIx, lap_data_field.name, lap_data_field.value)
        #print('---------------wktStep:',LapIx, lapData['wktStepType'])
        if lapData['wktStepType'] == 4: lapData['wktStepType'] = 'recover'
        if lapData['wktStepType'] == 5: lapData['wktStepType'] = 'active' # according to SDK, 5=interval
        if lapData['wktStepType'] == None: lapData['wktStepType'] = 'active'
        LapIx += 1
        #print('start:', lapData['timeStart'])
        lapTable.append(lapData)

    # FIX for non workout lap data, every other lap rest
    if lapTable[0]['wktStepType'] == 'active' and LapIx > 1 and not startWithWktStep == 'allActive':
        if lapTable[1]['wktStepType'] == 'active':
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

    #lapCountFit = len(lapTable)

    return lapTable

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
    
    # FIX empty/None cadence and power records. Fill with last. Merge creates this due to not all seconds from Conccept2
    for recordIx in range(len(recordTable)):
        if recordTable[recordIx]['cadence'] == None:
            recordTable[recordIx]['cadence'] = recordTable[recordIx-1]['cadence']
        if recordTable[recordIx]['power'] == None:
            recordTable[recordIx]['power'] = recordTable[recordIx-1]['power']

    return recordTable

# ================================================================

def merge_lapData_from_txt(lapTable, lapFromTxtTbl):
    print('----merge_lapData_from_txt', datetime.now())
    lapIx = 0

    for lapData in lapTable:
        
        lapData['totDist'] = lapFromTxtTbl[lapIx]['totDist']
        lapData['lapDist'] = lapFromTxtTbl[lapIx]['lapDist']
        lapData['level'] = lapFromTxtTbl[lapIx]['level'] 
        # Speed calc need to done here for thredmill where speed already is in place
        lapData['avgSpeed'] = lapData['lapDist'] / lapData['lapTime'] # calc speed based on lapdist/laptime
        lapIx += 1

    for recordData in recordTable:
        recordData['CIQlevel'] = lapData[recordData['lapNo']]['level']

    return lapTable

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
    for lapData in lapTable:
        #print(lapData['lapTime'], (lapData['timeEnd']-lapData['timeStart']).total_seconds()+1)
        if lapData['lapTime'] in [0, None]:
            lapData['lapTime'] = (lapData['timeEnd']-lapData['timeStart']).total_seconds()+1

    return lapTable

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
    CIQlevelLapSum = 0

    for recordData in recordTable:
        if recordData['speed'] == None: recordData['speed'] = 0
        if recordData['cadence'] == None: recordData['cadence'] = 0
        if recordData['power'] == None: recordData['power'] = 0
        if recordData['CIQstrokeLen'] == None: recordData['CIQstrokeLen'] = 0
        if recordData['CIQdragfactor'] == None: recordData['CIQdragfactor'] = 0
        if recordData['CIQlevel'] == None: recordData['CIQlevel'] = 0
        speedLapSum += recordData['speed']
        cadLapSum += recordData['cadence']
        powerLapSum += recordData['power']
        CIQstrokeLengthLapSum += recordData['CIQstrokeLen']
        CIQdragfactorLapSum += recordData['CIQdragfactor']
        CIQlevelLapSum += recordData['CIQlevel']
        recordData['lapNo'] = lapNo

        # IF LAP START
        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeStart']:
            lapTable[lapIx]['HRstart'] = recordTable[recordIx]['HR']
            lapTable[lapIx]['recordIxStart'] = recordIx
        
        # IF LAP END
        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeEnd']:
            lapTable[lapIx]['HRend'] = recordTable[recordIx]['HR']
            lapTable[lapIx]['recordIxEnd'] = recordIx
            if lapTable[lapIx]['lapDist'] in [0, None]:
                if lapIx == 0:
                    lapTable[lapIx]['lapDist'] = recordData['distance']
                else:
                    lapTable[lapIx]['lapDist'] = recordData['distance'] - lapTable[lapIx - 1]['totDist']
            if lapTable[lapIx]['totDist'] in [0, None]:
                lapTable[lapIx]['totDist'] = recordData['distance']
            if lapTable[lapIx]['avgSpeed'] in [0, None]:
                lapTable[lapIx]['avgSpeed'] = lapTable[lapIx]['lapDist'] / lapTable[lapIx]['lapTime'] # calc speed based on lapdist/laptime
            if lapTable[lapIx]['avgSpeed2'] in [0, None]:
                lapTable[lapIx]['avgSpeed2'] = speedLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1) # calc speed based on speed values
            if lapTable[lapIx]['avgCad'] in [0, None]:
                lapTable[lapIx]['avgCad'] = cadLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1)
            if lapTable[lapIx]['avgPower'] in [0, None]:
                lapTable[lapIx]['avgPower'] = powerLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1)
            lapTable[lapIx]['avgStrokeLen'] = CIQstrokeLengthLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1)
            lapTable[lapIx]['avgDragFactor'] = CIQdragfactorLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1)
            print( CIQlevelLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1))
            lapTable[lapIx]['level'] = CIQlevelLapSum / (lapTable[lapIx]['recordIxEnd'] - lapTable[lapIx]['recordIxStart']+1)
            lapTable[lapIx]['stepLen'] = (lapTable[lapIx]['lapDist']) / (lapTable[lapIx]['avgCad'] * lapTable[lapIx]['lapTime'] / 60)  # step length acc to FFRT
            #print ('lap:'+str(lapNo)+' dist:'+str(lapTable[lapIx]['lapDist'])+' time:'+str(lapTable[lapIx]['lapTime'])+' cad:'+str(lapTable[lapIx]['avgCad'])+' stepL:'+str(lapTable[lapIx]['stepLen'])+' m/sek:'+str(lapTable[lapIx]['stepLen']*lapTable[lapIx]['avgCad']/60))
            speedLapSum = 0
            cadLapSum = 0
            powerLapSum = 0
            CIQstrokeLengthLapSum = 0
            CIQdragfactorLapSum = 0
            CIQlevelLapSum = 0
            lapIx += 1
            lapNo = lapIx+1
        
        recordIx += 1
    
    totDist = lapTable[lapIx-1]['totDist']
        
    #print ("lapNo, lapData['lapDist'], lapData['totDist'], lapData['avgStrokeLen'], lapData['lapTime'], '=', lapData['avgCad'], lapData['HRstart'], lapData['HRend'], lapData['avgSpeed'], lapData['avgDragFactor'], lapData['stepLen']")
    #print(lapIx)
    #for lapData in lapTable:
        #print (lapNo, lapData['lapDist'], lapData['totDist'], lapData['avgStrokeLen'], lapData['lapTime'], '=', lapData['avgCad'], lapData['HRstart'], lapData['HRend'], lapData['avgSpeed'], lapData['avgDragFactor'], lapData['stepLen'])
    #print ('last rec: ', recordTable[recordIx - 1]['timestamp'])

    return lapTable, recordTable, totDist

# ================================================================

def calc_dist_speed_basedOn_cadence(recordTable, lapTable):
    print('---calc_dist_speed_basedOn_cadence', datetime.now())

    recordIx = 0
    lapIx = 0
    lapNo = lapIx+1
    lapSumOfRecordDist = 0
    sumOfRecordDist = 0

    for recordData in recordTable:
        
        recordDist = lapTable[lapIx]['stepLen']*recordData['cadence']/60
        lapSumOfRecordDist += recordDist
        sumOfRecordDist += recordDist

        if recordTable[recordIx]['timestamp'] == lapTable[lapIx]['timeEnd']:
            #print (lapNo, lapTable[lapIx]['totDist'], sumOfRecordDist, lapTable[lapIx]['lapDist'], lapSumOfRecordDist)
            corrPerMeter = (lapSumOfRecordDist - lapTable[lapIx]['lapDist']) / lapSumOfRecordDist
            #print (corrPerMeter)
            
            sumOfRecordDist = sumOfRecordDist - lapSumOfRecordDist
            lapSumOfRecordDist = 0
            for lapRecordIx in range(lapTable[lapIx]['recordIxStart'], lapTable[lapIx]['recordIxEnd']+1):
                recordDist = lapTable[lapIx]['stepLen']*recordTable[lapRecordIx]['cadence']/60
                recordDist = recordDist - recordDist * corrPerMeter
                lapSumOfRecordDist += recordDist
                sumOfRecordDist += recordDist
                recordTable[lapRecordIx]['distance'] = sumOfRecordDist
                recordTable[lapRecordIx]['speed'] = (recordTable[lapRecordIx]['distance'] - recordTable[lapRecordIx-1]['distance']) / 1 # 1 sec

            #print (lapNo, lapTable[lapIx]['totDist'], sumOfRecordDist, lapTable[lapIx]['lapDist'], lapSumOfRecordDist, lapTable[lapIx]['lapDist'], '\n')
            lapSumOfRecordDist = 0
            lapIx += 1
            lapNo = lapIx+1

        recordIx += 1

    return recordTable, lapTable

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
        if lapData['wktStepType'] in ['rest', 'recover']:
            restTime += lapData['lapTime']
            sumSpeedRest += lapData['avgSpeed'] * lapData['lapTime']
            sumCadRest += lapData['avgCad'] * lapData['lapTime']
            sumPowerRest += lapData['avgPower'] * lapData['lapTime']
    if activeTime != 0:
        avgSpeedActive = sumSpeedActive / activeTime
        avgCadActive = sumCadActive / activeTime
        avgPowerActive = sumPowerActive / activeTime
    else:
        avgSpeedActive = 0
        avgCadActive = 0
        avgPowerActive = 0

    if restTime != 0:
        avgSpeedRest = sumSpeedRest / restTime
        avgCadRest  = sumCadRest / restTime
        avgPowerRest  = sumPowerRest / restTime
    else:
        avgSpeedRest = 0
        avgCadRest  = 0
        avgPowerRest  = 0

    return avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest


# ================================================================

def saveToCSV(outNewRecordCSV_file_path, saveCadence, savePower, saveLevel, savelapTime):

    # CSV file with to be used to merge data in FFRT (developer tab, open in xl, paste data from csv, reimport xl)
    outNewDistTxt_file = open(outNewRecordCSV_file_path, 'w')
    header = ''
    header += 'distance'
    if saveCadence:
        header += ';cadence'
    if savePower: 
        header += ';power'
    header += ';speed'
    if saveLevel:
        header += ';level'
    if savelapTime:
        header += ';lapTime'
    header += ';pace'
    header += '\n'
    outNewDistTxt_file.write(header)

    for record in recordTable:
        csvLine = ''
        csvLine += str(record['distance']/1000).replace('.',',')
        if saveCadence:
            csvLine += ';'
            csvLine += str(record['cadence']).replace('.',',')
        if savePower:
            csvLine += ';'
            csvLine += str(record['power']).replace('.',',')
        csvLine += ';'
        csvLine += mps2kmph_alldecStr(record['speed']).replace('.',',')
        if saveLevel:
            csvLine += ';'
            csvLine += str(lapTable[record['lapNo']-1]['level'])
        if savelapTime:
            csvLine += ';'
            if lapTable[record['lapNo']-1]['wktStepType'] == 'active': 
                csvLine += str(round(lapTable[record['lapNo']-1]['lapTime']/60,1)).replace('.',',')
            else:
                csvLine += '0'
        csvLine += ';'
        csvLine += mps2minpkm_Str(record['speed']) #.replace(':','.')
        csvLine += '\n'
        outNewDistTxt_file.write(csvLine)
    
    return

# ================================================================

def saveShowLapDistances(outLapTxt_file, lapTable, totDist):
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
            lapTxtLine += str(round(lapData['stepLen'] / 10, 2))
            print (lapTxtLine)
            outLapTxt_file.write (lapTxtLine + '\n')
    print('Totaldist: ' + m2km_2decStr(totDist) + ' km')
    outLapTxt_file.write ('Totaldist: ' + m2km_2decStr(totDist) + ' km' + '\n')
    return
# ================================================================

def saveSpinBikeLapTable_to_txt():
    print('----saveSpinBikeLapTable_to_txt', datetime.now())
    
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    outLapTxt_file.write (fileInfo)
    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fitFile_path_name)
    outLapTxt_file.write ('Src: ' + fitFile_path_name +'\n')

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
        if lapData['wktStepType'] in ['rest', 'recover']:
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
    
    saveToCSV(outNewRecordCSV_file_path, False, False, True, True) #...saveCadence, savePover, saveLevel, saveLapTime

    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    outLapTxt_file.write (fileInfo)

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fitFile_path_name)
    outLapTxt_file.write ('Src: ' + fitFile_path_name +'\n')
    print('Src: ' + manualLapsFileName)
    outLapTxt_file.write ('Src: ' + manualLapsFileName + '\n')

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
        if lapData['wktStepType'] in ['rest', 'recover']:
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

    saveShowLapDistances(outLapTxt_file, lapTable, totDist)

    return

# ================================================================

def saveCTLapTable_to_txt():
    print('----saveCTLapTable_to_txt', datetime.now())

    saveToCSV(outNewRecordCSV_file_path, False, False, True, True) #...savCadence, savePover, saveLevel, saveLapTime

    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    outLapTxt_file.write (fileInfo)

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fitFile_path_name)
    outLapTxt_file.write ('Src: ' + fitFile_path_name +'\n')
    print('Src: ' + manualLapsFileName)
    outLapTxt_file.write ('Src: ' + manualLapsFileName + '\n')

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
        if lapData['wktStepType'] in ['rest', 'recover']:
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

    saveShowLapDistances(outLapTxt_file, lapTable, totDist)

    return

# ================================================================

def saveSkiErgLapTable_to_txt():
    print('----saveSkiErgLapTable_to_txt', datetime.now())
    
    saveToCSV(outNewRecordCSV_file_path, True, True, False, True) #...saveCadence, savePover, saveLevel, saveLapTime
        
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    outLapTxt_file.write (fileInfo)

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outNewRecordCSV_file_path +'\n')
    print('Dest: ' + outNewRecordCSV_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fitFile_path_name)
    outLapTxt_file.write ('Src: ' + fitFile_path_name +'\n')
    print('Src: ' + C2fitFile_path_name)
    outLapTxt_file.write ('Src: ' + C2fitFile_path_name + '\n')

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
            lapTxtLine += str(int(round(lapData['avgStrokeLen']*100,1))) + 'cm '
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
        if lapData['wktStepType'] in ['rest', 'recover']:
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
    if lapCountFit > 1:
        print('-----------')
        print('Speed compare with diff lap start points')
        print('-----------')
        lapNo = 0
        for lapData in lapTable:
            lapNo += 1
            if lapData['wktStepType'] == 'active' and lapNo < lapCountFit:
                speedLine = ''
                speedLine += mps2minp500m_Str( (recordTable[lapData['recordIxEnd']-4]['distance']-recordTable[lapData['recordIxStart']-4]['distance'])/lapData['lapTime']) + '-4 '
                speedLine += mps2minp500m_Str( (recordTable[lapData['recordIxEnd']-3]['distance']-recordTable[lapData['recordIxStart']-3]['distance'])/lapData['lapTime']) + '-3 '
                speedLine += mps2minp500m_Str( (recordTable[lapData['recordIxEnd']-2]['distance']-recordTable[lapData['recordIxStart']-2]['distance'])/lapData['lapTime']) + '-2 '
                speedLine += mps2minp500m_Str( (recordTable[lapData['recordIxEnd']-1]['distance']-recordTable[lapData['recordIxStart']-1]['distance'])/lapData['lapTime']) + '-1 '
                speedLine += mps2minp500m_Str( lapData['lapDist']/lapData['lapTime']) + '-0 '
                speedLine += mps2minp500m_Str( (recordTable[lapData['recordIxEnd']+1]['distance']-recordTable[lapData['recordIxStart']+1]['distance'])/lapData['lapTime']) + '+1 '
                speedLine += mps2minp500m_Str( (recordTable[lapData['recordIxEnd']+2]['distance']-recordTable[lapData['recordIxStart']+2]['distance'])/lapData['lapTime']) + '+2 '
                print(speedLine)
   
    return

# ================================================================

def saveRunLapTable_to_txt():
    print('----saveSpinBikeLapTable_to_txt', datetime.now())
    
    # TEXT file with lap info to be used for analyzing
    outLapTxt_file = open(outLapTxt_file_path, 'w')
    outLapTxt_file.write (fileInfo)

    # Destination and Source data
    print('-----------')
    print(str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime))
    outLapTxt_file.write (str(timeFirstRecord) + ', ' + activityType + ', ' + m2km_1decStr(totDist) + 'km, ' + sec2minSec_shStr(totTime) +'\n')
    print('Dest: ' + outLapTxt_file_path)
    outLapTxt_file.write ('Dest: ' + outLapTxt_file_path +'\n')
    print('Src: ' + fitFile_path_name)
    outLapTxt_file.write ('Src: ' + fitFile_path_name +'\n')

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
        if lapData['wktStepType'] in ['rest', 'recover']:
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
# Create BASE FILE NAME
# ================================================================
def createBaseFileName(timeFirstRecord, actName, totDist, totTime, wktName, product, SWver):
    out_baseFileName = ''
    out_baseFileName += str(timeFirstRecord.replace(tzinfo=None)).replace(':','-').replace(' ','-')
    out_baseFileName += '-' + actName
    if not totDist in [0, '', None]: out_baseFileName += '-' + m2km_1decStr(totDist) + 'km'
    out_baseFileName += '-' + sec2minSec_shStr(totTime).replace(':','.') + 'min'
    if not wktName == '': out_baseFileName += '-' + wktName
    if not product == '': out_baseFileName += '-' + product
    if not SWver == '': out_baseFileName += '-v' + str(SWver)
    return (out_baseFileName)

# ================================================================
# RENAME FIT
# ================================================================
def renameFitFile(fitFile_path_name, newFitFileName):
    if fitFile_path_name.lower() != newFitFileName.lower():
        if os.path.exists(newFitFileName):
            os.remove(newFitFileName)
        os.rename(fitFile_path_name, newFitFileName)
    return

# ================================================================
# REMOVE ZIP
# ================================================================
def removeZipFile(ext, zipFile_path_name):
    if ext == '.zip':
        os.remove(zipFile_path_name)
    return

# ================================================================
# OUT FILE PATHS
# ================================================================
def outFilePaths(pathPrefixFit, out_baseFileName):
    # TEXT FILE
    outLapTxt_file_path = pathPrefixFit + out_baseFileName + '-LapTables.txt'
    # CSV FILE
    outNewRecordCSV_file_path = pathPrefixFit + out_baseFileName + '-newDistCadPower.csv'
    # NEW FIT FILE NAME
    newFitFileName = pathPrefixFit + out_baseFileName
    if out_baseFileName.find('FFRTexpSecShift') >= 0:
        newFitFileName += '-FFRTexpSecShift.fit'
    if out_baseFileName.find('sec.fit') >= 0:
        newFitFileName += '-FFRTexpSecShift.fit'
    elif out_baseFileName.find('FFRTexp') >= 0:
        newFitFileName += '-FFRTexp.fit'
    elif out_baseFileName.find('fixed') >= 0:
        newFitFileName += '-FFRTexp.fit'
    elif out_baseFileName.find('analyzed') >= 0:
        newFitFileName += '-analyzed.fit'
    elif doRename:
        newFitFileName += '-renamed.fit' 
    else:
        newFitFileName += '-analyzed.fit'
    
    return(outLapTxt_file_path, outNewRecordCSV_file_path, newFitFileName)
    
# ================================================================
# ================================================================
# ================================================================
# START of program
# ================================================================

argsCount = len(sys.argv)
print('No of args:' + str(argsCount) + str(sys.argv))

#device = 'pc'
device = 'pc1drv'
#device = 'm'

# Hours to add to FIT file TIME
#TZhours = 2
timeZone = pytz.timezone('Europe/Stockholm')


# Text that can be collected in program to be saved first in TEXT LAP FILE
fileInfo = ''

# If no workout steps in file, then start with this, can be 'WarmupThenActive' OR 'WarmupAndRest' OR 'allActive'
startWithWktStep = 'allActive'    

# Assign ROOT FOLDERS based on DEVICE
if device == 'm':
    pathPrefixFit = '/storage/emulated/0/download/'
    manualLapsPathPrefix = '/storage/emulated/0/download/'
elif device == 'pc':
    pathPrefixFit = 'C:/users/peter/downloads/'
    manualLapsPathPrefix = 'C:/users/peter/downloads/'
else:
    pathPrefixFit = 'C:/Users/peter/OneDrive/Dokument Peter OneDrive/Träning/ActivityFiles/Peter activities/'
    manualLapsPathPrefix = 'C:/Users/peter/OneDrive/Dokument Peter OneDrive/Träning/ActivityFiles/Peter activities/'

if argsCount <= 1:
    # Check if no Args mode, assign type and files here in program
    ArgsMode = False
    test = False
    doRename = False
else:
    ArgsMode = True

    # Check if TEST
    if sys.argv[1] == 'test':
        test = True
    else:
        test = False

    # Check if RENAME
    if sys.argv[1] == 'rename':
        doRename = True
    else:
        doRename = False

# Decide and Assign activityType
if test:
    activityType = sys.argv[2]
    print ('Going into TEST phase. Test=:' + str(test) + ' Activitytype:' + activityType)
else:
    if ArgsMode:
        activityType = sys.argv[1]
    else:
        # NO Args mode, use fixed config below for activityType
        #activityType = 'spinbike'
        #activityType = 'gymbike'
        activityType = 'ct'
        #activityType = 'skierg'
        #activityType = 'run'

# Assign FIT File and other TEST files
#if doRename:
#    folder = pathPrefixFit
#    filter = sys.argv[2]
#else:
if test:
    pathPrefixFit += 'TESTfiles/'
    if activityType == 'gymbike':
        fitFile_path_name = pathPrefixFit + '2024-09-14-09-46-48-GymBike-31.2km-60.43min-Bike_5-4-3-2-1-1-2-3-4-5-epix2pro-v18.14-analyzed.fit'
        manualLapsFileName = pathPrefixFit + '2024-09-14-09-46-48-GymBike-60.43min-Bike_5-4-3-2-1-1-2-3-4-5-epix2pro-v18.14-LevelTotDist.txt'
        file_exist = os.path.isfile(manualLapsFileName)
        if not file_exist:
            print('---------------- TEST Lap txtFile does not exist! ', manualLapsFileName)
            exit()
    elif activityType == 'ct':
        fitFile_path_name = pathPrefixFit + '2024-10-06-11-31-25-Elliptical-4.0km-20.11min-epix2pro-v18.16-analyzed.fit'
        manualLapsFileName = pathPrefixFit + '2024-10-06-11-31-25-Elliptical-20.11min-epix2pro-v18.16-LevelTotDist.txt'
        file_exist = os.path.isfile(manualLapsFileName)
        if not file_exist:
            print('---------------- TEST Lap txtFile does not exist! ', manualLapsFileName)
            exit()
    elif activityType == 'skierg':
        fitFile_path_name = pathPrefixFit + '2024-09-30-16-48-09-SkiErg-11.0km-61.04min-Bike_4x3-2-1min-epix2pro-v18.15-analyzed.fit'
        C2fitFile_path_name = pathPrefixFit + '2024-09-30-16-46-00-SkiErg-11.0km-61min-concept2-v1.0-analyzed.fit'
        hasC2fitFile = True
        file_exist = os.path.isfile(C2fitFile_path_name)
        if not file_exist:
            print('---------------- TEST C2 FIT File does not exist!')
            exit()
    elif activityType == 'spinbike':
        fitFile_path_name = pathPrefixFit + '2024-09-26-16-27-04-SpinBike-18.4km-40.06min-epix2pro-v18.15-analyzed.fit'
    elif activityType == 'run':
        fitFile_path_name = pathPrefixFit + '2024-08-02-17-27-43-Trail_Run_Interval-5.4km-61.23min-epix2pro-v18.1-analyzed.fit'
    # Check if FIT file EXIST
    #file_exist = os.path.isfile(fitFile_path_name)
    #if not file_exist:
    #    print('---------------- TEST Fit File does not exist!')
    #    exit()
else: # NOT TEST, assign a FILE  
    if ArgsMode:
        fileNameTemp = Path(sys.argv[2]).name
        dirTemp = Path(sys.argv[2]).parent
        print('dir:',dirTemp,'file:',fileNameTemp)
        # Check if PATH is included in argument, for instance if opend from file explorer
        # ----------------------------------------------------------------------"
        print(pathPrefixFit)
        if dirTemp.is_absolute():
            # FULL PATH - argument
            # --------------
            pathPrefixFit = str(dirTemp).replace('\\','/') + '/'
            fitFile_path_name = pathPrefixFit + fileNameTemp
            print('dirTemp exists!')
        else:
            # FILE only - argument
            # --------------
            fitFile_path_name = pathPrefixFit + sys.argv[2]
    else:
        # NO Args mode, use fixed file name below
        fitFile_path_name = pathPrefixFit + '2024-10-06-11-31-25-Elliptical-4.0km-20.11min-epix2pro-v18.16-analyzed.fit'

# UNZIP if ZIP file and reassign FIT file
fileName = Path(fitFile_path_name).stem
ext = Path(fitFile_path_name).suffix

print('fitfile:'+fitFile_path_name)
print('Path:'+pathPrefixFit+'\nFilename:'+fileName+'\nExt:'+ext)

if not doRename:
    zipFile_path_name = fitFile_path_name
    if ext =='.zip':
        file_exist = os.path.isfile(zipFile_path_name)
        if not file_exist:
            print('---------------- ZIP File does not exist!')
            exit()
        zip = ZipFile(zipFile_path_name)
        zip.extractall(pathPrefixFit)
        zip.close()
        fitFile_path_name = pathPrefixFit + fileName + '_ACTIVITY.fit'

    # Check if FIT file EXIST
    file_exist = os.path.isfile(fitFile_path_name)
    if not file_exist:
        print('---------------- Fit File does not exist! : ' + fitFile_path_name)
        exit()
    #print('---------------- Fit File DOES exist! : ' + fitFile_path_name)
    #exit()
    # Extract SESSION data and show from org FIT file
    # AUTO and INFO kommand
    # ================================================================
    product, SWver, totDist, avgSpeed, lapCountFit, sport, startTime, subSport, totTime, actName, wktName, fileInfo = extract_session_data_from_fit(fitFile_path_name, fileInfo)

    # ================================================================
    # ================================================================
    # INFO
    # ================================================================
    if activityType == 'info':
        exit()

# ================================================================
# ================================================================
# AUTO
# ================================================================
activityType = activityType.lower()
if activityType == 'auto':
    if actName.lower().find('skierg') >= 0: activityType = 'skierg'
    if actName.lower().find('cykel inne') >= 0: activityType = 'gymbike'
    if actName.lower().find('gymbike') >= 0: activityType = 'gymbike'
    if actName.lower().find('ellipt') >= 0 : activityType = 'ct'
    if actName.lower().find('ct') >= 0: activityType = 'ct'
    if actName.lower().find('löpband') >= 0 : activityType = 'ct'
    if actName.lower().find('spin') >= 0: activityType = 'spinbike'
    if actName.lower().find('run') >= 0: activityType = 'run'

# CHECK if activity type is CORRECT
if activityType in ['spinbike','gymbike','ct','skierg','run','rename']:
    print('Using activityType: ' + activityType)
else:
    print('---------------Wrong activityType! ', activityType, actName)
    exit()

# ================================================================
# ================================================================
# RENAME
# ================================================================
if activityType == 'rename':

    folder = pathPrefixFit
    filter = fileName

    print('Rename in folder:', folder, 'With filter:',filter,'\n')

    files = os.listdir(folder)

    for file in files:
        if file.find(filter) >= 0 and (file.find('.fit') >= 0 or file.find('.zip') >= 0): 
            print(file)
            fitFile_path_name = folder + file

            # UNZIP if ZIP file and reassign FIT file
            fileName = Path(fitFile_path_name).stem
            ext = Path(fitFile_path_name).suffix

            zipFile_path_name = fitFile_path_name
            if ext =='.zip':
                file_exist = os.path.isfile(zipFile_path_name)
                if not file_exist:
                    print('---------------- ZIP File does not exist!')
                    exit()
                zip = ZipFile(zipFile_path_name)
                zip.extractall(pathPrefixFit)
                zip.close()
                fitFile_path_name = pathPrefixFit + fileName + '_ACTIVITY.fit'

            # Check if FIT file EXIST
            file_exist = os.path.isfile(fitFile_path_name)
            if not file_exist:
                print('---------------- Fit File does not exist!')
                exit()
            
            # Extract SESSION data and show from org FIT file
            # ================================================================
            product, SWver, totDist, avgSpeed, lapCountFit, sport, startTime, subSport, totTime, actName, wktName, fileInfo = extract_session_data_from_fit(fitFile_path_name, fileInfo)

            out_baseFileName = createBaseFileName(startTime, actName, totDist, totTime, wktName, product, SWver)
            outLapTxt_file_path, outNewRecordCSV_file_path, newFitFileName = outFilePaths(pathPrefixFit, out_baseFileName)
            print ('src:', fitFile_path_name)
            print ('dst:', newFitFileName)

            renameFitFile(fitFile_path_name, newFitFileName)
            removeZipFile(ext, zipFile_path_name)

    print('=============== RENAMING END ================')
    exit()


# ================================================================
# ================================================================
# SkiErg
# ================================================================
if activityType == 'skierg':
    needNew_C2FileName = True

    # Assign C2 FIT file if not test
    # ================================================================
    if not test:
        if ArgsMode:
            if argsCount >= 4:
                # has an args after, assume that is the C2 fit file
                hasC2fitFile = True
                if sys.argv[3] in ['x','X']:
                    # X - Argument, NOT used in SkiErg
                    # --------------
                    needNew_C2FileName = False
                    print('X as second argument is not allowed with SkiErg\n----------------------------------------')
                    exit()
                else:
                    #C2fitFile_path_name = pathPrefixFit + sys.argv[3]
                    # FILE - argument
                    # --------------
                    fileNameTemp = Path(sys.argv[3]).name
                    dirTemp = Path(sys.argv[3]).parent
                    print('=====> SecondArg =====> dir:',dirTemp,'file:',fileNameTemp)
                    # Check if PATH is included in argument, for instance if opened from file explorer
                    # ----------------------------------------------------------------------"
                    if dirTemp.is_absolute():
                        # FULL PATH - argument
                        # --------------
                        pathPrefixFit = str(dirTemp).replace('\\','/') + '/'
                        C2fitFile_path_name = pathPrefixFit + fileNameTemp
                    else:
                        # FILE only - argument
                        # --------------
                        C2fitFile_path_name = pathPrefixFit + sys.argv[3]
            else:
                # NO C2 FILE args
                # Try easy name LOCAL FILE
                C2fitFile_path_name = pathPrefixFit + 'C2.fit'
                file_exist = os.path.isfile(C2fitFile_path_name)
                if not file_exist:
                    # NO C2 FILE args, Probably already analyzed
                    hasC2fitFile = False
                else:
                    # NO C2 FILE args, Use the C2.fit file
                    hasC2fitFile = True
        else:
            # NO Args MODE, assign fixed file below
            C2fitFile_path_name = pathPrefixFit + '2024-09-30-16-46-00-SkiErg-11.0km-61min-concept2-v1.0-analyzed.fit'
            hasC2fitFile = True
        file_exist = os.path.isfile(C2fitFile_path_name)
        if not file_exist:
            print('---------------- C2 FIT File does not exist!')
            hasC2fitFile = False
            C2fitFile_path_name = 'No C2 FIT file used.'

    if hasC2fitFile:
        # Extract SESSION data and show from C2 FIT file
        # ================================================================
        C2product, C2SWver, C2totDist, C2avgSpeed, C2lapCountFit, C2sport, C2startTime, C2subSport, C2totTime, C2actName, C2wktName, fileInfo = extract_session_data_from_fit(C2fitFile_path_name, fileInfo)

        # Extract RECORD data from C2 FIT file
        # ================================================================
        C2recordTable, C2timeFirstRecord, C2timeLastRecord, C2totDist = extract_record_data_from_C2fit(C2fitFile_path_name)
    
    # Extract RECORD data from FIT file
    # ================================================================
    recordTable, timeFirstRecord, timeLastRecord = extract_record_data_from_fit(fitFile_path_name)

    # Extract LAP data from FIT file
    # ================================================================
    lapTable = extract_lap_data_from_fit(fitFile_path_name, startWithWktStep)

    if hasC2fitFile:
        # Check that the no of laps are equal in TXT and FIT
        # ================================================================
        print('date from C2 and watch file: ', C2timeFirstRecord, timeFirstRecord)
        if C2timeFirstRecord.date() != timeFirstRecord.date(): 
            # EXIT if files do not match date
            print('====================== NOT same DATE on FIT and C2FIT')
            exit()

        # Merge C2 RECORDS with recordTable
        # ================================================================
        recordTable = merge_C2records_with_recordTable(recordTable, C2recordTable)

    # Calc LAP TIME END in lapTable
    # ================================================================
    lapTable = calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord)

    # Calc LAP DATA fron recordTable
    # ================================================================
    lapTable, recordTable, totDistLastRecord = calc_lapData_from_recordTable(recordTable, lapTable)
    if totDist in [0, None]: totDist = totDistLastRecord

    # Calc AVG DATA in lapTable
    # ================================================================
    avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest = calc_avg_in_lapTable(lapTable)

    # Create OUT BASE FILE NAME
    # =========================
    out_baseFileName = createBaseFileName(timeFirstRecord, actName, totDist, totTime, wktName, product, SWver)
    outLapTxt_file_path, outNewRecordCSV_file_path, newFitFileName = outFilePaths(pathPrefixFit, out_baseFileName)

    if hasC2fitFile:
        C2out_baseFileName = createBaseFileName(C2timeFirstRecord, actName, C2totDist, C2totTime, C2wktName, C2product, C2SWver)
        C2outLapTxt_file_path, C2outNewRecordCSV_file_path, C2newFitFileName = outFilePaths(pathPrefixFit, C2out_baseFileName)
    
    # TEST Header
    if test:
        print('================ TEST =================')

    # SAVE TO TXT FILE
    # =========================
    saveSkiErgLapTable_to_txt()

    if hasC2fitFile:
        renameFitFile(C2fitFile_path_name, C2newFitFileName)


# ================================================================
# ================================================================
# GYMBIKE & CT
# ================================================================
if activityType in ['gymbike', 'ct']:
    needNew_manualLapsFileName = False
    hasManualLapsFile = True

    # Assign manualLaps file if not test
    # ================================================================
    if not test:
        if ArgsMode:
            if argsCount >= 4:
                # has an args after, assume that is the C2 fit file
                hasManualLapsFile = True
                if sys.argv[3] in ['x','X']:
                    # X - Argument, use 
                    # --------------
                    manualLapsFileName = createBaseFileName(startTime, actName, '', totTime, wktName, product, SWver)
                    manualLapsFileName = pathPrefixFit + manualLapsFileName + '-LevelTotDist.txt'
                else:
                    # FILE - argument
                    # --------------
                    fileNameTemp = Path(sys.argv[3]).name
                    dirTemp = Path(sys.argv[3]).parent
                    print('=====> SecondArg =====> dir:',dirTemp,'file:',fileNameTemp)
                    # Check if PATH is included in argument, for instance if opened from file explorer
                    # ----------------------------------------------------------------------"
                    if dirTemp.is_absolute():
                        # FULL PATH - argument
                        # --------------
                        pathPrefixFit = str(dirTemp).replace('\\','/') + '/'
                        manualLapsFileName = pathPrefixFit + fileNameTemp
                    else:
                        # FILE only - argument
                        # --------------
                        manualLapsFileName = pathPrefixFit + sys.argv[3]
            else:
                # NO manualLaps.txt FILE args
                # Try easy name LOCAL FILE
                manualLapsFileName = pathPrefixFit + 'laps.txt'
                file_exist = os.path.isfile(manualLapsFileName)
                if not file_exist:
                    # NO ManualLaps FILE args, Probably already analyzed
                    hasManualLapsFile = False
                    needNew_manualLapsFileName = True
                else:
                    # NO ManualLaps FILE args, Use the manualLaps.txt file
                    hasManualLapsFile = True
            
        else:
            # NO Args MODE, assign fixed file below
            manualLapsFileName = manualLapsPathPrefix + 'indoorBikeLapsLatest.txt'
            hasManualLapsFile = True
        
        file_exist = os.path.isfile(manualLapsFileName)
        if not file_exist:
            print('---------------- Lap txtFile does not exist! ', manualLapsFileName)
            hasManualLapsFile = False
            manualLapsFileName = 'No manualLaps file used.'

    # Extract LAP data from FIT file
    # ================================================================
    lapTable = extract_lap_data_from_fit(fitFile_path_name, startWithWktStep)

    for lapData in lapTable:
        print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

    if hasManualLapsFile:
        # Extract LAP data from TXT file
        # ================================================================
        lapFromTxtTbl, lapCountTxt, totDistTxtFile = extract_lap_data_from_txt(manualLapsFileName)
        totDist = totDistTxtFile

        for lapData in lapTable:
            print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

        # Check that the no of laps are equal in TXT and FIT
        # ================================================================
        print('lapCount in TXT and FIT files: ', lapCountTxt, lapCountFit)
        if lapCountTxt != lapCountFit: 
            # EXIT if lapCount do not match
            print('====================== NOT same LapCountDATE in FIT and manualLaps FILE')
            exit()

    for lapData in lapTable:
        print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

    # Extract RECORD and LAP data from FIT file
    # ================================================================
    recordTable, timeFirstRecord, timeLastRecord = extract_record_data_from_fit(fitFile_path_name)

    if hasManualLapsFile:
        # Merge manualLaps with recordTable
        # ================================================================
        lapTable = merge_lapData_from_txt(lapTable, lapFromTxtTbl)

    # Calc LAP TIME END in lapTable
    # ================================================================
    lapTable = calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord)

    for lapData in lapTable:
        print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

    # Calc LAP DATA fron recordTable
    # ================================================================
    lapTable, recordTable, totDistLastRecord = calc_lapData_from_recordTable(recordTable, lapTable)
    if totDist in [0, None]: totDist = totDistLastRecord
    
    for lapData in lapTable:
        print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

    if hasManualLapsFile:
        # Calc Distance amd Speed based on Cadence
        # ================================================================
        recordTable, lapTable = calc_dist_speed_basedOn_cadence(recordTable, lapTable)

    for lapData in lapTable:
        print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

    # Calc AVG DATA in lapTable
    # ================================================================
    avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest = calc_avg_in_lapTable(lapTable)

    for lapData in lapTable:
        print(lapData['lapNo'],lapData['lapDist'],mps2minpkm_Str(lapData['avgSpeed']),lapData['level'])

    # Create OUT BASE FILE NAME
    # =========================
    out_baseFileName = createBaseFileName(timeFirstRecord, actName, totDist, totTime, wktName, product, SWver)
    outLapTxt_file_path, outNewRecordCSV_file_path, newFitFileName = outFilePaths(pathPrefixFit, out_baseFileName)

    # TEST Header
    if test:
        print('================ TEST =================')

    # SAVE TO TXT FILE
    # =========================
    if activityType == 'gymbike':
        saveGymBikeLapTable_to_txt()
    if activityType == 'ct':
        saveCTLapTable_to_txt()

    newManualLapsFileName = createBaseFileName(startTime, actName, '', totTime, wktName, product, SWver)
    newManualLapsFileName = pathPrefixFit + newManualLapsFileName + '-LevelTotDist.txt'

    if hasManualLapsFile:
        renameFitFile(manualLapsFileName, newManualLapsFileName)

    # LAP DISTANCES to be used if script need to be run again
    # -------------------------------------------------------
    if needNew_manualLapsFileName:
        #os.remove(manualLapsFileName)
        #manualLapsFileName = createBaseFileName(startTime, actName, '', totTime, wktName, product, SWver)
        #manualLapsFileName = pathPrefixFit + manualLapsFileName + '-LevelTotDist.txt'
        inLapTxt_file = open(newManualLapsFileName, 'w')
        for lapData in lapTable:
            lapTxtLine = ''
            lapTxtLine += str(int(lapData['level']))
            lapTxtLine += ' '
            lapTxtLine += str(lapData['totDist']/10)
            inLapTxt_file.write (lapTxtLine + '\n')

# ================================================================
# ================================================================
# SPINBIKE
# ================================================================
if activityType == 'spinbike':
    recordTable, timeFirstRecord, timeLastRecord = extract_record_data_from_fit(fitFile_path_name)
    
    lapTable = extract_lap_data_from_fit(fitFile_path_name, startWithWktStep)
    
    lapTable = calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord)
    
    lapTable, recordTable, totDistLastRecord = calc_lapData_from_recordTable(recordTable, lapTable)
    if totDist in [0, None]: totDist = totDistLastRecord

    avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest = calc_avg_in_lapTable(lapTable)

    out_baseFileName = createBaseFileName(timeFirstRecord, actName, totDist, totTime, wktName, product, SWver)
    outLapTxt_file_path, outNewRecordCSV_file_path, newFitFileName = outFilePaths(pathPrefixFit, out_baseFileName)

    if test:
        print('================ TEST =================')

    saveSpinBikeLapTable_to_txt()

# ================================================================
# ================================================================
# RUN
# ================================================================
if activityType == 'run':
    recordTable, timeFirstRecord, timeLastRecord = extract_record_data_from_fit(fitFile_path_name)

    lapTable = extract_lap_data_from_fit(fitFile_path_name, startWithWktStep)

    lapTable = calc_lapTimeEnd_in_lapTable(lapTable, timeLastRecord)

    lapTable, recordTable, totDistLastRecord = calc_lapData_from_recordTable(recordTable, lapTable)
    if totDist in [0, None]: totDist = totDistLastRecord

    avgSpeedActive, avgCadActive, avgSpeedRest, avgCadRest, avgPowerActive, avgPowerRest = calc_avg_in_lapTable(lapTable)

    out_baseFileName = createBaseFileName(timeFirstRecord, actName, totDist, totTime, wktName, product, SWver)
    outLapTxt_file_path, outNewRecordCSV_file_path, newFitFileName = outFilePaths(pathPrefixFit, out_baseFileName)

    if test:
        print('================ TEST =================')

    saveRunLapTable_to_txt()


# ================================================================
# ================================================================
# THE END
# ================================================================
renameFitFile(fitFile_path_name, newFitFileName)
removeZipFile(ext, zipFile_path_name)

print('-----THE END', datetime.now())
if test:
    fileTemplate = pathPrefixFit + out_baseFileName + '-LapTables - copy.txt'
    if os.path.exists(fileTemplate):
        result = filecmp.cmp(fileTemplate, outLapTxt_file_path, shallow=False)
        if result: print('==TEST OK==, LapTables files match, test =', result)
        else:  print('==TEST NOT OK==, LapTables files DO NOT match, test =', result)
    else:
        print('==TEST NOT OK==, file name changed to: ', fileTemplate)
    print('================ TEST END =================')
