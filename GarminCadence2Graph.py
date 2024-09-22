import os.path
import matplotlib.pyplot as plt
import fitparse

def extract_cadence_from_fit(file_path):
    # Parse the FIT file
    fitfile = fitparse.FitFile(file_path)
    
    # List to store cadence data and time offsets
    cadences = []
    timestamps = []
    
    # Iterate over all messages of type "record"
    for record in fitfile.get_messages('record'):
        # Extract data fields
        for record_data in record:
            if record_data.name == 'cadence':
                # Append cadence value
                cadences.append(record_data.value)
            elif record_data.name == 'timestamp':
                # Append timestamp value
                timestamps.append(record_data.value)

    return timestamps, cadences

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

# File path to your FIT file
fit_file_path = 'c:/users/peter/documents/2024-09-14-09-46-48-indoorbike.fit'
check_file = os.path.isfile(fit_file_path)
print(check_file)
wait = input("Press Enter to continue.")

# Extract cadence data
timestamps, cadences = extract_cadence_from_fit(fit_file_path)
wait = input("Press Enter to continue.")
# Plot the cadence data
plot_cadence(timestamps, cadences)
wait = input("Press Enter to continue.")