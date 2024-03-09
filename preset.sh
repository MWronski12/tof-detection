echo -n "Powering on the sensor: "
echo 1 | sudo tee sysfs/chip_enable
echo -n "mode_8x8: "
echo 0 | sudo tee sysfs/app/mode_8x8
echo -n "spad_map_id: "
echo 1 | sudo tee sysfs/app/spad_map_id
echo -n "iterations: "
echo 4000000 | sudo tee sysfs/app/iterations
echo -n "report_perios_ms: "
echo 1 | sudo tee sysfs/app/report_period_ms
sudo cat sysfs/app/factory_calibration > calib.bin
