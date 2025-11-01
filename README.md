**make a standard file with sound level meter data.**

processes export from SVAN959, 01dB-fusion and Bruel and Kjaer 2250 en 2270
to a standard file with sound level meter data



--> SEE: https://environmental-noise-calculation.onrender.com/
-->  https://github.com/ChironeX1976/environmental-noise-calculation-dashboard/tree/main


**required fields**

timestamp, 

laeq1s, 

markers (value is nan or 1) - exclude marker is mandatory. 



**optional fields**

spectral data: lzeq25hz -> lzeq20000hz,

soundpath, 

statistics per second laf 1, 5, 10, 50, ...



**example**

isodatetime	              laeq1s	  exclude	

2024-05-20 20:04:42	      43.01				1.0	
2024-05-20 20:04:43       45.00       
...
