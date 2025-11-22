# **make a standard file-sound level meter data.**

Processes export from sound level meters SVAN959, 01dB-fusion,  Bruel and Kjaer 2250 & 2270 and Norsonic140 

To a standard file with sound level meter data that can be used to perform calculations in 
a deployed app

--> SEE: https://environmental-noise-calculation.onrender.com/

--> SEE: https://github.com/ChironeX1976/environmental-noise-calculation-dashboard/tree/main


**The minimal required output of columns:**

    timestamp (isodatetime), 

    laeq1s (float), 

    markers (value is nan or 1) - exclude marker is mandatory. 


**optional columns**

    spectral data: lzeq25hz -> lzeq20000hz,

    soundpath, 

    statistics per second laf 1, 5, 10, 50, ...


**example**

    isodatetime             laeq1s        exclude	lzeq25hz    ....
    -----------------------------------------------------------------
    2024-05-20 20:04:42      43.01	        1.0	    50.30
    2024-05-20 20:04:43      45.00          
    ...
