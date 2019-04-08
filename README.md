# delete_useless

This script deletes old log files, zips the others and extends the disk if there isn't space on the VM.

# Launch
delete_useless.py -H 10.10.10.10 -u toto -p totototo

# Improvements
1. Read config files to get data that is hardcoded at the moment (ex: VM manager, directory to xenlist)
2. Remove the output of commands ("debug" mode ON at the moment)
