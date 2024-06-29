# Bicycle detection with multi-zone tof sensor

This repository contains all the resources for implementation of bicycle detection through object speed estimation for diploma thesis.


## ROADMAP:


- [ ] Data aquisition
    - [x] Prepare test protocol (test branch has some start, should we gather some interfered samples!?)
    - [x] Gather data
    - [ ] Label data (Video/GPS)
        - [x] Proof of concept query gps data velocity by timestamp
        - [x] Proof of concept query video for velocity by timestamp
        - [x] Script that will repeatedly ask for a timestamp and display both gps and video velocity


- [ ] Detection algorithm
    - [ ] Implement simple averaged, scaled derrivative
    - [ ] Account for different distances from the sensor
    - [ ] Account for interferences


- [ ] Controller architecture improvements
    - [ ] Make Collector independent (not a component)

    - [ ] Improve buffer
        - [ ] Rewind to next 
        - [ ] Use numpy/pandas
        - [ ] Rewind per frame or per n_seconds
        - [ ] Get last n_seconds of data

    - [ ] Remove Event and add methods in Component base class
    - [ ] Drop double buffer in GUI, just emit refresh events for n_seconds of data

    - [ ] Extract strategy for transform
        - [ ] Add tranform possibility of aggregated transform like 'confidence --> bias --> EMA'

    - [ ] Add SpeedEstimator component
        - [ ] Consume each sample
        - [ ] Or update all samples
        - [ ] Communicate result to GUI for display

    - [ ] Add Signalizer component


- [ ] Final tests


- [ ] Thesis documentation
    - [x] LaTex template
    - [ ] Conspect
    - [ ] Document
