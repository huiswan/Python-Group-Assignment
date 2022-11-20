import argparse

class CLI :
    def __init__(self) :
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
            description="Parameters for the sudoku solver", 
            allow_abbrev=True, 
            add_help=True
        )
        
        self.parser.add_argument("-d", help="Debug Mode", action="store_true")
        self.parser.add_argument("-i", help="Image absolute path", default="./Testing_Images/1.jpg")
        # self.parser.add_argument("-w", help="Real time (Webcam)", action="store_false")
    
    def get_args(self) :
        return self.parser.parse_args()