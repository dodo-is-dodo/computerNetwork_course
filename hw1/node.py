import sys
import socket
import select
from threading import Timer
import time
import random
from datetime import datetime

def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))
def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))
def prPurple(prt): print("\033[95m {}\033[00m" .format(prt))
def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))
def prBlack(prt): print("\033[98m {}\033[00m" .format(prt))

color_list = [prRed, prCyan, prYellow, prGreen, prLightPurple, prLightGray, prBlack]

class Node:
    def __init__(self, e, pipe, n):
        self.MTU = 1000 # Maximum Transmit Unit for this medium (B)
        self.RECV_BUFFER = 2*self.MTU # Receive buffer size
        self.BANDWIDTH = 10000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
        self.TIME_SLOT = (self.MTU/self.BANDWIDTH)/100
        self.PDELAY = 0.1 # Propagation delay (s)
        self.e = e
        self.s = self.connect_to_medium()
        self.pipe = pipe
        self.n = n
        random.seed(n*9999)

    def connect_to_medium(self):
        host = '127.0.0.1' # Local host address
        port = 9009 # Medium port number
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.MTU/self.BANDWIDTH + self.PDELAY + 0.001)
        try:
            s.connect((host, port))
        except:
            print('Unable to connect')
            sys.exit()

        print('Connected. You can start sending packets')

        return s
    
    def chk_medium(self):
        return self.e.is_set()

    # Make and transmit a data packet
    def transmit(self, trans_data):

        packet = trans_data

        if len(packet) > self.MTU:
            print('Cannot transmit a packet -----> packet size exceeds MTU')
        else:
            packet = packet + '0'*(self.MTU-(len(trans_data)))
            self.s.send(packet.encode())
            color_list[self.n](str(self.n) + ' Transmit a packet')

    # Extract data
    def extract_data(self, packet):
        i=0
        for c in packet.decode():
            if c == '0':
                break
            else:
                i=i+1
                continue

        data = packet[0:i]
        return data

    def run(self):
        K=3
        while 1:
            socket_list = [self.pipe, self.s]

            # Get the list sockets which are readable
            ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])

            for sock in ready_to_read:
                if sock == self.s:
                    # Incoming data packet from medium
                    packet = sock.recv(self.RECV_BUFFER) # Recive a packet
                    data = self.extract_data(packet) # Extract data in a packet
                    if not data:
                        print('\nDisconnected')
                        sys.exit()
                    else:
                        print("\nReceive a packet : %s" % data)
                        # sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()
                else:
                    # random.seed(datetime.now())
                    if self.pipe in socket_list:
                        cmd = self.pipe.recv() 
                        if cmd == 'quit\n':
                            s.close()
                            sys.exit()
                        socket_list.remove(self.pipe)
                    while self.chk_medium():
                        pass
                    time.sleep(self.TIME_SLOT * random.randint(0, 2**K-1))
                    trans_data = 'DATA' # Data will be stored in packet
                    self.transmit(trans_data) # Transmit a data packet
                    try:
                        ack = self.s.recv(self.RECV_BUFFER)
                        if ack.decode() == "ACK":
                            color_list[self.n](str(self.n) + " received ack")
                            socket_list.append(self.pipe)
                            K = 3
                            break
                    except Exception as error:
                        print(error)
                        K += 1
                        # if (K > 8):
                        #     print("Failed to send packet")
                        #     break
        

def main(e, pipe, n):
    node = Node(e, pipe, n)
    sys.exit(node.run())
