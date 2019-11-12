import numpy as np

def print_cube(faces):
    """
    Print the cube in a 2d way in console
    :param faces: the cube data list
    """
    printL = []
    # Prints first two sides (BACK and UP)
    for i in range(2):
        for color in faces[i]:
            printL.append(color)
            if len(printL) == 3:
                print(' '.join(printL).center(17, " "))
                printL = []

    lside = []
    fside = []
    rside = []
    # Longer list needed
    for i in range(9):
        lside.append(faces[5][i])
        fside.append(faces[2][i])
        rside.append(faces[4][i])
        if (i + 1) % 3 == 0:
            print(' '.join(lside + fside + rside))
            lside = []
            fside = []
            rside = []

    for color in faces[3]:
        printL.append(color)
        if len(printL) == 3:
            print(' '.join(printL).center(17, " "))
            printL = []
    return


# Cube rotations
#---------------------------------------------------------------------------------------
# Indexes of faces


l_column = (0, 3, 6)
m_column = (1, 4, 7)
r_column = (2, 5, 8)
all_columns = (l_column, m_column, r_column)

u_row = (0, 1, 2)
m_row = (3, 4, 5)
d_row = (6, 7, 8)
all_rows = (u_row, m_row, d_row)



#          0  1  2  3  4  5
# faces = [B, U, F, D, R, L]
# All move functions needs integer specifying number of clockwise rotations

def rotate_sides(sides, side_slice, rotations, faces):
    """

    :param sides: a list of indexes of sides that will need updating
    :param side_slice: a list of tuples giving the index slice of face that will be affected
    :param rotations: int number of clockwise rotations
    :return: 4 new lists
    """
    for _ in range(rotations):
        updating_colors = []
        for i in range(4):
            updating_colors.append([faces[sides[i]][n] for n in side_slice[i]])
        for i in range(4):
            if i == 0:
                from_side = updating_colors[-1]
            else:
                from_side = updating_colors[i - 1]
            for j in range(len(side_slice[i])):
                faces[sides[i]][side_slice[i][j]] = from_side[j]


# Face to index in face list
moves_dict = {'U': 1, 'D': 3, 'F': 2, 'B': 0, 'L': 5, 'R': 4}
#                   side index order  slice of list to update
sides_affected = {'U': [[2, 5, 0, 4], [u_row, u_row, d_row[::-1], u_row]], 'D': [[2, 4, 0, 5], [d_row, d_row, u_row[::-1], d_row]],
                  'F': [[3, 5, 1, 4], [u_row, r_column, d_row[::-1], l_column[::-1]]], 'B': [[3, 4, 1, 5], [d_row, r_column[::-1], u_row[::-1], l_column]],
                  'L': [[2, 3, 0, 1], [l_column, l_column, l_column, l_column]], 'R': [[2, 1, 0, 3], [r_column, r_column, r_column, r_column]]}


def move(move_sequence, faces):
    """
    Given a string sequence of moves, apply them on the faces
    :param move_sequence: a list of string moves
    :param faces: teh np chararray of cube
    :return: np chararray of size 6, 9
    """

    # Move sequence is defined as ['U1', 'U2', 'F3']
    #          0  1  2  3  4  5
    # faces = [B, U, F, D, R, L]


    for move in move_sequence:
        # Rotate the face itself
        index = moves_dict[move[0]]
        faces[index] = np.reshape(np.rot90(np.reshape(faces[index], (3, 3)), int(move[1]), (1,0)), (9))

        # Rotate the other sides affected
        side_indexes = sides_affected[move[0]][0]
        side_slices = sides_affected[move[0]][1]



        if move[1] == '3':
            for i in range(3):
                faces[side_indexes[0]][side_slices[0][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[3]][side_slices[3][i]] \
                    = faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[3]][side_slices[3][i]], faces[side_indexes[0]][side_slices[0][i]]
        elif move[1] == '1':
            for i in range(3):
                faces[side_indexes[3]][side_slices[3][i]], faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[0]][side_slices[0][i]] \
                    = faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[0]][side_slices[0][i]], faces[side_indexes[3]][side_slices[3][i]]
        else:
            for i in range(3):
                faces[side_indexes[3]][side_slices[3][i]], faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[0]][side_slices[0][i]] \
                    = faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[0]][side_slices[0][i]], faces[side_indexes[3]][side_slices[3][i]]
            for i in range(3):
                faces[side_indexes[3]][side_slices[3][i]], faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[0]][side_slices[0][i]] \
                    = faces[side_indexes[2]][side_slices[2][i]], faces[side_indexes[1]][side_slices[1][i]], faces[side_indexes[0]][side_slices[0][i]], faces[side_indexes[3]][side_slices[3][i]]

        #rotate_sides(side_indexes, sides_affected[move[0]][1], int(move[1]), faces)

















