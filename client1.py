# ------------ Header Files ------------------#

from __future__ import division, print_function, unicode_literals  #to ease migration to future versions of Python 

import sys  #how Python script is interacting with the host system
import random 
import argparse #to parse command-line arguments
import logging #to track events that happen when some software runs
from Tkinter import *
import tkFileDialog
import tkMessageBox
import os #provides a way of using operating system dependent functionality
import PIL #support for opening, manipulating, and saving many different image file formats
from PIL import Image
import math
from Crypto.Cipher import AES
import hashlib #accessing different cryptographic hashing algorithms
import binascii #number of methods to convert between binary and various ASCII-encoded binary representations
import numpy as np
import socket #access to the BSD socket interface



global password 

def load_image(name):
    return Image.open(name)

# ----------------- Functions for 2-share encryption ---------------------#
def prepare_message_image(image, size):
    if size != image.size:
        image = image.resize(size, Image.ANTIALIAS)
    return image

def generate_secret(size, secret_image = None):
    width, height = size
    new_secret_image = Image.new(mode = "RGB", size = (width * 2, height * 2))

    for x in range(0, 2 * width, 2):
        for y in range(0, 2 * height, 2):
            color1 = np.random.randint(255)
            color2 = np.random.randint(255)
            color3 = np.random.randint(255)
            new_secret_image.putpixel((x,  y),   (color1,color2,color3))
            new_secret_image.putpixel((x+1,y),   (255-color1,255-color2,255-color3))
            new_secret_image.putpixel((x,  y+1), (255-color1,255-color2,255-color3))
            new_secret_image.putpixel((x+1,y+1), (color1,color2,color3))
                
    return new_secret_image

def generate_ciphered_image(secret_image, prepared_image):
    width, height = prepared_image.size
    ciphered_image = Image.new(mode = "RGB", size = (width * 2, height * 2))
    for x in range(0, width*2, 2):
        for y in range(0, height*2, 2):
            sec = secret_image.getpixel((x,y))
            msssg = prepared_image.getpixel((int(x/2),int(y/2)))
            color1 = (msssg[0]+sec[0])%256
            color2 = (msssg[1]+sec[1])%256
            color3 = (msssg[2]+sec[2])%256
            ciphered_image.putpixel((x,  y),   (color1,color2,color3))
            ciphered_image.putpixel((x+1,y),   (255-color1,255-color2,255-color3))
            ciphered_image.putpixel((x,  y+1), (255-color1,255-color2,255-color3))
            ciphered_image.putpixel((x+1,y+1), (color1,color2,color3))
                
    return ciphered_image


def generate_image_back(secret_image, ciphered_image):
    width, height = secret_image.size
    new_image = Image.new(mode = "RGB", size = (int(width / 2), int(height / 2)))
    for x in range(0, width, 2):
        for y in range(0, height, 2):
            sec = secret_image.getpixel((x,y))
            cip = ciphered_image.getpixel((x,y))
            color1 = (cip[0]-sec[0])%256
            color2 = (cip[1]-sec[1])%256
            color3 = (cip[2]-sec[2])%256
            new_image.putpixel((int(x/2),  int(y/2)),   (color1,color2,color3))
               
    return new_image


#------------------------ 2-share encryption -------------------#
def level_one_encrypt(Imagename):
    message_image = load_image(Imagename)
    size = message_image.size
    width, height = size

    secret_image = generate_secret(size)
    secret_image.save("secret.jpeg")

    prepared_image = prepare_message_image(message_image, size)
    ciphered_image = generate_ciphered_image(secret_image, prepared_image)
    ciphered_image.save("2-share_encrypt.jpeg")



# -------------------- construct encrypted image  ----------------#
def construct_enc_image(ciphertext,relength,width,height):
    asciicipher = binascii.hexlify(ciphertext)
    def replace_all(text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text

    # use replace function to replace ascii cipher characters with numbers
    reps = {'a':'1', 'b':'2', 'c':'3', 'd':'4', 'e':'5', 'f':'6', 'g':'7', 'h':'8', 'i':'9', 'j':'10', 'k':'11', 'l':'12', 'm':'13', 'n':'14', 'o':'15', 'p':'16', 'q':'17', 'r':'18', 's':'19', 't':'20', 'u':'21', 'v':'22', 'w':'23', 'x':'24', 'y':'25', 'z':'26'}
    asciiciphertxt = replace_all(asciicipher, reps)

        # construct encrypted image
    step = 3
    encimageone=[asciiciphertxt[i:i+step] for i in range(0, len(asciiciphertxt), step)]
       # if the last pixel RGB value is less than 3-digits, add a digit a 1
    if int(encimageone[len(encimageone)-1]) < 100:
        encimageone[len(encimageone)-1] += "1"
        # check to see if we can divide the string into partitions of 3 digits.  if not, fill in with some garbage RGB values
    if len(encimageone) % 3 != 0:
        while (len(encimageone) % 3 != 0):
            encimageone.append("101")

    encimagetwo=[(int(encimageone[int(i)]),int(encimageone[int(i+1)]),int(encimageone[int(i+2)])) for i in range(0, len(encimageone), step)]
    print(len(encimagetwo))
    while (int(relength) != len(encimagetwo)):
        encimagetwo.pop()

    encim = Image.new("RGB", (int(width),int(height)))
    encim.putdata(encimagetwo)
    encim.save("visual_encrypt.jpeg")


#------------------------- Visual-encryption -------------------------#
def encrypt(imagename,password):
    plaintext = list()
    plaintextstr = ""

    im = Image.open(imagename) 
    pix = im.load()

    width = im.size[0]
    height = im.size[1]
    
    # break up the image into a list, each with pixel values and then append to a string
    for y in range(0,height):
        for x in range(0,width):
            print (pix[x,y]) 
            plaintext.append(pix[x,y])
    print(width)
    print(height)

    # add 100 to each tuple value to make sure each are 3 digits long.  
    for i in range(0,len(plaintext)):
        for j in range(0,3):
            aa = int(plaintext[i][j])+100
            plaintextstr = plaintextstr + str(aa)


    # length save for encrypted image reconstruction
    relength = len(plaintext)

    # append dimensions of image for reconstruction after decryption
    plaintextstr += "h" + str(height) + "h" + "w" + str(width) + "w"

    # make sure that plantextstr length is a multiple of 16 for AES.  if not, append "n". 
    while (len(plaintextstr) % 16 != 0):
        plaintextstr = plaintextstr + "n"

    # encrypt plaintext
    obj = AES.new(password, AES.MODE_CBC, 'This is an IV456')
    ciphertext = obj.encrypt(plaintextstr)

    # write ciphertext to file for analysis
    cipher_name = imagename + ".crypt"
    g = open(cipher_name, 'w')
    g.write(ciphertext)
    construct_enc_image(ciphertext,relength,width,height)
    print("Visual Encryption done.......")
    level_one_encrypt("visual_encrypt.jpeg")
    print("2-Share Encryption done.......")
        



# ---------------------- decryption ---------------------- #
def decrypt(ciphername,password):

    secret_image = Image.open("secret.jpeg")
    ima = Image.open("2-share_encrypt.jpeg")
    new_image = generate_image_back(secret_image, ima)
    new_image.save("2-share_decrypt.jpeg")
    print("2-share Decryption done....")
    cipher = open(ciphername,'r')
    ciphertext = cipher.read()

    # decrypt ciphertext with password
    obj2 = AES.new(password, AES.MODE_CBC, 'This is an IV456')
    decrypted = obj2.decrypt(ciphertext)

    # parse the decrypted text back into integer string
    decrypted = decrypted.replace("n","")

    # extract dimensions of images
    newwidth = decrypted.split("w")[1]
    newheight = decrypted.split("h")[1]

    # replace height and width with emptyspace in decrypted plaintext
    heightr = "h" + str(newheight) + "h"
    widthr = "w" + str(newwidth) + "w"
    decrypted = decrypted.replace(heightr,"")
    decrypted = decrypted.replace(widthr,"")

    # reconstruct the list of RGB tuples from the decrypted plaintext
    step = 3
    finaltextone=[decrypted[i:i+step] for i in range(0, len(decrypted), step)]
    finaltexttwo=[(int(finaltextone[int(i)])-100,int(finaltextone[int(i+1)])-100,int(finaltextone[int(i+2)])-100) for i in range(0, len(finaltextone), step)]

    # reconstruct image from list of pixel RGB tuples
    newim = Image.new("RGB", (int(newwidth), int(newheight)))
    newim.putdata(finaltexttwo)
    newim.save("visual_decrypt.jpeg")
    print("Visual Decryption done......")
    
   
# ---------------------- Send ---------------------- #

def conn1():
	port = 60000                    # Reserve a port for your service.
	s = socket.socket()             # Create a socket object
	s.bind(('', port))            # Bind to the port
	s.listen(5)                     # Now wait for client connection.

	print ("Server listening....")
	global conn
	conn, addr = s.accept()     # Establish connection with client.
	print ('Got connection from', addr)
	data = conn.recv(1024)
	print('Server received', repr(data))
	
	tkMessageBox.showinfo("User Connected","Client in receiving mode")

def send():
	conn.send("I")
	conn.close()
	send1()
	send2()
	send3()
	tkMessageBox.showinfo("Done Sending","Client sent all the files")


def send1():
	port = 63000                    # Reserve a port for your service.
	s = socket.socket()             # Create a socket object
	s.bind(('', port))            # Bind to the port
	s.listen(5)                     # Now wait for client connection.

	print ("Server listening....")
	global conn
	conn, addr = s.accept()     # Establish connection with client.
	print ('Got connection from', addr)
	data = conn.recv(1024)
	print('Server received', repr(data))
	f4='images.jpeg.crypt'
	
    #file_path_e = os.path.dirname(filename)
	f = open(f4,'rb')
	l = f.read(1024)
	while (l):
	   conn.send(l)
	   #print('Sent ',repr(l))
	   l = f.read(1024)
	f.close()

	print('Done sending crypt file')
	
	conn.close()
   


def send2():
	port = 62000                    # Reserve a port for your service.
	s = socket.socket()             # Create a socket object
	s.bind(('', port))            # Bind to the port
	s.listen(5)                     # Now wait for client connection.

	print ("Server listening....")
	global conn
	conn, addr = s.accept()     # Establish connection with client.
	print ('Got connection from', addr)
	data = conn.recv(1024)
	print('Server received', repr(data))
	f2='secret.jpeg'
	
    #file_path_e = os.path.dirname(filename)
	f = open(f2,'rb')
	l = f.read(1024)
	while (l):
	   conn.send(l)
	   #print('Sent ',repr(l))
	   l = f.read(1024)
	f.close()

	print('Done sending secret image')
	conn.close()
		
		

def send3():
	port = 61000                    # Reserve a port for your service.
	s = socket.socket()             # Create a socket object
	s.bind(('', port))            # Bind to the port
	s.listen(5)                     # Now wait for client connection.

	print ("Server listening....")
	global conn
	conn, addr = s.accept()     # Establish connection with client.
	print ('Got connection from', addr)
	data = conn.recv(1024)
	print('Server received', repr(data))
	f1='2-share_encrypt.jpeg'

	#file_path_e = os.path.dirname(filename)
	f = open(f1,'rb')
	l = f.read(1024)
	while (l):
	   conn.send(l)
	   #print('Sent ',repr(l))
	   l = f.read(1024)
	f.close()

	print('Done sending 2-share_encrypt image')
	conn.close()
	print('Connection Closed')
   

# ---------------------
# GUI stuff starts here
# ---------------------

def pass_alert():
   tkMessageBox.showinfo("Password Alert","Please enter a password.")

def enc_success(imagename):
   tkMessageBox.showinfo("Success","Encrypted Image: " + imagename)

# image encrypt button event
def image_open():
    global file_path_e

    enc_pass = passg.get()
    if enc_pass == "":
        pass_alert()
    else:
        password = hashlib.sha256(enc_pass).digest()
        filename = tkFileDialog.askopenfilename()
        file_path_e = os.path.dirname(filename)
        encrypt(filename,password)

# image decrypt button event
def cipher_open():
    global file_path_d

    dec_pass = passg.get()
    if dec_pass == "":
        pass_alert()
    else:
        password = hashlib.sha256(dec_pass).digest()
        filename = tkFileDialog.askopenfilename()
        file_path_d = os.path.dirname(filename)
        decrypt(filename,password)

class App:
  def __init__(self, master):
    global passg
    title = "CLIENT 1"
    author = "Yash  -  Shivam"
    msgtitle = Message(master, text =title)
    msgtitle.config(font=('helvetica', 17, 'bold'), width=200)
    msgauthor = Message(master, text=author)
    msgauthor.config(font=('helvetica',10), width=200)

    canvas_width = 200
    canvas_height = 50
    w = Canvas(master,
           width=canvas_width,
           height=canvas_height)
    msgtitle.grid(row = 1, column = 1)
    msgauthor.grid(row = 4, column = 1)
    w.grid()

    passlabel = Label(master, text="Enter Encrypt/Decrypt Password:")
    passlabel.grid(row = 6, column = 1)
    passg = Entry(master, show="*", width=20)
    passg.grid(row = 7, column = 1)

    self.encrypt = Button(master,
                         text="Encrypt", fg="black",
                         command=image_open, width=25,height=2)
    self.encrypt.grid(row = 10,column = 0)
    self.decrypt = Button(master,
                         text="Decrypt", fg="black",
                         command=cipher_open, width=25,height=2)
    self.decrypt.grid(row = 10, column = 2)
    self.connect = Button(master,
                         text="Connect", fg="black",
                         command=conn1, width=25,height=2)
    self.connect.grid(row = 10, column = 1)
    
    self.send = Button(master,
                         text="Send Files", fg="black",
                         command=send, width=25,height=4)
    self.send.grid(row = 12, column = 1)
    
   
	
	
# ------------------ MAIN -------------#
root = Tk()
root.wm_title("Image Encryption")
app = App(root)
root.mainloop()
