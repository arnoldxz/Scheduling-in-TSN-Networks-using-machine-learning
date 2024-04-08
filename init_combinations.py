# from Solutions_Visualizer import DISTR_FILENAME, N_STREAMS
import itertools, os
from distribution_provider import Provider as dp
from config_provider import ConfigService

configService = ConfigService()
config = configService.config

N_STREAMS = configService.networkConfig["n_streams"]
DISTR_FILENAME = config["distributions"]
FILENAME =  config["results_filename"]
BASE_PATH = config["base_path"]
RESULTS_PATH = f"{BASE_PATH}\\{N_STREAMS}\\{FILENAME}"


def initDistribution(n):
    combs = itertools.combinations_with_replacement(list(range(0, n+1)), 3)
    correct_combs =list(filter(lambda x: (sum(x)==n), combs))
    perms = [ list(set(itertools.permutations(list(i)))) for i in correct_combs ]
    flat_perms = [dist for sublist in perms for dist in sublist]
    
    types = []
    for i in flat_perms:
        audio = i[0] * [1]
        video = i[1] * [2]
        control = i[2] * [3]
        types.append(list(itertools.chain(audio, video, control)))
        
    return types

def uniques(self):
    u = []
    for i in self:
        if i not in u:
            u.append(i)
    return u

def writeDistr(l):
    with open(DISTR_FILENAME, 'w') as f:
        for i in l:
            f.write(str(i) + '\n')
        f.close()

def readDistr():
    if (os.stat(DISTR_FILENAME).st_size == 0):
        print(" Empty file!!")
    with open(DISTR_FILENAME, 'r') as f:
        read = f.read()
        f.close()
    flow_types = []
    for line in read.split('\n'):
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.replace(' ', '')
        if line != '':
            tup = list(map(int, line.split(',')))
        flow_types.append(tup)
    return flow_types

def Repeated_elements(x):
    return len(set(x)) == 1

if __name__ == '__main__':
    print("INIT Distribution", N_STREAMS)
    l = initDistribution(N_STREAMS)
    l = uniques(l)
    # l = [e for e in l if not Repeated_elements(e)]
    writeDistr(l)