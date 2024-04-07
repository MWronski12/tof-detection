#!/usr/bin/bash

ITERATION=550000
SPAD_MAP_ID=1
REPORT_PERIOD_MS=1

echo -n "Powering on the sensor: "
echo 1 | sudo tee sysfs/chip_enable
echo -n "mode_8x8: "
echo 0 | sudo tee sysfs/app/mode_8x8
echo -n "spad_map_id: "
echo $SPAD_MAP_ID | sudo tee sysfs/app/spad_map_id
echo -n "iterations: "
echo $ITERATION | sudo tee sysfs/app/iterations
echo -n "report_perios_ms: "
echo $REPORT_PERIOD_MS | sudo tee sysfs/app/report_period_ms
sudo cat sysfs/app/factory_calibration > calib.bin
