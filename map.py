import math
import numpy as np
import cv2
import keyboard

class ColoredSquare:
    """
    Each contour OpenCV detects will go through rigorous testing to ensure it
    is in fact a sticker on the cube.

    If program detects the sticker, and instance of this class is created storing the details for the sticker
    """

    def __init__(self, x_centre, y_centre, width, color):
        """
        :param x_centre: int screen coordinate
        :param y_centre: int screen coordinate
        :param color: string
        """
        assert type(color) == str

        self.x = x_centre
        self.y = y_centre
        self.width = width
        self.color = color


class MapRubiksCube:

    BGR_color = {'yellow':(0, 255, 255), 'white':(255, 255, 255), 'red':(0, 0, 255), 'blue':(255, 0, 0), 'green':(0, 255, 0), 'orange':(0, 139, 255)}

    # Define a dictionary storing the lower and upper bounds of the colors
    color_ranges = {'yellow': ((16, 2, 26), (60, 255, 255)), 'green': ((44, 140, 100), (90, 255, 255)),
                'blue': ((90, 100, 100), (135, 255, 220)), 'red': ((160, 50, 50), (180, 255, 255)),
                'orange': ((1, 10, 60), (24, 255, 255)), 'white': ((0, 0, 155), (180, 20, 255))}

    # The data structure for the cube is a list of 6 lists, storing the colors of each side
    cube = []

    min_contour_area = 800
    max_contour_area = 4000
    # OpenCV will detect contours not on the cube, therefore must filter some
    # List containing the class of ColoredSquare
    valid_contours = []

    # ORDER of reading (must show the camera this order): B Orange, U Yellow, F Red, L Blue, R Green, D white
    sides = ('o', 'y', 'r', 'w', 'g', 'b')

    currently_reading = 'o'

    waiting_confirmation = False

    all_sides_read = False




    def showFrame(self, frame, name=str):
        """
        show a new frame window
        """
        assert type(name) == str
        cv2.imshow(name, frame)



    def index_colored_squares(self, squares, currentside):
        """
        :param squares: a list of class ColoredSquares
        :param currentside: a char specifying the color of side reading

        We are given 9 detected colored squares. Sort them and create a list of chars representing the colors in order.
        (Based on legend)

        :return: a list which its order is based on legend below. Will be called to update the whole 'cubies' list
        """
        # Assume Red is Front, White is Down, Yellow is Up
        # INDEX LEGEND as the picture would appear:
        """
        | 8 | 7 | 6 |
        -------------
        | 5 | 4 | 3 |
        -------------
        | 2 | 1 | 0 |
        """

        # List of length 9 that will be returned and store all colors in correct order
        side_list = []

        # A list holding the index in square list, followed by x coordinate, y coordinate
        all_squares = list(enumerate(zip([square.x for square in squares], [square.y for square in squares])))
        bottom_three = sorted(all_squares, key= lambda x: x[1][1])[-3:]
        sorted_right_left = sorted(bottom_three, key=lambda x: x[1][0], reverse=True)
        for i in range(3):
            side_list.append(squares[sorted_right_left[i][0]].color[0])

        # Bottom three squares read, remove them from all squares
        for x in sorted_right_left:
            all_squares.remove(x)

        # Now get top three from all squares
        top_three = sorted(all_squares, key= lambda x: x[1][1])[:3]
        # Sort 6, 7, 8, top right = 6
        sorted_top = sorted(top_three, key= lambda x: x[1][0], reverse=True)

        for x in sorted_top:
            all_squares.remove(x)

        middle_sorted = sorted(all_squares, key= lambda x: x[1][0])

        right_edge = middle_sorted[-1]
        left_edge = middle_sorted[0]

        # Append the colors in correct order
        side_list.append(squares[right_edge[0]].color[0])
        # Omit calculating middle because its already known
        side_list.append(currentside)
        side_list.append(squares[left_edge[0]].color[0])

        for i in range(3):
            side_list.append(squares[sorted_top[i][0]].color[0])


        # Current side is index 4, middle square is always known
        # Update currently reading side to next side
        index_of_current = self.sides.index(self.currently_reading)
        if index_of_current != len(self.sides) - 1:
            self.currently_reading = self.sides[index_of_current + 1]
        else:
            self.all_sides_read = True

        return side_list



    def show_capture(self, frame, colored_squares):
        """
        Output a new frame with a freeze frame on the button
        Have colored circles around the tiles representing their color
        :param frame: the image where 9 squares were detected
        :param colored_squares: the list of the squares position and color
        :return:
        """

        # Draw the centres
        for square in colored_squares:
            center = (square.x + square.width // 2, square.y + square.width // 2)
            cv2.circle(frame, center, square.width // 2, self.BGR_color[square.color], thickness=6, lineType=8, shift=0)
        self.showFrame(frame, "Colors Detected")

        return



    def get_contour_corners(self, corners):
        """
        Given all points of the contour, return the 4 corners
        :param contour:
        :return: a tuple that hold 4 points of the corners of the contour (upL, upR, downL, downR)
        """
        y_sorted = sorted(corners.reshape(len(corners), 2), key = lambda x: x[1])
        top_left_to_right_sorted = sorted(y_sorted[:2], key= lambda x: x[0])

        top_left = top_left_to_right_sorted[0]
        top_right = top_left_to_right_sorted[1]

        y_sorted = y_sorted[::-1]
        bottom_left_to_right_sorted = sorted(y_sorted[:2], key= lambda x: [0])
        bottom_left = bottom_left_to_right_sorted[0]
        bottom_right = bottom_left_to_right_sorted[1]

        return (top_left, top_right, bottom_left, bottom_right)



    def distance_2_points(self, a, b):
        """
        Use pythagorean theorem to compute the distance of two tupled points
        :param a: x, y
        :param b: x2, y2
        :return: int distance
        """
        return int(math.sqrt((a[1] - b[1])**2 + (a[0] - b[0])**2))



    def filter_contour(self, cnt, perc_flexibility, color):
        """
        Attempt to filter all countours detected by openCV that aren't possible stickers.
        Contour must be a square, and have minimum and maxiumum area
        :param cnt: the contour read by the color mask
        :param perc_flexibility: The percent amount the height can vary from the width
        :return: place the contour in the valid list if it meets criteria
        """
        # Note this function can have numerous ways of filtering, these are just a few tests
        # that make the reading somewhat accurate.


        if not self.min_contour_area < cv2.contourArea(cnt) < self.max_contour_area:
            return

        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * perimeter, True)

        # The contour must have 4 corners
        if len(approx) < 4:
            return

        # Function returns the top left point of contour and width/height
        (x, y, w, h) = cv2.boundingRect(cnt)

        x_centre = x + w // 2
        y_centre = y + h // 2

        # FRAME is 480 tall, 640 wide
        if not (170 <= x_centre <= 500):
            return
        if not (75 <= y_centre <= 405):
            return

        aspect_ratio = w/h
        # Check if the aspect ratio of the detected contour is close to one
        if not ((1 - 1*perc_flexibility) <= aspect_ratio <= (1 + 1*perc_flexibility)):
            return

        # Check if center is within another center of already found contours
        for valid_cnt in self.valid_contours:
            if (valid_cnt.x <= x + w // 2 <= valid_cnt.x + valid_cnt.width) and (valid_cnt.y <= y + h // 2 <= valid_cnt.y + valid_cnt.width):
                return

        (up_left, up_right, down_left, down_right) = self.get_contour_corners(approx)

        dist_left = self.distance_2_points(up_left, down_left)
        if not (dist_left - (300*perc_flexibility) <= self.distance_2_points(up_left, up_right) <= dist_left + (300*perc_flexibility)):
            return
        if not (dist_left - (300*perc_flexibility) <= self.distance_2_points(up_right, down_right) <= dist_left + (300*perc_flexibility)):
            return
        if not (dist_left - (300*perc_flexibility) <= self.distance_2_points(down_left, down_right) <= dist_left + (300*perc_flexibility)):
            return

        # Add a new ColoredSquare class to valid list if the countour makes it down this function this far
        self.valid_contours.append(ColoredSquare(x, y, w, color))



    def read_cube(self):
        """
        Take in all sides, read colors, create the proper ordered list
        :return: output the cube chars to a file
        """

        last_frame_pressed = False
        detecting_release = False
        camera = cv2.VideoCapture(0)
        while not self.all_sides_read:
            if not self.waiting_confirmation:
                # Capture frame by frame
                (grabbed, frame) = camera.read()

                # Operations on the frame
                blurred = cv2.GaussianBlur(frame, (5, 5), 0)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                self.valid_contours = []

                for key in self.color_ranges:
                    # Analyze all color ranges
                    new_mask = cv2.inRange(hsv, self.color_ranges[key][0], self.color_ranges[key][1])

                    # Had issues with red and white detection, so added another range of color values for them
                    if key == 'red':
                        second_red = cv2.inRange(hsv, (0, 130, 130), (5, 255, 255))
                        new_mask += second_red
                    if key == 'white':
                        second_white = cv2.inRange(hsv, (85, 12, 245), (112, 195, 255))
                        new_mask += second_white

                    new_mask = cv2.erode(new_mask, None, iterations=2)
                    new_mask = cv2.dilate(new_mask, None, iterations=2)
                    contours = cv2.findContours(new_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                    self.showFrame(new_mask, key)
                    for cnt in contours:
                        self.filter_contour(cnt, 0.15, str(key))

                    # If at 8 (we know the middle color) or 9 sticker colors detect detected, output the image showing colors analyzed
                    # And wait confirmation from user
                    if (len(self.valid_contours) == 8 and self.currently_reading == 'w') or len(self.valid_contours) == 9:
                        self.waiting_confirmation = True
                        self.show_capture(frame, self.valid_contours)


                # Display the resulting frame
                cv2.putText(frame, 'Currently Reading: ' + self.currently_reading, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                self.showFrame(frame, "RAW")
            else:
                # Keyboard interaction: If what the program detects are the wrong colors, space will reset
                #                       Else press '*' and it permanently captures the colors and move to next side
                if keyboard.is_pressed('space'):
                    last_frame_pressed = True
                    detecting_release = True
                elif detecting_release:
                    last_frame_pressed = False

                if detecting_release and not last_frame_pressed:
                    detecting_release = False
                    self.waiting_confirmation = False
                    self.cube.append(
                        self.index_colored_squares(self.valid_contours, currentside=self.currently_reading))

                if keyboard.is_pressed('*'):
                    self.waiting_confirmation = False

            # Exit program
            if 'q' == chr(cv2.waitKey(1) & 255):
                break

        camera.release()
        cv2.destroyAllWindows()

        # Write the cube to a file
        outfile = open('rubiks_data.txt', 'w')
        for each_face in self.cube:
            outfile.write("".join(each_face))
            outfile.write("\n")
        outfile.close()
