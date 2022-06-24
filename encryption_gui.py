import os
# e auf null setzen um später das syript vielleicht wieder auszuführen 
e = 0
# Alles installieren, was gebraucht wird und nicht schon installiert ist
try:
    import wget
except ImportError:
    print("Paket wget wird installiert...")
    os.system('pip install wget')
    import wget
    e = 1
try:
    import tkinter as tk
except ImportError:
    if e == 0:
        print("Paket tkinter wird installiert...")
    os.system('pip install tk')
    import tkinter as tk
    e = 1
try:
    import datetime
except ImportError:
    if e == 0:
        print("Paket datetime wird installiert...")
    os.system('pip install datetime') 
    import datetime
    e = 1
try:
    import PIL
except ImportError:
    if e == 0:
        print("Pakete PIL wird installiert...")
    os.system('pip install Pillow')
    import PIL
    e = 1
try:
    import matplotlib.pyplot as plt
except ImportError:
    if e == 0:
        print("Pakete matplotlib wird installiert...")
    os.system('pip install matplotlib')
    import matplotlib.pyplot as plt
    e = 1
try:
    import numpy
except ImportError:
    if e == 0:
        print("Pakete numpy wird installiert...")
    os.system('pip install numpy')
    import numpy
    e = 1

# Reset "pip uninstall wget -y & pip uninstall tk -y & pip uninstall datetime -y & pip uninstall Pillow -y"
import time
from PIL import Image
from tkinter import filedialog
from tkinter import * 
from tkinter.ttk import *

array = ['']
arrayfilename = ['']

# Aktuelles Datum einlesen
now = datetime.datetime.now()
histogramm = ['']

# Einzelne Datei einlesen und "verschlüsseln"
def encrypt_file(filename):
    print("\nProzess started")
    vortime = time.perf_counter()
    to_encrypt = open(filename, "rb").read()
    size = len(to_encrypt)
    key = os.urandom(size)
    with open(filename + ".key", "wb") as key_out:
        key_out.write(key)
    encrypted = bytes(a ^ b for (a, b) in zip(to_encrypt, key))
    with open(filename, "wb") as encrypted_out:
        encrypted_out.write(encrypted)    
    nachtime = time.perf_counter()
    wielange = round(nachtime - vortime, 3)
    print("\nFile is encrypted \nIt took " + str(wielange) + "seconds.")

# Einzelne Datei und key einlesen und "entschlüsseln"
def decrypt_file(filename, key):
    print("\nProzess started")
    vortime = time.perf_counter()
    file = open(filename, "rb").read()
    key = open(key, "rb").read()
    decrypted = bytes(a ^ b for (a, b) in zip(file, key))
    with open(filename, "wb") as decrypted_out:
        decrypted_out.write(decrypted)
    nachtime = time.perf_counter()
    wielange = round(nachtime - vortime, 3)
    print("\nFile is decrypted \nIt took " + str(wielange) + "seconds.")
# Nach Datei fragen
def enc():
    print("Select the file you want to encrypt")
    filename = filedialog.askopenfilename(title='Select the file you want to encrypt')
    encrypt_file(filename)
# Nach Datei fragen
def dec():
    print("Select the encrypted file")
    filename = filedialog.askopenfilename(title='Select the encrypted file')
    decrypt_file(filename, filename + ".key")

#folder---------------

# Verschlüsselungsvorgang
def encrypt(src, key_dst, filename): 
    to_encrypt = open(src + filename, "rb").read()
    size = len(to_encrypt)
    key = os.urandom(size)
    if not os.path.exists(os.path.dirname(key_dst)): 
        os.makedirs (os.path.dirname (key_dst))
    with open(key_dst + filename + ".key", "wb") as key_out: 
        key_out.write(key) 
    encrypted = bytes(a ^ b for (a, b) in zip(to_encrypt, key))
    with open(src + filename, "wb") as encrypted_out: 
        encrypted_out.write(encrypted)
# Entschlüsselungsvorgang
def decrypt(path, filename, key):
    file = open(path + filename, "rb").read() 
    key = open (key, "rb").read()
    decrypted = bytes (a ^ b for (a, b) in zip(file, key)) 
    with open (path + filename, "wb") as decrypted_out:
        decrypted_out.write(decrypted)

# Ganzen Ordner einlesen und "verschlüsseln"
def enc_folder(): 
    print("Select the folder you want to encrypt")
    src = filedialog.askdirectory(title='Select the folder you want to encrypt')
    print("Select the folder where the .key files will be stored")
    dst = filedialog.askdirectory(title='Select the folder where the .key files will be stored')
    print("\nProzess started")
    vortime = time.perf_counter()
    o = 0
    c = 0
    afs = 0
    for path, dirs, files in os.walk(src):
        if len(files) > 0: 
            for file in files:
                o = o + 1
                afs = afs + os.stat(path + '/' + file).st_size
                array.append(str(os.path.getsize(path + '/' + file)))
                arrayfilename.append(file)
    for path, dirs, files in os.walk(src):
        if len(files) > 0: 
            for file in files:
                c = c + 1
                print("File: " + str(c) + "/" + str(o) + "  Name:" + file)
                key_dst = (path + '\\').replace(src, dst) 
                encrypt(path + '\\', key_dst, file)
    nachtime = time.perf_counter()
    wielange = round(nachtime - vortime, 3)     
    profile = round(wielange / o, 3) 
    sps = round((afs / 1000000) / wielange, 3) 
    print("\n\n" + str(o) + " Files took " + str(wielange) + "seconds. Equals " + str(profile) + "s/file")
    print("Size of all Files: " + str(round(afs / 1000000000, 3)) + "GB. Equals " + str(sps) + "MB/s")
    print("The folder was Encrypted successfully")
    """plt.bar(arrayfilename, array)
    plt.show()
"""

# Ganten Ordner einlesen, passenden key-Ordner einlesen und "entschlüsseln"
def dec_folder(): 
    print("Select the folder with the encrypted files")
    src = filedialog.askdirectory(title='Select the folder with the encrypted files')
    print("Select the folder with the .key files")
    key = filedialog.askdirectory(title='Select the folder with the .key files')
    print("\nProzess started")
    vortime = time.perf_counter()
    o = 0
    c = 0
    afs = 0
    for path, dirs, files in os.walk(src):
        if len(files) > 0: 
            for file in files:
                o = o + 1
                afs = afs + os.stat(path + '/' + file).st_size
                array.append(str(os.path.getsize(path + '/' + file)))
                arrayfilename.append(file)
    for path, dirs, files in os.walk(src): 
        if len(files) > 0: 
            for file in files:
                c = c + 1
                print("File: " + str(c) + "/" + str(o) + "  Name:" + file)
                key_src = (path + '\\').replace(src, key) 
                decrypt(path + '\\', file, key_src + file + '.key')
    for path, dirs, files in os.walk(key):
        if len(files) > 0: 
            for file in files:
                os.remove(path + "/" + file)
    nachtime = time.perf_counter()
    wielange = round(nachtime - vortime, 3)     
    profile = round(wielange / o, 3) 
    sps = round((afs / 1000000) / wielange, 3) 
    print("\n\n" + str(o) + " Files took " + str(wielange) + "seconds. Equals " + str(profile) + "s/file")
    print("Size of all Files: " + str(round(afs / 1000000000, 3)) + "GB. Equals " + str(sps) + "MB/s")
    print("The folder was decrypted successfully")
    """plt.bar(arrayfilename, array)
    plt.show()"""

####----------------------------------------------------------------------###

def equalize(path_1, path_2):
    dat1 = open(path_1, "rb").read()
    dat2 = open(path_2, "rb").read()
    l_dat1 = len(dat1)
    l_dat2 = len(dat2)
    if l_dat1 > l_dat2:
        dat2 += os.urandom(l_dat1 - l_dat2)
    else:
        dat1 += os.urandom(l_dat2 - l_dat2)
    with open(path_1, "wb") as out:
        out.write(dat1)
    with open(path_2, "wb") as out:
        out.write(dat2)
def keygen(orig_path, enc_path, key_path):
    print("In Prozess...")
    equalize(orig_path, enc_path)
    original = open(orig_path, "rb"). read()
    encrypted = open(enc_path, "rb"). read()
    key = bytes(a ^ b for (a, b) in zip(original, encrypted))
    with open(key_path + enc_path + ".key", "wb") as key_out:
        key_out.write(key)
    print("encrypted")
def decryptttt(enc_path, key_path, dec_path):
    print("In Prozess...")
    encrypted = open(enc_path, "rb").read()
    key = open(key_path, "rb").read()
    decrypted = bytes(a ^ b for (a, b) in zip(encrypted, key))
    with open(dec_path, "wb") as decrypted_out:
        decrypted_out.write(decrypted)
    os.remove(key_path)
    print("decrypted")
def encccc():
    orig_path = filedialog.askopenfilename(title='Select File to hide (Wird Versteckt)')
    enc_path = filedialog.askopenfilename(title='Select Original file (Bleibt erhalten)')
    print("\n\n" + orig_path + " will be hidden in " + enc_path)
    keygen(orig_path, enc_path, "")
def decccc():
    orig_path = filedialog.askopenfilename(title='Select Original file')
    enc_path = filedialog.askopenfilename(title='Select the key file')
    wo_enddat = filedialog.askdirectory(title='Select the folder where outcoming file will be stored')
    key_path = input("\n\nEnter the name of the Original file:")
    decryptttt(orig_path, enc_path,wo_enddat + "/" + key_path)

###------------------------------------------------------------------###

def window():
    global master
    master = Tk()
    master.geometry('300x250')
    icopath = os.path.dirname(__file__)
    if os.path.isfile( icopath + "/"+ 'icon.ico'):
        print()
    else:
        if e == 1:    
            os.system('exit')
            os.system('python ' + __file__)
        print ("Download icon")
        url = "https://www.diekinderdertotenstadt.de/images/favicon.png"
        wget.download(url, icopath + "/" + 'icon.png')
        filename = icopath + "/" + 'icon.png'
        img = PIL.Image.open(filename)
        img.save(icopath + "/" + 'icon.ico')
        os.remove(icopath + "/" + 'icon.png')
        print ("\n")

    master.iconbitmap(icopath + "/" + 'icon.ico')
    master.title("Encryption/Decryption")

    Label(master, text="What do you want to do?").grid(row=5, sticky=W)
    Button(master, text='Encrypt a file', command=enc).grid(row=6, sticky=W, pady=4)
    Button(master, text='Decrypt a file', command=dec).grid(row=7, sticky=W, pady=4)
    Button(master, text='Encrypt a folder', command=enc_folder).grid(row=8, sticky=W, pady=4)
    Button(master, text='Decrypt a folder', command=dec_folder).grid(row=9, sticky=W, pady=4)
    Button(master, text='Encrypt file to file', command=encccc).grid(row=10, sticky=W, pady=4)
    Button(master, text='Decrypt file to file', command=decccc).grid(row=11, sticky=W, pady=4)
    Button(master, text='Quit', command=master.quit).grid(row=12, sticky=W, pady=4)
    mainloop()


window()