import os
import sys
import cv2
import numpy as np

# The coordinates defining the square selected will be kept in this list.
select_coords = []
# While we are in the process of selecting a region, this flag is True.
selecting = False

def get_square_coords(x, y, cx, cy):
    """
    Get the diagonally-opposite coordinates of the square.
    (cx, cy) are the coordinates of the square centre.
    (x, y) is a selected point to which the largest square is to be matched.

    """

    # Selected square edge half-length; don't stray outside the image boundary.
    a = max(abs(cx-x), abs(cy-y))
    a = min(a, w-cx, cx, h-cy, cy)
    return cx-a, cy-a, cx+a, cy+a


def region_selection(event, x, y, flags, param): 
    """Callback function to handle mouse events related to region selection."""
    global select_coords, selecting, image

    if event == cv2.EVENT_LBUTTONDOWN: 
        # Left mouse button down: begin the selection.
        # The first coordinate pair is the centre of the square.
        select_coords = [(x, y)]
        selecting = True

    elif event == cv2.EVENT_MOUSEMOVE and selecting:
        # If we're dragging the selection square, update it.
        image = rotate_image(original, rotation)
        x0, y0, x1, y1 = get_square_coords(x, y, *select_coords[0])
        cv2.rectangle(image, (x0, y0), (x1, y1), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP: 
        # Left mouse button up: the selection has been made.
        select_coords.append((x, y))
        selecting = False


def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result


# Load the image and get its filename without path and dimensions.
in_directory = sys.argv[1]
out_directory = sys.argv[2]
for basename in os.listdir(in_directory):
    rotation = 0
    filename = os.path.join(in_directory, basename)
    if (os.path.splitext(basename)[1] == '.gif'):
        capture = cv2.VideoCapture(filename)
        original = capture.read()[1]
    else:
        original = cv2.imread(filename)
    h, w = original.shape[:2]
    select_coords = []
    # The cropped image will be saved with this filename.
    cropped_filename = os.path.join(out_directory, os.path.splitext(basename)[0] + '.jpg')
    # Store a clone of the original image (without selected region annotation).
    image = original.copy() 
    # Name the main image window after the image filename.
    cv2.namedWindow(basename) 
    cv2.setMouseCallback(basename, region_selection)

    # Keep looping and listening for user input until 'c' is pressed.
    while True: 
        # Display the image and wait for a keypress 
        cv2.imshow(basename, image) 
        key = cv2.waitKey(1) & 0xFF
        # If 'q' is pressed, quit the program
        if key == ord('q'):
            exit()
        # If 'd' is pressed, skip the current image
        if key == ord('d'):
            break
        # If 's' is pressed, rotate image 5deg counterclockwise 
        if key == ord('a'):
            rotation += 5
            image = rotate_image(original, rotation)
            select_coords = []
        # If 'f' is pressed, rotate image 5deg clockwise
        if key == ord('s'):
            rotation -= 5
            image = rotate_image(original, rotation)
            select_coords = []
        # If space is pressed and we have made a selection, save cropped image
        if key == 32 and len(select_coords) == 2:
            cx, cy = select_coords[0]
            x, y = select_coords[1]
            x0, y0, x1, y1 = get_square_coords(x, y, cx, cy)
            # Crop the image to the selected region and display in a new window.
            cropped_image = rotate_image(original, rotation)[y0:y1, x0:x1]
            cv2.imwrite(cropped_filename, cropped_image)
            break
    # Destroy all windows before advancing to next image
    cv2.destroyAllWindows()

