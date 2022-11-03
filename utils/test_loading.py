import pydicom
import glob
import os
import numpy as np
import tqdm
from cv2 import cv2

# Директория с дайкомами (не обязательно последняя)
directory = r'C:\Users\User\PycharmProjects\MedicalAnnotator\test_data\many_2D_slices_DICOM\01'

# Индексы нужных срезов
axial_slice_ind = 0  # Основная проекция для разметки
# Две другие
saggital_slice_ind = 0
coronal_slice_ind = 0


def apply_windowing(img, window_center, window_width, intercept=0, slope=1, inverted=False):
    img = (img * slope + intercept)  # for translation adjustments given in the dicom file.
    img_min = window_center - window_width // 2  # minimum HU level
    img_max = window_center + window_width // 2  # maximum HU level
    img[img < img_min] = img_min  # set img_min for all HU levels less than minimum HU level
    img[img > img_max] = img_max  # set img_max for all HU levels higher than maximum HU level
    if inverted:
        img = -img
        img_min = img.min()
        img_max = img.max()
    img = (img - img_min) / (img_max - img_min) * 255.0
    img = np.array(img, dtype=np.uint8)
    return img


def visualize(image):
    # ТОЛЬКО ДЛЯ ВИЗУАЛИЗАЦИИ
    image = apply_windowing(image, 40, 400)
    cv2.namedWindow('w')
    cv2.imshow('w', image)
    cv2.waitKey(0)


def get_files(directory):
    paths = glob.glob(os.path.join(directory, '**'),
                      recursive=True)  # Получаем рекурсивно все папки и файлы из директории
    paths = list(filter(lambda path: not os.path.isdir(path), paths))  # Оставляем только файлы
    paths = list(filter(lambda path: os.path.getsize(path) / 1024 > 20,
                        paths))  # Оставляем только файлы больше 20Кб (потому что иногда бывают битые пустые)
    return paths


def split_by_surveys(paths):
    survey_ids = {os.path.split(path)[-2] for path in paths}  # Получаем ID исследований
    # Разделяем все файлы по ID исследований
    surveys = [list(filter(lambda path: os.path.split(path)[-2] == survey_id, paths)) for survey_id in survey_ids]
    return surveys


def get_axial_slice(image, ind):
    return image[ind, :, :]


def get_coronal_slice(image, ind):
    return image[:, ind, :]


def get_saggital_slice(image, ind):
    return image[:, :, ind]


def main():
    paths = get_files(directory)
    surveys = split_by_surveys(paths)
    for survey in surveys:
        array = []  # Будущий 3D снимок
        for dicom_path in tqdm.tqdm(survey):
            single_slice = pydicom.dcmread(dicom_path)
            array.append(single_slice.pixel_array)
        array = np.array(array)

        # Просто для примера
        image = get_saggital_slice(array, 250)
        visualize(image)

        single_slice.pixel_array = image
        single_slice.save_as('MyCoolDicomName.dcm')


def get_my_slices(array, idx, axis=0):
    window_width = 10
    left_idx = min(idx - window_width, 0)
    right_idx = max(idx + window_width, array.shape[axis])
    for i in range(left_idx, right_idx + 1):
        if axis == 0:
            yield get_axial_slice(array, i)
        elif axis == 1:
            yield get_coronal_slice(array, i)
        elif axis == 2:
            yield get_saggital_slice(array, i)


if __name__ == '__main__':
    main()
