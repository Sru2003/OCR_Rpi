import time
import picamera
import cv2
import pytesseract
from pytesseract import Output
import RPi.GPIO as GPIO
# Initialize the camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)  # Set your desired resolution

# Initialize Tesseract
# Path to Tesserac                                                                                                             t executable
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Initialize GPIO pins for motors
motor_pins = [6, 5, 23, 13, 19, 24]  # Replace with your motor's GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


# Function to capture and process the image
def capture_and_process_image():
    # Capture an image
    image_filename = 'captured_image.jpg'
    camera.capture(image_filename)

    # Load and preprocess the image using OpenCV
    image = cv2.imread(image_filename, cv2.IMREAD_GRAYSCALE)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    _, image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Perform OCR
    extracted_text = pytesseract.image_to_string(
        image, output_type=Output.STRING)

    return extracted_text


# Function to map alphabet letters and numbers to Braille patterns
def map_to_braille(character):
    braille_mapping = {
        'a': [1, 0, 0, 0, 0, 0],
        'b': [1, 1, 0, 0, 0, 0],
        'c': [1, 0, 0, 1, 0, 0],
        'd': [1, 0, 0, 1, 1, 0],
        'e': [1, 0, 0, 0, 1, 0],
        'f': [1, 1, 0, 1, 0, 0],
        'g': [1, 1, 0, 1, 1, 0],
        'h': [1, 1, 0, 0, 1, 0],
        'i': [0, 1, 0, 1, 0, 0],
        'j': [0, 1, 0, 1, 1, 0],
        'k': [1, 0, 1, 0, 0, 0],
        'l': [1, 1, 1, 0, 0, 0],
        'm': [1, 0, 1, 1, 0, 0],
        'n': [1, 0, 1, 1, 1, 0],
        'o': [1, 0, 1, 0, 1, 0],
        'p': [1, 1, 1, 1, 0, 0],
        'q': [1, 1, 1, 1, 1, 0],
        'r': [1, 1, 1, 0, 1, 0],
        's': [0, 1, 1, 1, 0, 0],
        't': [0, 1, 1, 1, 1, 0],
        'u': [1, 0, 1, 0, 0, 1],
        'v': [1, 1, 1, 0, 0, 1],
        'w': [0, 1, 0, 1, 1, 1],
        'x': [1, 0, 1, 1, 0, 1],
        'y': [1, 0, 1, 1, 1, 1],
        'z': [1, 0, 1, 0, 1, 1],
        '1': [0, 1, 0, 0, 0, 0],
        '2': [0, 1, 0, 0, 1, 0],
        '3': [0, 1, 0, 1, 0, 0],
        '4': [0, 1, 0, 1, 1, 0],
        '5': [0, 1, 0, 0, 0, 1],
        '6': [0, 1, 0, 1, 0, 1],
        '7': [0, 1, 0, 1, 1, 1],
        '8': [0, 1, 0, 0, 1, 1],
        '9': [0, 0, 1, 0, 0, 0],
        '0': [0, 0, 1, 0, 0, 1]
    }

    return braille_mapping.get(character, None)


# Main loop
try:
    while True:
        # Wait for the 's' key to be pressed or 'e' to exit
        input_key = input("Press 's' to capture a photo, 'e' to exit: ")

        if input_key == 's':
            extracted_text = capture_and_process_image()

            # Convert extracted text to lowercase for matching
            extracted_text = extracted_text.lower()

            # Check if any alphabet letters or numbers are detected
            detected_characters = [
                char for char in extracted_text if char.isalpha() or char.isdigit()]

            # Activate motors based on Braille patterns
            for char in detected_characters:
                braille_pattern = map_to_braille(char)
                if braille_pattern:
                    print(f"Detected character: {char}")
                    print(f"Braille pattern: {braille_pattern}")
                    print("Activating motors in 3 seconds...")
                    print(f"Activating motors: {braille_pattern}")
                    for pin, action in zip(motor_pins, braille_pattern):
                        GPIO.output(pin, action)

                    # Wait for 4 seconds while motors are on
                    time.sleep(1)
                    # Turn off all motors
                    for pin in motor_pins:
                        GPIO.output(pin, GPIO.LOW)

                    # Wait for 2 seconds with all motors off
                    time.sleep(2.5)

            # Wait for a few seconds before resetting LEDs
            time.sleep(3)
        elif input_key == 'e':
            break  # Exit the program if 'e' is pressed
except KeyboardInterrupt:
    pass
finally:
    camera.close()
    GPIO.cleanup()
