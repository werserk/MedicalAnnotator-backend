import pydicom
import os
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
    scan = np.array(scan, dtype=np.uint16).tobytes()
    return scan, tags


def read_survey(path):
    survey = pydicom.dcmread(path)
    scan = survey.pixel_array
    return survey, scan


def get_axial_slice(image, ind):
    return image[ind, :, :]


def get_coronal_slice(image, ind):
    return image[:, ind, :]


def get_saggital_slice(image, ind):
    return image[:, :, ind]


def get_my_slices(array, axis=0):
    for i in range(0, array.shape[axis]):
        if axis == 0:
            yield get_axial_slice(array, i)
        elif axis == 1:
            yield get_coronal_slice(array, i)
        elif axis == 2:
            yield get_saggital_slice(array, i)


def get_slice_path(i, web_path):
    return web_path + str(i) + ".dcm"


def get_my_slices_paths(web_path, dst_folder, idx, axis=0):
    WINDOW_WIDTH = 5
    dicom_file_names = os.listdir(dst_folder)
    left_idx = max(idx - WINDOW_WIDTH, 0)
    right_idx = min(idx + WINDOW_WIDTH, len(dicom_file_names) - 1)  # ???
    for i in range(left_idx, right_idx):
        if axis == 0:
            yield get_slice_path(i, web_path + "axial/")
        elif axis == 1:
            yield get_slice_path(i, web_path + "coronal/")
        elif axis == 2:
            yield get_slice_path(i, web_path + "saggital/")


def slice_survey(paths, dst_folder, axis=0):
    array = []
    os.makedirs(dst_folder)
    for path in paths:  # Создаём 3D объект
        single_slice = pydicom.dcmread(path)
        array.append(single_slice.pixel_array)
    array = np.array(array)

    # Выбираем нужные нам срезы
    for i, image in enumerate(get_my_slices(array, axis)):
        single_slice.PixelData = image.tobytes()
        path = os.path.join(dst_folder, str(i) + '.dcm')
        single_slice.save_as(path)  # Сохраняем


def slice_get_paths(paths, slices_folder, web_path, axial_id=None, coronal_id=None, saggital_id=None):
    if os.path.isdir(slices_folder):
        axial_slices_paths = []
        coronal_slices_paths = []
        saggital_slices_paths = []
        if axial_id is not None:
            axial_slices_paths = list(
                get_my_slices_paths(web_path=web_path, idx=int(axial_id), dst_folder=slices_folder + "axial/", axis=0))
        if coronal_id is not None:
            coronal_slices_paths = list(
                get_my_slices_paths(web_path=web_path, idx=int(coronal_id), dst_folder=slices_folder + "coronal/",
                                    axis=1))
        if saggital_id is not None:
            saggital_slices_paths = list(
                get_my_slices_paths(web_path=web_path, idx=int(saggital_id), dst_folder=slices_folder + "saggital/",
                                    axis=2))
    else:
        slice_survey(paths=paths, dst_folder=slices_folder + "axial/", axis=0)
        slice_survey(paths=paths, dst_folder=slices_folder + "coronal/", axis=1)
        slice_survey(paths=paths, dst_folder=slices_folder + "saggital/", axis=2)
        axial_slices_paths = list(
            get_my_slices_paths(web_path=web_path, idx=0, dst_folder=slices_folder + "axial/", axis=0))
        coronal_slices_paths = list(
            get_my_slices_paths(web_path=web_path, idx=0, dst_folder=slices_folder + "coronal/", axis=1))
        saggital_slices_paths = list(
            get_my_slices_paths(web_path=web_path, idx=0, dst_folder=slices_folder + "saggital/", axis=2))

    return axial_slices_paths, coronal_slices_paths, saggital_slices_paths

# def slice_survey(paths, idx, dst_folder, axis=0):
#     # paths - все пути секвенции DICOM
#     WINDOW_WIDTH = 5
#     array = []
#     for path in paths:  # Создаём 3D объект
#         single_slice = pydicom.dcmread(path)
#         array.append(single_slice.pixel_array)
#     array = np.array(array)

#     # Выбираем нужные нам срезы
#     for i, image in enumerate(get_my_slices(array, axis, window_width=WINDOW_WIDTH)):
#         single_slice.pixel_array = image
#         path = os.path.join(dst_folder, str(axis), str(idx) + '.dcm')
#         single_slice.save_as(path)  # Сохраняем
#         yield path
