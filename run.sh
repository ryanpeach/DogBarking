#!/usr/bin/env bash

# This script is used to run the dogbarking module
# It will restart the module if it crashes
# It will also pass any command line arguments to the module

while true; do
    /usr/bin/env python3 -m dogbarking $@
    rc=$?
    if [ $rc -eq 0 ]; then
        exit 0
    else
        echo "Restarting. Press Ctrl+C (again) to exit"
        sleep 1
    fi
done
