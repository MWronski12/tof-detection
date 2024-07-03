# Bicycle detection with multi-zone tof sensor

This repository contains all the resources for implementation of bicycle detection through object speed estimation for diploma thesis.


## ROADMAP:


- [x] TMF8828 Data Source
    - [x] Driver installation
    - [x] Reading sensor data
    - [x] Custom sensor configuration
    - [x] Serving data on a TCP port
    - [x] Saving data to CSV file


- [ ] Data Aquisition
    - [x] Prepare test protocol
    - [x] Gather data
    - [x] Label data (Video/GPS)
        - [x] Proof of concept query gps data velocity by timestamp
        - [x] Proof of concept query video for velocity by timestamp
        - [x] Script that will repeatedly ask for a timestamp and display both gps and video velocity
        - [x] Prepare csv file with timestamp, gps_velocity, video_velocity
        - [ ] Handle pedestrian data
        - [ ] Handle random movement data

- [ ] Detection Algorithm
    - [ ] Describe collected data sets
    - [ ] Create a batch data pipeline template for algorithm evaluation
        - [x] Load data
        - [x] Transform with distance selection strategy
        - [x] Apply partitioning function
        - [ ] Apply merging function
        - [ ] Prepare set of training samples
    - [ ] Adjust data pipeline to implement and evaluate detection algorithm
        - [ ] Use algorithmic approach
            - [ ] Detect series of at least 3, non-zero, strictly monotonic measurements
            - [ ] Calculate average velocity in each series
            - [ ] Merge neighbouring series and average velocity estimation
            - [ ] Evaluate estimation
    - [ ] Translate algorithm to real-time detection


- [ ] Controller Architecture Improvements
    - [x] Make Collector independent (not a component)
    - [x] Remove Event and add methods in Component base class
    - [ ] Improve buffer
        - [x] Rewind to next motion
        - [x] Use numpy/pandas
        - [ ] Rewind per frame or per n_seconds
        - [ ] Get last n_seconds of data
    - [x] Live strategy change in controller
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


- [ ] Final Functional Tests


- [ ] Thesis Documentation
    - [x] LaTex template
    - [ ] Conspect
    - [ ] Document
