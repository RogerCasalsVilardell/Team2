import os
from glob import glob
import cv2
import numpy as np
import time


def TextBoxRemovalDark(img):
    # Resize image
    original_size = img.shape[:2]
    img = cv2.resize(img,(1000,1000))

    kernel = np.ones((10,50),np.uint8)
    dark = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    # bright = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    # mask = bright
    mask = dark

    finished = False
    start_row = 0
    while not finished:
        last_row_ind = -1
        last_col_width = -1
        mask_gray = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        for col_width in range(int(0.5*mask.shape[1]),int(0.1*mask.shape[1]),-2):
            last_col_width = col_width
            for row_ind in range(start_row,mask.shape[0]-int(0.02*mask.shape[0])):
                indexes = [row_ind,row_ind+int(0.02*mask.shape[0]),int(0.5*mask.shape[1])-int(col_width*0.5),int(0.5*mask.shape[1])+int(col_width*0.5)]
                rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
                if np.max(rectangle)-np.min(rectangle) < 10:
                    last_row_ind = row_ind
                    break
            if last_row_ind != -1:
                break

        for col_width in range(last_col_width,mask.shape[1],2):
            last_col_width = col_width
            indexes = [last_row_ind,last_row_ind+int(0.02*mask.shape[0]),int(0.5*mask.shape[1])-int(col_width*0.5),int(0.5*mask.shape[1])+int(col_width*0.5)]
            rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
            if np.max(rectangle)-np.min(rectangle) > 10:
                last_col_width = col_width-1
                break

        for row_length in range(int(0.02*mask.shape[0]),mask.shape[0]-int(0.02*mask.shape[0])):
            indexes = [last_row_ind,last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5),int(0.5*mask.shape[1])+int(last_col_width*0.5)]
            rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
            if np.max(rectangle)-np.min(rectangle) > 10:
                break

        print(last_row_ind)
        ratio = (last_row_ind+row_length-last_row_ind)/(int(0.5*mask.shape[1])+int(last_col_width*0.5)-int(0.5*mask.shape[1])+int(last_col_width*0.5))
        print("ratio:",ratio)
        if ratio > 0.1:
            finished = True
        else:
            start_row = last_row_ind+row_length+1

    mask = np.zeros(shape=mask.shape,dtype=np.uint8)
    mask[last_row_ind:last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5):int(0.5*mask.shape[1])+int(last_col_width*0.5)] = 255
    print((int(0.5*mask.shape[1]),last_row_ind+int(0.02*mask.shape[0])+10))

    mask = cv2.resize(mask,(original_size[1],original_size[0]))
    return mask

def TextBoxRemovalBright(img):
    # Resize image
    original_size = img.shape[:2]
    img = cv2.resize(img,(1000,1000))

    kernel = np.ones((10,50),np.uint8)
    # dark = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    bright = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    mask = bright
    # mask = dark
    # return mask

    finished = False
    start_row = 0
    while not finished:
        last_row_ind = -1
        last_col_width = -1
        mask_gray = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        for col_width in range(int(0.5*mask.shape[1]),int(0.1*mask.shape[1]),-2):
            last_col_width = col_width
            for row_ind in range(start_row,mask.shape[0]-int(0.02*mask.shape[0])):
                indexes = [row_ind,row_ind+int(0.02*mask.shape[0]),int(0.5*mask.shape[1])-int(col_width*0.5),int(0.5*mask.shape[1])+int(col_width*0.5)]
                rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
                if np.max(rectangle)-np.min(rectangle) < 10:
                    last_row_ind = row_ind
                    break
            if last_row_ind != -1:
                break

        for col_width in range(last_col_width,mask.shape[1],2):
            last_col_width = col_width
            indexes = [last_row_ind,last_row_ind+int(0.02*mask.shape[0]),int(0.5*mask.shape[1])-int(col_width*0.5),int(0.5*mask.shape[1])+int(col_width*0.5)]
            rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
            if np.max(rectangle)-np.min(rectangle) > 10:
                last_col_width = col_width-1
                break

        for row_length in range(int(0.02*mask.shape[0]),mask.shape[0]-int(0.02*mask.shape[0])):
            indexes = [last_row_ind,last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5),int(0.5*mask.shape[1])+int(last_col_width*0.5)]
            rectangle = mask_gray[indexes[0]:indexes[1],indexes[2]:indexes[3]]
            if np.max(rectangle)-np.min(rectangle) > 10:
                break

        print(last_row_ind)
        ratio = (last_row_ind+row_length-last_row_ind)/(int(0.5*mask.shape[1])+int(last_col_width*0.5)-int(0.5*mask.shape[1])+int(last_col_width*0.5))
        print("ratio:",ratio)
        if ratio > 0.1:
            finished = True
        else:
            start_row = last_row_ind+row_length+1

    mask = np.zeros(shape=mask.shape,dtype=np.uint8)
    mask[last_row_ind:last_row_ind+row_length,int(0.5*mask.shape[1])-int(last_col_width*0.5):int(0.5*mask.shape[1])+int(last_col_width*0.5)] = 255
    print((int(0.5*mask.shape[1]),last_row_ind+int(0.02*mask.shape[0])+10))

    mask = cv2.resize(mask,(original_size[1],original_size[0]))
    return mask
        


def main():
    for img_path in glob(os.path.join(r"C:\Users\PC\Documents\Roger\Master\M1\Project\Week2\qsd1_w2_bright","*.jpg"))[:]:
        print("\nUsing img_path",img_path)
        start = time.time()
        img = cv2.imread(img_path)
        # mask = TextBoxRemovalDark(img)
        mask = TextBoxRemovalBright(img)
        cv2.imwrite(img_path.replace(".jpg","_mask.png"),mask)
        print("time used:",str(time.time()-start))

if __name__ == '__main__':
    main()
