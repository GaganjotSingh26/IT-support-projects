# 🖥️ IT System Monitoring Dashboard

Real-time terminal monitor for CPU, memory, disk and network.
Logs alerts when thresholds are exceeded and generates HTML reports.

## Features
- Live terminal dashboard refreshing every 5 seconds
- Configurable alert thresholds (CPU, RAM, Disk)
- Alert logging to CSV file
- HTML daily report auto-generated on exit

## Run
pip install psutil
python monitor.py

## Tech
Python 3.8+ · psutil

## Background
Built to demonstrate system monitoring skills developed while administering
IT infrastructure for a logistics platform processing 100-500 weekly shipments.
