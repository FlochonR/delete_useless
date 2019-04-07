__author__ = 'flru'

class Storage:
    def __init__(self, source, size, pcent, target):
        self.__source = source #/dev/...
        self.__size = float(size[:-1]) #size in GB
        self.__pcent_usage = int(''.join(filter(lambda x: x.isdigit(), pcent))) #percent usage of the disk
        self.__directory = target #/, /tmp, /var

    #Setter
    def setSource(self, source):
        self.__source = source

    def setSize(self, size):
        self.__size = float(size[:-1])

    def setUsage(self, pcent):
        self.__pcent_usage = int(''.join(filter(lambda x: x.isdigit(), pcent)))

    def setDirectory(self, target):
        self.__directory = target

    #Getter
    def getSource(self):
        return self.__source

    def getSize(self):
        return self.__size

    def getUsage(self):
        return self.__pcent_usage

    def getDirectory(self):
        return self.__directory
