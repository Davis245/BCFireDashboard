#!/bin/bash
# Setup script to configure hourly weather data updates via cron

SCRIPT_DIR="/Users/davisfranklin/BCFireWeatherDashboard/backend"
PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python"
MANAGE_PY="$SCRIPT_DIR/manage.py"
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Create the cron job command
CRON_COMMAND="0 * * * * cd $SCRIPT_DIR && $PYTHON_PATH $MANAGE_PY update_weather_data >> $LOG_DIR/update_weather.log 2>&1"

echo "======================================================================"
echo "BC Fire Weather Dashboard - Hourly Update Setup"
echo "======================================================================"
echo ""
echo "This will set up a cron job to update weather data every hour."
echo ""
echo "Cron command that will be added:"
echo "$CRON_COMMAND"
echo ""
echo "This means:"
echo "  - Runs at minute 0 of every hour (1:00, 2:00, 3:00, etc.)"
echo "  - Updates all active weather stations"
echo "  - Logs output to: $LOG_DIR/update_weather.log"
echo ""
echo "======================================================================"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "update_weather_data"; then
    echo "⚠️  Cron job already exists!"
    echo ""
    echo "Current crontab:"
    crontab -l | grep "update_weather_data"
    echo ""
    read -p "Do you want to replace it? (yes/no): " REPLACE
    
    if [ "$REPLACE" != "yes" ]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    # Remove existing cron job
    crontab -l | grep -v "update_weather_data" | crontab -
    echo "Removed existing cron job."
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo ""
echo "✓ Cron job added successfully!"
echo ""
echo "To verify:"
echo "  crontab -l"
echo ""
echo "To view update logs:"
echo "  tail -f $LOG_DIR/update_weather.log"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (then delete the line containing 'update_weather_data')"
echo ""
echo "======================================================================"
