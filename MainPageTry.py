import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, 'MEIPASS', os.path.dirname(os.path.abspath(__file_)))
    return os.path.join(base_path, relative_path)


import kivy
kivy.require('1.9.0') # replace with your current kivy version !
from tkinter import filedialog
from tkinter import *
from kivy.app import App
from kivy.uix.button import Label , Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from PIL import Image, ImageDraw, ImageFont
import kivy.uix.image as Kimage
import image_partition as impa
import predictions as predict
import imageReader as imread
from kivy.graphics import *
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.base import EventLoop
import shutil
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks

from kivy.config import Config
Config.set('graphics','width','1100')
Config.set('graphics','height','700')


class bidirectional_iterator(object):
    def __init__(self, collection):
        self.collection = collection
        self.index = 0

    def start(self):
        return self.collection[0]

    def next(self):
        self.index += 1
        if self.index == len(self.collection):
            self.index = self.index - 1
            return self.collection[self.index]
        result = self.collection[self.index]
        return result

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = 0
            return self.collection[self.index]
        result = self.collection[self.index]
        return result

    def __iter__(self):
        return self

class Layout(FloatLayout):
    imglist =[]
    imgdirectory=""
   # def update(self, imdir):
    #    self.rect.source = imdir
    def selectDirectory(self):
        Tk().withdraw()
        try:
            self.folder.text = filedialog.askdirectory()
        except FileNotFoundError:
            pass
        #print (self.folder.text)
        directory = os.listdir(self.folder.text)
        self.imgdirectory = self.folder.text
        imglist = []
        for file in directory:
            if ".JPG" in file or ".jpg" in file:
                imglist.append(file)
        #print (imglist)

        im = self.imgdirectory + "/" + imglist[0]
        self.imglist = bidirectional_iterator(imglist)
        print (im)
        #print (im)
        with self.imprint.canvas:
           Rectangle(source=im, size=self.imprint.size, pos=self.imprint.pos)
                # need to figure out how kivys file thing works

    def Predict(self):
        Folder = self.folder.text
        altitude = float(self.altitude.text)
        threshold = float(self.threshold.text)
        impa.main(Folder)
        predict.main(Folder, threshold)
        imread.main(Folder, altitude)
        partdirectory = os.path.dirname(Folder + '/Partitions/')
        os.rmdir(partdirectory)
        self.Imglist()

        im = self.imgdirectory + "/"+str(self.imglist.start())
        EcoCensus.abcd = im
        self.imprint.canvas.clear()
        with self.imprint.canvas:
            Rectangle(source=EcoCensus.abcd, size=self.imprint.size, pos=self.imprint.pos)

    def Imglist(self):
        print("entered imagelist")
        directory = os.listdir(self.folder.text)
        posdirectory = os.listdir(self.folder.text + "/Positive")
        if not os.path.exists(self.folder.text + "/DrawnSelections/"):
            os.makedirs(self.folder.text + "/DrawnSelections/")
        self.imgdirectory = os.path.dirname(self.folder.text + "/DrawnSelections/")
        imglist = []
        for file in directory:
            if ".JPG" in file or ".jpg" in file:
                newfile = shutil.copy(self.folder.text + "/" + file, self.imgdirectory + "/" + file)
                newfiles = Image.open(newfile)
               # rawfile = Image.open(file)
                for selection in posdirectory:
                    image = selection.split("_", 3)
                    if file == image[2]:

                        pix1 = int(image[0])
                        pix2 = int(image[1])
                        draw = ImageDraw.Draw(newfiles)
                        print(pix1)
                        print(pix2)
                        topleft = (pix1,pix2)
                        topright = (pix1+150,pix2)
                        bottomleft = (pix1,pix2+150)
                        bottomright = (pix1+150,pix2+150)

                        draw.rectangle(((pix1+300,pix2+300),(pix1,pix2)), outline = "red", width=15)

                        del draw
                        newfiles.save((self.imgdirectory +"/" +file), "JPEG")
                imglist.append(file)
        self.imglist = bidirectional_iterator(imglist)
        print("exit imagelist")

    def next(self):
        if self.imglist == []:
            #print("returning from next")
            return
        im = self.imgdirectory + "/" +str(self.imglist.next())
        #print(self.folder.text + "/" + str(self.imglist.next))
        print("im object = " + str(im))
        EcoCensus.abcd = im
        #print(EcoCensus.abcd)
        self.imprint.canvas.clear()
        with self.imprint.canvas:
            Rectangle(source=EcoCensus.abcd, size=self.imprint.size, pos=self.imprint.pos)
        #print (self.ids.imprint.source + "Heres the dir")
        #self.update(self, im)
        #self.Canvas(self.imglist.next())

    def prev(self):
        if self.imglist == []:
            #print ("returning from prev")
            return
        im = self.imgdirectory  + "/"+str(self.imglist.prev())
        #print (self.folder.text + "/" + str(self.imglist.prev))
        print ("im object = " + str(im))
        EcoCensus.abcd = im
        #print(EcoCensus.abcd)
        self.imprint.canvas.clear()
        with self.imprint.canvas:
            Rectangle(source = EcoCensus.abcd, size = self.imprint.size, pos = self.imprint.pos)

        #super.ids.imprint.canvas[Rectangle].source = im
        #EventLoop.window.abcd = im
        #self.Rectangle.source = 'example.jpg'
        #print (self.ids.imprint.source + "Heres the dir")
        #Canvas(self.imglist.prev())

#class LineRectangle(Widget):
    #pass

class EcoCensus(App):
    abcd = StringProperty('Background.png')
    def build(self):
        #FloatLayout.add_widget(LineRectangle(self, Widget))
        return Layout()

    def callback(self):
        self.abcd = Layout.prev.im


if __name__ == '__main__':
    EcoCensus().run()