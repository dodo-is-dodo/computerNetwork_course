#2012313610
#Economics
#이도현
import sys
import multiprocessing as mp
import time
import node, medium
import random
import pandas as pd
from pandas import Series, DataFrame
from numpy import nan as NA

class Node_process:
    def __init__(self, n):
        self.pipe = mp.Pipe()
        self.node = mp.Process(name='node {0}'.format(n),
                                    target=node.main,
                                    args=(e, c, self.pipe[1], n))
    def order(self, data):
        self.pipe[0].send(data)

    def start(self):
        self.node.start()

if __name__ == '__main__':
    random.seed(time.time())
    node_number = 4
    e = mp.Event()
    c = mp.Event()
    s_pipe, r_pipe = mp.Pipe()
    m = mp.Process(name='m',
                   target=medium.main,
                   args=(e,c,r_pipe))

    node_list = []

    for i in range(node_number):
        node_list.append(Node_process(i))

    m.start()

    for i in range(node_number):
        node_list[i].start()

    time.sleep(3)

    end = time.time() + 15
    while time.time() < end:
        node_list[random.randint(0, node_number-1)].order("Hi!")
        time.sleep(0.135)
    for i in range(node_number):
        node_list[i].order('quit\n')
        node_list[i].node.join()
    # hdf = pd.HDFStore('data.h5')
    # print(hdf)
    # for i in range(node_number):
    #     print("Node {0}".format(i))
    #     print()
    #     print(hdf["node_{0}".format(i)])
    #     print()
    # hdf.close()
    s_pipe.send("quit\n")
    sys.exit()

