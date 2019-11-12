import numpy as np
import copy
from rubiks_cube import *

# Implementation of thislethwaites algorithm

moves = ('F', 'B', 'U', 'D', 'L', 'R')

get_opposite = {'r':'o', 'o':'r', 'y':'w', 'w':'y', 'g':'b', 'b':'g'}

face_to_color = {'F': 'r', 'B':'o', 'U':'y', 'D':'w', 'R':'g', 'L':'b'}


edges = (1, 3, 5, 7)
corners = (0, 2, 6, 8)
#                           0  1  2  3  4  5
# Order of the faces given: B, U, F, D, R, L
# Given the index of face,

#               face index: {dict of edges to matching list index}]
face_to_edges = {
    0: {1: (3, 7), 3: (5, 3), 5: (4, 5), 7: (1, 1)},
    1: {1: (0, 7), 3: (5, 1), 5: (4, 1), 7: (2, 1)},
    2: {1: (1, 7), 3: (5, 5), 5: (4, 3), 7: (3, 1)},
    3: {1: (2, 7), 3: (5, 7), 5: (4, 7), 7: (0, 1)},
    4: {1: (1, 5), 3: (2, 5), 5: (0, 5), 7: (3, 5)},
    5: {1: (1, 3), 3: (0, 3), 5: (2, 3), 7: (3, 3)}
}

def move_list_to_string(move_list):
    """
    :param move_list: a list of tupled moves
    :return: A simplified string format of the moves
    """
    # A move is defined as a number of rotations on a given face 'char'
    # Function will handle moves in a tuple of length 2 (int rotations, 'face')
    curr_string = ""
    for move in move_list:
        if move[1] == '1':
            curr_string += move[0]
        elif move[1] == '2':
            curr_string += move
        elif move[1] == '3':
            curr_string += move[0] + "'"
        curr_string += " "

    return curr_string



def is_phase1_complete(faces):
    """
    Check if cube is done phase 1
    :param faces: the cube list
    :return: True of False whether phase one is done
    """

    # Criteria listed in phase1 function docstring

    if faces[1][1] == 'o' or faces[1][5] == 'r' or faces[1][5] == 'g' or faces[1][5] == 'b' or faces[1][7] == 'r' or faces[1][7] == 'o' or faces[1][3] == 'b' or faces[1][3] == 'g':
        return False
    if faces[3][1] == 'r' or faces[3][3] == 'b' or faces[3][5] == 'g' or faces[3][7] == 'o' or faces[3][1] == 'o' or faces[3][3] == 'g' or faces[3][5] == 'b' or faces[3][7] == 'r':
        return False
    if (faces[0][1] == 'b' or faces[0][1] == 'g') or (faces[0][3] == 'b' or faces[0][3] == 'g') or (faces[0][5] == 'b' or faces[0][5] == 'g') or (faces[0][7] == 'b' or faces[0][7] == 'g'):
        return False
    if (faces[2][1] == 'b' or faces[2][1] == 'g') or (faces[2][3] == 'b' or faces[2][3] == 'g') or (faces[2][5] == 'b' or faces[2][5] == 'g') or (faces[2][7] == 'b' or faces[2][7] == 'g'):
        return False
    if (faces[4][1] == 'o' or faces[4][1] == 'r') or (faces[4][3] == 'o' or faces[4][3] == 'r') or (faces[4][5] == 'o' or faces[4][5] == 'r') or (faces[4][7] == 'o' or faces[4][7] == 'r'):
        return False
    if (faces[5][1] == 'o' or faces[5][1] == 'r') or (faces[5][3] == 'o' or faces[5][3] == 'r') or (faces[5][5] == 'o' or faces[5][5] == 'r') or (faces[5][7] == 'o' or faces[5][7] == 'r'):
        return False
    return True


def is_phase2_complete(faces):
    """
    Check if cube is done phase 2
    :param faces: the cube list
    :return: True of False whether phase one is done
    """

    """
    We are complete phase 2 when all L and R corners are on their sides, can be on opposite
    """


    for corner_index in corners:
        # Check L
        if not (faces[5][corner_index] == face_to_color['L'] or faces[5][corner_index] == face_to_color['R']):
            return False
        if not (faces[4][corner_index] == face_to_color['L'] or faces[4][corner_index] == face_to_color['R']):
            return False

    middle_edges = (1, 7)
    non_LR_sides = {'F': 2, 'B': 0, 'U': 1, 'D': 3}
    for side in non_LR_sides:
        side_list = faces[non_LR_sides[side]]
        for edge in middle_edges:
            if side_list[edge] == 'b' or side_list[edge] == 'g':
                return False

    return True




def depth_search(omit_moves, max_depth, condition_func, faces):
    """
    Return the string of moves needed to solve the phase
    :param omit_moves: the banned moves for this stage
    :param condition_func: boolean function to test if phase is satisfied
    :param max_depth: the max number of moves to solve the stage
    :param faces: the original state of the cube given in a 2d list
    :return: a list of strings
    """
    phase_moves = np.array(
        ['U1', 'U2', 'U3', 'D1', 'D2', 'D3', 'F1', 'F2', 'F3', 'B1', 'B2', 'B3', 'R1', 'R2', 'R3', 'L1', 'L2', 'L3'])

    # Filter phase moves
    for omit_move in np.nditer(omit_moves):
        phase_moves = np.delete(phase_moves, np.argwhere(phase_moves == omit_move))

    # Have a dictionary that has keys of each move, and the next depth moves to search as a value
    new_depth_dict = {}
    for each_move in phase_moves:
        new_depth_dict[each_move] = np.array([m for m in phase_moves if m[0] != each_move[0]])

    new_depth_moves_len = {}
    for each_move2 in new_depth_dict:
        new_depth_moves_len[each_move2] = len(new_depth_dict[each_move2])

    # Initialize starting depth
    phase_move_data = np.ndarray((len(phase_moves), 2), dtype=object)

    for i in range(len(phase_moves)):
        phase_move_data[i][0] = [phase_moves[i]]
        phase_move_data[i][1] = np.array(faces)
        move(phase_move_data[i][0], phase_move_data[i][1])


        if condition_func(phase_move_data[i][1]):
            return phase_move_data[i][0]


    previous_depth = phase_move_data

    # Now starting at depth 2 search
    for curr_depth in range(2, max_depth + 1):
        print("Calculating Depth " + str(curr_depth))
        new_depth_moves = np.empty((0, 2), dtype=object)

        for x in np.nditer(previous_depth, flags=['external_loop', 'refs_ok'], order='F'):
            for move_list in np.nditer(x, ['refs_ok']):
                last_move_str = move_list.tolist()[-1]

                new_str_moves = new_depth_dict[last_move_str] # list of str moves
                next_depth_moves = np.ndarray((new_depth_moves_len[last_move_str], 2), dtype=object)

                for index, next_move in np.ndenumerate(new_str_moves):
                    new_move_list = move_list.tolist() + [next_move]
                    next_depth_moves[index][0] = new_move_list
                    next_depth_moves[index][1] = np.array(faces)
                    move(new_move_list, next_depth_moves[index][1])

                    if condition_func(next_depth_moves[index][1]):
                        return next_depth_moves[index][0]
                new_depth_moves = np.concatenate((new_depth_moves, next_depth_moves))

            break
        previous_depth = new_depth_moves



    # curr_depth = 2
    # while curr_depth <= max_depth:
    #     next_phase_data = np.ndarray((, 2), dtype=object)
    #     # Create new phase moves
    #     for x in np.ndi
    #     # Check the phase move




            # Add each move

    # # Loop until current depth reaches max depth
    # for curr_depth in range(1, max_depth + 1):
    #     # Test all moves
    #     for move_sequence in all_moves: # This move is a list of a sequence of moves
    #         # Perform move rotations
    #         # Return the sequence if it solves the stage
    #         if condition_func(move(move_sequence, faces)) == True:
    #             return move_sequence
    #
    #     # Add new depth moves
    #     if curr_depth < max_depth:
    #         # moves_list = [[(1, 'U'), (1, 'D')], [(1, 'U'), (3, 'D')], [(3, 'U'), (1, 'D')], [(3, 'U'), (3, 'D')]]
    #         new_moves_list = []
    #         for move_sequence in all_moves:
    #             add_moves = new_permissible_moves(omit_moves, move_sequence[-1])
    #
    #             for i in range(len(add_moves)):
    #                 new_sequence = []
    #                 new_sequence += move_sequence
    #                 new_sequence.append(add_moves[i])
    #                 new_moves_list.append(new_sequence)
    #
    #         all_moves = []
    #         all_moves += new_moves_list
    #         print("Increased to depth" + str(curr_depth))


def new_permissible_moves(omit_moves, last_move):
    """
    Create a new pool of moves to add to search list
    :param omit_moves: the moves to not allowed in stage
    :param last_move: a char of the face last moves
    :return: a new list of moves (tuples)
    """
    # This is called as once going to next depth
    # Since it is unpractical to move the same face as last moved, ensure they get filtered

    new_moves = []
    for c in moves:
        for n in range(1, 4):
            if (not c+str(n) in omit_moves) and c != last_move:
                new_moves.append(c+str(n))
    return new_moves



def phase1(faces):
    """
    Objective is to orient all edge pieces correctly
    :return: a string of moves to complete phase 1
    """
    """
    Edge pieces are not corners nor middles

    A 'GOOD' edge piece is defined as being able to be moved to its home position without
    a quarter turn of the U or D faces. (U2 or D2 fine)

    Pattern detected:
    Go through all faces but U and D,
    if the 4 edge pieces are of same color as side OR opposite side, GOOD
    if edge is yellow or white, and its attached edge is not same or opposite color, GOOD

    """
    # Compute the MINIMUM number of moves that would satisfy phase 1
    # Recursion, depth search
    # In recursion, the next possible rotations should omit the previous face rotation

    """
    DATA STRUCTURE for a move, tuple of length two
    (int rotations, 'char of face')
    """

    max_depth = 7 # Inclusive

    # Check if cube already done phase 1
    if is_phase1_complete(faces):
        return "No Phase 1 moves"

    # Create a list of the banned moves for phase 1
    banned = np.array(['U2', 'D2'])
    return depth_search(banned, max_depth, is_phase1_complete, faces)


def phase2(faces):
    """
    Objective is to get all L and R corners on their faces, and orient FU, FD, BU, BD edges
    :return: a string of moves that satisfy phase 2
    """

    if is_phase2_complete(faces):
        return "No Phase 2 moves"

    max_depth = 10
    # Banned moves for phase 2
    banned = np.array(['U1', 'U3', 'D1', 'D3'])
    return depth_search(banned, max_depth, is_phase2_complete, faces)

















def solve(faces):
    """
    Output the moves that solves the given cube
    :param CUBE: the class instance of the current rubiks cube
    :return: nothing, the phases will output their moves
    """
    solved1 = phase1(faces)


    # Put the moves on the faces that solved previous stage
    # Ensure there was moves that solved it
    if type(solved1) == list:
        print(move_list_to_string(solved1))
        move(solved1, faces)
    else:
        print(solved1)


    solved2 = phase2(faces)


    if type(solved2) == list:
        print(move_list_to_string(solved2))
        move(solved2, faces)
    else:
        print(solved2)


