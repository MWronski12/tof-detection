# Bicycle detection with multi-zone tof sensor

This repository contains all the resources for implementation of bicycle detection through object speed estimation for diploma thesis.


## ROADMAP:


- [x] TMF8828 Data Source
    - [x] Driver installation
    - [x] Reading sensor data
    - [x] Custom sensor configuration
    - [x] Serving data on a TCP port
    - [x] Saving data to CSV file


- [x] Data Aquisition
    - [x] Prepare test protocol
    - [x] Gather data
    - [x] Label data (Video/GPS)
        - [x] Proof of concept query gps data velocity by timestamp
        - [x] Proof of concept query video for velocity by timestamp
        - [x] Script that will repeatedly ask for a timestamp and display both gps and video velocity
        - [x] Prepare csv file with timestamp, gps_velocity, video_velocity
        - [x] Handle pedestrian data
        - [x] Handle random movement data


- [ ] Detection Algorithm
    - [ ] Describe collected data sets
    - [x] Create a batch data pipeline template for algorithm evaluation
        - [x] Load data
        - [x] Transform with distance selection strategy
        - [x] Apply partitioning function
        - [x] Apply merging function
            - [x] Use objects for estimated velocity motion representation
        - [x] Prepare set of training samples
    - [x] Adjust data pipeline to implement and evaluate detection algorithm
        - [x] Come up with a single metric that can be applied for testing detection
        - [x] Use algorithmic approach
            - [x] Detect series of at least 3, non-zero, strictly monotonic measurements
            - [x] Calculate average velocity in each series
            - [x] Merge neighbouring series and average velocity estimation
            - [x] Improve merging not to account unmatching direction series and too high variance series in motion velocity estimation
            - [x] Evaluate estimation
    - [x] Translate algorithm to real-time detection
        - [x] Write a pseudo code algorithm for live data partitioning
        - [x] Write a real algorithm
        - [x] Create a procedure for estimating velocity of a partitioned motion sample
            - [x] Use algorithmic to determine if velocity is above bicycle threshold
            - [x] Use linear regression for bicycle velocity estimation 


- [ ] Controller Architecture Improvements
    - [x] Make Collector independent (not a component)
    - [x] Remove Event and add methods in Component base class
    - [x] Improve buffer
        - [x] Rewind to next motion
        - [x] Use numpy/pandas
    - [x] Live strategy change in controller
    - [x] Drop double buffer in GUI, just emit refresh events for n_seconds of data
    - [x] Extract strategy for transform
        - [x] Add tranform possibility of aggregated transform like 'confidence --> bias --> EMA'
    - [x] Use numpy already in the data collector
    - [x] Add Detector component
        - [x] Consume each sample
        - [x] Or update all samples
        - [x] Dispatch bicycle detection event with estimated velocity
        - [x] Test in simulated live data environment
    - [ ] Add Signalizer component


- [ ] Final touches
    - [ ] Solve problem of gui triggering detector update all on refresh
    - [ ] Fix RT motion partitioner
    - [ ] Move tmf server C code to a separate folder


- [ ] Final Functional Tests
    - [ ] Test for behavior with multiple objects in the fov


- [ ] Thesis Documentation
    - [x] LaTex template
    - [ ] Conspect
    - [ ] Document
