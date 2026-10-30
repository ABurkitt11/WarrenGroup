import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math
import scipy.signal
from scipy.signal import find_peaks, peak_prominences
from matplotlib.ticker import AutoMinorLocator
import matplotlib.ticker as ticker

plt.rcParams['font.family'] = 'Arial'
#### GAS CHROMATOGRAPHY ###
#Instrument Agilent 6890 w/ TCD
#Method - WarrenShort

#### Experimental Parameters###

## Import Data from .csv

GC_directory = input('please input the GC file path:')
GC_output_path = os.path.join(GC_directory, "GC_plot.png")

#Get all the Standard files in the folder
GC_files = glob.glob(os.path.join(GC_directory, "*.csv"))
df_list = [] 

#Compile and Modify the file
for file in GC_files:
    df = pd.read_csv(file, header=None, encoding='utf-16')
    file_name = os.path.basename(file)  # get the file name

    #Get the first column
    col = df.columns[0]

    #Rename the first column
    df.rename(columns={df.columns[0]: 'Time (mins)', df.columns[1]: 'Detector Signal (μV)'}, inplace=True)

    #Convert to numeric columns
    df['Time (mins)'] = pd.to_numeric(df['Time (mins)'], errors='coerce')
    df['Detector Signal (μV)'] = pd.to_numeric(df['Detector Signal (μV)'], errors='coerce')

    mask = (df['Time (mins)'] > 1) & (df['Time (mins)'] < 1.3)
    mean_signal = df.loc[mask, 'Detector Signal (μV)'].mean()
    df['Baseline Subtracted Detector Signal'] = df['Detector Signal (μV)'] - mean_signal

    signal= df['Baseline Subtracted Detector Signal']

    peaks, properties = find_peaks(signal, height=1, prominence=1, distance=10)
    first_peak_positions = peaks[0]

    first_peak_time = df.loc[first_peak_positions, 'Time (mins)']
   
    df['Time (mins), first peak aligned'] = df['Time (mins)'] - first_peak_time

    print(first_peak_time)
    print(peaks, 'peaks')

    peak_times = df.loc[peaks, 'Time (mins)'].values
    peak_heights = properties['peak_heights']
    peak_coordinates = [[x, y] for x, y in zip(peak_times, peak_heights)]
    print(peak_coordinates)

    compound_names = ['O2','N2', 'CO2']
    named_peaks = {name: [float(x), float(y)] for name, (x, y) in zip(compound_names, zip(peak_times, peak_heights))}
    print(named_peaks)

    text_content = "\n".join([f"{name}: {coords[0]:.1f} min" for name, coords in named_peaks.items()])
    
    #Add a column with the file name
    file_name = os.path.basename(file)
    df[file_name] = ''
    df['/'] = ''

    #Append the new dataframe
    df_list.append(df)

#concatenate the files, horizontally
combined_df = pd.concat(df_list, axis=1)
    #Output to CSV
output_file = 'Combined_Data.csv' #input('Please enter a name for the data output:')
output_path = os.path.join(GC_directory, output_file)
combined_df.to_csv(output_path, index=False)
print('Files combined')


### Full Graph ### 

# Path to save the file
output_path = os.path.join(GC_directory, "GC_plot.png")

##Plot the CV data##
N = len(df_list)

print(f'{N}')

if N == 1:
    colors = ['black']

else: 
    cmap = plt.colormaps.get_cmap('rainbow')
    colors = [cmap(i/(N)) for i in range(N)]

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 16})
ax = plt.gca()

for spine in ax.spines.values():
    spine.set_linewidth(2)  

ax.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
ax.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(3))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))
ax.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False)

for i, df in enumerate(df_list):
    file_name = os.path.basename(GC_files[i])
    to_remove = ".csv"
    new_name = file_name.replace(to_remove,"")
    plt.plot(df['Time (mins)'], df['Detector Signal (μV)'],
             label=new_name, color=colors[i], linewidth=1.5)
    
plt.xlabel('Time (minutes)', fontsize=16)
plt.ylabel('Detector Signal (μV)', fontsize=16)
plt.title(f'{file_name}', fontsize=12)
plt.legend(loc='upper right', fontsize='16', facecolor='none', edgecolor='none', framealpha=1)
plt.grid(False)
plt.xlim(0, 12)

# Save
plt.savefig(output_path, dpi=450, bbox_inches='tight')
plt.close()
print(f"Plot saved as {output_path}")

### CO graph ###

# Path to save the file
output_path = os.path.join(GC_directory, "GC_CO_plot.png")

##Plot the GC data##
N = len(df_list)

if N == 1:
    colors = ['black']

else: 
    cmap = plt.colormaps.get_cmap('rainbow')
    colors = [cmap(i/(N)) for i in range(N)]

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 16})
ax = plt.gca()

for spine in ax.spines.values():
    spine.set_linewidth(2)  

ax.tick_params(width=2, length=6) 

for i, df in enumerate(df_list):
    file_name = os.path.basename(GC_files[i])
    to_remove = ".csv"
    new_name = file_name.replace(to_remove,"")
    plt.plot(df['Time (mins)'], df['Detector Signal (μV)'],
             label=new_name, color=colors[i], linewidth=1.5)
    

mask = (df['Time (mins)'] > 0) & (df['Time (mins)'] < 5)
min_signal = df.loc[mask, 'Detector Signal (μV)'].min()

def round_nearest_quarter(min_signal):
    return round(min_signal* 4) / 4.0

min_value = round_nearest_quarter(min_signal) - 1.0
max_value = round_nearest_quarter(min_signal) + 2.5

plt.xlabel('Time (minutes)', fontsize=16)
plt.ylabel('Detector Signal, Baseline Subtracted', fontsize=16)
plt.title(f'{file_name}', fontsize=12)
plt.legend(loc='upper right', fontsize='14', facecolor='white', edgecolor='black', framealpha=1)
plt.grid(False)
plt.xlim(1.5, 3.5)
plt.ylim(min_value, max_value)

#Save
plt.savefig(output_path, dpi=450, bbox_inches='tight')
plt.close()
print(f"Plot saved as {output_path}")

### Combined Plot ###
output_path_combined = os.path.join(GC_directory, "GC_Comparison.png")

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 18})
ax = plt.gca()

if N == 1:
    colors = ['black']
else: 
    cmap = plt.colormaps.get_cmap('rainbow')
    colors = [cmap(i/N) for i in range(N)]

for i, df in enumerate(df_list):
    file_name = os.path.basename(GC_files[i])
    new_name = file_name.replace(".csv", "")
    
    #Full Plot
    ax.plot(df['Time (mins)'], df['Detector Signal (μV)'],
             label=new_name, color=colors[i], linewidth=1.5)
    ax.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False)

ax_inset = ax.inset_axes([0.25, 0.4, 0.5, 0.5])  

for i, df in enumerate(df_list):

    #CO plot - inset
    ax_inset.plot(df['Time (mins)'], df['Detector Signal (μV)'],
             label=new_name, color=colors[i], linewidth=1.5)
    #ax_inset.tick_params(axis='both', which='major', direction='out',width=2, length=8)
    ax.minorticks_on()
    ax_inset.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax_inset.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_inset.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
    ax_inset.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False, pad=6 )  # (length optional)

#Total plot formatting
ax.set_xlabel('Time (minutes)')
ax.set_ylabel('Detector Signal')
ax.set_xlim(0, 12)

for spine in ax.spines.values(): spine.set_linewidth(2)

#CO plot formatting
ax_inset.set_xlim(1.5, 3.5)
ax_inset.set_ylim(min_value, max_value) # Uses the min/max calculated in your CO block
for spine in ax_inset.spines.values(): spine.set_linewidth(2)
    
plt.savefig(output_path_combined, dpi=450, bbox_inches='tight')
plt.close()


##Plot the GC data, baseline subtracted##
N = len(df_list)

if N == 1:
    colors = ['black']

else: 
    cmap = plt.colormaps.get_cmap('rainbow')
    colors = [cmap(i/(N)) for i in range(N)]

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 16})
ax = plt.gca()

for spine in ax.spines.values():
    spine.set_linewidth(2)  

ax.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
ax.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(4))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))
ax.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False)

for i, df in enumerate(df_list):
    file_name = os.path.basename(GC_files[i])
    to_remove = ".csv"
    new_name = file_name.replace(to_remove,"")
    plt.plot(df['Time (mins)'], df['Baseline Subtracted Detector Signal'],
             label=new_name, color=colors[i], linewidth=1.5)
    

mask = (df['Time (mins), first peak aligned'] > 0) & (df['Time (mins), first peak aligned'] < 5)
min_signal = df.loc[mask, 'Baseline Subtracted Detector Signal'].min()

def round_nearest_quarter(min_signal):
    return round(min_signal* 4) / 4.0

min_value = round_nearest_quarter(min_signal) - 1 #defatult -0.1
max_value = round_nearest_quarter(min_signal) + 1.5

plt.xlabel('Time (mins), first peak aligned', fontsize=16)
plt.ylabel('Detector Signal', fontsize=16)
plt.title(f'{new_name}', fontsize=12)
plt.legend(loc='upper right', fontsize='14', facecolor='white', edgecolor='black', framealpha=1)
plt.grid(False)
plt.xlim(1.5, 3.5)
plt.ylim(min_value, max_value)

#ax.set_ylim(13, 15)
#ax.autoscale(enable=False, axis='y')

#Save
plt.savefig(output_path, dpi=450, bbox_inches='tight')
plt.close()
print(f"Plot saved as {output_path}")

### Combined Plot ###
output_path_combined = os.path.join(GC_directory, "GC_Comparison_baselinesubtract.png")

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 18})
ax = plt.gca()

##Default Values - 0.15, 0.25, 0.5, 0.5 - CO ..... for H2 (0.4, 0.25, 0.5, 0.5)
ax_inset = ax.inset_axes([0.15, 0.25, 0.5, 0.5])

if N == 1:
    colors = ['black']

elif N == 2:
    colors = ['black', 'red']

elif N == 3:
    colors = ['black', 'red', 'blue']

elif N == 4:
    colors = ['black', 'red', 'blue','green']

else: 
    cmap = plt.colormaps.get_cmap('rainbow')
    colors = [cmap(i/(N-1)) for i in range(N)]

for i, df in enumerate(df_list):
    file_name = os.path.basename(GC_files[i])
    to_remove = ".CSV"
    new_name = file_name.replace(to_remove,"")
    
    #Full Plot
    ax.plot(df['Time (mins), first peak aligned'], df['Baseline Subtracted Detector Signal'],
             label=new_name, color=colors[i], linewidth=1.5)
    ax.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False)       
    #ax.scatter(df['Time (mins), first peak aligned'][peaks], df['Baseline Subtracted Detector Signal'][peaks], color='black', marker='X', s=5, zorder=3)
    
for i, df in enumerate(df_list):
    #CO plot - inset
    ax_inset.plot(df['Time (mins), first peak aligned'], df['Baseline Subtracted Detector Signal'],
             label=new_name, color=colors[i], linewidth=1.5)
    #ax_inset.tick_params(axis='both', which='major', direction='out',width=2, length=8)
    ax.minorticks_on()
    ax_inset.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax_inset.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_inset.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
    ax_inset.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False, pad=6 )  # (length optional)

#Total plot formatting
ax.set_xlabel('Time (mins), First Peak aligned')
ax.set_ylabel('Detector Signal, Baseline Subtracted')
ax.set_xlim(-1, 12)
## default upper left for CO , upper right for H2
plt.legend(loc='upper left', fontsize='14', facecolor='none', edgecolor='none', framealpha=1)
for spine in ax.spines.values(): spine.set_linewidth(2)

#CO plot formatting
ax_inset.set_xlim(-0.5, 1.5)
ax_inset.set_ylim(min_value, max_value) # Uses the min/max calculated in your CO block
for spine in ax_inset.spines.values(): spine.set_linewidth(2)

plt.savefig(output_path_combined, dpi=450, bbox_inches='tight')
plt.close()

