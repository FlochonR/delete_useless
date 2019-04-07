__author__ = 'flru'


from fabric import Transfer
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
from library.classes import *

class Extend:
    def __init__(self):
        self.__day_to_use = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 8, 00)
        self.__hypervisor = ""
        self.__disk = ""
        self.__datastore = ""

    #Getter
    def getHypervisor(self):
        return self.__hypervisor

    #Public

    #Extend of the disk on the hypervisor
    def extend(self, ssh_extend, store):
        output = ssh_extend.sudo("vgs -o vg_name,vg_free --units g | grep " + self.__datastore)

        size_free = self.__parser_size_datastore(output.stdout)

        if store.getSize() >= 1000:
            size_to_add = 100
        else:
            size_to_add = (store.getSize() * (10/100))

        if size_free > size_to_add:
            ssh_extend.sudo("lvresize -L +" + str(size_to_add) + "G " + self.__disk)
            extend_status = True
        else:
            extend_status = False

        return extend_status

    #Read xenlist file
    def load_information_xenlist(self, vm_to_check, directory_to_check):
        directory = self.__parser_directory_xen(directory_to_check)

        xen: ListCfg = pickle.load(open("/var/tmp/save_" + str(self.__day_to_use.year) + "-" + str(self.__day_to_use.month) + "-" + str(self.__day_to_use.day) + "_" + str(self.__day_to_use.hour) + ".pkl", "rb"))

        load = False
        for hyp in xen.xen_srvs:
            for vm in hyp.run_vms:
                if vm.name == vm_to_check:
                    for disk in vm.disks:
                        if directory in disk.path:
                            self.__hypervisor = hyp.name
                            self.__disk = self.__parser_disk(disk.path)
                            self.__datastore = self.__parser_datastore(self.__disk)
                            load = True
                            break
                    break
            if load:
                break

        return load

    #Get the current file xenlist
    def repatriate_xenlist(self, ssh_manager):
        get_file = True

        #Get the date of the last file
        self.__define_date_file_xenlist()

        #Transfert of the file
        try:
            transfert = Transfer(ssh_manager)

            ssh_manager.sudo("cp /xenmanager/pklsavefiles/save_" + str(self.__day_to_use.year) + "-" + str(self.__day_to_use.month) + "-" + str(self.__day_to_use.day) + "_" + str(self.__day_to_use.hour) + ".pkl /var/tmp/")
            ssh_manager.sudo("chmod 755 /var/tmp/save_" + str(self.__day_to_use.year) + "-" + str(self.__day_to_use.month) + "-" + str(self.__day_to_use.day) + "_" + str(self.__day_to_use.hour) + ".pkl")
            transfert.get("/var/tmp/save_" + str(self.__day_to_use.year) + "-" + str(self.__day_to_use.month) + "-" + str(self.__day_to_use.day) + "_" + str(self.__day_to_use.hour) + ".pkl", "/var/tmp/save_" + str(self.__day_to_use.year) + "-" + str(self.__day_to_use.month) + "-" + str(self.__day_to_use.day) + "_" + str(self.__day_to_use.hour) + ".pkl")
            ssh_manager.sudo("rm /var/tmp/save_" + str(self.__day_to_use.year) + "-" + str(self.__day_to_use.month) + "-" + str(self.__day_to_use.day) + "_" + str(self.__day_to_use.hour) + ".pkl")
        except ValueError:
            get_file = False

        return get_file


    #Private

    # Define the date to use to choose file
    def __define_date_file_xenlist(self):
        day_midnight = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 00, 00)
        day_morning = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 8, 00)
        day_evening = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 16, 00)
        day_before_evening = day_evening + relativedelta(days=-1)

        if day_morning < datetime.now() < day_evening:
            self.__day_to_use = day_morning
        elif day_midnight < datetime.now() < day_morning:
            self.__day_to_use = day_before_evening
        else:
            self.__day_to_use = day_evening

    #Parser
    def __parser_directory_xen(self, directory):
        dir = directory.replace("/", "")

        if dir == "":
            dir = "root"

        return dir

    def __parser_disk(self, directory):
        dir = directory.split(":")
        return dir[1]

    def __parser_datastore(self, directory):
        dir = directory.split("/")
        return dir[2]

    def __parser_size_datastore(self, output):
        temp = output.replace("\n", "")

        i = 0
        size = ""
        while temp[len(temp) - i - 1] != " ":
            size += (temp[len(temp) - i - 1])
            i += 1

        size = size[::-1]
        size = float(size[:-1])

        return size