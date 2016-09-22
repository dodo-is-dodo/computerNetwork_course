import multiprocessing as mp
import time
import node, medium
import random

class Node_process:
    def __init__(self, n):
        self.pipe = mp.Pipe()
        self.node = mp.Process(name='node {0}'.format(n),
                                    target=node.node,
                                    args=(e, self.pipe[1]))
    def order(self, data):
        self.pipe[0].send(data)

    def start(self):
        self.node.start()
    

if __name__ == '__main__':
    node_number = 2
    e = mp.Event()
    m = mp.Process(name='m', 
                   target=medium.medium,
                   args=(e,))

    node_list = []
    
    for i in range(node_number):
        node_list.append(Node_process(i))
        
    m.start()
    for i in range(node_number):
        node_list[i].start()
        
    time.sleep(1)

    while True:
        node_list[random.randint(0, node_number-1)].order("Hi!")
        time.sleep(0.05)
