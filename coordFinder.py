#!/user/bin/python3.5
"""
EcoCensus Coordinate converter
Copyright 2017: Morgan West, Rebekah Loving, Morgan Friend
"""

import math
import utm

# This class will take the x,y coordinates of fauna found in a given
# image and output the real world coordinates.
# This class will be called per image list with identical non-metadata variables eg FOV, direciton.
# For example:
"""
find = coordFinder(94,0)
for droneCoords,droneHeight,focalLength,plantCoords in classifiedImages:
    classifiedCoordinateList.append(find.processCoords(droneCoords,droneHeight,focalLength,plantCoords))
"""

class coordFinder:

    # if there is no defined direction, pass direction as 0 to assume north-up orientation
    def __init__(self,FOV,direction,height):
        self.theta = float(FOV / 2)
        self.phi = math.radians(direction) # polar rotation coordinate converted to radians
        self.droneHeight = height # in meters
        return
    """
    toDecimalDegrees is correct
    """
    # Converts coordinates from geographic to decimal degrees
    # Used because coordinates stored in image metadata are in geographic form
    def toDecimalDegrees(self,droneCoords):
        # Geographic coords stored as tuple of lists ([hours,minutes,seconds],[hours,minutes,seconds])
        # Conversion formula is (hr + (min/60) + (sec/3600))
        latitude = droneCoords[0]
        longitude = droneCoords[1]
        newLatitude = float(latitude[0] + float(latitude[1] / 60) + float(latitude[2] / 3600))
        newLongitude = float(longitude[0] + float(longitude[1] / 60) + float(longitude[2] / 3600))
        return (newLatitude,newLongitude)

    # Converts decimal degrees to universal transverse mercador in zone 5Q (Big Island).
    # Returns a coordinate tuple in UTM.
    def toUTM(self,coords):
        latitude = coords[0]
        longitude = coords[1]
        return utm.from_latlon(latitude,longitude) # see documentation for utm library

    # Takes the coordinate given from the image data and calculates the edge
    def getEdges(self,droneDD,imageRatio):
        # defining and setting variables
        droneLat = droneDD[0]
        droneLong = droneDD[1]
        edges = [] # list of edges [top, right, bottom, left]
        distToEdge = float(self.droneHeight*math.tan(self.theta))
        
        # conversion from meters to decimal degrees
        # 1 m = 0.0004858 dd
        distToEdge = float(distToEdge * 0.0004858)

        # edge calculations assuming orientation is north-up
        NSdistToEdge = float(distToEdge * imageRatio) # since the image is wider than it is tall
        northx = droneLat
        northy = droneLong + NSdistToEdge 
        westx = droneLat + distToEdge
        westy = droneLong
        southx = droneLat
        southy = droneLong - NSdistToEdge
        eastx = droneLat - distToEdge
        easty = droneLong

        # add coordinates to list in NESW order
        edges.append((northx,northy))   # N
        edges.append((westx,westy))     # E
        edges.append((southx,southy))   # S
        edges.append((eastx,easty))     # W
        return edges

    # Finds the midpoint of the coordinates calculated for multiple images that contain the same
    #   geographic location.
    def midpoint(self,coordinates):
        xsum = 0
        ysum = 0
        for coord in coordinates:
            xsum += coord[0]
            ysum += coord[1]
        xcoord = xsum / len(coordinates)
        ycoord = ysum / len(coordinates)
        return (xcoord,ycoord)

    # Rotates the coordinate around the origin (droneCoords) of the image to match direcitonal rotation
    #       of the drone.
    def rotate(self, coords, origin):

        # change image coordinates to emulate the center of the image as (0,0)
        xcoord = float(coords[0] - origin[0])
        ycoord = float(coords[1] - origin[1])

        # rotate coordinates around new origin
        # x' = xcos(phi)-ysin(phi)
        # y' = ycos(phi)+xsin(phi)       
        newCoordX = float(xcoord * math.cos(self.phi) - ycoord * math.sin(self.phi))
        newCoordY = float(ycoord * math.cos(self.phi) - xcoord * math.sin(self.phi))

        # move back the origin and return the coordinates
        newCoordX += origin[0]
        newCoordY += origin[1]      
        return (newCoordX, newCoordY)

    def WGS84toUTM(self,Lat, Lon):
        """
        Helper function to convert the GPS coordinates stored in decimal degrees to UTM coordinates
        :param value:
        :type value: decimal degrees WGS-84 datum
        :rtype: float
        """

        falseEasting = 500e3
        falseNorthing = 10000e3

        zone = math.floor((Lon + 180) / 6) + 1  # Longitudinal Zone
        centralMeridian = ((zone - 1) * 6 - 180 + 3) * math.pi / 180.0

        mgrsLatBands = 'CDEFGHJKLMNPQRSTUVWXX'  # Latidunial Band
        LatBand = mgrsLatBands[math.floor(Lat / 8 + 10)]

        Lat = Lat * math.pi / 180.0
        Lon = Lon * math.pi / 180.0 - centralMeridian

        a = 6378137  # WGS-84 ellipsoid radius
        f = 1 / 298.257223563  # WGS-84 flattening coefficient

        k0 = 0.9996  # UTM scale on the central meridian

        # ---- easting, northing: Karney 2011 Eq 7-14, 29, 35:
        ecc = math.sqrt(f * (2 - f))  # eccentricity
        n = f / (2 - f)  # 3rd flattening
        n2 = n * n
        n3 = n * n2
        n4 = n * n3
        n5 = n * n4
        n6 = n * n5

        cosLon = math.cos(Lon)
        sinLon = math.sin(Lon)
        tanLon = math.tan(Lon)

        tau = math.tan(Lat)
        sigma = math.sinh(ecc * math.atanh(ecc * tau / math.sqrt(1 + tau * tau)))

        tau_p = tau * math.sqrt(1 + sigma * sigma) - sigma * math.sqrt(
            1 + tau * tau)  # prime (_p) indicates angles on the conformal sphere

        xi_p = math.atan2(tau_p, cosLon)
        eta_p = math.asinh(sinLon / math.sqrt(tau_p * tau_p + cosLon * cosLon))

        A = a / (1 + n) * (1 + 1 / 4 * n2 + 1 / 64 * n4 + 1 / 256 * n6)  # 2πA is the circumference of a meridian

        alpha = [None,  # note alpha is one-based array (6th order Krüger expressions)
                 1 / 2 * n - 2 / 3 * n2 + 5 / 16 * n3 + 41 / 180 * n4 - 127 / 288 * n5 + 7891 / 37800 * n6,
                 13 / 48 * n2 - 3 / 5 * n3 + 557 / 1440 * n4 + 281 / 630 * n5 - 1983433 / 1935360 * n6,
                 61 / 240 * n3 - 103 / 140 * n4 + 15061 / 26880 * n5 + 167603 / 181440 * n6,
                 49561 / 161280 * n4 - 179 / 168 * n5 + 6601661 / 7257600 * n6,
                 34729 / 80640 * n5 - 3418889 / 1995840 * n6,
                 212378941 / 319334400 * n6]

        xi = xi_p
        for j in range(1, 7):
            xi = xi + alpha[j] * math.sin(2 * j * xi_p) * math.cosh(2 * j * eta_p)

        eta = eta_p
        for j in range(1, 7):
            eta = eta + alpha[j] * math.cos(2 * j * xi_p) * math.sinh(2 * j * eta_p)

        x = k0 * A * eta
        y = k0 * A * xi

        # ---- shift x/y to false origins
        x = x + falseEasting  # make x relative to false easting
        if y < 0:
            y = y + falseNorthing  # make y in southern hemisphere relative to false northing

        # ---- round to cm
        x = round(x, 2)
        y = round(y, 2)

        if Lat >= 0:
            h = 'N'
        else:
            h = 'S'

        return (zone, LatBand, h, x, y)

    # Function for processing real life UTM coordinates given image and image coordinates of
    #   detected plants.
    def processCoords(self, droneCoords, plantCoords, SensorH, SensorW, focal, pitch, yaw, imageDims):

        # defining and setting values for variables
        imageRatio = float(imageDims[0] / imageDims[1])
        # droneCoords = self.toDecimalDegrees(droneCoords)
        edges = self.getEdges(droneCoords, imageRatio)
        imageOrigin = (imageDims[0] / 2, imageDims[1] / 2)  # middle of the picture in image coords
        edgeN = edges[0]
        edgeE = edges[1]
        edgeS = edges[2]
        edgeW = edges[3]

        realCoordsX = 0  # these should not be 0 when returned
        realCoordsY = 0  # /
        lat = droneCoords[0]
        lon = droneCoords[1]

        ImageW = imageDims[0]
        ImageH = imageDims[1]
        UTM = self.WGS84toUTM(lat, lon)
        TargetD = self.droneHeight

        # rotate coordinates along origin for direction
        # plantCoords = self.rotate(plantCoords, imageOrigin)
        #
        xcoord, ycoord = self.rotate(plantCoords, imageOrigin) # this is an important line everything besides this and the roberto code is used for nothing

        # calculate distance from origin

        # calculating distances and ratios
        distWE = math.fabs(edgeW[0] - edgeE[0])
        distNS = math.fabs(edgeN[1] - edgeS[1])
        xratio = float(xcoord / imageDims[0])
        yratio = float(ycoord / imageDims[1])
        ratioWE = distWE * xratio
        ratioNS = distNS * yratio

        # calculating coordinates with ratios
        if xcoord < imageOrigin[0]:
            realCoordsX = lat + (distWE / 2) - (distWE * xratio)
        if xcoord > imageOrigin[0]:
            realCoordsX = edgeW[0] - (distWE * xratio)
        if xcoord == imageOrigin[0]:
            realCoordsX = lat
        realCoordsY = edgeN[1] + (distNS * yratio)


        # starting of roberto execution

        u = xcoord +150
        v = ycoord +150
        X_p = (1 / focal) * (SensorH / ImageH) * (TargetD) * (float(ImageH) / 2.0 - v)
        Y_p = (1 / focal) * (SensorW / ImageW) * (TargetD) * (u - float(ImageW) / 2.0)
        # perform rotation in case of near nadir
        # if math.abs(pitch + pi/2) < 0.02:
        #   X = - X_p * math.cos(yaw) - Y_p * math.sin (yaw)

        # perform rotation otherwise
        X = (X_p * math.cos(pitch) * math.cos(yaw)) + (TargetD * math.sin(pitch) * math.cos(yaw)) - (
                Y_p * math.sin(yaw))
        Y = (Y_p * math.cos(yaw)) + (X_p * math.cos(pitch) * math.sin(yaw)) + (
                TargetD * math.sin(pitch) * math.sin(yaw))
        # calculate UTM coordinates

        Easting = UTM[3] + Y
        Northing = UTM[4] + X
        Easting = round(Easting, 2)
        Northing = round(Northing, 2)

        # UTMcoords = self.toUTM((realCoordsX, realCoordsY))

        # return (UTMcoords)

        return Easting, Northing
#return (UTMcoords, (realCoordsX, realCoordsY))
                
