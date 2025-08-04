#!/bin/bash

XVFB_PID=$(ps aux | grep '[X]vfb :99' | awk '{print $2}')

if [ -z "$XVFB_PID" ]; then
  echo "No Xvfb process found on display :99"
else
  kill $XVFB_PID
  echo "Xvfb process on display :99 stopped"
fi

Xvfb :99 -screen 0 1920x1080x16 &
XVFB_PID=$!

export DISPLAY=:99

python evaluate.py

kill $XVFB_PID
