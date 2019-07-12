"""
.. module:: single_conn
    :synopsis: Module for visualization of C. Elegans' neural connections with a GUI

.. moduleauthor:: Marc Javin
"""

from os.path import dirname
HERE = '.'

import pandas as pd
import numpy as np
import hvplot.networkx as hvnx
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import ArrowStyle

dfs = pd.read_csv(HERE+'/data/Neuro279_Syn.csv', index_col=0)
dfg = pd.read_csv(HERE+'/data/Neuro279_EJ.csv', index_col=0)
    
dfcat = pd.read_csv(HERE+'/data/neuron_categories.csv', index_col=1, header=0)
nbs = [i for i in range(len(dfs.index))]
cats = dfcat.loc[dfg.index]
motors = cats.index[cats['Category']=='MOTOR']
inters = cats.index[cats['Category']=='INTERNEURON']
sensors = cats.index[cats['Category']=='SENSORY']


""" Preferences : you can change the shape and colors of neuron categories here """
SENSOR_COLOR = '#006000'
SENSOR_SHAPE = 'o'
INTER_COLOR = '#000060'
INTER_SHAPE = 'o'
MOTOR_COLOR = '#600000'
MOTOR_SHAPE = 'o'
NODE_SIZE = 2500

style = ArrowStyle("wedge", tail_width=2., shrink_factor=0.2)
styleg = ArrowStyle("wedge", tail_width=0.6, shrink_factor=0.4)
CONN_STYLE = 'arc3, rad=0.3'


def connections(neuron='BAGL', connstyle=CONN_STYLE):
    '''Prepare graph for plotting'''
    G = nx.DiGraph()
    
    syn_in = dfs.index[dfs[neuron] > 0].tolist()
    intens_in = dfs.loc[dfs[neuron] > 0, neuron]
    syni = [(pre, neuron, {}) for pre in syn_in]
    G.add_edges_from(syni)

    gaps_ = dfg.index[dfg[neuron] > 0].tolist()
    intens_g = 0.1*dfg.loc[dfg[neuron] > 0, neuron]
    gaps = [(neuron, k, {}) for k in gaps_] + [(k, neuron, {}) for k in gaps_]
    G.add_edges_from(gaps)
    
    syn_out = dfs.T.index[dfs.T[neuron] > 0].tolist()
    intens_out = dfs.T.loc[dfs.T[neuron] > 0, neuron]
    syno = [(neuron, post, {}) for post in syn_out]
    G.add_edges_from(syno)
    
    G.remove_node(neuron)
    pos = nx.layout.circular_layout(G, scale=2)
    G.add_node(neuron)
    pos[neuron] = np.array([0,0])
    
    def draw_nodes(shape='o', category=inters, col='k'):
        hvnx.draw_networkx_nodes(G, pos, node_color=col, 
                               nodelist=[n for n in G.nodes if n in category],
                               node_size=NODE_SIZE, alpha=0.9)
    draw_nodes(SENSOR_SHAPE, sensors, SENSOR_COLOR)
    draw_nodes(INTER_SHAPE, inters, INTER_COLOR)
    draw_nodes(MOTOR_SHAPE, motors, MOTOR_COLOR)

    nx.draw_networkx_labels(G, pos, font_color='w', font_weight='bold')
    
    nx.draw_networkx_edges(G, pos, arrowstyle=style, edgelist=syni, edge_color='g', connectionstyle=connstyle,
                           arrowsize=10, alpha=0.7, width=intens_in, node_size=NODE_SIZE)
    nx.draw_networkx_edges(G, pos, arrowstyle=style, edgelist=syno, edge_color='r', connectionstyle=connstyle,
                           arrowsize=10, alpha=0.5, width=intens_out, node_size=NODE_SIZE)
    nx.draw_networkx_edges(G, pos, arrowstyle=styleg, edgelist=gaps, edge_color='Gold',
                           arrowsize=10, alpha=0.8, width=np.hstack((intens_g,intens_g)), 
                           node_size=NODE_SIZE)
    #plt.axis('off')
    hvnx.draw(G, pos)
    hvnx.show()

connections()

    
