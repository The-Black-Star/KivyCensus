from PIL import Image
import Get_lat_lon_exif_xmp as Gll
import utm
import os, sys
import cv2
import numpy as np
import struct
import scipy
import scipy.misc
import scipy.cluster

def main(directorys):
    print("entered image partition")
    rootdir = directorys +'/' #'/Users/bound_to_love/Downloads/Test02142018'
    directory = os.path.dirname(directorys + '/Partitions/') #/Users/bound_to_love/Downloads/Test02142018/Partitions/')
    if os.path.exists(directory):
        print ("Directory already exists")
    if not os.path.exists(directory):
        os.makedirs(str(directory))
        print ("Directory made for partitions")
    f = open(str(directorys) + "/Drone_coords.txt", "w+")
    g = open(str(directorys) + "/Drone_xmp.txt", "w+")
    files = os.listdir(rootdir)
    for file in files:
        if ".JPG" in file or ".jpg" in file:
            image = Image.open(rootdir + file)

            lat, lon, ImageW, ImageH, SensorH, SensorW, focal = Gll.process_exif(image)
            pitch, yaw = Gll.process_xmp(str(rootdir + file))

            #exif_data = gll.get_exif_data(image)
            #dir, lat, lon = gll.get_lat_lon(exif_data)

            f.write(file + " " + str(lat) + " " + str(lon) + " " + str(ImageW) + " " + str(ImageH) + " " + str(SensorW) + " " +  str(SensorH)+ " " + str(focal) +  str("\n"))
            g.write(file + " " + str(pitch) + " " + str(yaw) + str("\n"))

            imgPartition = cv2.imread(rootdir + file)
            x, y, c = imgPartition.shape
            xp = len(str(x))
            yp = len(str(y))
            i, j = 0, 0
            #while i < (x/10)*10:
                #while j < (y/10)*10:
                    #partition = imgPartition.crop((i, j, (i + x / 10), (j + y / 10)))
            while i < x:
                i2 = i + 300
                while j < y:
                    j2 = j + 300
                    newfile = directory + "/" + str(j).zfill(yp) + "_" + str(i).zfill(xp) + "_" + file
                    partition = imgPartition[i:i2, j:j2] #cv2.resize(imgPartition[i:i2, j:j2],(x, y), interpolation = cv2.INTER_LINEAR)
                    cv2.imwrite(newfile, partition)
                    #j += y / 10
                    j += 300
                #i += x / 10
                i += 300
                j = 0
    f.close()
    g.close()
    print("leaving image partition")

if __name__ == "__main__":
    main()