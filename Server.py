import socket
from _thread import *
import threading
from datetime import datetime

print_lock = threading.Lock()

# thread function 
def threaded(c, clients):
    # Get the username
    username = (c.recv(1024)).decode()
    
    # Register new user
    if not username in clients:
        print('New User added: ' + str(username))
        clients[username]=c
        return_clients= ''
        for keys in clients:
            return_clients += str(keys)
            return_clients += ', '
        # send 1 as a success code that the user has registered successful
        c.send('1'.encode())
        c.send(('Server added you! Users online: ' + return_clients[:-2]).encode())
    # if the user exists, return error code  
    else:
        print('Username already in use! Try a new name')
        # send 0 as an error code that the user has not registered successful
        c.send('0'.encode())
        c.send(('Username already in use! Try a new name').encode())
        c.close()
        return 0
    
    # Data exchange between server and the client
    while True:
        # get informations out of the received message
        receiver, sender, timestamp, length, data = extract_message(c)
        header = create_header(sender, receiver, timestamp, data)
        
        # test if client wants to disconnect
        if data == 'quit':
            # Send a broadcast message, that the user has left
            data = str('User ' + sender + ' has left the chat!')
            sender = 'Server'
            header = create_header(sender, receiver, timestamp, data)
            return_message = header + data
            # Send to every connected client
            for element in clients:
                c_broadcast = clients[element]
                c_broadcast.send(return_message.encode())
            break
        
        # create the message
        header = create_header(sender, receiver, timestamp, data)
        return_message = header + data
                
        # Try to distribute message to the receivers
        try:
            for element in receiver:
                c_distribute = clients[element]
                c_distribute.send(return_message.encode())
            c.send(return_message.encode())
        except:
            # except: User is not reachable
            # make a notification to the sender
            header = create_header('server', receiver, timestamp, 'User not found')
            return_message = header + 'User not found'
            c.send(return_message.encode())
            print('User not found')
    
    # Close of the connections
    del clients[username]
    c.close()
    print('Bye ' + str(username))
    
# get the data out of an incoming message    
def extract_message(s):
    # get the informations out of the message
    number_of_receivers = (int((s.recv(2)).decode()))
    header = (s.recv(40+number_of_receivers*20-2)).decode()
    header_list = header.split('/')
    receiver = header_list[1:number_of_receivers+1]
    for i in range (0,number_of_receivers):
        receiver[i] = receiver[i].strip()
    sender = (header_list[number_of_receivers+1]).strip()
    timestamp = (header_list[number_of_receivers+2]).strip()
    length = int((header_list[number_of_receivers+3]).strip())
    data = (s.recv(1024).decode()).strip()
    return receiver, sender, timestamp, length, data

# Create a header for sending a message
def create_header(username, destination, timestamp, data):
    #fixed length strings
    number_of_receivers = '{:<2}'.format(len(destination))
    sender = '{:<20}'.format(username)
    receiver = ''
    for element in destination:
        receiver += '{:<20}'.format(element)
        receiver += '/'
    length = '{:<10}'.format(len(data))
    header = str(f'{number_of_receivers}/{receiver}{sender}/{timestamp}/{length}')
    return header
    
# main procedure: start the server and threads new connections
def Main():
    host = ""
    port = 4017
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    print('Socket binded to port', port)
    
    # put the socket into listening mode
    s.listen(5)
    print('Socket is listening')
    clients = {}
    # a forever loop until client wants to exit
    try:
        while True:
            # establish connection with client
            c, addr = s.accept()
            # lock acquired by client
            print('Connected to:', addr[0], ':', addr[1])
            # Start a new thread and return its identifier
            start_new_thread(threaded, (c,clients,))
            
    except KeyboardInterrupt:  
        print('Server beendet!')
    finally:
        s.close()
        print('Everything closed')

if __name__ == '__main__':
    Main()
