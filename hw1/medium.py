#2012313610
#Economics
#이도현
import sys
import pickle
import socket
import select
import time
from threading import Timer

class Medium:
    def __init__(self, e, c, pipe):
        self.HOST = ''
        self.socket_list = []
        self.PORT = 9009
        self.e = e
        self.c = c
        self.pipe = pipe
        self.STATUS = False

        # Settable parameters
        self.NUM_OF_NODES = 10 # The maximum number of nodes
        self.BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
        self.MTU = 10000 # Maximum Transmit Unit for this medium (B)
        self.RECV_BUFFER = 2*self.MTU # Receive buffer size
        self.PDELAY = 0.01 # Propagation delay (s)
        self.medium_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.medium_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.medium_socket.bind((self.HOST, self.PORT))
        self.medium_socket.listen(self.NUM_OF_NODES)
        self.socket_list.append(self.medium_socket)
        self.socket_list.append(self.pipe)
        print("Medium is Activated (port:" + str(self.PORT) + ") ")

    def run(self):
        Timer(1, self.send_addrs).start() # Collided packet is still in medium
        t1 = Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.change_status) # Collided packet is still in medium
        t2 = Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.change_collision) # Collided packet is still in medium
        # Thread(None, self.delay_change).start()
        while 1:
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], [])
            try:
                for sock in ready_to_read:
                # A new connection request received
                    if sock == self.medium_socket: # 0.0.0.0 : 9009 (sock)
                        sockfd, addr = self.medium_socket.accept()
                        self.socket_list.append(sockfd)
                        print("Node (%s, %s) connected" % addr)
                    elif sock == self.pipe:
                        cmd = self.pipe.recv() 
                        if cmd == 'quit\n':
                            self.medium_socket.close()
                            sys.exit()
                    # A message from a node, not a new connection
                    else: # 127.0.0.1 : 9009 (sock)
                        try:
                        # Receiving packet from the socket.
                            packet = sock.recv(self.RECV_BUFFER)
                            if packet:
                                if self.STATUS:
                                    print('!!!!Collision has happend on medium!!!!')
                                    t.cancel()
                                    self.c.set()
                                    if t1.is_alive() or t2.is_alive():
                                        t1.cancel()
                                        t2.cancel()
                                    t1 = Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.change_status) # Collided packet is still in medium
                                    t2 = Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.change_collision) # Collided packet is still in medium
                                    t1.start()
                                    t2.start()
                                else:
                                    self.change_status() #Change status to busy
                                    # Message packet is being propagated to nodes through medium
                                    t=Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.forward_pkt, (sock, packet))
                                    t.start()
                            else:
                                if sock in self.socket_list:
                                    print("Node (%s, %s) disconnected" % sock.getpeername())
                                    self.socket_list.remove(sock)
                                    continue

                        # Exception
                        except Exception as e:
                            print("medium ", e)
                            if sock in self.socket_list:
                                print("Error! Check Node (%s, %s)" % sock.getpeername())
                                self.socket_list.remove(sock)
                            continue
            except Exception as e:
                print(e)
                print('\nMedium program is terminated')
                self.medium_socket.close()
                sys.exit()

# Forward_pkt to all connected nodes exclude itself(source node)

    def forward_pkt (self, sock, message):
        data = pickle.loads(message)
        dest = data[1]
        # print("fwd packet : ", str(data))
        for socket in self.socket_list:
            if socket != self.medium_socket and socket!= self.pipe and socket.getpeername() == dest:
                try:
                    print("fwd packet : ", str(data))
                    socket.send(message)
                except:
                    # Broken socket connection
                    socket.close()
                    # Broken socket, remove it
                    if socket in socket_list:
                        self.socket_list.remove(socket)

        #Packet transmission is finished
        self.change_status() #Change status to idle


    def send_addrs(self):
        addr_list = []
        for sock in self.socket_list:
            if sock != self.medium_socket and sock != self.pipe:
                addr_list.append(sock.getpeername())
        for sock in self.socket_list:
            if sock != self.medium_socket and sock != self.pipe:
                sock.send(pickle.dumps(addr_list))



    # Chaning medium status 
    def change_status(self):
        Timer(self.PDELAY/4, self.change_out_status).start() # Collided packet is still in medium
        if self.STATUS:
            # print("STATUS is False")
            self.STATUS = False
        else:
            # print("STATUS is True")
            self.STATUS = True

    def change_out_status(self):
        if self.e.is_set():
            # print("e is False")
            self.e.clear()
        else:
            # print("e is True")
            self.e.set()
            
    def change_collision(self):
        if self.c.is_set():
            # print("idle now")
            self.c.clear()
        else:
            self.c.set()
            
def main(e, c, pipe):
    medium = Medium(e, c, pipe)
    sys.exit(medium.run())
