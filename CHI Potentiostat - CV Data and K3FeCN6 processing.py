import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import AutoMinorLocator

plt.rcParams['font.family'] = 'Arial'

## CV EXPERIMENTAL PARAMETERS ## 
Sample_Name = ''
choice = input('Working Electrode Choice. Enter 1 for GC, 2 for BPG:')
Counter = 'Basal Planar Graphite'
Reference = 'Ag/AgCl'

if choice == '1':
    Working = 'GC'
    Working_diameter = 3 #Working Electrode Diameter (mm)
    Working_radius = Working_diameter/2/10 #Working Electrode radius (cm)
    Working_area = 3.1415*Working_radius*Working_radius # (cm^2)
elif choice == '2':
    Working = 'BPG'
    Working_area = 0.3*0.3 #cm^2

print(Working)
print(f'working area is {Working_area} cm^2')
## Standard Potential Adjustment ##

#enter the pH
pH = 8.85

#Reference Electrode Potential
AgCl_vs_SHE = +0.197 # (V), Ag/AgCl vs SHE (sat. KCl, 25 °C)

#Full converstion to the RHE
AgCl_to_RHE  = AgCl_vs_SHE + 0.0591*pH 

#E1/2 of K3Fe(CN)6 CV
Ehalf_K3FeCN6_ref = 0.23 #Literature value
Ehalf_K3FeCN6_exp = 0.23 #Experimental Value, determined experimentally, calculated below
K3FeCN6_factor = Ehalf_K3FeCN6_ref - Ehalf_K3FeCN6_exp #Applied reference offset

#Path to the files
Standard_Directory = input('please input the directory for the standard CV:')
Standard_output_path = os.path.join(Standard_Directory, "Standard_plot.png")
CV_directory = input('Please input the CV files path:')

#Get all the Standard files in the folder
Standard_files = glob.glob(os.path.join(Standard_Directory, "*6.csv"))
df_list = [] 

#Get all the CSV files in the folder
CSV_files = glob.glob(os.path.join(CV_directory, "*.csv"))
df_list = [] 

#Compile and Modify the file
for file in Standard_files:
    df = pd.read_csv(file, header=None)
    file_name = os.path.basename(file)  # get the file name
    
    #Get the first column
    col = df.columns[0]
    #Target value
    target = 'Potential/V'
    #Find the first row where it appears
    matches = df.index[df[col].astype(str).str.strip() == target]

    if len(matches) == 0:
        print(f"Value '{target}' not found in column {col}")
        continue
    header_idx = matches[0]
    
    #Find the header row, skip the header, keep all data afterwards
    df = df.loc[header_idx+1:].reset_index(drop=True) 
    df = df.iloc[:, :2]  # keep only last two columns
    #Rename the original columns
    df.rename(columns={df.columns[0]: 'Potential (V)', df.columns[1]: 'Current (A)'}, inplace=True)

    #Convert to numeric columns
    df['Potential (V)'] = pd.to_numeric(df['Potential (V)'], errors='coerce')
    df['Current (A)'] = pd.to_numeric(df['Current (A)'], errors='coerce')

    #Find the maximum and minimum current

    mask = (df['Potential (V)'] > 0.1) & (df['Potential (V)'] < 0.4)
    ipc = df.loc[mask, 'Current (A)'].max()
    ipc_idx = df.loc[mask, 'Current (A)'].idxmax()
    Epc = df.loc[ipc_idx]['Potential (V)']


    ipa = df.loc[mask, 'Current (A)'].min()
    ipa_idx = df.loc[mask, 'Current (A)'].idxmin()
    Epa = df.loc[ipa_idx]['Potential (V)']

    #Calculate Ehalf
    E_half = (Epc + Epa)/2

    #Set the Experimental Ehalf according to the calculated value
    Ehalf_K3FeCN6_exp = E_half

    #Applied reference offset
    K3FeCN6_factor = Ehalf_K3FeCN6_ref - Ehalf_K3FeCN6_exp #Applied reference offset

    #Total potential shift to be applied. (Convert from experimental Ag/AgCl to RHE, including standard potential offset)
    delta_E2 = AgCl_to_RHE + K3FeCN6_factor

    print(file_name)
    print("E half", E_half)
    print("Calibration Factor", K3FeCN6_factor)

    ## Create the plot##
    plt.plot(df['Potential (V)'], df['Current (A)'], label=file_name)
    plt.scatter(Epc, ipc, color='red', label='Epc')
    plt.scatter(Epa, ipa, color='blue', label='Epa')
    plt.axvline(x=E_half, color='b', linestyle='--', label='E_1/2' )
    plt.text(Epa, ipa, f'{Epa:.4f}', fontsize=12, color='black')
    plt.text(Epc, ipc, f'{Epc:.4f}', fontsize=12, color='black')
    plt.text(E_half, ipc/10, f'{E_half:.4f}', fontsize=12, color='black')

    plt.figure(figsize=(8,8))
    plt.rcParams.update({'font.size': 18})

    ax = plt.gca()

    for spine in ax.spines.values():
        spine.set_linewidth(2)  

    ax.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False)

    plt.xlabel('Potential (V vs Ag/AgCl)')
    plt.ylabel('Current Density (A)')
    plt.title('')
    plt.legend(loc='upper left', fontsize='18', facecolor='none', edgecolor='none', framealpha=1)
    plt.grid(False)
    #Flip the x-axis
    plt.gca().invert_xaxis()
    plt.gca().invert_yaxis()
    #Save as PNG
    plt.savefig(Standard_output_path, dpi=450)
    plt.close()

###CV Data files###

#Compile and Modify the file
for file in CSV_files:
    df = pd.read_csv(file, header=None)
  
    # Get the first column dynamically
    col = df.columns[0]
    # Target value
    target = 'Potential/V'
     # Find the first row where it appears
    matches = df.index[df[col].astype(str).str.strip() == target]

    if len(matches) == 0:
        print(f"Value '{target}' not found in column {col}")
        continue

    header_idx = matches[0]
    #Find the header row, skip the header, keep all data afterwards
    df = df.loc[header_idx+1:].reset_index(drop=True) 
    df = df.iloc[:, :2]  # keep only first two columns
    #Rename the original columns
    df.rename(columns={df.columns[0]: 'Potential (V)', df.columns[1]: 'Current (A)'}, inplace=True)

    #Convert to numeric columns
    df['Potential (V)'] = pd.to_numeric(df['Potential (V)'], errors='coerce')
    df['Current (A)'] = pd.to_numeric(df['Current (A)'], errors='coerce')

    #Add calculated columns 
    df['Potential (V vs RHE)'] = df['Potential (V)'] + delta_E2
    df['Current Density (mA/cm²)'] = df['Current (A)'] * 1000 / Working_area

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
output_path = os.path.join(CV_directory, output_file)
combined_df.to_csv(output_path, index=False)

print('Files combined')


# Path to save the file
output_path = os.path.join(CV_directory, "CV_plot.png")

##Plot the CV data##
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
plt.rcParams.update({'font.size': 18})

ax = plt.gca()

for spine in ax.spines.values():
    spine.set_linewidth(2)  

ax.tick_params(axis='both', which='major', width=2, length=6, direction='in', top=False, right=False, pad=6 )  # (length optional)
ax.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))
ax.tick_params(axis='both', which='minor', width=2, length=3, direction='in', top=False, right=False)

for i, df in enumerate(df_list):
    file_name = os.path.basename(CSV_files[i])
    to_remove = ".csv"
    new_name = file_name.replace(to_remove,"")
    plt.plot(df['Potential (V vs RHE)'], df['Current Density (mA/cm²)'], 
             label=new_name, color=colors[i])

plt.xlabel('Potential (V vs RHE)', fontsize=18)
plt.ylabel('Current Density (mA/cm²)', fontsize=18)
plt.title(Sample_Name, fontsize=18)  
#plt.xlim(-1.5, 0.2)
plt.ylim(-5, 15)
if N > 1: 
    plt.legend(loc='upper left', fontsize='18', facecolor='none', edgecolor='none', framealpha=1)

else: 
    plt.grid(False)

plt.grid(False)

#Flip the x-axis
plt.gca().invert_xaxis()

#Save as PNG
plt.savefig(output_path, dpi=450, bbox_inches='tight', pad_inches=0.1)
plt.close()
print(f"Plot saved as {output_path}")




