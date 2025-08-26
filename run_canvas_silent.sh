#!/bin/bash
# Set Canvas environment variables
export CANVAS_BASE_URL="YOUR_INSTITUTION'S_URL"
export CANVAS_TOKEN="CANVAS_ACCESS_TOKEN"

# Make sure 'requests' is installed
pip install requests

# Run Python script silently
python3 ~/Desktop/canvas_to_ics_silent.py --all-day --future-only
