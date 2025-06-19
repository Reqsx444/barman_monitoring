# Automated Barman Backup Report Script Description
## Introduction
This script generates an automated report on the status of Barman backups, checks for errors, attempts repairs, and emails the report. The script is designed to run on a daily basis and is ideal for inclusion in a cron job to ensure regular and automated monitoring of backup configurations.

## Features
Date Formatting: Converts the current date to a specific format (YYYYMMDD) for file naming. \
Report Initialization: Creates and initializes a report file with HTML formatting. \
Configuration Handling: Lists available Barman configurations, excluding templates. \
Backup Status Check: Verifies the status of each backup configuration and attempts to repair any failed configurations. \
Backup File Verification: Checks the validity of backup files created on the current day. \
Log Cleanup: Cleans up the report file by removing unnecessary entries and formatting the results. \
HTML Report Generation: Converts the report file into an HTML format. \
Email Notification: Emails the HTML report to a specified address. \
Archiving and Cleanup: Archives the HTML report and deletes the original text report.

## Usage
### Prerequisites:
- Python 3
- Libraries: os, sys, datetime, shutil, subprocess, airium
- Barman

## Example Usage
To run the script, simply execute it with Python 3. For automated daily execution, it is recommended to add this script to your crontab.
```
python barman_backup_report.py
```
## Adding to Crontab
To ensure the script runs daily, add the following line to your crontab file:
```
0 2 * * * /usr/bin/python3 /path/to/barman_backup_report.py
```
