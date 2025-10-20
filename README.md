make a standard file with noise data.

**required fields**
isodatetime timestamp, 
laeq1s, 
markers (value is nan or 1) - exclude marker is mandatory. 

**optional fields**
spectral data: lzeq25hz -> lzeq20000hz,
soundpath, 
statistics per second laf 1, 5, 10, 50, ...



example
isodatetime	laeq1s	exclude	hockey	pauze	resid	Sound	soundpath	laf1	laf5	laf10	laf50	laf90	laf95	laf99	lafmin	lafmax	lzeq25hz	lzeq31.5hz	lzeq40hz	lzeq50hz	lzeq63hz	lzeq80hz	lzeq100hz	lzeq125hz	lzeq160hz	lzeq200hz	lzeq250hz	lzeq315hz	lzeq400hz	lzeq500hz	lzeq630hz	lzeq800hz	lzeq1khz	lzeq1.25khz	lzeq1.6khz	lzeq2khz	lzeq2.5khz	lzeq3.15khz	lzeq4khz	lzeq5khz	lzeq6.3khz	lzeq8khz	lzeq10khz	lzeq12.5khz	lzeq16khz	lzeq20khz
2024-05-20 20:04:42	43.01					1.0	SR0.wav									44.68	38.69	39.49	37.5	34.77	35.24	35.36	36.03	33.7	35.81	32.4	27.09	33.06	36.1	35.08	30.75	29.67	30.31	30.32	32.75	32.92	28.82	29.12	29.59	30.77	30.34	30.04	29.85	29.54	28.09	24.07
