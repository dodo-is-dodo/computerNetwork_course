import sys
import socket
import select
import time
from threading import Timer

class Medium:
    def __init__(self, e):
        self.HOST = ''
        self.SOCKET_LIST = []
        self.PORT = 9009 
        self.e = e

        # Settable parameters
        self.NUM_OF_NODES = 10 # The maximum number of nodes
        self.BANDWIDTH = 10000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
        self.MTU = 1000 # Maximum Transmit Unit for this medium (B)
        self.RECV_BUFFER = 2*self.MTU # Receive buffer size
        self.PDELAY = 0.1 # Propagation delay (s)
        self.medium_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.medium_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.medium_socket.bind((self.HOST, self.PORT))
        self.medium_socket.listen(self.NUM_OF_NODES)
        self.SOCKET_LIST.append(self.medium_socket)
        print("Medium is Activated (port:" + str(self.PORT) + ") ")

    def run(self):
        t=None; # Event Scheduler
        while 1:
            try:
                # Get the list sockets which are ready to be read through select
                ready_to_read, ready_to_write, in_error = select.select(self.SOCKET_LIST, [], [], 0)

                for sock in ready_to_read:
                # A new connection request received
                    if sock == self.medium_socket: # 0.0.0.0 : 9009 (sock)
                        sockfd, addr = self.medium_socket.accept()
                        self.SOCKET_LIST.append(sockfd)
                        print("Node (%s, %s) connected" % addr)
                    # A message from a node, not a new connection
                    else: # 127.0.0.1 : 9009 (sock)
                        try:
                        # Receiving packet from the socket.
                            packet = sock.recv(self.RECV_BUFFER)
                            if packet:
                                # Check medium here!
                                # if STATUS == BUSY:
                                if self.e.is_set():
                                    print('Collision has happend on medium!')
                                    t.cancel()
                                    Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.change_status).start() # Collided packet is still in medium
                                    # Collision occurs!
                                    # elif STATUS ==IDLE:
                                    # elif not e.is_set():
                                else:
                                    self.change_status() #Change status to busy
                                    # Message packet is being propagated to nodes through medium
                                    t=Timer(self.MTU/self.BANDWIDTH+self.PDELAY, self.forward_pkt, (sock, packet))
                                    t.start()
                                    # else:
                                    #   print('Undefined status')
                            else:
                                if sock in self.SOCKET_LIST:
                                    print("Node (%s, %s) disconnected" % sock.getpeername())
                                    self.SOCKET_LIST.remove(sock)
                                    continue

                        # Exception
                        except Exception as e:
                            print("medium ", e)
                            if sock in self.SOCKET_LIST:
                                print("Error! Check Node (%s, %s)" % sock.getpeername())
                                self.SOCKET_LIST.remove(sock)
                            continue
            except:
                print('\nMedium program is terminated')
                self.medium_socket.close()
                sys.exit()

# Forward_pkt to all connected nodes exclude itself(source node)
    def forward_pkt (self, sock, message):
        # global STATUS
        ACK = "ACK"

        for socket in self.SOCKET_LIST:
            # Send the message only to peer
            if socket != self.medium_socket and socket != sock:
                try:
                    socket.send(message)
                except:
                    # Broken socket connection
                    socket.close()
                    # Broken socket, remove it
                    if socket in SOCKET_LIST:
                        self.SOCKET_LIST.remove(socket)
            # elif socket == sock:
            #     try:
            #         socket.send(ACK.encode())
            #     except:
            #         # Broken socket connection
            #         socket.close()
            #         # Broken socket, remove it
            #         if socket in SOCKET_LIST:
            #             SOCKET_LIST.remove(socket)
        for socket in self.SOCKET_LIST:
            # Send the message only to peer
            if socket == sock:
                try:
                    socket.send(ACK.encode())
                except:
                    # Broken socket connection
                    socket.close()
                    # Broken socket, remove it
                    if socket in self.SOCKET_LIST:
                        self.SOCKET_LIST.remove(socket)

        #Packet transmission is finished
        self.change_status() #Change status to idle

    # Chaning medium status 
    def change_status(self):

        if self.e.is_set():
            self.e.clear()
        else:
            self.e.set()

    
def main(e):
    medium = Medium(e)
    sys.exit(medium.run())
