import cv2
import numpy as np
import mysql.connector
from datetime import datetime

def nothing(x):
    pass

# Function to get the color name based on HSV values
def get_color_name(hsv_value):
    h, s, v = hsv_value

    if s < 40 and v > 200:
        return "White"
    elif v < 50:
        return "Black"
    elif h >= 0 and h <= 10:
        return "Red"
    elif h > 10 and h <= 25:
        return "Orange"
    elif h > 25 and h <= 35:
        return "Yellow"
    elif h > 35 and h <= 85:
        return "Green"
    elif h > 85 and h <= 125:
        return "Cyan"
    elif h > 125 and h <= 160:
        return "Blue"
    elif h > 160 and h <= 170:
        return "Purple"
    elif h > 170 and h <= 179:
        return "Pink"
    else:
        return "Unknown"

# Function to insert the event into the MySQL database
def insert_event_into_db():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",  # Replace with your MySQL server address if it's remote
            user="your_username",  # Replace with your MySQL username
            password="your_password",  # Replace with your MySQL password
            database="water_quality"  # Replace with your database name
        )

        # Get the current date and time
        current_time = datetime.now()

        # SQL query to insert data into the table
        sql_insert_query = "INSERT INTO silver_ion_events (event_time) VALUES (%s)"
        cursor = connection.cursor()
        cursor.execute(sql_insert_query, (current_time,))
        connection.commit()

        print("Event inserted into the database successfully")

    except mysql.connector.Error as error:
        print(f"Failed to insert event into MySQL table: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Initialize the webcam (typically index 0)
cap = cv2.VideoCapture(0)

# Create a window for adjusting HSV ranges
cv2.namedWindow("Trackbars")

# Create trackbars for adjusting the lower and upper HSV range
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

while True:
    # Capture frame-by-frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Get frame dimensions
    height, width, _ = frame.shape

    # Define a centered rectangle (you can adjust size as needed)
    center_x, center_y = width // 2, height // 2
    rect_width, rect_height = width // 4, height // 4
    top_left_x = center_x - rect_width // 2
    top_left_y = center_y - rect_height // 2
    bottom_right_x = center_x + rect_width // 2
    bottom_right_y = center_y + rect_height // 2

    # Draw the rectangle on the frame (for visualization)
    cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), 2)

    # Crop the region of interest (ROI) inside the rectangle
    roi = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

    # Convert the cropped ROI to HSV color space
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Get the current positions of the trackbars for lower and upper HSV values
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    # Define the lower and upper HSV range for color detection
    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    # Create a mask for detecting colors within the HSV range
    mask = cv2.inRange(hsv_roi, lower_bound, upper_bound)

    # Perform a bitwise-AND on the cropped frame (ROI) and mask to isolate the detected color
    result = cv2.bitwise_and(roi, roi, mask=mask)

    # Calculate the average color in the rectangle (in BGR format)
    avg_color_bgr = cv2.mean(roi, mask=mask)[:3]  # ignore alpha channel

    # Convert BGR to HSV for getting color name
    avg_color_hsv = cv2.cvtColor(np.uint8([[avg_color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]

    # Get the color name
    color_name = get_color_name(avg_color_hsv)

    # Print the average color in HSV format and the color name
    print(f"Average color in HSV: {avg_color_hsv}, Color Name: {color_name}")

    # Check if the color is black and raise an alert
    if color_name == "Black":
        print("ALERT: Water intoxicated with Silver ion")
        insert_event_into_db()  # Insert the event into the database

        # Optionally, display the alert on the video feed
        cv2.putText(frame, "Water intoxicated with Silver ion", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the original frame with rectangle, mask, and result side by side
    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()