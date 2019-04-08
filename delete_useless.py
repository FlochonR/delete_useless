#!/usr/bin/env python
"""Usage:
    delete_useless.py -H <argument> -u <argument> -p <argument> [-P <argument>] [-d <argument>]
    delete_useless.py -h

Options:
    -h                                              Show this screen.
    -H, --hostname=ADDRESS                          Host
    -u, --user=STRING                               User
    -p, --password=STRING                           Password
    -P, --port=INT                                  Port
    -d, --directory=STRING                          Directory

Example:
    delete_useless.py -H 10.22.130.122 -u toto -p totototo
"""

__author__ = 'flru'


from Trash import Trash
from NagiosHelper import NagiosHelper
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments["--hostname"]:
        argHost = arguments["--hostname"]
    if arguments["--user"]:
        argUser = arguments["--user"]
    if arguments["--password"]:
        argPwd = arguments["--password"]
    if arguments["--port"]:
        argPort = int(arguments["--port"])
    else:
        argPort = 22
    if arguments["--directory"]:
        argDirectory = arguments["--directory"]
        if argDirectory == "root":
            argDirectory = ""
    else:
        argDirectory = ""

    # nagios = NagiosHelper()

    if argDirectory != "" and argDirectory != "var" and argDirectory != "tmp":
        print("WARNING - For " + argDirectory + " check manually")
    elif "exx" in argHost or argHost == "prd210":
        print("CRITICAL - VM Exxoss, AWS or savebox, check it manually")
    else:
        #Connect to VM
        try:
            trash = Trash(argHost, argPort, argUser, argPwd)
            connection = True
        except ValueError:
            connection = False

        if connection == True:
            #Delete or zip files needed
            trash.delete_file(argDirectory)
            trash.zip_file(argDirectory)

            #Space on VM
            storage = trash.get_information_storage()

            #Extend
            message = ""
            extend_status = False
            for element in storage:
                if element.getUsage() >= 80:
                    if element.getDirectory() == "/tmp" or element.getDirectory() == "/var" or element.getDirectory() == "/":
                        print("INFO - An extend is running on " + element.getDirectory() + ", this action can take time...")
                        extend_status = trash.do_extend("teleferic", 22, argHost, element)

                        if extend_status == 0:
                            message += "Extend done on " + element.getSource() + " for " + element.getDirectory() + "\n"
                        elif extend_status == 1:
                            message += "Extend not done on " + element.getSource() + " for " + element.getDirectory() + " because no more space in the datastore\n"
                        elif extend_status == 2:
                            message += "Extend not done on " + element.getSource() + " for " + element.getDirectory() + " because the VM isn't found in the xenlist\n"
                        elif extend_status == 3:
                            message += "Extend not done on " + element.getSource() + " for " + element.getDirectory() + " because impossible to connect to the VM manager or the repatriate of xenlist file failed\n"
                        else:
                            message += "Extend not done on " + element.getSource() + " for " + element.getDirectory() + "(No more information)\n"
                    else:
                        print("WARNING - For " + element.getDirectory() + " check manually")
                else:
                    message += "All is ok on " + element.getSource() + " for " + element.getDirectory() + "\n"

            if extend_status == 0:
                print("INFO - " + message)
            elif extend_status == 1:
                print("WARNING - " + message)
            else:
                print("CRITICAL - " + message)

            #Disconnect to VM
            trash.close_ssh()
        else:
            print("CRITICAL - Error connection to the VM")

    #print(nagios.getMessage())
    #exit(nagios.code)