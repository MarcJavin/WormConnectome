"""
.. module:: single_conn
    :synopsis: Module for visualization of C. Elegans' neural connections with a GUI

.. moduleauthor:: Marc Javin
"""

from os.path import dirname
HERE = dirname(__file__)
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def init():
    dfs = pd.read_csv(HERE+'/data/Neuro279_Syn.csv', index_col=0)
    dfg = pd.read_csv(HERE+'/data/Neuro279_EJ.csv', index_col=0)
    return dfs, dfg
    
DFS, DFG = init()
dfcat = pd.read_csv(HERE+'/data/neuron_categories.csv', index_col=1, header=0)
nbs = [i for i in range(len(DFS.index))]
cats = dfcat.loc[DFG.index]
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
CONN_STYLE = 'arc3, rad=0.3'

RICH1 = ['AVAL', 'AVAR', 'AVBL', 'AVBR', 'AVDL', 'AVDR', 'AVEL', 'AVER', 'PVCL', 'PVCR', 'DVA']
RICH2 = ['RIBL']
RICH3 = ['AIBR', 'RIAR']
select = ['AIBL', 'AIBR', 'ALA', 'ALNL', 'ALNR', 'AS10', 'ASKL', 'ASKR', 'AVAL',
       'AVAR', 'AVBL', 'AVBR', 'AVEL', 'AVER', 'AVFL', 'AVFR', 'BAGL', 'DA01',
       'DA07', 'DA09', 'DB01', 'DB02', 'DB07', 'DVA', 'DVC', 'LUAR', 'OLQDL',
       'OLQDR', 'OLQVL', 'OLQVR', 'PDA', 'PHAR', 'PVCL', 'PVCR', 'PVNL',
       'PVNR', 'RIBL', 'RIBR', 'RID', 'RIFR', 'RIMR', 'RIS', 'RIVR', 'RMED',
       'RMEL', 'RMEV', 'SABD', 'SABVL', 'SABVR', 'SIADL', 'SIADR', 'SIAVL',
       'SIAVR', 'SMDDL', 'SMDDR', 'SMDVL', 'SMDVR', 'VA01', 'VA11', 'VA12',
       'VB02', 'VB11', 'VD11', 'VD13']

DFG = DFG.loc[select, select]
DFS = DFS.loc[select, select]

labels = {i:DFG.index[i] for i in range(DFG.shape[0])}

def get_s():
    G1 = nx.from_numpy_matrix(DFS.values, create_using=nx.DiGraph())
    G1 = nx.relabel.relabel_nodes(G1, labels)
    return G1

def get_g():
    #Digraph to count double
    G2 = nx.from_numpy_matrix(DFG.values, create_using=nx.DiGraph())
    G2 = nx.relabel.relabel_nodes(G2, labels)
    return G2

def get_graph(di=False):
    if di:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    g1 = get_s()
    G.add_edges_from(g1.edges.data())
    g2 = get_g()
    G.add_edges_from(g2.edges.data())
    return G, g1, g2

G = get_graph()[0]

def draw_nodes(pos, shape='o', category=inters, col='k', size=NODE_SIZE, G=G):
            nx.draw_networkx_nodes(G, pos, node_shape=shape, node_color=col, 
                                   nodelist=set(G.nodes).intersection(category),
                                   node_size=size, alpha=0.9)
        
def draw_rich(pos, neurs=RICH1, sk=2.8*NODE_SIZE, sr=2.6*NODE_SIZE, sg=2*NODE_SIZE, s=NODE_SIZE, G=G):
        draw_nodes(pos, 'o', neurs, 'white', size=sk, G=G)
        draw_nodes(pos, 'o', neurs, 'r', size=sr, G=G)
        draw_nodes(pos, 'o', neurs, 'Gold', size=sg, G=G)
        draw_nodes(pos, INTER_SHAPE, neurs, INTER_COLOR, size=s, G=G)
        
def whole(pos=None, rich=False, nodesize=NODE_SIZE):  
    
    if pos is None:
        G = get_graph()[0]
        pos = nx.layout.spring_layout(G)
    G, G1, G2 = get_graph(di=True)
    
            
    draw_nodes(pos, 'o', G.nodes, 'white', size=1.1*nodesize, G=G)
    draw_nodes(pos, SENSOR_SHAPE, sensors, SENSOR_COLOR, size=nodesize, G=G)
    draw_nodes(pos, MOTOR_SHAPE, motors, MOTOR_COLOR, size=nodesize, G=G)
    draw_nodes(pos, INTER_SHAPE, inters, INTER_COLOR, size=nodesize, G=G)
    
    nx.draw_networkx_edges(G, pos, edge_color='#303060', node_size=nodesize, arrowstyle='->', edgelist=G1.edges, 
                           alpha=0.6, width=list(nx.get_edge_attributes(G1, 'weight').values()), arrowsize=10, connectionstyle=CONN_STYLE)
    nx.draw_networkx_edges(G, pos, edge_color='#505020', node_size=nodesize, arrowstyle='->', edgelist=G2.edges, 
                           alpha=0.6, width=list(nx.get_edge_attributes(G2, 'weight').values()), connectionstyle=None)

    nx.draw_networkx_labels(G, pos, font_color='w', font_weight='bold', font_size=26.*nodesize/NODE_SIZE)

    plt.axis('off')
    
    if rich:
        draw_rich(pos, RICH3, sk=1.84*nodesize, sr=0, sg=1.8*nodesize, s=nodesize, G=G)
        draw_rich(pos, RICH2, sk=2.24*nodesize, sr=2.2*nodesize, sg=1.8*nodesize, s=nodesize, G=G)
        draw_rich(pos, RICH1, sk=2.8*nodesize, sr=2.6*nodesize, sg=2*nodesize, s=nodesize, G=G)
    
    return pos
    




import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Window(QWidget):
    '''Main window containing potentially several visualisations'''

    def __init__(self, img_size):
        super(Window, self).__init__()

        self.neurons = []
        layout = QVBoxLayout()
        
        '''Plotting'''
        self.figure = plt.figure(0, figsize=(img_size,img_size))
        self.canvas = FigureCanvas(self.figure)
        
        '''Rich club option'''
        self.rich = QCheckBox('Rich club')
        self.rich.setChecked(True)
        self.rich.stateChanged.connect(lambda x: self.draw())

        '''Neuron size'''
        sizetext = QLabel('Node size :')
        self.nodesize = QSlider(Qt.Horizontal)
        self.nodesize.setMinimum(10)
        self.nodesize.setMaximum(1000)
        self.nodesize.setValue(2000)
        self.nodesize.setTickPosition(QSlider.TicksBelow)
        self.nodesize.setTickInterval(50)
        self.nodesize.sliderReleased.connect(self.draw)

        subl = QHBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(subl)
        subl.addWidget(self.rich)
        subl.addWidget(sizetext)
        subl.addWidget(self.nodesize)
        self.setLayout(layout)

        self.resize(500, 500)
        self.move(300, 300)
        self.setWindowTitle("Connectome Visualizer")
        
        self.pos = None
        self.draw()
        
    def draw(self):
        self.figure.clf()
        self.pos = whole(self.pos, rich=self.rich.isChecked(), nodesize=self.nodesize.value())
        self.canvas.draw()



if __name__=='__main__':

    app = QApplication(sys.argv)
    w = Window(10)
    w.show()
    sys.exit(app.exec_())


