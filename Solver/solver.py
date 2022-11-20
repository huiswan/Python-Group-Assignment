class SudokuSolver :
    def __init__(self, board):
        # board is a 2D array or a 2D nested list of the form : [[]]
        self.board = board

    def find_empty(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == 0:
                    # Return (row, column)
                    return (i, j)  
        return None
    
    def valid_row(self, number, position) : 
        for i in range(len(self.board[0])):
            if self.board[position[0]][i] == number and position[1] != i:
                return False
        return True

    def valid_column(self, number, position) :
        for i in range(len(self.board)):
            if self.board[i][position[1]] == number and position[0] != i:
                return False
        return True

    def valid_box(self, number, position) :
        box_x = position[1] // 3
        box_y = position[0] // 3
        for i in range(box_y*3, box_y*3 + 3):
            for j in range(box_x * 3, box_x*3 + 3):
                if self.board[i][j] == number and (i,j) != position:
                    return False
        return True


    def valid(self, number, position) :
        if(self.valid_row(number, position) and self.valid_column(number, position) and self.valid_box(number, position)) :
            return True
        return False

        
    def solve(self):
        res = self.find_empty(self.board)
        if not res:
            return True
        else:
            row, col = res
        for i in range(1,10):
            if self.valid(self.board, i, (row, col)):
                self.board[row][col] = i
                if self.solve(self.board):
                    return True
                self.board[row][col] = 0
        return False

    def print_board(self):
        # Print the sudoku board in the CLI (For debugging)
        for i in range(len(self.board)):
            if (i % 3 == 0 and i != 0):
                print("- - - - - - - - - - - - - ")
            for j in range(len(self.board[0])):
                if j % 3 == 0 and j != 0:
                    print(" | ", end="")
                if j == 8:
                    print(self.board[i][j])
                else:
                    print(str(self.board[i][j]) + " ", end="")