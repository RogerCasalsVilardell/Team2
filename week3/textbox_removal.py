import os
from glob import glob
import cv2
import numpy as np
import time


def TextBoxRemoval(img):
    # Parameters
    resize_size = (1000,1000)
    rectangle_max_min_difference = 10
    col_width_cut = 10
    th_gray = 30
    min_ratio = 0.08
    max_ratio = 0.4
    row_limits = [0.35,0.65]

    # Resize image
    original_size = img.shape[:2]
    img = cv2.resize(img,resize_size)

    # Opening and closing separately
    kernel_size = (10,50)
    kernel = np.ones(kernel_size,np.uint8)
    dark = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    bright = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    dark = np.abs(np.max(dark,axis=2)-np.min(dark,axis=2))
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
    bright = np.abs(np.max(bright,axis=2)-np.min(bright,axis=2))
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))

    cv2.imwrite(r"C:\Users\PC\Documents\Roger\Master\M1\Project\Week3\tests_folder\testdark.png",dark)
    cv2.imwrite(r"C:\Users\PC\Documents\Roger\Master\M1\Project\Week3\tests_folder\testbright.png",bright)

    # Search for largest uniform rectangle on both opening and closing
    rectangles = {"bright": None, "dark": None}
    for mask,mask_name in zip([bright, dark],["bright","dark"]):
        # print("mask_name:",mask_name)
        mask_gray = mask
        finished = False
        start_row = 0
        start_col_width = int(0.5*mask.shape[1])
        # mask_gray = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        # mask_gray = mask[:,:,1]
        while not finished:
            last_row_ind = -1
            last_col_width = -1
            for col_width in range(start_col_width,int(0.1*mask.shape[1]),-2):
                # print("col_width:",col_width,"start_row:",start_row)
                last_col_width = col_width
                for row_ind in range(start_row,mask.shape[0]-int(0.02*mask.shape[0])):
                    # print("    row_ind:",row_ind)
                    start_row = 0
                    indexes = [row_ind,row_ind+int(0.02*mask.shape[0]),int(0.5*mask.shape[1])-int(col_width*0.5),int(0.5*mask.shape[1])+int(col_width*0.5)]
                    rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
                    mean_rectangle = np.mean(rectangle)
                    if mask_name == "bright":
                        cond = mean_rectangle <= th_gray
                    else:
                        cond = mean_rectangle <= th_gray
                    if np.max(rectangle)-np.min(rectangle) < rectangle_max_min_difference and cond:
                        last_row_ind = row_ind
                        break
                if last_row_ind != -1:
                    break

            if last_row_ind == -1:
                break

            start_col_width = last_col_width-1

            for col_width in range(last_col_width,mask.shape[1],2):
                last_col_width = col_width
                indexes = [last_row_ind,last_row_ind+int(0.02*mask.shape[0]),int(0.5*mask.shape[1])-int(col_width*0.5),int(0.5*mask.shape[1])+int(col_width*0.5)]
                rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
                mean_rectangle = np.mean(rectangle)
                if mask_name == "bright":
                    cond = mean_rectangle <= th_gray
                else:
                    cond = mean_rectangle <= th_gray
                if np.max(rectangle)-np.min(rectangle) > rectangle_max_min_difference and cond:
                    last_col_width = col_width-col_width_cut
                    break

            for row_length in range(int(0.02*mask.shape[0]),mask.shape[0]-int(0.02*mask.shape[0])):
                indexes = [last_row_ind,last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5),int(0.5*mask.shape[1])+int(last_col_width*0.5)]
                rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
                mean_rectangle = np.mean(rectangle)
                if mask_name == "bright":
                    cond = mean_rectangle <= th_gray
                else:
                    cond = mean_rectangle <= th_gray
                if np.max(rectangle)-np.min(rectangle) > rectangle_max_min_difference and cond:
                    break

            ratio = row_length*original_size[0]/((int(0.5*mask.shape[1])+int(last_col_width*0.5)-int(0.5*mask.shape[1])+int(last_col_width*0.5))*original_size[1])
            # print("ratio:",ratio,"last_row_ind:",last_row_ind)
            first_x = last_row_ind
            last_x = last_row_ind+row_length
            # print("first_x:",first_x,"last_x:",last_x)
            condition = (last_x < row_limits[0]*mask.shape[0] or first_x > row_limits[1]*mask.shape[0])
            if min_ratio < ratio < max_ratio and condition:
                finished = True
                rectangles[mask_name] = [last_row_ind,row_length,last_col_width]
            else:
                start_row = last_row_ind+1
                if start_row > mask.shape[0]-int(0.04*mask.shape[0]):
                    start_row = 0

    # Deciding which rectangle to use (the one from opening or closing)
    if rectangles["bright"] is None and rectangles["dark"] is None:
        mask = np.ones(shape=(mask.shape[0],mask.shape[1]),dtype=np.uint8)*255
        mask = cv2.resize(mask,(original_size[1],original_size[0]))
        return mask, [[0,0],[mask.shape[0],mask.shape[1]]]
    elif rectangles["bright"] is None and rectangles["dark"] is not None:
        last_row_ind = rectangles["dark"][0]
        row_length = rectangles["dark"][1]
        last_col_width = rectangles["dark"][2]
    elif rectangles["bright"] is not None and rectangles["dark"] is None:
        last_row_ind = rectangles["bright"][0]
        row_length = rectangles["bright"][1]
        last_col_width = rectangles["bright"][2]
    else:
        last_row_ind = rectangles["bright"][0]
        row_length = rectangles["bright"][1]
        last_col_width = rectangles["bright"][2]
        indexes = [last_row_ind,last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5),int(0.5*mask.shape[1])+int(last_col_width*0.5)]
        bright_rect = img[indexes[0]:indexes[1],indexes[2]:indexes[3]]
        mean_0_bright = np.mean(bright_rect[:,:,0])
        mean_1_bright = np.mean(bright_rect[:,:,1])
        mean_2_bright = np.mean(bright_rect[:,:,2])

        last_row_ind = rectangles["dark"][0]
        row_length = rectangles["dark"][1]
        last_col_width = rectangles["dark"][2]
        indexes = [last_row_ind,last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5),int(0.5*mask.shape[1])+int(last_col_width*0.5)]
        dark_rect = img[indexes[0]:indexes[1],indexes[2]:indexes[3]]
        mean_0_dark = np.mean(dark_rect[:,:,0])
        mean_1_dark = np.mean(dark_rect[:,:,1])
        mean_2_dark = np.mean(dark_rect[:,:,2])

        means_bright = (np.abs(mean_0_bright-mean_1_bright)+np.abs(mean_0_bright-mean_2_bright)+np.abs(mean_2_bright-mean_1_bright))/3
        means_dark = (np.abs(mean_0_dark-mean_1_dark)+np.abs(mean_0_dark-mean_2_dark)+np.abs(mean_2_dark-mean_1_dark))/3

        if bright_rect.shape[0]*bright_rect.shape[1] < dark_rect.shape[0]*dark_rect.shape[1]:
            print("decision dark")
            last_row_ind = rectangles["dark"][0]
            row_length = rectangles["dark"][1]
            last_col_width = rectangles["dark"][2]
        else:
            print("decision bright")
            last_row_ind = rectangles["bright"][0]
            row_length = rectangles["bright"][1]
            last_col_width = rectangles["bright"][2]

    tl = [last_row_ind,int(0.5*mask.shape[1])-int(last_col_width*0.5)]
    br = [last_row_ind+row_length,int(0.5*mask.shape[1])+int(last_col_width*0.5)]
    tl[0] = int(tl[0]*original_size[0]/resize_size[0])
    tl[1] = int(tl[1]*original_size[1]/resize_size[1])
    br[0] = int(br[0]*original_size[0]/resize_size[0])
    br[1] = int(br[1]*original_size[1]/resize_size[1])
    mask = np.ones(shape=(mask.shape[0],mask.shape[1]),dtype=np.uint8)*255
    mask = cv2.resize(mask,(original_size[1],original_size[0]))
    mask[tl[0]:br[0],tl[1]:br[1]] = 0

    return mask, [tl,br]

def main():
    for img_path in glob(os.path.join(r"C:\Users\PC\Documents\Roger\Master\M1\Project\Week2\qsd1_w2","*.jpg"))[:]:
        print("\nUsing img_path",img_path)
        start = time.time()
        img = cv2.imread(img_path)
        mask = TextBoxRemoval(img)
        cv2.imwrite(img_path.replace(".jpg","_mask.png"),mask)
        print("time used:",str(time.time()-start))

if __name__ == '__main__':
    main()
