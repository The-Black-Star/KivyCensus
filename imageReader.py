#!/user/bin/python3.5
"""
Image Reader
EcoCensus
Copyright 2017: Rebekah Loving and Morgan West
"""

# TODO: Find a library to read in metadata/exifdata that puts the data in a usable format.
#   ExifRead puts the data into an unusable format that cannot be changed or manipulated and can
#   only be printed.
import os, sys
import coordFinder as crdfdr # class to calculate coordinates of selected plants in images
import fnmatch

def main(imageDirectory, altitude):
    print("entered image reader")
    pixelCoords = imageDirectory + "/Drone_coords.txt"
    realCoords = imageDirectory + "/Real_coords.txt"
    pixelXmp =  imageDirectory + "/Drone_xmp.txt"
    positiveDirectory = os.path.dirname(imageDirectory + '/Positive/')

    c = crdfdr.coordFinder(94,0, float(altitude)) # 94 FOV, 0 direction, 30 meter height
    realC = open(realCoords, 'w+')
    droneCoords = [0, 0]
    plantCoords = [0, 0]
    with open(pixelCoords) as f:  # exif data from the images pre partition
        with open(pixelXmp) as g:  # xmp data from the images pre partition

            for fline, gline in zip(f, g):

                image_name, droneCoords[0], droneCoords[
                    1], ImageW, ImageH, SensorH, SensorW, focal = fline.split()  # data inide the dronecoords file.
                image_name, pitch, yaw = gline.split()  # image name should be ther same

                for root, dirs, files in os.walk(positiveDirectory):
                    for filename in fnmatch.filter(files, str("*" + image_name + "*")):
                        plantCoords[0], plantCoords[1], rest = filename.split('_', 2)
                        plant = c.processCoords((float(droneCoords[0]), float(droneCoords[1])),
                                                (float(plantCoords[0]), float(plantCoords[1])), float(SensorH), float(SensorW), float(focal),
                                                float(pitch), float(yaw), (float(ImageW), float(ImageH)))
                        # plant = c.processCoords((float(droneCoords[0]), float(droneCoords[1])), (float(plantCoords[0]), float(plantCoords[1])), (float(ImageW), float(ImageH)))
                        realC.write(str(rest) + ", " + str(plant[0]) + " " + str(plant[1]) + str("\n"))
    realC.close()
    print("leaving image reader")