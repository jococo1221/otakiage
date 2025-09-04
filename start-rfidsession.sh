sudo systemctl stop osc_control.service
/usr/bin/tmux new-session -d -s rfidsession
/usr/bin/tmux send-keys -t rfidsession "python /home/pi/otakiage/osc_control_rfid_spi.py" C-m
tmux attach -t rfidsession
