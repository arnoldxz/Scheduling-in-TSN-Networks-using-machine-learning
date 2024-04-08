##################################### ILP Model starts here #####################################
# The ILP took as base for this code appears in the paper 
# Optimization algorithms for the scheduling of IEEE 802.1 Time-Sensitive Networking (TSN)
# The authors are Michael Lander and Raagaard Paul Pop

from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.core import Var


"""
____________Input Variables______________ 


This values are received from the outside. According to our microservices topology, 
all these parameters should ber provided as a input from preprocessing microservice
Number_of_Streams
Network_links,
Link_order_Descriptor,
Streams_Period, 
Hyperperiod,
Frames_per_Stream, 
Max_frames, 
Num_of_Frames,
Model_Descriptor, 
Model_Descriptor_vector, 
Deathline_Stream, 
Repetitions, 
Repetitions_Descriptor, 
Unused_links, 
Frame_Duration

"""


# Boolean function that indicates if a combination of Frame Link and Stream exists or not
def frame_exists(Model_Descriptor_vector, stream, frame) :
    return len([*filter(lambda x: x >= 1, Model_Descriptor_vector[stream][frame])])
#Objective Function


def Latency_Num_Queues_rule(model):
    return sum(model.Num_Queues[link] - 1 for link in model.Links )
#    return (0.9) * sum(model.Latency[stream] - model.Lower_Latency[stream] for link in model.Links ) + (0.1) * sum(model.Num_Queues[stream] - 1 for stream in model.Streams )

#Constraints

class ILP_Raagard_solver :
    
    def __init__(self, Number_of_Streams, Network_links, \
                Link_order_Descriptor, \
                Streams_Period, Hyperperiod, Frames_per_Stream, Max_frames, Num_of_Frames, \
                Model_Descriptor, Model_Descriptor_vector, Deathline_Stream, \
                Repetitions, Repetitions_Descriptor, unused_links, Frame_Duration, \
                periods_fix, TIMEOUT):

        self.Number_of_Streams = Number_of_Streams
        self.Network_links = Network_links
        self.Link_order_Descriptor = Link_order_Descriptor
        self.Streams_Period = Streams_Period
        self.Hyperperiod = Hyperperiod
        self.Frames_per_Stream = Frames_per_Stream 
        self.Max_frames = Max_frames 
        self.Num_of_Frames = Num_of_Frames
        self.Model_Descriptor = Model_Descriptor
        self.Model_Descriptor_vector = Model_Descriptor_vector
        self.Deathline_Stream = Deathline_Stream
        self.Repetitions = Repetitions
        self.Repetitions_Descriptor = Repetitions_Descriptor
        self.unused_links = unused_links
        self.Frame_Duration = Frame_Duration
        print("\n\n\nINPUT VALUES")
        print("Number_of_Streams:", Number_of_Streams)
        print("Network_links:", Network_links)
        print("Streams_Period:", Streams_Period)
        print("Hyperperiod:", Hyperperiod)
        print("Num_of_Frames:", Num_of_Frames)
        print("Model_Descriptor:", Model_Descriptor)
        print("Model_Descriptor_vector:", Model_Descriptor_vector)
        print("Deathline_Stream:", Deathline_Stream)
        print("Repetitions:", Repetitions)
        print("Repetitions_Descriptor:", Repetitions_Descriptor)
        print("unused_links:", unused_links)
        print("Frame_Duration:", Frame_Duration)
        # print("periods_fix:", periods_fix)
        # Streams_Period = periods_fix
        #FIXED Streams_Period

        self.model = AbstractModel()
        self.model.Streams = Set(initialize= range(self.Number_of_Streams)) # Num of streams
        self.model.Repetitions = Set(initialize= range(int(max(Repetitions) + 1))) # This is the maximum number of Repetitions
        self.model.Frames = Set(initialize= frozenset(range(Max_frames))) # Maximum number of streams
        self.model.Links = Set(initialize = frozenset(range(len(Network_links)))) # Links Ids

        # Parameters
        self.model.Hyperperiod = Param(initialize=Hyperperiod)
        self.model.Large_Number = Param(initialize=9999999999)
        self.model.Max_Syn_Error = Param(initialize=0.00000001)
        self.model.Model_Descriptor = Param(self.model.Streams, self.model.Frames, self.model.Links, initialize= Model_Descriptor)
        self.model.Deathline_Stream = Param(self.model.Streams, initialize = Deathline_Stream)
        self.model.Period = Param(self.model.Streams, initialize=Streams_Period)
        self.model.Frame_Duration = Param(self.model.Streams, self.model.Frames, self.model.Links, initialize = self.Frame_Duration)
        self.model.Num_of_Frames = Param(self.model.Streams, initialize=Num_of_Frames)

        # Variables
#        self.model.Frame_Offset = Var(self.model.Streams, self.model.Links, self.model.Frames, within=PositiveIntegers, initialize=1)
        self.model.Frame_Offset = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        self.model.Aux_Same_Queue = Var(self.model.Streams, self.model.Links, self.model.Streams, within=Binary, initialize=0)
        self.model.Queue_Assignment = Var(self.model.Streams, self.model.Links, within=NonNegativeReals, initialize=1)
        self.model.Aux_Var_Dis = Var(self.model.Streams, self.model.Frames, self.model.Streams, self.model.Frames, self.model.Links, self.model.Repetitions, self.model.Repetitions, within=Binary, initialize = 0)
        self.model.w = Var(self.model.Streams, self.model.Frames, self.model.Streams, self.model.Frames, self.model.Links, within=Binary, initialize=0)

        #Variables of the Objective Function
        self.model.Lower_Latency = Var(self.model.Streams, within=NonNegativeReals, initialize=0)
        self.model.Latency = Var(self.model.Streams, within=Integers, initialize=0)
        self.model.Num_Queues = Var(self.model.Links, within=PositiveIntegers, initialize=1)
        
        
        # Defining the objective function
        @self.model.Objective(sense=minimize)
        def Latency_Num_Queues_rule(model):
            return sum(model.Num_Queues[link] - 1 for link in model.Links )
        #   return sum(model.Latency[stream] - model.Lower_Latency[stream] for stream in model.Streams) 
        #   return (0.9) * sum(model.Latency[stream] - model.Lower_Latency[stream] for link in model.Links ) + (0.1) * sum(model.Num_Queues[stream] - 1 for stream in model.Streams )
            # return sum(model.Latency[stream] - model.Frame_Duration[stream, 0, 0] for stream in model.Streams) 

        
        
        # Defining the constraints
        @self.model.Constraint(self.model.Streams, self.model.Links)
        def Constraint_27_rule(model, stream, link):
            if self.Model_Descriptor[(stream, 0, link)]:
                return model.Num_Queues[link] >= model.Queue_Assignment[stream, link]
            else :
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams)
        def Constraint_28_rule(model, stream): 
            return model.Latency[stream] == model.Frame_Offset[stream, self.Link_order_Descriptor[stream][-1], (len(self.Frames_per_Stream[stream]) -1) ] + model.Frame_Duration[stream, (len(self.Frames_per_Stream[stream]) -1) , self.Link_order_Descriptor[stream][-1] ] - model.Frame_Offset[stream, self.Link_order_Descriptor[stream][0] , 0 ]
        
        @self.model.Constraint(self.model.Streams)
        def Constraint_29_rule(model, stream):
            return model.Latency[stream] <= model.Deathline_Stream[stream]        
        
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links)
        def Constraint_30_rule(model, stream, frame, link):
            if self.Model_Descriptor[(stream, frame, link)]:
                return model.Frame_Offset[stream, link, frame] <= model.Period[(stream)] - model.Frame_Duration[stream, frame, link]
            else :
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links)
        def Constraint_31_rule(model, stream, frame, link):
            if self.Model_Descriptor[(stream, frame, link)] and self.Link_order_Descriptor[stream].index(link) != 0 :
                return model.Frame_Offset[stream, link, frame] >= model.Frame_Offset[stream, self.Link_order_Descriptor[stream][self.Link_order_Descriptor[stream].index(link)-1],frame] + model.Frame_Duration[stream, frame, Link_order_Descriptor[stream][Link_order_Descriptor[stream].index(link)-1]] + model.Max_Syn_Error
            else :
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links)
        def Constraint_32_rule(model, stream, frame, link): 
            if self.Model_Descriptor[(stream, frame, link)] and frame :
                return model.Frame_Offset[stream, link, frame - 1 ] + model.Frame_Duration[stream, frame - 1, link] <= model.Frame_Offset[stream, link, frame]
            else:
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links, self.model.Streams, self.model.Frames, self.model.Repetitions, self.model.Repetitions)

        def Constraint_34_rule(model, stream, frame, link, stream_2, frame_2, repetition, repetition_2):
            if frame_exists(self.Model_Descriptor_vector, stream, frame) and frame_exists(self.Model_Descriptor_vector, stream_2, frame_2) and self.Model_Descriptor[(stream,frame,link)] and self.Model_Descriptor[(stream_2,frame_2,link)] and self.Repetitions_Descriptor[stream][repetition] != 9 and self.Repetitions_Descriptor[stream_2][repetition_2] != 9 and stream != stream_2 :
                return self.Repetitions_Descriptor[stream][repetition] * model.Period[(stream)] + model.Frame_Offset[stream, link, frame] + model.Frame_Duration[stream, frame, link] <= self.Repetitions_Descriptor[stream_2][repetition_2] * model.Period[(stream_2)] + model.Frame_Offset[stream_2, link, frame_2] +  model.Large_Number * model.Aux_Var_Dis[stream, frame, stream_2, frame_2, link, repetition, repetition_2]
            else:
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links, self.model.Streams, self.model.Frames, self.model.Repetitions, self.model.Repetitions)

        def Constraint_35_rule(model, stream, frame, link, stream_2, frame_2, repetition, repetition_2):
            if frame_exists(self.Model_Descriptor_vector, stream, frame) and frame_exists(self.Model_Descriptor_vector, stream_2, frame_2) and self.Model_Descriptor[(stream,frame,link)] and self.Model_Descriptor[(stream_2,frame_2,link)] and self.Repetitions_Descriptor[stream][repetition] != 9 and self.Repetitions_Descriptor[stream_2][repetition_2] != 9 and stream != stream_2:
                return self.Repetitions_Descriptor[stream_2][repetition_2] * model.Period[(stream_2)] + model.Frame_Offset[stream_2, link, frame_2] + model.Frame_Duration[stream_2, frame_2, link] <= self.Repetitions_Descriptor[stream][repetition] * model.Period[(stream)] + model.Frame_Offset[stream, link, frame] + model.Large_Number * (1 - model.Aux_Var_Dis[stream, frame, stream_2, frame_2, link, repetition, repetition_2]) 
            else:
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links, self.model.Streams, self.model.Frames, self.model.Repetitions, self.model.Repetitions)

        def Constraint_36_rule(model, stream, frame, link, stream_2, frame_2, repetition, repetition_2 ):
            if frame_exists(self.Model_Descriptor_vector, stream, frame) and frame_exists(self.Model_Descriptor_vector, stream_2, frame_2) and self.Model_Descriptor[(stream,frame,link)] and self.Model_Descriptor[(stream_2,frame_2,link)] and self.Link_order_Descriptor[stream].index(link) and self.Link_order_Descriptor[stream_2].index(link) and self.Repetitions_Descriptor[stream][repetition] != 9 and self.Repetitions_Descriptor[stream_2][repetition_2] != 9 and stream != stream_2:
                return self.Repetitions_Descriptor[stream][repetition] * model.Period[stream] + model.Frame_Offset[stream, link, frame] <= self.Repetitions_Descriptor[stream_2][repetition_2] * model.Period[stream_2] + model.Frame_Offset[stream_2,self.Link_order_Descriptor[stream][self.Link_order_Descriptor[stream].index(link)-1], frame_2] + model.Large_Number * (model.w[stream, frame, stream_2, frame_2, link] + model.Aux_Same_Queue[stream, link, stream_2] + model.Aux_Same_Queue[stream_2, link, stream])
            else : 
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links, self.model.Streams, self.model.Frames, self.model.Repetitions, self.model.Repetitions)
        def Constraint_37_rule(model, stream, frame, link, stream_2, frame_2, repetition, repetition_2):
            if frame_exists(self.Model_Descriptor_vector, stream, frame) and frame_exists(self.Model_Descriptor_vector, stream_2, frame_2) and self.Model_Descriptor[(stream,frame,link)] and self.Model_Descriptor[(stream_2,frame_2,link)] and self.Link_order_Descriptor[stream].index(link) and self.Link_order_Descriptor[stream_2].index(link) and self.Repetitions_Descriptor[stream][repetition] != 9 and self.Repetitions_Descriptor[stream_2][repetition_2] != 9 and stream != stream_2:
                return self.Repetitions_Descriptor[stream_2][repetition_2] * model.Period[stream_2] + model.Frame_Offset[stream_2, link, frame_2] <= self.Repetitions_Descriptor[stream][repetition] * model.Period[stream] + model.Frame_Offset[stream, self.Link_order_Descriptor[stream][self.Link_order_Descriptor[stream].index(link)-1], frame] + model.Large_Number * (1- model.w[stream, frame, stream_2, frame_2, link] + model.Aux_Same_Queue[stream, link, stream_2] + model.Aux_Same_Queue[stream_2, link ,stream])
            else : 
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Links, self.model.Streams)
        def Constraint_39_rule(model, stream, link, stream_2):
            if self.Model_Descriptor[(stream, 0, link)] and self.Model_Descriptor[(stream_2, 0, link)] and stream != stream_2:
                return model.Queue_Assignment[stream_2, link] - model.Queue_Assignment[stream, link] - model.Large_Number * (model.Aux_Same_Queue[stream, link, stream_2] - 1) >= 1 
            else : 
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Links, self.model.Streams)
        def Constraint_40_rule(model, stream, link, stream_2):
            if self.Model_Descriptor[(stream, 0, link)] and self.Model_Descriptor[(stream_2, 0, link)] and stream != stream_2:
                return model.Queue_Assignment[stream_2, link] - model.Queue_Assignment[stream, link] - model.Large_Number * model.Aux_Same_Queue[stream, link, stream_2] <= 0
            else : 
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links, self.model.Streams, self.model.Frames, self.model.Repetitions, self.model.Repetitions)
        def Constraint_41_rule(model, stream, frame, link, stream_2, frame_2, repetition, repetition_2):
            if frame_exists(self.Model_Descriptor_vector, stream, frame) and frame_exists(self.Model_Descriptor_vector, stream_2, frame_2) and self.Model_Descriptor[(stream, frame, link)] and self.Model_Descriptor[(stream_2, frame_2, link)] and self.Link_order_Descriptor[stream].index(link) and self.Link_order_Descriptor[stream_2].index(link) and self.Repetitions_Descriptor[stream][repetition] != 9 and self.Repetitions_Descriptor[stream_2][repetition_2] != 9 and stream != stream_2:
                return  self.Repetitions_Descriptor[stream][repetition] * model.Period[stream] + model.Frame_Offset[stream, link, frame] + model.Max_Syn_Error <= self.Repetitions_Descriptor[stream_2][repetition_2] * model.Period[stream_2] + model.Frame_Offset[stream_2,self.Link_order_Descriptor[stream_2][self.Link_order_Descriptor[stream_2].index(link)-1], frame_2] + model.Large_Number * (model.w[stream, frame, stream_2, frame_2, link] + model.Aux_Same_Queue[stream, link, stream_2] + model.Aux_Same_Queue[stream_2, link, stream])
            else : 
                return Constraint.Skip
        @self.model.Constraint(self.model.Streams, self.model.Frames, self.model.Links, self.model.Streams, self.model.Frames, self.model.Repetitions, self.model.Repetitions)
        def Constraint_42_rule(model, stream, frame, link, stream_2, frame_2, repetition, repetition_2):    
            if frame_exists(self.Model_Descriptor_vector, stream, frame) and frame_exists(self.Model_Descriptor_vector, stream_2, frame_2) and self.Model_Descriptor[(stream, frame, link)] and self.Model_Descriptor[(stream_2, frame_2, link)] and self.Link_order_Descriptor[stream].index(link) and self.Link_order_Descriptor[stream_2].index(link) and self.Repetitions_Descriptor[stream][repetition] != 9 and self.Repetitions_Descriptor[stream_2][repetition_2] != 9 and stream != stream_2:
                return self.Repetitions_Descriptor[stream_2][repetition_2] * model.Period[stream_2] + model.Frame_Offset[stream_2, link, frame_2] + model.Max_Syn_Error <= self.Repetitions_Descriptor[stream][repetition] * model.Period[stream] + model.Frame_Offset[stream, self.Link_order_Descriptor[stream][self.Link_order_Descriptor[stream].index(link)-1], frame] + model.Large_Number * (1 - model.w[stream, frame, stream_2, frame_2, link] + model.Aux_Same_Queue[stream, link, stream_2] + model.Aux_Same_Queue[stream_2, link, stream])
            else : 
                return Constraint.Skip
        @self.model.Constraint(self.model.Links)
        #unused_links_generator(Network_links, Link_order_Descriptor)
        def Constraint_reliever_rule(model, link):
            if link in self.unused_links :
                print("applying for link", link)
                return model.Num_Queues[link] == 1
            else : 
                return Constraint.Skip
        ### This part is the creation of the instance in the ilp system
        opt = SolverFactory('gurobi')
        #opt = SolverFactory('gurobi', solver_io="python")
        self.instance = self.model.create_instance()
        self.results = opt.solve(self.instance, options={'TimeLimit': TIMEOUT})
        self.instance.solutions.load_from(self.results)


    # Before equation 25 there are missing equations, necessaries for reduce the latency 

    