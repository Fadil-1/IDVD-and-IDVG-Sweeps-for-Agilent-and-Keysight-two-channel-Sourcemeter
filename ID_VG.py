"""
Written by Fadil Isamotu
November 16, 2021
isamotufadil15@gmail.com
"""
import pyvisa
import numpy  
import os
from time import time as time_Elapsed 
import datetime                 
#import matplotlib.pyplot as plt 
import csv
from matrix_state import mtrx, matrix_Close

#------------------------------------------------------------------------------------------------PYVISA INITIALIZATION-------------------------------------------------------------------------------------------------
# pyvisa's resource manager to get devices Id
rm = pyvisa.ResourceManager()
#print(rm.list_resources()) #__Optional__ To check what visa devices are available
smu  = rm.open_resource('ENTER YOUR SMU ID HERE') # SMU ID



def ID_VG(state = "on", message = '', VG_Start = -3,  VG_End = 5, VDS_Start = 0.5, VDS_END = 3,
    VG_Data_Points = 242, VDS_Data_Points = 6, device_Name ='',
    ID_COMPLIANCE = 12e-2, ID_RESOLUTION = 0.01, IG_COMPLIANCE = 1e-3,
    IG_RESOLUTION = 0.01, directory= "D:\TESTS", folder_Name = 'IDVG_SWEEP_', device_Channel ='1', measurement = 'ID_VG'):

    """This function performs ID/VG sweeps using channel 1 of B2902A SMU for drain bias and channel 2 for gate bias.
    The bias consists of a forward and backward gate voltage sweep (From VG_Start to VG_End, then from VG_End to VG_Start).
    A CSV file of the biased and measured data are saved in a directory specified by the "directory" parameter.
    The directory' and files' names contain the date and time during which they were created. 


    "Start" and "End" parameters respectively specify at what numeric value to start and end the sweep.


    The "datapoints" parameters specify in how many increments/slices/steps the corresponding argument must be divided.
    datapoints = [(End value)/(Increment/Step value)] + 1 (The first data point is the value of “start”.)

    Ex1: VG/VD_start = 0, VG/VD_End = 18.  
    VG/VD_Data_Points = 7,  ==> step = 3      ==>  [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0]
    VG/VD_Data_Points = 10, ==> step = 2      ==>  [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

    Ex2: VG/VD_start = 4, VG/VD_End = 48.
    VG/VD_Data_Points = 5,  ==> step = 11      ==>  (4.0, 15.0, 26.0, 37.0, 48.0)
    VG/VD_Data_Points = 4,  ==> step = 14.66   ==>  (4.0, 18.666666666666664, 33.33333333333333, 48.0)
    VG/VD_Data_Points = 6,  ==> step = 8.8     ==>  (4.0, 12.8, 21.6, 30.400000000000002, 39.2, 48.0)

    Resolution parameters (PLC) affect the measurement speed and quality.
    The highest speed setting (0.01) results in increased noise and lower measurement accuracy, whereas the lowest speed (10) results in best measurement quality.
    """ 
    if state != "on": return
    start_Time = time_Elapsed()
    print(message)
    HALF_OF_VG_DATAPOINTS = int(VG_Data_Points/2)

    # Creating empty lists to store output data
    Vds        = []
    sensed_VDS = []
    Vg         = []
    sensed_VG  = []
    Ig         = []
    Id         = []

    smu.write('*rst')                                   # Resets the sourcemeter
    smu.write('opc?')                                   # Waits for all commands to be executed before executing next commands
    mtrx.write('*RST')                                  # Resets the switching matrix
    mtrx.write('opc?')                                  # Waits for all commands to be executed before executing next commands
    matrix_Close(device_Channel)                        # Closing specified channel

    # Channel 1 config

    smu.write(":SENS1:CURR:RANG:AUTO ON")               # Setting channel 1's sensing range to automatic mode
    smu.write(f':sens1:func ""curr""')                  # Setting channel to sense current
    smu.write(f':sens1:curr:nplc {ID_RESOLUTION}')      # Measurement Resolution
    smu.write(f':sens1:curr:prot {ID_COMPLIANCE}')      # Drain to source current Compliance
    smu.write(":SOUR1:FUNC:MODE VOLT")                  # Setting channel 1 to source voltage
    smu.write(":OUTP ON")                               # Turning channel 1 on

    # Channel 2 config

    smu.write(":SENS2:CURR:RANG:AUTO ON")               # Setting channel 2's sensing range to automatic mode
    smu.write(f':sens2:func ""curr""')                  # Setting channel to sense current
    smu.write(f':sens2:curr:nplc {IG_RESOLUTION}')      # Measurement Resolution
    smu.write(f':sens2:curr:prot {IG_COMPLIANCE}')      # Gate current Compliance
    smu.write(":SOUR2:FUNC:MODE VOLT")                  # Setting channel 2 to source voltage
    smu.write(":OUTP ON")                               # Turning channel 2 on

    smu.write('opc?')                                   # Waits for all commands to be executed before executing next commands

    # Setting up loops 

    for VDS in numpy.linspace(VDS_Start, VDS_END, num = VDS_Data_Points):           # Outer loop alters VD
        
        #smu.write(f':SYST:BEEP 300, 0.4')                                           # Beep at every VD increment
        smu.write(":SOUR1:VOLT " + str(VDS))                                        # Sources programmed value of VDS

        smu.write('opc?')                                                           # Waits for all commands to be executed before executing next commands
            
        for VG_UP in numpy.linspace(VG_Start, VG_End, num = HALF_OF_VG_DATAPOINTS): # First inner loop alters VG increments
            # Appends set values of VG and VDS to their specific lists
            Vds.append(VDS)                                                         # Appends programmed value of VDS to VDS's list 
            Vg.append(VG_UP)                                                        # Appends programmed value of VG to VG's list 
            smu.write(":SOUR2:VOLT " + str(VG_UP) )                                 # Sources programmed value of VG from channel 2

            # Getting sensed Gate, and Drain Source voltages
            smu.write(f':meas:VOLT? (@1)')              # Queries voltage value measured at channel 1
            sensed_VDS.append(smu.read().rstrip("\n"))  # Removes newline from acquired value and appends it to sensed_VDS
            smu.write(f':meas:VOLT? (@2)')              # Queries voltage value measured at channel 2
            sensed_VG.append(smu.read().rstrip("\n"))   # Removes newline from acquired value and appends it to sensed_VG
            
            # Getting sensed current 
            smu.write(f':meas:curr? (@1)')              # Queries current value measured at channel 1
            Id.append(smu.read().rstrip("\n"))          # Removes newline from acquired value and appends it to Id
            smu.write(f':meas:curr? (@2)')              # Queries current value measured at channel 2
            Ig.append(smu.read().rstrip("\n"))          # Removes newline from acquired value and appends it to Ig
            
            smu.write('opc?')                           # Waits for all commands to be executed before executing next commands
        
        for VG_DOWN in numpy.linspace(VG_End, VG_Start, num = HALF_OF_VG_DATAPOINTS): # Second inner loop alters VG decrements
            Vds.append(VDS)
            Vg.append(VG_DOWN)
            
            smu.write(":SOUR2:VOLT " + str(VG_DOWN))    # Sources programmed value of VDS
            
            # Getting sensed Gate, and Drain Source voltages
            smu.write(f':meas:VOLT? (@1)')              # Queries voltage value measured at channel 1
            sensed_VDS.append(smu.read().rstrip("\n"))    # Removes newline from acquired value and appends it to sensed_VDS
            smu.write(f':meas:VOLT? (@2)')              # Queries voltage value measured at channel 2
            sensed_VG.append(smu.read().rstrip("\n"))     # Removes newline from acquired value and appends it to sensed_VG

            smu.write(f':meas:curr? (@1)')              # Queries current value measured at channel 1
            Id.append(smu.read().rstrip("\n"))          # Removes newline from acquired value and appends it to Id
            smu.write(f':meas:curr? (@2)')              # Queries current value measured at channel 2
            Ig.append(smu.read().rstrip("\n"))          # Removes newline from acquired value and appends it to Ig
           
            smu.write('opc?')                           # Waits for all commands to be executed before executing next commands
        
            
    #smu.write(f':SYST:BEEP 400, 1')                     # Longbeep for 1 second after sweeps are over

    
    # Converting all sensed values from strings to floats
    Ig          = [eval(x) for x in Ig]
    Id          = [eval(x) for x in Id]
    sensed_VDS  = [eval(x) for x in sensed_VDS]
    sensed_VG   = [eval(x) for x in sensed_VG]

    # Creating lists with absolute value of IG and ID for IDVG plot
    Ig_ABSL = [abs(num) for num in Ig]
    Id_ABSL = [abs(num) for num in Id]

    # Folder to save files
    today = datetime.datetime.today()                                                                             # Indexing current date and time with variable "today" 
    export_Folder = (f"{directory}\{folder_Name}{today:%m-%d-%Y}")                                                # Formatting export folder  
    if not os.path.exists(export_Folder):                                                                         # To make sure that no additional folder is created is saving folder already exists
        os.makedirs(export_Folder)

    # Writing results to a .CSV file and saving it to created folder
    IDVG_CSV = (f"{device_Name}_IDVG_{today:%m-%d-%Y-%H_%M}_{time_Elapsed() - start_Time}.CSV")                                                     # Formating file's name
    with open( os.path.join( export_Folder,  IDVG_CSV) , 'w', newline='' ) as myfile:                                 # Saving CSV file in created directory
        writer = csv.writer(myfile)
        writer.writerow(["VG", "sensed_VG", "ID_abs", "IG_abs", "Id", "IG", "VDS", "sensed_VDS"])                     # File's header
        for v in range (0, VG_Data_Points*VDS_Data_Points):                                                           # Setting range to read all values in lists
            writer.writerow ([ Vg[v], sensed_VG[v], Id_ABSL[v], Ig_ABSL[v], Id[v], Ig[v], Vds[v], sensed_VDS[v] ])    # Specifying rows
        myfile.close() 