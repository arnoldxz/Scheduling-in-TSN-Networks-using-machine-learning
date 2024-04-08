# This code is for calculation the previous parameters of the ILP 

# This code generates a matrix that will be used to 
# indicate wheter of not a frame in a stream and in a link exists or not
from RanNet_Generator import Random_Network_Generator
from Djikstra_Path_Calculator import *
from RandStream_Parameters import *
def Model_Descriptor_generator(Number_of_Streams, Max_frames, Network_links, Frames_per_Stream, Links_per_Stream) :
    Model_Descriptor = {}

    for stream in range(Number_of_Streams):
        for frame in range(Max_frames):
            for link in range(len(Network_links)):
                Model_Descriptor[(stream,frame,link)]= 0

    Model_Descriptor_vector = [[[0 for link in range(len(Network_links))] for frame in range(Max_frames)] for stream in range(Number_of_Streams)]

    x = 0
    for stream in Frames_per_Stream:
        y = 0
        for frame in stream:
            z = 0
            for link in Links_per_Stream[x]:
                Model_Descriptor[(x,y,z)] = frame * link 
                Model_Descriptor_vector [x][y][z] = frame * link
                z = z +  1
            y = y + 1
        x = x + 1
    Streams = range(Number_of_Streams)
    return Model_Descriptor, Model_Descriptor_vector, Streams


# Links per stream, basically is a list that indicates if a link is used for transmitting in a stream
def Links_per_Stream_generator(Network_links, Link_order_Descriptor) : 
    Links_per_Stream = [[0 for link in range(len(Network_links))] for stream in range(len(Link_order_Descriptor))]
    stream_index = 0
    for stream in Link_order_Descriptor :
        for link in stream :
            Links_per_Stream[stream_index][link] = 1
        stream_index = stream_index + 1 
    return Links_per_Stream  

# Boolean function that indicates if a combination of Frame Link and Stream exists or not
def frame_exists(Model_Descriptor_vector, stream, frame) :
    return len([*filter(lambda x: x >= 1, Model_Descriptor_vector[stream][frame])])

# Simply, fills the duration of the streams with a fixed value, can be changed in future
# def Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links ) :
#     Frame_Duration = {}
#     for stream in range(Number_of_Streams):
#         for frame in range(Max_frames):
#             for link in range(len(Network_links)):
#                 Frame_Duration[(stream,frame,link)]= 5 # This has to be 12
#     return Frame_Duration
def Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links, flow_types, configService, frame_resolution):
    Frame_Duration = {}
    
    networkConfig = configService.networkConfig
    streamsConfig = configService.streamsConfig

    for stream in range(Number_of_Streams):
        for frame in range(Max_frames):
            for link in range(len(Network_links)):
                #FIXME: Fix frame durations according to transmission time (ms) for each frame
                # flow_type = flow_types[stream]
                # duration = ((streamsConfig[flow_type-1]["Size"] * 8) / networkConfig["Bandwidth"]) * 1000
                duration = frame_resolution
                Frame_Duration[(stream,frame,link)] = duration # This has to be 12

                # Frame_Duration[(stream,frame,link)]= 123 # This has to be 12
    print("Frame_Durations:", Frame_Duration)
    return Frame_Duration

#This function generates the following:

# Repetitions: a vector with all the number of repetitions
# Repetition matrix: a matrix filled with ones regarding the number of repetitions in each stream
# Repetitions Descriptor: a matrix used for determining if a repetition in a determined stream exists or not
# max_repetitions: Simply the maximum number of repetitions in any stream
def Repetitions_generator(Streams_Period, Streams, Hyperperiod, configService) :
    Repetitions = []
    for period in range(len(Streams_Period)):
        Repetitions.append(float(Hyperperiod)/Streams_Period[(period)] - 1)
    #FIXED Fix Repetitions_generator method
    # Repetitions  = fix_repetitions(configService)
    Repetitions_Matrix = []
    for repetition in Repetitions :
        Repetitions_Matrix.append([1 for rep in range(int(repetition))])

    print("Getting Repetitions", Repetitions, "and Streams", Streams)
    if max(Repetitions) == 0 :
        Repetitions_Descriptor = [[0] for stream in Streams ]
    else :
        Repetitions_Descriptor = [[0 for repetition in range(int(max(Repetitions)))] for stream in Streams ]
    x = 0
    for stream in Repetitions_Matrix:
        y = 0
        for repetition in stream:
            Repetitions_Descriptor[x][y] = repetition * (y+1)
            y = y +1
        x = x + 1
    try :
        max_repetitions = max([max(stream) for stream in Repetitions_Descriptor])
    except :
        max_repetitions = 0


    # This is a patch for including the repetition 0 in the constraints 34 and 35
    y = 0
    try :
        for stream in Repetitions_Descriptor :
            x = 0
            for repetition in stream :
                if repetition == 0 :
                    Repetitions_Descriptor[y][x] = 9
                x = x +1
            Repetitions_Descriptor[y].insert(0 ,0)
            y = y +1

    except :
        print("Then it is not necessary")

    print("Repetitions_generator ORIGINAL: ",Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions)
    return Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions

def fix_repetitions(configService):
    return [0.0 for _ in range(configService.config["N_STREAMS"])]
### Defined unused links
def unused_links_generator(Network_links, Link_order_Descriptor):
    number_of_links = len(Network_links)
    unused_links = []
    for i in range(number_of_links) :
        totalizer = 0
        for link in Link_order_Descriptor:
            for sub_link in link:
                if sub_link == i :
                    totalizer = 1
        if totalizer == 0:
            unused_links.append(i)
    return unused_links



# Stream_Source_Destination = Random_flows_generator(Number_of_Streams, Number_of_edges)
# network = Network_Topology(Adjacency_Matrix) # Using the Network Topology class
# all_paths_matrix = all_paths_matrix_generator(Network_nodes, network)
# Streams_paths = Streams_paths_generator(all_paths_matrix, Stream_Source_Destination)
# Streams_links_paths = Streams_links_paths_generator(Streams_paths)
# Link_order_Descriptor = Link_order_Descripto_generator(Streams_links_paths)
# Links_per_Stream = Links_per_Stream_generator(Network_links, Link_order_Descriptor)
# Streams_size , Streams_Period, Streams_Period_list = Random_Stream_size_and_period_generator(Links_per_Stream)
# Hyperperiod = Hyperperiod_generator(Streams_Period_list)
# Frames_per_Stream, Max_frames, Num_of_Frames = Frames_per_Stream_generator(Streams_size)
# ################################################################
# Model_Descriptor, Model_Descriptor_vector, Streams = Model_Descriptor_generator(Number_of_Streams, Max_frames, Network_links, Frames_per_Stream, Links_per_Stream)
# Frame_Duration = Frame_Duration(Number_of_Streams, Max_frames, Network_links )
# Deathline_Stream = Deathline_Stream_generator(Frames_per_Stream)
# Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions= Repetitions_generator(Streams_Period, Streams)
# unused_links = unused_links_generator(Network_links, Link_order_Descriptor)

