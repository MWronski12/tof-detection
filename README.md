# Bicycle detection with multi-zone tof sensor

This repository contains all the resources for implementation of bicycle detection through object speed estimation for diploma thesis.


## ROADMAP:


- [x] TMF8828
    - [x] Driver installation
    - [x] Reading sensor data
    - [x] Custom sensor configuration
    - [x] Serving data on a TCP port
    - [x] Saving data to CSV file


- [ ] Data aquisition
    - [x] Prepare test protocol
    - [x] Gather data
    - [ ] Label data (Video/GPS)
        - [x] Proof of concept query gps data velocity by timestamp
        - [x] Proof of concept query video for velocity by timestamp
        - [x] Script that will repeatedly ask for a timestamp and display both gps and video velocity
        - [ ] Prepare csv file with timestamp, gps_velocity, video_velocity


- [ ] Detection algorithm
    - [ ] Implement simple averaged, scaled derrivative
        - [ ] Account for different distances from the sensor
        - [ ] Account for interferences
    - [ ] Implement ML algorithms
        - [ ] Extract features from samples
        - [ ] Start with linear regression
        - [ ] Algorithms comparrison


- [ ] Controller architecture improvements
    - [x] Make Collector independent (not a component)
    - [x] Remove Event and add methods in Component base class
    - [ ] Improve buffer
        - [ ] Rewind to next motion
        - [x] Use numpy/pandas
        - [ ] Rewind per frame or per n_seconds
        - [ ] Get last n_seconds of data
    - [ ] Live strategy change in controller
    - [x] Drop double buffer in GUI, just emit refresh events for n_seconds of data
    - [x] Extract strategy for transform
        - [x] Add tranform possibility of aggregated transform like 'confidence --> bias --> EMA'
    - [x] Use numpy already in the data collector
    - [ ] Add SpeedEstimator component
        - [ ] Consume each sample
        - [ ] Or update all samples
        - [ ] Communicate result to GUI for display
    - [ ] Add Signalizer component
    - [ ] Unit tests


- [ ] Final functional tests


- [ ] Thesis documentation
    - [x] LaTex template
    - [ ] Conspect
    - [ ] Document
