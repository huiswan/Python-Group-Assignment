import numpy as np

from CLI_Parser import CLI
from image_utils import *
from OCR.digit_recognition import OCR
from Solver.solver import SudokuSolver


if __name__ == "__main__" :    
    img_height = 450
    img_width = 450

    cli = CLI().get_args()
    image_path = cli.i

    # 1. Reading and Preprocessing Image

    read_and_prepare_options = {
        "img_width": img_width,
        "img_height": img_height,
    } 
    img = read_and_prepare(image_path, read_and_prepare_options)
    img_threshold = preprocess(img)
    img_blank = np.zeros((img_height, img_width, 3), np.uint8)
    
    # 2. Variable Declaration

    img_contours = img.copy() 
    img_contours_cpy = img.copy() 
    img_detected_digits = img_blank.copy()
    img_solved_digits = img_blank.copy()

    # 3. Finding Contours

    contours, hierarchy = find_contours(img_threshold)
    draw_all_contours(img_contours, contours, (0, 255, 0))


    # 4. Find The Sudoku : 
    # (Assumption) The largest_contour area of
    # a quadrilateral in the image is the sudoku 

    largest_contour, max_area = find_biggest_contours(contours)

    if largest_contour.size != 0:

        largest_contour = reorder_for_warp_perspective(largest_contour)
        draw_all_contours(img_contours_cpy, largest_contour, (255, 0, 0), 20)

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
            "convert_to_color" : True
        }

        img_warp_colored = default_warp(img, default_warp_options)

      
        # 5. Finding The Digits

        boxes = split_into_boxes(img_warp_colored)

        # 6. Get The Numbers From The Image
        
        model = OCR().get_model()
        numbers = model.get_predection(boxes, model)
        
        img_detected_digits = display_result(img_detected_digits, numbers, color=(255, 0, 255))

        numbers = np.asarray(numbers)
        pos = np.where(numbers > 0, 0, 1)

        # 7. Find The Solution For The Sudoku Board

        board = np.array_split(numbers, 9)
        ss = SudokuSolver(board)
        try:
            ss.solve(board)
            ss.print_board(board)
        except:
            print("NOT SOLVED !")
            pass
        
        res = []
        for sublist in board:
            for item in sublist:
                res.append(item)

        solved_numbers = res * pos
        img_solved_digits = display_result(img_solved_digits,solved_numbers)

        # 8. Overlay The Solution

        default_warp_options_inv = default_warp_options.copy()
        default_warp_options_inv.points = [pts2, pts1]

        img_warp_colored = default_warp(img_solved_digits, default_warp_options_inv)

        output_image = cv2.addWeighted(img_warp_colored, 1, img, 0.5, 1)

        img_detected_digits = draw_grid(img_detected_digits)
        img_solved_digits = draw_grid(img_solved_digits)

        cv2.imshow("Output", output_image)

    else:
        print("No Sudoku Found")

cv2.waitKey(0)
cv2.destroyAllWindows()
