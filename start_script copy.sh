
#start tmux session
echo Fuego running
/usr/bin/tmux new-session -d -s fuegosession
/usr/bin/tmux send-keys -t fuegosession "python /home/pi/otakiage/fire_audio.py" C-m
#tmux send-keys -t fuegosession "python /home/pi/ymca/ymca_loop.py >> /home/pi/rc_local_log.txt 2>&1 &" C-m


#other command that I want to run
#python /home/pi/ymca/ymca_loop.py >> /home/pi/rc_local_log.txt 2>&1 &


# Optionally, you can detach from the tmux session after starting it
#tmux detach -s mysession
