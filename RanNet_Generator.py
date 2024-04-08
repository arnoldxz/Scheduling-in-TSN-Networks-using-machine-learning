# Gets as input the Number of edges and the connection probability between nodes

import networkx as nx 
from networkx.generators.random_graphs import erdos_renyi_graph
import matplotlib.pyplot as plt
import pandas as pd
import random


#All of this functions are randomizers that shouldn't be used if the values are provided
#Network_nodes, 
#Network_links, 
#Adjacency_Matrix, 
#plot_network
#Stream_Source_Destination


def adj(connections):
    ##step 1
    temp=(set(elem[0] for elem in connections).union(
        set(elem[1] for elem in connections)))
    n=max(temp)+1
    ans=[]
    ##step 2
    for i,_ in enumerate(temp):
        ans.append([])
        for j,_ in enumerate(temp):
            ans[i].append(0)
    ##step 3
    for pair in connections:
        ans[pair[0]][pair[1]]=1
        ans[pair[1]][pair[0]]=1
    return ans

# Determine if a list has a 0 element
def allcmp(existing_indicator) :
    for item in existing_indicator :
        if item == 0 :
            return False
    return True

# Validates if all the elements in the matrix are connected
def Matrix_Validator(element_list):
    existing_indicator = [0 for i in range(len(element_list[0]))]
    x = 0
    for element in element_list :
        y = 0 
        for element_2 in element :
            existing_indicator[y] = existing_indicator[y] + element_2
            y = y +1
        x = x +1
    return allcmp(existing_indicator)

# This function generates the Random Network 
def Random_Network_Generator(Number_of_edges, Connection_probability) :
    ensurer = False
    while ensurer == False :
        g = erdos_renyi_graph(Number_of_edges, Connection_probability)

        Network_nodes =  list(g.nodes)
        Network_links = list(g.edges)
        Sources = [link[0] for link in Network_links]
        Destinations = [link[1] for link in Network_links]

        # Checks if the random values are suitable for the Adjacency Matrix
        try: 
            Adjacency_Matrix = adj(Network_links)
            ensurer = Matrix_Validator(Adjacency_Matrix) # Determine if the all the nodes are connected
            if len(Adjacency_Matrix) != Number_of_edges:
                ensurer = False
        except:
            ensurer = False 
            

    # Build a dataframe with the Source and destination connections

    df = pd.DataFrame({ 'from': Sources , 'to': Destinations})

    # Build the graph
    G=nx.from_pandas_edgelist(df, 'from', 'to')

    # Plot the graph
    plot_network = plt.figure(1, figsize=(14, 7))
    plt.subplot(221)
    plt.title("Network Topology")
    nx.draw(G, with_labels=True)

    return Network_nodes, Network_links, Adjacency_Matrix, plot_network

# This function generates a set of flows from a destination to an end
# This function is placed here because it needs both parameters from the network and the Streams 
def Random_flows_generator(Number_of_Streams, Number_of_edges) :
    Stream_Source_Destination = []
    print("Number_of_Streams",Number_of_Streams)
    for i in range(Number_of_Streams) :
#       Stream_Source_Destination.append(random.sample(range(0, Number_of_edges), 2))
        Stream_Source_Destination.append([0,1])
        print("Stream_Source_Destination",Stream_Source_Destination)
    return Stream_Source_Destination

#Network_nodes, Network_links, Adjacency_Matrix, plot_network = Random_Network_Generator(5, 0.3)