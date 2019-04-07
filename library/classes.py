__author__ = 'deri'

class Xen():
    def __init__(self):
        self.name = ""
        self.ip = ""
        self.run_vms = []
        self.memory = 0
        self.free_memory = 0
        self.release = ""

    def add_vm(self, vm):
        self.run_vms.append(vm)

class Vm():
    def __init__(self):
        self.domid = ""
        self.name = ""
        self.ram = ""
        self.vcpu = ""
        self.disks = []
        self.ip = ""
        self.mac = ""
        self.vncdisplay = ""

    def add_disk(self, lv):
        self.disks.append(lv)

    def __repr__(self):
        return "\t%s (Vcpu: %s, Memory: %s, ip: %s, mac: %s, vnc: %s)" % (self.name, self.vcpu, self.ram, self.ip,
                                                                          self.mac, self.vncdisplay)

class Vg():
    def __init__(self):
        self.name = ""
        self.size = ""
        self.free = ""

class Lv():
    def __init__(self):
        self.name = ""
        self.size = ""
        self.free = ""
        self.path = ""
    def __repr__(self):
        return "\t\tDisk : %s" % (self.path)

class ListCfg(object):
    """List of Xen servers ,vm configuration,lv  and Vm to backup (loaded from .ini file)"""
    def __init__(self):
        self.xen_srvs = []

    def add_xen_srv(self, xensrv):
        self.xen_srvs.append(xensrv)

    def get(self):
        return self.xen_srvs
