import base64
import socket

import cv2
import numpy as np
import imutils


class UDP:
    def __init__(self):
        self.BUFF_SIZE = 65536  # Kullanılabilecek veri bellek boyutu
        self.Main_socket = socket.socket(socket.AF_INET,
                                         socket.SOCK_DGRAM)  # UDP için temel tanımlama   " (socket.SOCK_DGRAM) ifadesi udp olduğunu belirtiyor."
        self.Main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)  # UDP için temel tanımlama
        self.port = 9999
