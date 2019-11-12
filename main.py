from rubiks_cube import *
from map import MapRubiksCube
from solve import solve
import numpy as np

def getCube_fromFile():
    """
    Read characters from file and covert into a np chararray, the data structure for the cube
    :return: a numpy char array of the cube colors
    """
    path = "C:/Users/rymar/PycharmProjects/SolveRubiks/rubiks_data.txt"
    infile = open(path, 'r')
    faces = np.chararray((6, 9), 1, True)
    for i, line in enumerate(infile):
        for j, c in enumerate(line[:-1]):
            faces[i][j] = c

    infile.close()
    return faces

# Map the cube from webcam and create cube data
map = MapRubiksCube()
#map.read_cube()

# GET THE DATA STRUCTURE OF CUBE, list of chars!
cube = getCube_fromFile()

print(cube)
print("INITIAL")
print_cube(cube)
print()
# for n in range(1, 4):
#     for move in ('U', 'R', 'F', 'L', 'D', 'B'):
#         print(move + " " + str(n))
#         rubiks_cube.move([move+str(n)], cube)
#         rubiks_cube.print_cube(cube)
#         print()
#rubiks_cube.print_cube(cube)

# Call solve function that outputs moves
solve(cube)

