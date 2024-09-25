import os.path
import matplotlib.pyplot as plt
import fitparse

def extract_lapHRdata_from_fit(file_path):
    # Parse the FIT file
    fitfile = fitparse.FitFile(file_path)
    #print (len(fitfile))
    
    # List to store cadence data and time offsets
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
                print(timestamps[recordNo])
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
    
    return timestamps, level, HR, timestamps

def plot_cadence(timestamps, cadences):
    # Plotting the cadence data
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, cadences, label='Cadence', color='blue')
    plt.xlabel('Time')
    plt.ylabel('Cadence (RPM)')
    plt.title('Cadence over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

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

# File path to your destination text file
outLapTxt_file_path = pathPrefix + 'documents/latestActivityLapTables.txt'


# Extract cadence data
timestamps, level, HR, timestamps = extract_lapHRdata_from_fit(fit_file_path)
#wait = input("Press Enter to continue.")
# Plot the cadence data
#plot_cadence(timestamps, cadences)
#wait = input("Press Enter to continue.")