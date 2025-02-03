#called from /etc/rc.local

#start tmux session
#echo RFID session
echo test Hue session
# /usr/bin/tmux new-session -d -s rfidsession
# /usr/bin/tmux send-keys -t rfidsession "python /home/pi/otakiage/osc_control_rfid_spi.py" C-m

#start tmux session as user pi, to see if this initiates bluetooth audio
#sudo -u pi env XDG_RUNTIME_DIR=/run/user/1000 tmux new-session -d -s rfidsession

# Wait to ensure PulseAudio and necessary directories are ready

# 241231 CURRENTY JUST STARTING THE SESSION AND DOING NOTHING
#sleep 40
#sudo -u pi env XDG_RUNTIME_DIR=/run/user/1000 tmux send-keys -t rfidsession "python /home/pi/otakiage/osc_control_rfid_spi.py" C-m

/usr/bin/tmux new-session -d -s huesession
tmux send-keys -t huesession "python /home/pi/otakiage/hue_test2.py" C-m

#to access session from terminal> tmux attach -t rfidsession


#tmux send-keys -t fuegosession "python /home/pi/ymca/ymca_loop.py >> /home/pi/rc_local_log.txt 2>&1 &" C-m


#other command that I want to run
#python /home/pi/ymca/ymca_loop.py >> /home/pi/rc_local_log.txt 2>&1 &


# Optionally, you can detach from the tmux session after starting it
#tmux detach -s mysession
