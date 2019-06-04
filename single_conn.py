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
        nx.draw_networkx_nodes(G, pos, node_shape=shape, node_color=col, 
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
    plt.axis('off')
    return pos




import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Visu(QVBoxLayout):
    '''Layout for one neuron visualization'''

    nb = 0

    def __init__(self, img_size=12):
        super(Visu, self).__init__()

        Visu.nb += 1
        self.nb = Visu.nb
        # Figure and mouse clicking
        self.figure = plt.figure(self.nb, figsize=(img_size,img_size))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMouseTracking(True)
        self.canvas.mousePressEvent = lambda e: Visu.mousePressEvent(e, self)

        subl = QHBoxLayout()
        
        '''List of neurons'''
        self.cb = QComboBox()
        self.cb.addItems(sorted(dfs.index))
        self.cb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cb.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cb.view().window().setMaximumHeight(400)
        
        '''Style option'''
        self.style = QCheckBox('Curved')
        self.style.setChecked(True)
        
        self.cb.currentIndexChanged.connect(lambda x: self.draw())
        self.style.stateChanged.connect(lambda x: self.draw())
        
        '''Add everything in layout'''
        self.addWidget(self.canvas)
        subl.addStretch()
        subl.addWidget(self.cb)
        subl.addWidget(self.style)
        subl.addStretch()
        self.addLayout(subl)

        self.pos = None
        self.draw()

    def draw(self, neur=None, style=None):
        '''Draw with @neur in the center'''
        self.figure.clf()
        plt.figure(self.nb)
        if neur is None:
            neur = self.cb.currentText()
        if self.style.isChecked():
            style = CONN_STYLE
        self.pos = connections(neur, style)
        self.canvas.draw()
        
    @staticmethod
    def mousePressEvent(event, self):
        '''Put clicked neuron on the center'''
        X = self.canvas.width()
        Y = self.canvas.height()
        x = (event.pos().x() * 6 / X) - 3
        y = - (event.pos().y() * 6 / Y) + 3
        p = np.array([[x, y]])
        nodes = np.array(list(self.pos.values()))
        dist = np.sum((nodes - p)**2, axis=1)
        close = np.argmin(dist)
        if dist[close] < 0.2:
            neur = list(self.pos.keys())[close]        
            self.draw(neur=neur)

    def delete(self):   
        '''Delete slot'''
        self.setParent(None)
        self.cb.setParent(None)
        self.style.setParent(None)
        self.canvas.setParent(None)


class Window(QWidget):
    '''Main window containing potentially several visualisations'''

    def __init__(self):
        super(Window, self).__init__()

        self.neurons = []
        layout = QVBoxLayout()
        self.visu_layout = QHBoxLayout()

        '''Buttons to add or remove slots'''
        self.b1 = QPushButton("Add slot")
        self.b1.clicked.connect(self.add_visu)
        self.b2 = QPushButton("Remove slot")
        self.b2.clicked.connect(self.remove_visu)

        subl = QHBoxLayout()
        subl.addWidget(self.b1)
        subl.addWidget(self.b2)
        layout.addLayout(subl)
        self.visu_layout.addLayout(Visu())
        layout.addLayout(self.visu_layout)
        self.setLayout(layout)

        self.resize(500, 500)
        self.move(300, 300)
        self.setWindowTitle("Connectome Visualizer")

    def add_visu(self):
        '''Add neuron visalization'''
        self.neurons.append(Visu())
        self.visu_layout.addLayout(self.neurons[-1])

    def remove_visu(self):
        '''Remove last neuron visualization'''
        self.neurons[-1].delete()
        self.visu_layout.removeItem(self.neurons[-1])
        self.neurons.pop()


if __name__=='__main__':

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())

