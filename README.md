# Water Quality Detection System with Color Sensor and AWS Integration

## Overview

This project uses an ESP32 microcontroller to detect specific water quality indicators using a color detection sensor. The system reads RGB values, matches them with predefined colors, displays the results on an LCD screen, and sends the data to AWS for online storage and monitoring.

## Components Used

- **ESP32 Microcontroller**: For processing and Wi-Fi connectivity.
- **Adafruit TCS34725 Color Sensor**: To measure the RGB values of the water.
- **LCD Screen (I2C Interface)**: To display the color and alert level.
- **AWS**: For online data storage and monitoring.

## Code Functionality

### Key Libraries Used

- **Adafruit TCS34725**: To interface with the color sensor.
- **Wire**: For I2C communication.
- **LiquidCrystal_I2C**: For interfacing with the LCD.

### Main Code Structure

1. **Initialization**: 
   - The code initializes the color sensor, sets up I2C communication, and prepares the LCD display.

2. **RGB Color Levels**:
   - Predefined RGB color levels are defined to categorize the detected color.
   - Each color has an associated name and alert level.

3. **Color Detection Logic**:
   - The `calculate_color_distance` function computes the Euclidean distance between two RGB colors.
   - The `get_color_level` function determines the closest predefined color level based on the average RGB values detected.

4. **Main Loop**:
   - Continuously reads RGB values from the TCS34725 sensor.
   - Displays the detected RGB values and the corresponding color name and alert level on the LCD.
   - If the detected color is within the threshold of predefined colors, it sends the alert level to AWS for storage.

5. **AWS Integration**:
   - Uses HTTP requests to send data to an AWS endpoint (API Gateway or Lambda).
   - Stores the detected alert level and timestamp for online monitoring.

## Requirements

- **Hardware**: ESP32, TCS34725 Color Sensor, LCD Display (I2C)
- **Software**: Arduino IDE with necessary libraries installed
- **AWS Setup**: Create an API endpoint to receive data

## Conclusion

This project serves as a foundation for developing smart water quality monitoring systems. By leveraging color detection and online storage, it provides real-time insights into water quality parameters.

## Future Enhancements

- Add more color levels for improved detection accuracy.
- Implement data visualization on a web dashboard.
- Integrate alerts for critical water quality issues.
