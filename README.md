# Footfall Analysis System

Uses the Yolo model for the live-tracking of the number of unique visitors per hour into a CSV file for analysis. Only operates during visitor hours (you can specify).

## Requirements

- Python 3.11.8 (see below on Installation)
- Webcam or screen area to monitor

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/alexandertsai/footfall-analysis.git
cd footfall-analysis
```

Note this project can only be done in Python 3.11, please use the correct Python version.

```bash
pyenv install 3.11.8
pyenv local 3.11.8
```

### 2. Set Up a Virtual Environment

Virtual environments keep your project dependencies isolated. This is important! Follow these steps to create and activate one:

```bash
# Open Command Prompt or PowerShell
# Navigate to your project directory

# Create a virtual environment
python -m venv venv

# Activate the virtual environment for windows
venv\Scripts\activate

# Activate the virtual environment for mac
source venv/bin/activate
```

You'll know the virtual environment is active when you see `(venv)` at the beginning of your command prompt.

### 3. Install Required Packages

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install all necessary dependencies including YOLOv8, OpenCV, and other required libraries.

## Usage

To start the footfall analysis system:

```bash
# Run the screen capture to help the script determine where you survellience footage is on your screen
# Simply run the script and then drag it over the area of your screen you want to capture
python screen.py
```

Based off the screen dimensions outputted, modify the screen dimensions in line 21 in `main.py`.

```bash
# Run the application
python main.py
```

The system will:
- Run continuously without needing to be restarted
- Track visitors during operating hours (9am-10pm)
- Enter low-resource standby mode outside operating hours
- Generate a `data.csv` file with hourly visitor counts 

### Stopping the System

To stop the system safely, press `Ctrl+C` in the command prompt. The system will save all current data before exiting.

## Customization

You can modify the following in `main.py`:

- **Operating Hours**: Change the `9 <= now.hour < 22` condition to adjust operating hours
- **Screen Capture Area**: Modify the `ImageGrab.grab(bbox=(0, 0, 1920, 1080))` parameters to change the monitored area
- **Visitor Cooldown**: Adjust the `cooldown_minutes=30` parameter to change how long before the same person is counted as a new visitor

## Troubleshooting

### Common Issues

1. **Installation Errors**:

Make sure you have the latest pip: `python -m pip install --upgrade pip`

2. **"No module named 'distutils'"**:

This occurs with Python 3.12. Use Python 3.11 instead as stated above

## Data Format

The `data.csv` file follows this format:

- First column: Date (YYYY-MM-DD)
- Subsequent columns: Hourly visitor counts from 9:00 to 21:00
- Example:
  ```
  Date,9:00,10:00,11:00,12:00,13:00,14:00,15:00,16:00,17:00,18:00,19:00,20:00,21:00
  2025-05-20,15,24,38,42,46,38,29,32,36,42,28,17,8
  2025-05-21,12,22,36,45,48,40,33,35,39,45,30,20,10
  ```

## Acknowledgements

This project uses:
- [YOLOv8](https://github.com/ultralytics/ultralytics) for object detection
- [OpenCV](https://opencv.org/) for image processing
- [Pillow](https://python-pillow.org/) for screen capture
