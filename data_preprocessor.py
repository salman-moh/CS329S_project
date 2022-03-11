import os
import shutil
import sys
import re
from PIL import Image
import numpy as np
import pandas as pd


def yolo_v5_preprocess_new(dir_path):
    os.chdir(dir_path)
    dest_loc_img = "yolov5_data/"
    dest_loc_annot = "yolov5_data/"
    for i in range(1, 101):  # Go through all dirs
        print("Going through dir:", i)
        sub_dir_path = str(i)
        image_class = str(i-1)
        with open(sub_dir_path + "/" + "bb_info.txt") as bb_file:
            for j, line in enumerate(bb_file.readlines()):
                if j == 0:
                    continue  # Skip the first line, that only contains info

                contents = re.split(" ", line.strip())
                img_nr = contents[0]
                x_0 = int(contents[1])
                y_0 = int(contents[2])
                x_max = int(contents[3])
                y_max = int(contents[4])

                # Get corresponding img dims
                img_path = sub_dir_path + "/" + img_nr + '.jpg'
                im = Image.open(img_path)
                width, height = im.size

                # Copy that image to the target directory
                if not os.path.exists(dest_loc_img + img_nr + ".jpg"):
                    shutil.copy(img_path, dest_loc_img + img_nr + ".jpg")

                # Convert to yolov5 data
                nr_decimals = 3
                x_mid = round(((x_max - x_0) / 2 + x_0) / width, nr_decimals)
                y_mid = round(((y_max - y_0) / 2 + y_0) / height, nr_decimals)

                x_width = round((x_max - x_0) / width, nr_decimals)
                y_height = round((y_max - y_0) / height, nr_decimals)

                dest_path = dest_loc_annot + img_nr + ".txt"
                entry = image_class + " " + str(x_mid) + " " + str(y_mid) + " " + str(x_width) + " " + str(y_height)

                # Add a new file or write to existing file
                # append mode will create the file if it does not already exist
                with open(dest_path, "a") as dest_file:
                    dest_file.write(entry + "\n")


def split_into_folders(from_path):
    # Paths
    img_train_path = "images/train/"
    img_eval_path = "images/validation/"
    img_test_path = "images/test/"
    lbl_train_path = "labels/train/"
    lbl_eval_path = "labels/validation/"
    lbl_test_path = "labels/test/"
    paths = [img_train_path, img_eval_path, img_test_path, lbl_train_path, lbl_eval_path, lbl_test_path]

    # Split the files into the correct subgroups
    files = os.listdir(from_path)
    img_arr = []
    txt_arr = []
    for file in files:
        if file.endswith('.txt'):
            txt_arr.append(file)
        elif file.endswith('.jpg'):
            img_arr.append(file)
        else:
            print("SKIPPING FILE:", file)

    os.chdir(from_path)

    # Create new folders
    # os.mkdir("images")
    # os.mkdir("labels")
    # for path in paths:
    #     os.mkdir(path)

    # Gather indices
    df = pd.DataFrame()
    df["inds"] = range(len(img_arr))
    mask = np.random.rand(len(df)) < 0.8
    df_train = df[mask]
    df_remain = df[~mask]
    mask2 = np.random.rand(len(df_remain)) < 0.5
    df_eval = df_remain[mask2]  # 10% each
    df_test = df_remain[~mask2]  # 10% each

    # Move everything
    for i, row in df_train.iterrows():
        print("train row:", i)
        img_file = img_arr[i]
        txt_file = txt_arr[i]
        shutil.move(img_file, img_train_path + img_file)
        shutil.move(txt_file, lbl_train_path + txt_file)

    for i, row in df_eval.iterrows():
        print("validation row:", i)
        img_file = img_arr[i]
        txt_file = txt_arr[i]
        shutil.move(img_file, img_eval_path + img_file)
        shutil.move(txt_file, lbl_eval_path + txt_file)

    for i, row in df_test.iterrows():
        print("test row:", i)
        img_file = img_arr[i]
        txt_file = txt_arr[i]
        shutil.move(img_file, img_test_path + img_file)
        shutil.move(txt_file, lbl_test_path + txt_file)


def yolo_v5_preprocess(dir_path):
    os.chdir(dir_path)
    dest_loc_img = "yolov5_data/"
    dest_loc_annot = "yolov5_data/"
    for i in range(1, 101):  # Go through all dirs
        print("Going through dir:", i)
        sub_dir_path = str(i)
        files = os.listdir(sub_dir_path)
        for file in files:  # Go through all files in dir
            if file == "bb_info.txt":
                continue
            elif file.endswith('.txt'):
                # Get corresponding img dims
                im = Image.open(sub_dir_path + "/" + file[:-3] + 'jpg')
                width, height = im.size

                # Get bounding box position
                with open(sub_dir_path + "/" + file, "r") as txt_file:
                    contents = re.split("\s", txt_file.read())  # \s is whitespace characters
                    img_class = contents[0]
                    x_0 = int(contents[1])
                    x_max = int(contents[2])
                    y_max = int(contents[3])
                    y_0 = int(contents[4])

                # Convert to yolov5 data
                nr_decimals = 3
                x_mid = round(((x_max - x_0) / 2 + x_0) / width, nr_decimals)
                y_mid = round(((y_max - y_0) / 2 + y_0) / height, nr_decimals)

                x_width = round((x_max - x_0) / width, nr_decimals)
                y_height = round((y_max - y_0) / height, nr_decimals)

                dest_path = dest_loc_annot + file
                entry = img_class + " " + str(x_mid) + " " + str(y_mid) + " " + str(x_width) + " " + str(y_height)

                # Add a new file or write to existing file
                # append mode will create the file if it does not already exist
                with open(dest_path, "a") as dest_file:
                    dest_file.write(entry + "\n")

            elif file.endswith('.jpg'):
                # Just copy all images to destination location, we don't care if we overwrite
                shutil.copy(sub_dir_path + "/" + file, dest_loc_img + file)

            else:
                print("Encountered unexpected file:", file)


def arrange_images(dir_path):
    os.chdir(dir_path)
    dest_loc_img = "Images/"
    dest_loc_annot = "Annotations/"
    for i in range(100):
        fpath = str(i)
        files = os.listdir(fpath)
        for file in files:
            if file.endswith('.txt'):
                shutil.move(fpath + "/" + file, dest_loc_annot + file)
            else:
                shutil.move(fpath + "/" + file, dest_loc_img + file)

        break


if __name__ == "__main__":
    dir_p = sys.argv[1]
    # yolo_v5_preprocess_new(dir_path)
    split_into_folders((dir_p + "yolov5_data/"))
    print("Done!")
