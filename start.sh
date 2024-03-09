sudo ./preset.sh
sudo cat ./input > /dev/null &
sudo ./app &
watch -n 0.1 cat view
