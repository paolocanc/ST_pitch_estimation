# Speech Technologies #
#### Master’s degree in Telecommunications Engineering (MET). Universitat Politècnica de Catalunya ####

# ST_pitch_estimation
  
Professor: José Adrián Rodríguez Fonollosa
Student: Paolo Cancello

The objective of this assignment is the analysis of the basic properties of the speech signal: voicing and pitch, and to develop accurate estimation algorithms of these parameters.

The methods that have been implemented for the pitch estimation and voicing detection are the Autocorrelation Method and the Cepstrum one. The starting point of the work has been the provided [pitch.py](pitch.py) script.
The performances of this implementations have been tested on the FDA-UE database, using the provided C++ [pitch_compare](pitch_compare.cpp) program to report the results as v/uv errors, uv/v errors, gross pitch errors (>20%) and MSE (Mean Squared Error) of the relative fine pitch errors.

The results can be seen by running the [pitch_estimation.py](pitch_estimation.py) script with the chosen method, using [fda_ue.gui] as input file list, and then running the [pitch_compare.cpp](pitch_compare.cpp) program. 
