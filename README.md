# dino-ium

Welcome to dino-ium! This project brings the classic dinosaur game (Chrome Dino) to life on a Raspberry Pi Pico with an SSD1306 OLED display. The game features a jumping dino that dodges obstacles like cacti and birds. Some versions are coded with help from Microsoft Copilot (e.g. the bitmaps).

## Features

- **Dynamic Gameplay**: The game gets progressively harder and faster as the dino encounters more obstacles.
- **Various Obstacles**: Includes small cacti, medium cacti, large cacti, and birds.
- **Adaptive Difficulty**: Birds appear as obstacles only after scoring 100 points.
- **Smooth Animations**: Utilises SSD1306 OLED display for smooth pixel graphics of about 100Hz (theoretically)
- **User Input**: Interactive controls with jump and duck buttons.

## Hardware Requirements

- Raspberry Pi Pico
- SSD1306 OLED display (128x64, I2C, monochrome)
- Push buttons (for jump and duck)
- Connecting wires

## Software Requirements

- MicroPython installed on Raspberry Pi Pico
- Required libraries: `machine`, `ssd1306`, `utime`, `random`

## Installation

1. **Prepare the Raspberry Pi Pico**:
   - Install MicroPython on the Raspberry Pi Pico.
   - Connect the SSD1306 OLED display to the I2C pins (SDA to GP16, SCL to GP17).
   - Connect push buttons to GPIO pins 0 and 11 for jump and duck; other ends connect to ground.

2. **Upload the Code**:
   - Copy the provided Python script to your Raspberry Pi Pico using an IDE like Thonny or VSCode; in development, I used ViperIDE (https://viper-ide.org/) on a ChromeBook, which worked quite well.

## How to Play

- **Jump**: Press the jump button to make the dino jump over obstacles.
- **Duck**: Press the duck button to make the dino duck under obstacles.
- **Score**: The score increases as you dodge more obstacles. Birds appear as obstacles once you score 100 points.
