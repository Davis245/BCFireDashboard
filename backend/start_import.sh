#!/bin/bash
# Script to run the full BC weather data import in the background
# This will import data from 2025 only (about 5-6 hours estimated)

cd /Users/davisfranklin/BCFireWeatherDashboard/backend

echo "======================================================================"
echo "BC Fire Weather Dashboard - Background Data Import"
echo "======================================================================"
echo "Start time: $(date)"
echo "Importing 2025 data for all 167 BC stations (~320 MB)"
echo "This process will run in the background and take 5-6 hours"
echo ""
echo "To monitor progress:"
echo "  tail -f import_log.txt"
echo ""
echo "To check if it's still running:"
echo "  ps aux | grep import_all_stations"
echo ""
echo "======================================================================"
echo ""

# Run the import in the background with logging
nohup .venv/bin/python manage.py import_all_stations \
    --skip-existing \
    > import_log.txt 2>&1 &

IMPORT_PID=$!

echo "Import started with PID: $IMPORT_PID"
echo "Log file: import_log.txt"
echo ""
echo "To stop the import:"
echo "  kill $IMPORT_PID"
echo ""
echo "======================================================================"
