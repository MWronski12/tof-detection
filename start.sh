sudo ./preset.sh
sudo cat ./input > /dev/null &
echo "Input proc id: $!"
sudo ./app &
echo "App proc id: $!"
watch -n 0.1 cat view
