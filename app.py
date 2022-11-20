import numpy as np

from CLI_Parser import CLI
from image_utils import *
from OCR.digit_recognition import OCR
from Solver.solver import SudokuSolver


if __name__ == "__main__" :    
    
    required_img_height = 450
    required_img_width = 450

    cli = CLI().get_args()
    image_path = cli.i
    debug_mode = cli.d

    print("INPUT IMAGE PATH : ", image_path)
    print("DEBUG MODE : ", debug_mode)

    # 1. Reading and Preprocessing Image

    # read_and_prepare_options = {
    #     "img_width": img_width,
    #     "img_height": img_height,
    # } 
    # img = read_and_prepare(image_path, read_and_prepare_options)

    try :
        img = cv2.imread(image_path)
    except :
        print("ERROR WHILE READING THE FILE !")
        exit(0)
    

    img_height = img.shape[0] 
    img_width = img.shape[1]

    img_threshold = preprocess(img)
    img_blank = np.zeros((required_img_height, required_img_width, 3), np.uint8)
    
    if(debug_mode) :
        cv2.imshow("Input Image", img)
        cv2.imshow("Image After Thresholding", img_threshold)

    # 2. Variable Declaration

    img_contours = img.copy() 
    img_contours_cpy = img.copy() 

    # 3. Finding Contours

    contours, hierarchy = find_contours(img_threshold)
    draw_all_contours(img_contours, contours, (0, 255, 0))

    if(debug_mode) :
        cv2.imshow("Contours", img_contours)


    # 4. Find The Sudoku : 
    # (Assumption) The largest_contour area of
    # a quadrilateral in the image is the sudoku 

    largest_contour, max_area = find_biggest_contours(contours)

    if largest_contour.size != 0:
        img_detected_digits = img_blank.copy()
        img_solved_digits = img_blank.copy()

        largest_contour = reorder_for_warp_perspective(largest_contour)
        draw_all_contours(img_contours_cpy, largest_contour, (255, 0, 0), 20)

        if(debug_mode) :
            cv2.imshow("Largest Contour After Reordering", img_contours_cpy)

        # Prepare the points for warping

        pts1 = np.float32(largest_contour) 
        pts2 = np.float32(
            [
                [0, 0],
                [img_width, 0], 
                [0, img_height], 
                [img_width, img_height]
            ]
        ) 

        default_warp_options = {
            "points" : [pts1, pts2],
            "dimensions" : [img_width, img_height],
            "convert_to_gray" : True
        }

        sudoku_img = default_warp(img, default_warp_options)
        sudoku_img = cv2.resize(sudoku_img, (required_img_width, required_img_height))
        sudoku_img = sharpen(sudoku_img)

        if(debug_mode) :
            cv2.imshow("Image After Warping", sudoku_img)        

        cv2.imshow("Identified Sudoku", sudoku_img)
      
        # 5. Finding The Digits

        boxes = split_into_boxes(sudoku_img)

        # 6. Get The Numbers From The Image
        
        model = OCR()
        result_threshold = 0.7
        numbers = model.get_prediction(boxes, result_threshold)
        
        img_detected_digits = display_result(img_detected_digits, numbers, color=(255, 0, 255))

        if(debug_mode) :
            cv2.imshow("Detected Digits", img_detected_digits)

        numbers = np.asarray(numbers)
        pos = np.where(numbers > 0, 0, 1)

        # 7. Find The Solution For The Sudoku Board

        board = np.array_split(numbers, 9)
        ss = SudokuSolver(board)
        try:
            ss.solve()
            ss.print_board()
        except:
            print("SUDOKU COULD NOT BE SOLVED !")
            exit(0)
        
        res = []
        for sublist in board:
            for item in sublist:
                res.append(item)

        solved_numbers = res * pos
        img_solved_digits = display_result(img_solved_digits,solved_numbers)

        
        if(debug_mode) :
            cv2.imshow("Solved Digits", img_solved_digits)

        # 8. Overlay The Solution

        img_solved_digits = cv2.cvtColor(img_solved_digits, cv2.COLOR_BGR2GRAY)

        output_image = cv2.addWeighted(img_solved_digits, 2, sudoku_img, 0.25, 1)

        img_detected_digits = draw_grid(img_detected_digits)
        img_solved_digits = draw_grid(img_solved_digits)

        cv2.imshow("Output", output_image)

    else:
        print("No Sudoku Found")

cv2.waitKey(0)
cv2.destroyAllWindows()
