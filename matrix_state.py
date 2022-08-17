"""
Written by Fadil Isamotu
November 16, 2021
isamotufadil15@gmail.com
"""

import pyvisa 
# pyvisa's resource manager to get devices Id
rm = pyvisa.ResourceManager()
#print(rm.list_resources()) #__Optional__ To check what visa devices are available
mtrx = rm.open_resource('ENTER YOUR SWITCHING MATRIX ID HERE') # Switching matrix ID


#-----------------------------------------------------------------------------------------------------SWITCHING MATRIX----------------------------------------------------------------------------------------------------
def matrix_Open(device):
    """This function opens specified channels on DB25 Breakout 25 Pin Connector using U2751A switching matrix.  
    
    >>> matrix_Open(1)
    Opens channels for transistor 1

    >>> matrix_Open("all")
    Opens all channels

    >>> matrix_Open("RST")
    Resets the switching matrix (Opens all channels)
    """  
    
    if device == 'all' or device == 'ALL' or device == 'All':
        
        mtrx.write(f'ROUTe:OPEN (@ 101, 202, 103, 204, 105, 206, 107, 208)')
        
    elif device == "RST" or device == "RESET" or device == "reset" or device == "rst":
        
        mtrx.write('*RST')    
        
    elif device == '1':
        
        mtrx.write(f'ROUTe:OPEN (@ 101, 202)')
        
    elif device == '2':
        
        mtrx.write(f'ROUTe:OPEN (@ 103, 204)')
        
    elif device == '3':
        
        mtrx.write(f'ROUTe:OPEN (@ 105, 206)')
    
    elif device == '4':
        mtrx.write(f'ROUTe:OPEN (@ 107,208)')

    mtrx.write('opc?')                       # Waits for all commands to be executed before executing next commands   

def matrix_Close(device): 
    """This function closes specified channels on DB25 Breakout 25 Pin Connector using U2751A switching matrix.  
    
    >>> matrix_Open(1)
    Closes channels for transistor 1

    >>> matrix_Open("all")
    Closes all channels

    >>> matrix_Close("RST")
    Resets the switching matrix (Opens all channels)
    """ 
    
    if device == 'all' or device == 'ALL' or device == 'All':
        
        mtrx.write(f'ROUTe:CLOSE (@ 101, 202, 103, 204, 105, 206, 107, 208)')
        
    elif device == "RST" or device == "RESET" or device == "reset" or device == "rst":
        
        mtrx.write('*RST')    
        
    elif device == '1':
        
        mtrx.write(f'ROUTe:CLOSE (@ 101, 202)')
        
    elif device == '2':
        
        mtrx.write(f'ROUTe:CLOSE (@ 103, 204)')
        
    elif device == '3':
        
        mtrx.write(f'ROUTe:CLOSE (@ 105, 206)')
    
    elif device == '4':
        mtrx.write(f'ROUTe:CLOSE (@ 107,208)')
    
    mtrx.write('opc?')                       # Waits for all commands to be executed before executing next commands    
