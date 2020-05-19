# sensorless-AO-interface
An interface to perform generic sensorless adaptive optics using Dynamic optics' 18 actuators adaptive lens by optimizing microscopy images directly from the acquisition computer's screen.

Pyqt4 is required, as well as pyDONEc (https://github.com/csi-dcsc/pyDONEc).

This Github repository is meant to accompany the paper "Plug-and-play adaptive optics for commercial laser scanning fluorescence microscopes based on an adaptive lens". This is the software used for the experimental measurements reported, and is provided to facilitate replication of the results and implementation of the methodology. However, since some parameters are inevitably tied to the calibration of the specific adaptive lens used, they are not provided here, as they would need to be separately derived for a different device. As such, the software will not work "out of the box".
Changing the whole structure of the file "mir_ctrl" could theoretically allow use with any adaptive device, but this was not tested.

Feel free to use and modify any part of the software according to your necessities. If substantial parts of this code are used for a scientific publication, please consider citing our work.
