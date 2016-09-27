#2012313610
#Economics
#이도현
import sys
import socket
import pickle
import select
from threading import Timer, Thread
import time
import random
from datetime import datetime
import pandas as pd
from pandas import Series, DataFrame
from numpy import nan as NA

#colorPrint
def prRed(prt): print("\033[31m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[32m {}\033[00m" .format(prt))
def prOrange(prt): print("\033[33m {}\033[00m" .format(prt))
def prBlue(prt): print("\033[34m {}\033[00m" .format(prt))
def prPurple(prt): print("\033[35m {}\033[00m" .format(prt))
def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))
def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))
def prBlack(prt): print("\033[70m {}\033[00m" .format(prt))

color_list = [prRed, prBlue, prGreen, prOrange, prPurple, prYellow, prCyan, prLightGray, prBlack]

class Node:
    def __init__(self, e, c, pipe, n):
        self.MTU = 10000 # Maximum Transmit Unit for this medium (B)
        self.RECV_BUFFER = 2*self.MTU # Receive buffer size
        self.BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
        self.PDELAY = 0.05 # Propagation delay (s)
        self.TOTALDELAY = (self.MTU/self.BANDWIDTH) * 2
        self.TIME_SLOT = (self.TOTALDELAY)*2/100
        print(self.TOTALDELAY)
        self.e = e
        self.c = c
        self.s = self.connect_to_medium()
        self.addr = self.s.getsockname()
        self.pipe = pipe
        self.socket_list = [self.pipe, self.s]
        self.n = n
        self.data = 0
        self.df = DataFrame(columns=["deliver_time", "K", "success"])
        random.seed(n*9999)

    def connect_to_medium(self):
        host = '127.0.0.1' # Local host address
        port = 9009 # Medium port number
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((host, port))
        except:
            print('Unable to connect')
            sys.exit()

        print('Connected. You can start sending packets')

        return s
    
    def packet_generator(self, dest):
        self.data += 1
        data = [self.addr, dest, "DATA", [self.data]]
        self.start = time.time()
        
        return pickle.dumps(data)

    def chk_medium(self):
        return self.e.is_set()

    # Make and transmit a data packet

    def transmit(self, packet):
        self.s.send(packet)
        color_list[self.n % len(color_list)](str(self.n) + ' Transmit a packet ' + str(self.data) + "  " + str(time.time()))

    # Extract data

    def extract_data(self, packet):
        return pickle.loads(packet)

    def cprint(self, s):
        color_list[self.n](s)

    def sense_send_detect(self):
        while self.chk_medium():
            pass
        self.transmit(self.trans_packet) # Transmit a data packet
        end = time.time() + self.TOTALDELAY #+ 0.002
        while time.time() < end:
            if self.c.is_set():
                self.cprint("**detected collision**")
                return False
        self.cprint("successfully sent packet")
        return True

    def threadManage(self):
        # time.sleep(self.TIME_SLOT * random.randint(0, 2**(self.K-1)))
        while not self.sense_send_detect():
            self.K += 1
            if self.K > 8:
                self.cprint("Failed to send packet")
                break
            wait = self.TIME_SLOT * random.randint(0, 2**(self.K))
            start = time.time()
            self.cprint("start : " + str(start) + " wait : " + str(wait))
            time.sleep(wait)
            self.cprint("end : " + str(time.time()) + " diff : " + str(time.time() - start))
        self.df.loc[len(self.df)] = [time.time() - self.start, self.K, int(self.K < 9)]
        self.K = 3
        self.send_state = False
        # self.socket_list.append(self.pipe)

    def run(self):
        self.addr_list = pickle.loads(self.s.recv(self.RECV_BUFFER))
        self.addr_list.remove(self.addr)
        self.K=3
        self.send_state = False
        while 1:
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], [])

            for sock in ready_to_read:
                if sock == self.s:
                    # Incoming data packet from medium
                    packet = sock.recv(self.RECV_BUFFER) # Recive a packet
                    data = self.extract_data(packet) # Extract data in a packet
                    if not data:
                        print('\nDisconnected')
                        sys.exit()
                    else:
                        color_list[self.n]("Receive a packet : %s" % str(data))
                else:
                    if not self.send_state:
                        cmd = self.pipe.recv() 
                        if cmd == 'quit\n':
                            self.s.close()
                            # hdf  = pd.HDFStore("data.h5")
                            # hdf["node_{0}".format(self.n)] = self.df
                            # hdf.close()
                            # print(str(self.n), " hdf saved")
                            print(self.df)
                            sys.exit()
                        dest = self.addr_list[random.randint(0, len(self.addr_list)-1)]
                        self.trans_packet = self.packet_generator(dest) # Data will be stored in packet
                        self.send_state = True
                        self.t = Thread(group=None, target=self.threadManage)
                        self.t.start()

def main(e, c, pipe, n):
    node = Node(e, c, pipe, n)
    sys.exit(node.run())
