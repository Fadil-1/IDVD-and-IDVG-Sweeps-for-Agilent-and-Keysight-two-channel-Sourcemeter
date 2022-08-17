# IDVD and IDVG Sweeps for Agilent and Keysight two channel Sourcemeter.
This repository contains three python files:

IDVD.py implementing an IDVD sweep 
IDVG.py implementing an IDVG sweep
matrix_state.py implementing the state condition of a switxhing matrix.
The scripts were tested on, and initially written for a B2902-A sourcemeter and a Keysight U2751A switching matrix.

They sweep scripts can be run in loop by unpacking the JSON parameter files a theur functions' arguments as such:


while True: # or countdown contidion using time.sleep module
  ID_VD (**arg("DEVICE_IDVD_Args"))
  ID_VG (**arg("DEVICE_IDVG_Args"))

Arguments can be modified during runtime using the JSON files.


