# This set of functions is for the visualization of the values of the ILP 

import pandas as pd
import matplotlib.pyplot as plt

from RanNet_Generator import *
from Djikstra_Path_Calculator import *
from RandStream_Parameters import *
from Preprocessing import *
from ILP_Generator import *
import time

import csv
from distribution_provider import Provider
from config_provider import ConfigService
from results_checker import ResultCheck

configService = ConfigService() 
config = configService.config

N_STREAMS = configService.networkConfig["n_streams"]
DISTR_FILENAME = config["distributions"]
FILENAME =  config["results_filename"]
BASE_PATH = config["base_path"]
TIMEOUT = config["timeout"]
RESULTS_PATH = f"{BASE_PATH}\\{N_STREAMS}\\{FILENAME}"

dp = Provider(DISTR_FILENAME)


def Transmission_ranges(clean_offsets, flow_types, configService):
    transmissionRanges = []
    print("clean_offsets", clean_offsets)
    for i in range(len(flow_types)):
        flow_type = flow_types[i]
        flow_size = configService.streamsConfig[flow_type-1]["Size"] * 8
        flow_duration = flow_size / configService.networkConfig["Bandwidth"] * 1000
        flow_start = clean_offsets[i]["Start"]
        flow_end = flow_start + flow_duration
        transmissionRanges.append((flow_start, flow_end))
    print(f"Distribution: {flow_types}")
    print("Transmission ranges: ", transmissionRanges)
    return transmissionRanges

def Overlap_check(transmissionRanges):
    for i in range(len(transmissionRanges)):
        for j in range(i+1, len(transmissionRanges)):
            if transmissionRanges[i][0] < transmissionRanges[j][1] and transmissionRanges[j][0] < transmissionRanges[i][1]:
                print("\n! Overlapping ranges: ", transmissionRanges[i], transmissionRanges[j])
                return True
    print("\nNo overlapping ranges")
    return False


def ILP_results_visualizer(instance, Model_Descriptor_vector):
    print("instance.Streams", instance.Streams)
    print("instance.Frames", instance.Frames)
    print("############### This is the set of offsets ######################")
    Result_offsets = []
    Clean_offsets_collector = []
    Feasibility_indicator = 0
    for i in instance.Streams:
        for j in instance.Links:
            for k in instance.Frames:
                if Model_Descriptor_vector [i][k][j] :
                    print("The offset of stream", i, "link", j, "frame", k, "is",instance.Frame_Offset[i,j,k].value)
                    frame_indicator = ("S", i, "L", j, "F", k)
                    helper = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value, "Finish" : (instance.Frame_Offset[i,j,k].value +12), "Color" : j }
                    clean_offset = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value }
                    Result_offsets.append(helper)
                    Clean_offsets_collector.append(clean_offset)
                    if instance.Frame_Offset[i,j,k].value != 1 :
                        Feasibility_indicator = Feasibility_indicator + 1         
    print("############### This is the set of latencies ######################")
    Results_latencies = []
    for stream in instance.Streams:
        print("The latency of Stream", stream, "is",instance.Latency[stream].value)
        Results_latencies.append(instance.Latency[stream].value)
        
    print("############### This is the set of queues ######################")
    for link in instance.Links:
        print("The number of queues of link ", link, "is",instance.Num_Queues[link].value)

    print("############### This is the set of queues per stream and link######################")
    for stream in instance.Streams:
        for link in instance.Links:
            print("The number of queues of Link",link , "Stream" , stream, "is", instance.Queue_Assignment[stream, link].value)

    print("############### This is the set of auxiliar queues variables######################")
    for stream in instance.Streams :
        for stream_2 in instance.Streams :
            for link in instance.Links :
                print("Aux variable for stream_1 ", stream, "Stream_2", stream_2, "link", link, ":", instance.Aux_Same_Queue[stream_2, link ,stream].value)
    return Feasibility_indicator, Result_offsets, Clean_offsets_collector, Results_latencies

##### For printing the model results and variables #####
#UNCOMMENT if necessary 

# instance.display()
# results.write()
# results.solver.status 
######################## For now on, this code is for generate the Gant chart ########################


def gantt_chart_generator(Result_offsets, Repetitions, Streams_Period, frame_duration) :
    data = [[frame['Task'], frame['Start']] for frame in Result_offsets]
    Repetitions = [repetition + 1 for repetition in Repetitions]

    color=['black', 'red', 'green', 'blue', 'cyan', 'magenta', 'fuchsia', 'yellow', 'grey', 'orange', 'pink']

    # This set of code is for generating the repetitions values in the dataset
    #For printing the full gant Chart
    New_offsets = []
    stream_index = 0
    for repetition in Repetitions :
        for frame in Result_offsets:
            substring = "'S', " +  str(stream_index)
            if substring in frame["Task"] :
                for i in range(int(repetition)) :
                    Repeated_Stream = {'Task' : frame["Task"] , 'Start' : frame["Start"] + Streams_Period[stream_index]*(i), 'Color' : color[frame["Color"]]}
                    New_offsets.append(Repeated_Stream)
        stream_index = stream_index + 1

    Result_offsets = New_offsets
    data = [[frame['Task'], frame['Start'], frame['Color']] for frame in New_offsets]
    df = pd.DataFrame(data, columns = ['Process_Name', 'Start', 'Color'])


    # This is for printing the gant Chart 
    plt.subplot(212)
    #plt.figure(figsize=(12, 5))
    plt.barh(y=df.Process_Name, left=df.Start, width=frame_duration, color=df.Color)
    plt.grid(axis='x', alpha=0.5)
    plt.ylabel("Frames")
    plt.xlabel("Time in miliseconds")
    plt.title("Gantt Chart")
    plt.savefig('testing.png')

    return df


def information_generator(Num_of_Frames, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths, v_distribution):
    #Frames per stream
    #period per stream
    #Links used per stream
    #Network_links
    # Streams_links_paths
    plt.subplot(222)
    plt.text(0.1, 0.9, "Network-links: \n" + str(Network_links), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.7, "Frames per stream: \n" + str(Num_of_Frames), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.5, "Streams periods: \n" + str(Streams_Period), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.3, "Indexed Links order per stream: \n " + str(Link_order_Descriptor), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.1, "Streams Paths: \n " + str(Streams_links_paths), bbox=dict(facecolor='red', alpha=0.5))
    plt.axis('off')
    # plt.show()
    plt.savefig(f"{RESULTS_PATH}\\{v_distribution}.png")
    plt.close()
    # # comment for avoiding showing de result
    # TAG


def dataframe_printer(instance, Clean_offsets, Results_latencies, Feasibility_indicator, Adjacency_Matrix, Stream_Source_Destination,
                    Link_order_Descriptor, Links_per_Stream, Frames_per_Stream, Deathline_Stream, Streams_Period, Streams_size, v_distribution, overlapping):
    Feasibility = False
    if Feasibility_indicator > 1 and overlapping == False:
        Feasibility = True
    # Definition of the Data Frame
    # Each schedule provides the following:
    Full_scheduled_data = {
        "Distribution": v_distribution,
        #Parameter of the network 
        "Adjacency_Matrix" : Adjacency_Matrix, 
        #Parameters of the Streams
        "Stream_Source_Destination" : Stream_Source_Destination, 
        "Link_order_Descriptor" : Link_order_Descriptor,
        "Links_per_Stream" : Links_per_Stream, 
        "Number_of_Streams" : len(instance.Streams),
        "Frames_per_Stream" : Frames_per_Stream,
        "Deathline_Stream" : Deathline_Stream,
        "Streams_Period" : Streams_Period,
        #Results
        "Streams_size" : Streams_size,
        "Clean_offsets" : Clean_offsets,
        "Latencies" : Results_latencies,
        "Feasibility" : Feasibility
    }
    if Feasibility is True:
        print("\n✔ Feasible\n")
    else:
        print("\n✖ Not Feasible\n")
    
    v_distribution.append(Feasibility)
    v_distribution.append(False)

    with open(f"{RESULTS_PATH}\\{FILENAME}.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow(v_distribution)

    print(Full_scheduled_data)
    ### This will store the results into a txt for further usage
    with open(f"{RESULTS_PATH}\\{FILENAME}.txt", 'a') as f :
        f.write("\n" + str(Full_scheduled_data))

def Evaluation_function(Number_of_edges, Connection_probability,Number_of_Streams) :

### This is just the part where the program can select betweeen generating a new network
#Number_of_edges, Connection_probability = 2 , 0.8
#Number_of_Streams = 5

################################################################
    # Generation of random Network
    try :
        initial_time = time.time()
        Network_nodes, Network_links, Adjacency_Matrix, plot_network = Random_Network_Generator(Number_of_edges, Connection_probability)
        Stream_Source_Destination = Random_flows_generator(Number_of_Streams, Number_of_edges) 
        print("Stream_Source_Destination",Stream_Source_Destination)
        ################################################################
        #Djikstra scheduler
        network = Network_Topology(Adjacency_Matrix) # Using the Network Topology class
        all_paths_matrix = all_paths_matrix_generator(Network_nodes, network)
        Streams_paths = Streams_paths_generator(all_paths_matrix, Stream_Source_Destination)
        Streams_links_paths = Streams_links_paths_generator(Streams_paths)
        Link_order_Descriptor = Link_order_Descriptor_generator(Streams_links_paths, Network_links)


        ################################################################
        # Random Streams parameters
        # Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams = Random_Stream_size_and_period_generator(Number_of_Streams)
        flow_types = dp.provide()
        #FIXED: Provide new stream periods list = [hyperperiod]
        Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams, distribution, v_distribution = Random_Stream_size_and_period_generator(Number_of_Streams, list(flow_types), configService)
        Hyperperiod = Hyperperiod_generator(Streams_Period_list)
        print("Hyperperiod: ", Hyperperiod)
        periods_fix = {index: value for index, value in enumerate([Hyperperiod for _ in Streams_Period])}
        Frames_per_Stream, Max_frames, Num_of_Frames, frame_duration = Frames_per_Stream_generator(Streams_size)
        ################################################################
        # Preprocessing
        Links_per_Stream = Links_per_Stream_generator(Network_links, Link_order_Descriptor)
        Model_Descriptor, Model_Descriptor_vector, Streams = Model_Descriptor_generator(Number_of_Streams, Max_frames, Network_links, Frames_per_Stream, Links_per_Stream)
        Frame_Duration = Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links, flow_types,configService, frame_duration)
        Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions= Repetitions_generator(Streams_Period, Streams, Hyperperiod, configService)
        unused_links = unused_links_generator(Network_links, Link_order_Descriptor)

        ################################################################
        scheduler = ILP_Raagard_solver(Number_of_Streams, Network_links, \
                        Link_order_Descriptor, \
                        Streams_Period, Hyperperiod, Frames_per_Stream, Max_frames, Num_of_Frames, \
                        Model_Descriptor, Model_Descriptor_vector, Deathline_Stream, \
                        Repetitions, Repetitions_Descriptor, unused_links, Frame_Duration, \
                        periods_fix, TIMEOUT)
        instance, results = scheduler.instance, scheduler.results
        final_time = time.time()
        ################################################################
        Feasibility_indicator, Result_offsets, Clean_offsets_collector, Results_latencies  = ILP_results_visualizer(instance, Model_Descriptor_vector)
        df = gantt_chart_generator(Result_offsets, Repetitions, Streams_Period, frame_duration)

        overlapping = ResultCheck.overlapping_check(Clean_offsets_collector, frame_duration)

        information_generator(Num_of_Frames, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths, v_distribution)
        dataframe_printer(instance, Clean_offsets_collector, Results_latencies, Feasibility_indicator, Adjacency_Matrix, Stream_Source_Destination,
                        Link_order_Descriptor, Links_per_Stream, Frames_per_Stream, Deathline_Stream, Streams_Period, Streams_size, v_distribution, overlapping)
        ### This will store the results into a txt for further usage
        
        time_evaluation = final_time - initial_time
        with open('results_gurobi_local'  + str(Number_of_edges)  + '_'
                                    + str(Connection_probability) + '_'
                                    + str(Number_of_Streams) + '.txt', 'a') as f :
            f.write(str(time_evaluation) + "\n")
        
    except ValueError:
        print("One error has occurred")



while(dp.readlines(DISTR_FILENAME) is not None):
    for n in [N_STREAMS]:
        for i in range(1):
            # Evaluation_Function(number_of_nodes, connection_probability, number of streams)
            Evaluation_function(2, 1, n)