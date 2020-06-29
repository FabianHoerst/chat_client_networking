# Import all modules
import socket
import time
from datetime import datetime
from _thread import *
import threading
import sys

# Sending the data to the server and get data back
def Main(username):
    # declare username
    username = username
    # local host IP '127.0.0.1', socket settings 
    host = '127.0.0.1'
    port = 4017
    
    # set up socket and connect to the server 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # send username to the server
    s.send(username.encode())
    
    # check if username is in use
    flag = (s.recv(1).decode())
    print(s.recv(1024).decode())
    while flag == '0':
        s.close()
        username = input('Username: ')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(username.encode())
        flag = s.recv(1)
        print(s.recv(1024).decode())
    
    # start thread for receiving messages
    stop_threads = False
    getting = threading.Thread(target=threaded, args=(s, lambda : stop_threads, ), daemon=True)
    getting.start()
    
    # first destination (whether one or multiple (groupchat))
    destination = change_client()

    # loop: waiting for input of the user and then send data to the server and so on
    while True:
        # create the message and get back data, destination and header
        data, destination, header = create_message(username, destination)
        message = header + data
        
        # if the user wants to quit, enter 'quit'
        if data == 'quit':
            s.send(message.encode())
            print('Connection closed!')
            break
          
        # change the destinations if the client wants to change the destination
        if data == 'change_client':
            destination = change_client()
            continue
            
        # make message out of data and header
        message = header + data
        # send message
        s.send(message.encode())
    
    # If the clients quit, close the socket and stop the thread for receiving the messages
    s.close()
    stop_threads = True
    print('Everything closed!')
    return 0


# thread updating from server
def threaded(s, stop):
    try:
        while True:
            # Message received from the server
            receiver, sender, timestamp, length, data = extract_message(s)
            # display response from server
            print(f'{sender}, {timestamp}: {data}')
            if stop(): 
                break
    except:
        pass
        

# Build a message
def create_message(username, destination):
    data = input('')
    header = create_header(username, destination, data)
    return data, destination, header

# build the header
def create_header(username, destination, data):
    #fixed length strings
    number_of_receivers = '{:<2}'.format(len(destination))
    sender = '{:<20}'.format(username)
    receiver = ''
    for element in destination:
        receiver += '{:<20}'.format(element)
        receiver += '/'
    timestamp = datetime.now().strftime("%H" + ":" + "%M" + ":" + "%S")
    length = '{:<10}'.format(len(data))
    header = str(f'{number_of_receivers}/{receiver}{sender}/{timestamp}/{length}')
    return header

# extract the data that is inside the header and extract the data
def extract_message(s):
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
 
# change the client to get new destinations
def change_client():
    receiver = input('Destination:')
    destination = []
    # groupchat
    if receiver == 'groupchat':
        print('Type in the name of the desired group members. If you have typed in all group members,')
        print('type in \'ready\' to start the conversation')
        i = 1
        while True:
            receiver = input((f'Destination {i}:'))
            if receiver == 'ready':
                break
            destination.append(receiver)
            i += 1
    # kein groupchat
    else: 
        destination.append(receiver)
    return destination
            
    
# Start routine
if __name__ == '__main__':
    print('To start the conversation, type in your username. Forbidden names are \'ready\' and \'groupchat\' ')
    username = input('Username: ')
    print('--- Hello ' + username + '---')
    print('To send a message to one client, just enter the client\'s name in destination.')
    print('After that you can start the chat. If you want to send a message to another client,')
    print('Just type in change_client. If you want to start a groupchat, type in groupchat in destination field')
    Main(username)
        
