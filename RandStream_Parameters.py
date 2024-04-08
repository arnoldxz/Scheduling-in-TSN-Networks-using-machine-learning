## This set of functions is for the random statement of the parameters of the network
import random
from math import gcd
import numpy as np

from RanNet_Generator import Random_Network_Generator
from Djikstra_Path_Calculator import *

"""
Fortunately the only input is the number of streams in the network
# Number of streams

"""


########## PARAMETERS ##########
# Stream_size (Provided - Randomized)
# Streams_Period (Provided - Randomized)
# Streams_Period_list (generated)
# Hiperperiod (generated)
# Frames_per_Stream (generated) 
# Max_frames, (generated)
# Num_of_Frames (generated)
# Deathline_Stream (Provided - Randomized)

# def Random_Stream_size_and_period_generator(Number_of_Streams): 
#     # In the Luxembourg paper the proportions of the code is as follows:
#     #15% Audio streams 
#         #• 128 or 256 byte frames • periods: one frame each 1.25ms • deadline constraints either 5 or 10ms
#     #16% Video Streams
#         # 
#     #69% Control Streams
#     # Stream sizes are in bytes
#     # Stream periods are in nano seconds
# #    type_selector = random.choices([1,2,3],weights=(16,15,69), k= Number_of_Streams)
# #    type_selector = random.choices([1,2,3],weights=(33,33,34), k= Number_of_Streams)
#     type_selector = [1,2,3]
#     print ("type_selector",type_selector)
#     Streams_size = []
#     Streams_Period = {}
#     Streams_Period_list = [(v[0]) for k, v in Streams_Period.items()]
#     Deathline_Stream = {}
#     for i in range(len(type_selector)) :
#         if type_selector[i] == 1: # Audio
#             Streams_size.append(3*100)
#             Streams_Period[(i)] = 600
#             Deathline_Stream[(i)] = 400
#         if type_selector[i] == 2: # Video
#             Streams_size.append(100)
#             Streams_Period[(i)] = 300
#             Deathline_Stream[(i)] = 1200
#         if type_selector[i] == 3: # Control
#             Streams_size.append(100)
#             Streams_Period[(i)] = 600
#             Deathline_Stream[(i)] = 1200
#         print(type_selector[i],Streams_Period[(i)])
#     Streams_Period_list = [v for k,v in Streams_Period.items()]
    
#     return Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams

def to_time_units(size, bandwidth):
        return int(((size * 8) / bandwidth) * 1000) # miliseconds

def Random_Stream_size_and_period_generator(Number_of_Streams, type_selector, configService): 
    # In the Luxembourg paper the proportions of the code is as follows:
    #15% Audio streams 
        #• 128 or 256 byte frames • periods: one frame each 1.25ms • deadline constraints either 5 or 10ms
    #16% Video Streams
        # 
    #69% Control Streams
    # Stream sizes are in bytes
    # Stream periods are in nano seconds
    # 16,15,69
    # type_selector = random.choices([1,2,3],weights=(33,33,34), k= Number_of_Streams)
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', flow_type)
    # input()
    streamsConfig = configService.streamsConfig

    Streams_size = []
    Streams_Period = {}
    Streams_Period_list = [(v[0]) for k, v in Streams_Period.items()]
    Deathline_Stream = {}
    
    audio = 0
    video = 0
    control = 0
    bw = configService.networkConfig["Bandwidth"]
    for i in range(len(type_selector)) :

        if type_selector[i] == 1: # Audio
            Streams_size.append(to_time_units(streamsConfig[0]["Size"], bw))
            Streams_Period[(i)] = streamsConfig[0]["Period"]
            Deathline_Stream[(i)] = streamsConfig[0]["Deadline"]
            audio= audio +1
            
        if type_selector[i] == 2: # Video
            Streams_size.append(to_time_units(streamsConfig[1]["Size"], bw))
            Streams_Period[(i)] = streamsConfig[1]["Period"]
            Deathline_Stream[(i)] = streamsConfig[1]["Deadline"]
            video=video +1
            
        if type_selector[i] == 3: # Control
            Streams_size.append(to_time_units(streamsConfig[2]["Size"], bw)) 
            Streams_Period[(i)] = streamsConfig[2]["Period"]
            Deathline_Stream[(i)] = streamsConfig[2]["Deadline"]
            control=control +1

    Streams_Period_list = [v for k,v in Streams_Period.items()]

    v_distribution = [audio, video, control]
    distribution = {
        'Audio': audio,
        'Video': video,
        'Control': control,
        'Feasibility': None
        }
    #FIXED streams_size = ttx * hp/period
    # Streams_size = fix_streams_size(Streams_size, Streams_Period_list, Streams_Period)
    print("\nRandom_Stream_size_and_period_generator:", Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams, distribution, v_distribution)
    return Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams, distribution, v_distribution

def fix_streams_size(Streams_size, Streams_Period_list, periods):
    hyperperiod = Hyperperiod_generator(Streams_Period_list)
    print("fix_streams_size", hyperperiod, Streams_size, Streams_Period_list, periods)
    return [time_unit * (hyperperiod/periods[i]) for i, time_unit in enumerate(Streams_size)]


def time_resolution(arr):
    return np.gcd.reduce([int(e) for e in arr])

# This funciton reads the periods of the strems and provides the hyperperiod (lcm of all the periods)
def Hyperperiod_generator(Streams_Period_list) :
    Hyperperiod = 1
    for i in Streams_Period_list:
        Hyperperiod = Hyperperiod*i//gcd(Hyperperiod, i)
    return Hyperperiod

# This function generates the frames_per_stream, basically a list with the number of frames per stream represented 
# as a set of 1's
# Provides also the maximum number of frames in an stream
def Frames_per_Stream_generator(Streams_size):
    # Streams_size = [300, 100, 100, 100]
    
    resolution = time_resolution(Streams_size)
    print("Resolution:", resolution)
    Frames_per_Stream = []
    for repetition in (Streams_size):
        # FIXME Frames per stream
#        Frames_per_Stream.append([1 for frame in range(int(float(repetition)/1500))])
        # Frames_per_Stream.append([1 for frame in range(int(float(repetition)/100))])
        Frames_per_Stream.append([1 for frame in range(int(float(repetition)/resolution))])
        Frames_per_Stream = [x if x else [1] for x in Frames_per_Stream]

    Max_frames = max([len(frame) for frame in Frames_per_Stream])
    Num_of_Frames = []
    for i in Frames_per_Stream : Num_of_Frames.append(len(i))
    print(f"Frames_per_Stream_generator: Streams_size:{Streams_size} \nFrames_per_Stream:{Frames_per_Stream}\nMax_frames:{Max_frames}\nResolution:{resolution}\nNum_of_Frames: {Num_of_Frames}")
    return Frames_per_Stream, Max_frames, Num_of_Frames, resolution
