import pydicom
import os
import json
# import tifffile as tiff
import numpy as np


def apply_boolean_mask(array, array_criterion, criterion, value):
    array.copy()
    if array.shape != array_criterion.shape:
        print("Размеры не совпадают")
        return
    if len(array.shape) == 2:
        for i in range(len(array)):
            for j in range(len(array[i])):
                if criterion(array_criterion[i][j]):
                    array[i][j] = value
    elif len(array.shape) == 3:
        for i in range(len(array)):
            for j in range(len(array[i])):
                for k in range(len(array[i][j])):
                    if criterion(array_criterion[i][j][k]):
                        array[i][j][k] = value
    return array


def tag2int(x):
    # get x[0] as in int is x is a 'pydicom.multival.MultiValue', otherwise get int(x)
    if isinstance(x, pydicom.multival.MultiValue):
        x = x[0]
    x = str(x)
    x = x.split(',')[0]
    return int(float(x))


def data2tags(data):
    windowing = {}
    try:
        windowing['window_center'] = tag2int(data[('0028', '1050')].value)  # window center
        windowing['window_width'] = tag2int(data[('0028', '1051')].value)  # window width
    except KeyError:
        windowing['window_center'] = 2048
        windowing['window_width'] = 4096
    try:
        windowing['intercept'] = tag2int(data[('0028', '1052')].value)  # window center
        windowing['slope'] = tag2int(data[('0028', '1053')].value)  # window width
    except KeyError:
        windowing['intercept'] = 0
        windowing['slope'] = 1
    try:
        windowing['image_mode'] = str(data[('0028', '0004')].value)  # monochrome1 or not
    except KeyError:
        pass
    return windowing


def reformat_survey(src_path):
    filename = os.path.split(src_path)[-1].split('.')[0]
    data, scan = read_survey(src_path)
    tags = data2tags(data)
    # with open(os.path.join(dst_path, filename + '_tags.json'), mode='w') as f:
    #     json.dump(tags, f)
    scan = np.array(scan, dtype=np.uint16).tobytes()
    # tiff.imwrite(os.path.join(dst_path, filename + '.tiff'), scan)
    return scan, tags  # TODO: scan - байты, отсылаем на фронт


def read_survey(path):
    survey = pydicom.dcmread(path)
    scan = survey.pixel_array
    return survey, scan
