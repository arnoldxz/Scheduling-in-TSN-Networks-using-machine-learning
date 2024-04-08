import os

class Provider(object):

    def __init__(self, filename="distr2.txt"):
        self._filename = filename
        self._distribution = None
        
    @property
    def filename(self):
        return self._filename
    
    @property
    def distribution(self):
        return self._distribution
    
    @distribution.setter
    def distribution(self, value):
        self._distribution = value

    @staticmethod
    def pop_distribution(file):
        lines = Provider.readlines(file)
        if lines is not None:
            line = lines.pop(0)
            Provider.writelines(file, lines)
            actual_lines = Provider.readlines(file)
            print("Provider -> Retrieved:{}".format(line))
            return Provider.processline(line)
        else:
            return []

    def provide(self):
        print("Providing from filename {}".format(self._filename))
        self._distribution = self.pop_distribution(self._filename)
        return self._distribution

    @staticmethod
    def readlines(file):
        try:
            if (os.stat(file).st_size == 0):
                print("Provider -> Empty File!")
                return None
            with open(file,'r') as f:
                lines = f.readlines()
                f.close()
            return lines
        except:
            print("Error reading lines")
            return None

    @staticmethod
    def writelines(DISTR_FILENAME, lines):
        with open(DISTR_FILENAME,'w') as f:
            f.writelines(lines)
            f.close()

    @staticmethod
    def processline(line):
        try:
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.replace(' ', '')
            if line != '':
                tup = list(map(int, line.split(',')))
            return tup
        except:
            print("Error processing line")
            return None
    

