#!/bin/bash

# The package name of your Flet application
APP_PACKAGE="com.mycompany.my_comfy"

echo "Searching for PID of $APP_PACKAGE..."

# Use pidof to get the PID of the running application
PID=$(adb shell pidof "$APP_PACKAGE")

# Check if a PID was found
if [ -z "$PID" ]; then
    echo "Application $APP_PACKAGE is not running or could not be found."
    exit 1
fi

echo "Found PID: $PID"
echo "Starting logcat for PID $PID..."
echo "Press Ctrl+C to exit."

# Start adb logcat with the found PID
adb logcat --pid="$PID"
