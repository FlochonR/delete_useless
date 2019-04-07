import fabric
import keyring as keyring

__author__ = 'flru'


from fabric import Connection
from datetime import date
from dateutil.relativedelta import relativedelta
from Storage import Storage
from Extend import Extend

class Trash:
    def __init__(self, argHost, argPort, argUser, argPwd):
        self.__ssh_client = self.__connect_ssh(argHost, argPort, argUser, argPwd)
        self.__user = argUser
        self.__password = argPwd

    #Connect to VM
    def __connect_ssh(self, argHost, argPort, argUser, argPwd):
        ssh = Connection(argHost, argUser, argPort, connect_kwargs={"password": argPwd})

        keyring.set_password(argHost, argUser, argPwd)
        ssh.config.sudo.password = keyring.get_password(argHost, argUser)

        return ssh

    #Close connection to VM
    def close_ssh(self, ssh = None):
        if ssh is None:
            self.__ssh_client.close()
        else:
            ssh.close()


    #Public functions

    #Zip files
    def zip_file(self, directory):
        list_file = self.__get_file_logs_recent(directory)

        for file in list_file:
            self.__ssh_client.sudo("gzip " + file)

    #Delete files
    def delete_file(self, directory):
        list_file = self.__get_file_logs_old(directory)
        list_file += self.__get_file_zip(directory)

        for file in list_file:
            self.__ssh_client.sudo("rm -rf " + file)

        self.__restart_wildfly()

    # List the storages(ext) mounted on the VM
    def get_information_storage(self):
        output = self.__ssh_client.sudo("df -lhT --block-size G | grep \"ext\"") #df -hl --output=source,fstype,pcent,target | grep \"ext\"
        list_storage = self.__parse_storage(output.stdout)
        return list_storage

    def do_extend(self, vm_manager, port_vm_manager, vm_to_check, storage):
        extend = Extend()

        #Connect to Teleferic and get the right file for VM's information
        ssh_manager: Connection = self.__connect_ssh(vm_manager, port_vm_manager, self.__user, self.__password)
        get_file = extend.repatriate_xenlist(ssh_manager)
        self.close_ssh(ssh_manager)

        if get_file:
            #Load and treat the informations
            load = extend.load_information_xenlist(vm_to_check, storage.getDirectory())

            if load:
                #Extend
                ssh_extend = self.__connect_ssh(extend.getHypervisor(), port_vm_manager, self.__user, self.__password)
                extend = extend.extend(ssh_extend, storage)
                ssh_extend.close()

                if extend:
                    self.__ssh_client.sudo("resize2fs " + storage.getSource())
                    extend_status = 0
                else:
                    extend_status = 1
            else:
                extend_status = 2
        else:
            extend_status = 3

        return extend_status


    #Private functions

    # Get list of logs files to zip (more 1 day)
    def __get_file_logs_recent(self, directory):
        list_file = []
        if directory == "var" or directory == "":
            output_var1 = self.__ssh_client.sudo("find /var/log -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(days=-1))))
            output_var2 = self.__ssh_client.sudo("find /var/local -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(days=-1))))
            list_file_var1 = self.__parser(output_var1.stdout)
            list_file_var2 = self.__parser(output_var2.stdout)
            list_file += list_file_var1 + list_file_var2
        elif directory == "":
            output_root1 = self.__ssh_client.sudo("find /usr -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(days=-1))))
            output_root2 = self.__ssh_client.sudo("find /home -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(days=-1))))
            list_file_root1 = self.__parser(output_root1.stdout)
            list_file_root2 = self.__parser(output_root2.stdout)
            list_file += list_file_root1 + list_file_root2

        return list_file

    # Get list of logs files to delete (more 1 month)
    def __get_file_logs_old(self, directory):
        list_file = []
        if directory == "var" or directory == "":
            output_var1 = self.__ssh_client.sudo("find /var/log -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            output_var2 = self.__ssh_client.sudo("find /var/local -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            output_var3 = self.__ssh_client.sudo("find /var/tmp -mindepth 1 -maxdepth 1 ! -newermt " + str((date.today() + relativedelta(days=-1))))
            list_file_var1 = self.__parser(output_var1.stdout)
            list_file_var2 = self.__parser(output_var2.stdout)
            list_file_var3 = self.__parser(output_var3.stdout)
            list_file += list_file_var1 + list_file_var2 + list_file_var3
        elif directory == "tmp":
            output_tmp1 = self.__ssh_client.sudo("find /tmp -mindepth 1 -maxdepth 1 ! -newermt " + str((date.today() + relativedelta(days=-1))))
            list_file_tmp1 = self.__parser(output_tmp1.stdout)
            list_file += list_file_tmp1
        elif directory == "":
            output_root1 = self.__ssh_client.sudo("find /usr -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            output_root2 = self.__ssh_client.sudo("find /home -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            list_file_root1 = self.__parser(output_root1.stdout)
            list_file_root2 = self.__parser(output_root2.stdout)
            list_file += list_file_root1 + list_file_root2

        return list_file

    # Get list of zip log files to delete
    def __get_file_zip(self, directory):
        list_file = []
        if directory == "var" or directory == "":
            output_var1 = self.__ssh_client.sudo("find /var/log -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?\.(zip|tar.gz|gz)$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            output_var2 = self.__ssh_client.sudo("find /var/local -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?\.(zip|tar.gz|gz)$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            list_file_var1 = self.__parser(output_var1.stdout)
            list_file_var2 = self.__parser(output_var2.stdout)
            list_file += list_file_var1 + list_file_var2
        elif directory == "":
            output_root1 = self.__ssh_client.sudo("find /usr -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?\.(zip|tar.gz|gz)$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            output_root2 = self.__ssh_client.sudo("find /home -type f -regextype egrep -regex '^.*\.log(\.[0-9]*)?\.(zip|tar.gz|gz)$' ! -newermt " + str((date.today() + relativedelta(months=-1))))
            list_file_root1 = self.__parser(output_root1.stdout)
            list_file_root2 = self.__parser(output_root2.stdout)
            list_file += list_file_root1 + list_file_root2

        return list_file

    #Check if a wildfly turn and restart it
    def __restart_wildfly(self):
        output_old = self.__ssh_client.sudo("[ -f /etc/init.d/wildfly ] && echo \"0\" || echo \"1\"")
        output_new = self.__ssh_client.sudo("[ -f /lib/systemd/system/wildfly.service ] && echo \"0\" || echo \"1\"")
        if output_old.stdout == "0":
            self.__ssh_client.sudo("/etc/init.d/wildfly restart")
            print("restart old")
        elif output_new.stdout == "0":
            self.__ssh_client.sudo("systemctl restart wildfly")
            print("restart new")

    #Parse informations files
    def __parser(self, output):
        list_element = output.split("\n")
        del list_element[len(list_element) - 1]
        return list_element

    #Parse insformations storages
    def __parse_storage(self, output):
        list_element = output.split("\n")
        del list_element[len(list_element) - 1]

        list_storage = []
        for element in list_element:
            list_storage.append(element.split())

        list_final = []
        for element in list_storage:
            list_final.append(Storage(element[0], element[2], element[5], element[6]))

        return list_final
