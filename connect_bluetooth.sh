#!/bin/bash
export XDG_RUNTIME_DIR="/run/user/1000"
sleep 10
bluetoothctl << EOF
power on
pair 00:1B:B8:AE:05:4F
trust 00:1B:B8:AE:05:4F
connect 00:1B:B8:AE:05:4F
EOF
