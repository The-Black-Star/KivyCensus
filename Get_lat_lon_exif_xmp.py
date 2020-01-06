import math
from PIL import Image, ImageTk, ExifTags

def dms_to_degrees(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    f_d = value[0]
    f_m = value[1]
    f_s = value[2]

    d=float(f_d[0])/float(f_d[1])
    m=float(f_m[0])/float(f_m[1])
    s=float(f_s[0])/float(f_s[1])

    return d + (m / 60.0) + (s / 3600.0)

def get_xmp(path):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    fd = open(path, encoding="latin1")
    d= fd.read()

    xmp_start = d.find('<x:xmpmeta')
    xmp_end = d.find('</x:xmpmeta')
    xmp_str = d[xmp_start:xmp_end+12]

    return(xmp_str)

def get_sensor(model):
    """
    Helper function to lookup sensor dimensions based on EXIF model tag
    :param value:
    :type value: string
    :rtype: float
    """

    if 'FC6520' in model:
        SensorW = 17.42  # X5S sensor dimensions (mm)
        SensorH = 13.05
    elif 'FC6510' in model:
        SensorW = 13.13  # X4S sensor dimensions (mm)
        SensorH = 8.76
    elif 'FC350' in model:
        SensorW = 6.20  # X3 sensor dimensions (mm)
        SensorH = 4.65
    elif 'FC6310' in model:
        SensorW = 13.13  # P4P sensor dimensions (mm)
        SensorH = 8.76
    elif 'FC300C' in model:
        SensorW = 6.20  # P3S sensor dimensions (mm)
        SensorH = 4.65
    elif 'FC220' in model:
        SensorW = 6.20  # Mavic Pro sensor dimensions (mm)
        SensorH = 4.65
    # else:
    #    SensorW = simpledialog.askfloat("Input", "What is the Sensor Width (mm)?", minvalue=0.0, maxvalue=1000.0)
    #    SensorH = simpledialog.askfloat("Input", "What is the Sensor Height (mm)?", minvalue=0.0, maxvalue=1000.0)

    return (SensorW, SensorH)


def process_exif(PILFile):
    exifData = {}
    exifDataRaw = PILFile._getexif()
    for tag, value in exifDataRaw.items():
        decodedTag = ExifTags.TAGS.get(tag, tag)
        exifData[decodedTag] = value
    ImageW = exifData['ExifImageWidth']
    ImageH = exifData['ExifImageHeight']
    FocalLength = exifData['FocalLength']
    focal = float(FocalLength[0]) / float(FocalLength[1])
    model = exifData['Model']
    (SensorW, SensorH) = get_sensor(model)


    gpsinfo = exifData['GPSInfo']
    lat = dms_to_degrees(gpsinfo[2])
    if gpsinfo[1] != 'N':
        lat = 0 - lat
    lon = dms_to_degrees(gpsinfo[4])
    if gpsinfo[2] != 'E':
        lon = 0 - lon

    return lat, lon, ImageW, ImageH, SensorH, SensorW , focal

def process_xmp(path):
    xmp = get_xmp(path)
    # Get yaw and pitch from XMP string
    c = '"'
    enum = [pos for pos, char in enumerate(xmp) if char == c]

    yaw_str = xmp[enum[36] + 1:enum[37]]
    # print(yaw_str)
    yaw = float(yaw_str)
    # print(yaw)

    pitch_str = xmp[enum[38] + 1:enum[39]]
    # print(pitch_str)
    pitch = float(pitch_str)
    # print(pitch)

    # Magnetic Declination Correction
    yaw = yaw + 9.45

    # Convert to radians and define pitch as pointing down
    pitch = ((pitch + 90.0) * math.pi / 180.0)
    yaw = (yaw * math.pi / 180.0)
    if yaw < 0:
        yaw = yaw + 2 * math.pi

    return pitch, yaw
    # print(pitch, yaw)