import numpy as np
import cv2

def read_and_prepare(file_path, options) :
    """
        1. Read the image
        2. Resize the image to given proportions
    """
    try :
        img = cv2.imread(file_path)
        img = cv2.resize(img, (options["img_width"], options["img_height"]))  
        return img
    except :
        print("Error while reading file !")
        exit(0)
        
def preprocess(img):

    """
        1. Convert to grayscale
        2. Add Gaussian blur to reduce noise
        3. Add Adaptive Threshold to create a binary image    
    """

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) 
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, 1, 1, 11, 2) 
    
    return imgThreshold


def find_contours(img) :
    """
        1. cv2.RETR_EXTERNAL : Gets the outer contour
        2. cv2.CHAIN_APPROX_SIMPLE : It removes all redundant points and compresses the contour, thereby saving memory
    """
    return cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

def draw_all_contours(img, contours, color, thickness=3) :
    return cv2.drawContours(img, contours, -1, color, thickness)

def find_biggest_contours(contours):

    """
        1. Iterate over all contours
        2. Find its area and check if it is greater 
           than some threshold (here, 200)
        3. Check if the contour has 4 sides
        4. If so, compute the maximum area of such contours
        5. Return the largest contour and the maximum area
    """

    biggest = np.array([])
    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 200:
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)

            # It has to be a quadrilateral
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area

    return biggest,max_area


def reorder_for_warp_perspective(points) :

    """
        1. Get the 4 corners of the contour. This can be 
           found by taking the extreme values on both 
           sides of the contour
        2. Modify the 4 corners to give a warp effect
    """

    points = points.reshape((4, 2))
    points_new = np.zeros((4, 1, 2), dtype=np.int32)

    s = points.sum(1)
    points_new[0] = points[np.argmin(s)]
    points_new[3] = points[np.argmax(s)]

    diff = np.diff(points, axis=1)
    points_new[1] = points[np.argmin(diff)]
    points_new[2] = points[np.argmax(diff)]
    
    return points_new


def default_warp(img, options) :
    p1, p2 = options["points"]
    w, h = options["dimensions"]
    col = options["convert_to_color"]
   
    matrix = cv2.getPerspectiveTransform(p1, p2)
    img_warp = cv2.warpPerspective(img, matrix, (w, h))
   
    if(col) :
        return cv2.cvtColor(img_warp, cv2.COLOR_BGR2GRAY)

    return img_warp

def split_into_boxes(img):
    rows = np.vsplit(img,9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r,9)
        for box in cols:
            boxes.append(box)
    return boxes

def display_result(img, numbers, color=(255, 0, 0)) :
    """
        sw : sector (box) width 
        sh : sector (box) height
    """
    sw = int(img.shape[1] / 9)
    sh = int(img.shape[0] / 9)

    for x in range (0,9):
        for y in range (0,9):
            # If the cell is not empty
            if numbers[(y * 9) + x] != 0 :
                cv2.putText(
                    img, 
                    str(numbers[(y * 9) + x]),
                    (x * sw + int(sw / 2) - 10,
                    int((y + 0.8) * sh)), 
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    2,
                    color,
                    2,
                    cv2.LINE_AA
                )
    return img

def draw_grid(img):
    """
        sw : sector (box) width 
        sh : sector (box) height
    """
    sw = int(img.shape[1] / 9)
    sh = int(img.shape[0] / 9)
    
    for i in range (0,9):
        pt1 = (0, sh * i)
        pt2 = (img.shape[1], sh * i)
        pt3 = (sw * i, 0)
        pt4 = (sw * i,img.shape[0])

        cv2.line(img, pt1, pt2, (255, 255, 0), 2)
        cv2.line(img, pt3, pt4, (255, 255, 0), 2)

    return img
