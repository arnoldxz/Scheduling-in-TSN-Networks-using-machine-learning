# This part gets as input the Number of streams and the network parameters
# This function is called for generating the calculation of the network paths independly on the frames an periods

"""
Entry parameters

Adjacency_Matrix (rand_net)
Network_nodes (rand_net)
Stream_Source_Destination (rand_net) This value has to be regard as it is not properly from the rand net
Network_links (rand_net)

"""
# Djikstra algorithm is here !
class Network_Topology(): 
    # A constructor to iniltialize the values
    def __init__(self, graph):
        nodes = len(graph)
        #distance array initialization
        self.distArray = [0 for i in range(nodes)]
        #visited nodes initialization
        self.vistSet = [0 for i in range(nodes)]
        #initializing the number of nodes
        self.V = nodes
        #initializing the infinity value
        self.INF = 1000000
        #initializing the graph matrix
        #self.graph = [[0 for column in range(nodes)]  
        #            for row in range(nodes)]
        self.graph = graph    
    def dijkstra(self, srcNode):
        for i in range(self.V):
          #initialise the distances to infinity first
          self.distArray[i] = self.INF
          #set the visited nodes set to false for each node
          self.vistSet[i] = False
        #initialise the first distance to 0
        self.distArray[srcNode] = 0
        paths={}
        for i in range(self.V): 
  
            # Pick the minimum distance node from  
            # the set of nodes not yet processed.  
            # u is always equal to srcNode in first iteration 
            u = self.minDistance(self.distArray, self.vistSet) 
  
            # Put the minimum distance node in the  
            # visited nodes set
            self.vistSet[u] = True
             # Update dist[v] only if is not in vistSet, there is an edge from 
            # u to v, and total weight of path from src to  v through u is 
            # smaller than current value of dist[v]
            for v in range(self.V): 
                if self.graph[u][v] > 0 and self.vistSet[v] == False and self.distArray[v] > self.distArray[u] + self.graph[u][v]: 
                        self.distArray[v] = self.distArray[u] + self.graph[u][v]
                        # This is for creating a dictorionary that stores the keys and values of the node and the last visited node in the path
                        # Used for generating the list with the elements on the paths
                        paths[v] = u 
        self.full_paths_set = []
        for i in range(0,self.V):
            full_path =  self.paths_generator(i, srcNode , paths, [])
            self.full_paths_set.append(full_path)
        
        self.printSolution(self.distArray)

    #A utility function to find the node with minimum distance value, from 
    # the set of nodes not yet included in shortest path tree 
    def minDistance(self, distArray, vistSet): 
  
        # Initilaize minimum distance for next node
        min = self.INF
  
        # Search not nearest node not in the  
        # unvisited nodes
        for v in range(self.V): 
            if distArray[v] < min and vistSet[v] == False: 
                min = distArray[v] 
                min_index = v 
  
        return min_index

    def printSolution(self, distArray): 
        print ("Node \tDistance from 0")
        for i in range(self.V): 
            print (i, "\t", distArray[i])

    #This recursive function generates the path from a source to a destination based on the paths
    def paths_generator(self, node, source, paths, full_path_per_node):
        if node != source:
            if paths[node] != source:
                full_path_per_node.append(paths[node])
                self.paths_generator(paths[node], source, paths, full_path_per_node)
            else:
                return [source]
        else :
            full_path_per_node = []
        return full_path_per_node

# This is function generates a matrix with all the paths from one node to the other calculated by djikstra
def all_paths_matrix_generator(Network_nodes, network) :
    all_paths_matrix = [] 
    for node in Network_nodes:
        network.dijkstra(node) # This matrix saves all the existing paths in the network from one point to the othe 
        all_paths_matrix.append(network.full_paths_set)
    return all_paths_matrix

# Determining the path for each Stream generating a list of of all the nodes from source to destination
def Streams_paths_generator(all_paths_matrix, Stream_Source_Destination) :
    Streams_paths = [0 for i in range(len(Stream_Source_Destination))]
    n = 0
    for stream in Stream_Source_Destination:
        
        if len(all_paths_matrix[stream[1]][stream[0]]) == 1 : 
            Streams_paths[n]=all_paths_matrix[stream[1]][stream[0]]
            if stream[1] != all_paths_matrix[stream[1]][stream[0]][0] : 
                Streams_paths[n].append(stream[1])
        else :
            Streams_paths[n]=all_paths_matrix[stream[1]][stream[0]]
        Streams_paths[n].insert(0,stream[0])
        if Streams_paths[n][0] == Streams_paths[n][1]:
            del Streams_paths[n][0]
        n = n +1
    return Streams_paths

# Determining the path for each Stream regarding the links
def Streams_links_paths_generator(Streams_paths):
    Streams_links_paths = []
    for stream in Streams_paths :
        print(stream[1:])
        n = 1
        stream_allocator = []
        for i in stream[1:]:
            stream_allocator.append([stream[n-1], i])
            n = n+1
        Streams_links_paths.append(stream_allocator)
    return Streams_links_paths

# this function generates the link_order_descriptor 
#Basically, the link order descriptor is a list of the index of each link in the path
#from source to destination of a stream #
def Link_order_Descriptor_generator(Streams_links_paths, Network_links) :
    Link_order_Descriptor = []
    for stream in Streams_links_paths :
        link_order_helper = []
        for link in stream :
            try:
                link_order_helper.append(Network_links.index(tuple(link)))
            except:
                link_order_helper.append(Network_links.index(tuple([link[1],link[0]])))
        Link_order_Descriptor.append(link_order_helper)
    return Link_order_Descriptor
