import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.cm as cm

plt.rcParams['font.family'] = 'Arial'
## UV EXPERIMENTAL PARAMETERS ## 

Sample_Name = ''
#Path to the files

UV_directory = input('Please input the UV-Vis Spectra files path:')

#Get all the CSV files in the folder
UV_files = glob.glob(os.path.join(UV_directory, "*.csv"))
df_list = [] 

###CV Data files###

#Compile and Modify the file
for file in UV_files:
    df = pd.read_csv(file, header=None)
    file_name = os.path.basename(file)

  
    # Get the first column dynamically
    col = df.columns[0]
    # Target value
    target = "Wavelength (nm)"
     # Find the first row where it appears
    matches = df.index[df[col].astype(str).str.strip() == target]

    if len(matches) == 0:
        print(f"Value '{target}' not found in column {col}")
        continue

    header_idx = matches[0]
    #Find the header row, skip the header, keep all data afterwards
    df = df.loc[header_idx-1:].reset_index(drop=True) 
    # keep only last first columns
    df = df.iloc[:, 2:]  
    #Rename the original columns
    df.rename(columns={df.columns[0]: 'Wavelength (nm)', df.columns[1]: 'Abs'}, inplace=True)

    #Convert to numeric columns
    df['Wavelength (nm)'] = pd.to_numeric(df['Wavelength (nm)'], errors='coerce')
    df['Abs'] = pd.to_numeric(df['Abs'], errors='coerce')

    mask = (df['Wavelength (nm)'] > 500) & (df['Wavelength (nm)'] < 900)
    max_abs = df.loc[mask, 'Abs'].max()
    peak_idx = df.loc[mask, 'Abs'].idxmax()
    peak_nm = df.loc[peak_idx]['Wavelength (nm)']
    df['Normalized_Abs'] = df['Abs'] / max_abs

    #Add a column with the file name
    df[file_name] = ''
    df['/'] = ''
    
    #Append the new dataframe
    df_list.append(df)
    print(f'{file_name}, {peak_nm}, {max_abs}')

#concatenate the files, horizontally
combined_df = pd.concat(df_list, axis=1)

#Output to CSV
output_file = 'compiled_data.csv' #input('Please enter a name for the data output:')
output_path = os.path.join(UV_directory, output_file)
combined_df.to_csv(output_path, index=False)



print("Files combined.")

# Path to save the file
output_path = os.path.join(UV_directory, "UV_plot_Normalized.png")

##Plot the NORMALIZED data##
N = len(df_list)

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
    colors = [cmap(i/(N)) for i in range(N)]

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 16})

ax = plt.gca()   # get current axis

# ---- Set axis spine widths ----
for spine in ax.spines.values():
    spine.set_linewidth(2)  # Axis line thickness

# ---- Set tick line thickness ----
ax.tick_params(axis='both', which='major', width=2, length=5, direction='in', top=True, right=True, pad=6 )  # (length optional)
ax.minorticks_on()
ax.tick_params(axis='both', which='minor', width=2, length=2.5, direction='in', top=True, right=True)

for i, df in enumerate(df_list):
    file_name = os.path.basename(UV_files[i])
    to_remove = ".csv"
    new_name = file_name.replace(to_remove,"")
    plt.plot(df['Wavelength (nm)'], df['Normalized_Abs'],
             label=new_name, color=colors[i], linewidth=1.5)

plt.xlabel('Wavelength (nm)', fontsize=16)
plt.ylabel('Normalized Absorbance', fontsize=16)
plt.title(Sample_Name, fontsize=18)

plt.legend(loc='upper left', fontsize='16',
           facecolor='none', edgecolor='none', framealpha=1)

plt.grid(False)
plt.ylim(0, 1.1)
plt.xlim(300, 900)

# Save
plt.savefig(output_path, dpi=450, bbox_inches='tight')
plt.close()
print(f"Plot saved as {output_path}")


##Plot the raw data##
output_path = os.path.join(UV_directory, "UV_plot.png")

N = len(df_list)

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
    colors = [cmap(i/(N)) for i in range(N)]

plt.figure(figsize=(8,8))
plt.rcParams.update({'font.size': 16})

ax = plt.gca()

for spine in ax.spines.values():
    spine.set_linewidth(2)  


ax.tick_params(axis='both', which='major', width=2, length=5, direction='in', top=True, right=True, pad=6 )  # (length optional)
ax.minorticks_on()
ax.tick_params(axis='both', which='minor', width=2, length=2.5, direction='in', top=True, right=True)

for i, df in enumerate(df_list):
    file_name = os.path.basename(UV_files[i])
    to_remove = ".csv"
    new_name = file_name.replace(to_remove,"")
    plt.plot(df['Wavelength (nm)'], df['Abs'],
             label=new_name, color=colors[i], linewidth=1.5)
    
plt.xlabel('Wavelength (nm)', fontsize=16)
plt.ylabel('Absorbance', fontsize=16)
plt.title(Sample_Name, fontsize=18)
plt.legend(loc='best', fontsize='16',
           facecolor='none', edgecolor='none', framealpha=1)
plt.grid(False)
plt.xlim(300, 900)
plt.ylim(0, 1.3)
# Save
plt.savefig(output_path, dpi=450, bbox_inches='tight')
plt.close()
print(f"Plot saved as {output_path}")

