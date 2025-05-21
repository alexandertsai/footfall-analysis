import torch.serialization
from ultralytics import YOLO
import cv2
import numpy as np
import time
import datetime
import csv
import os
from PIL import ImageGrab

# Visitor tracking
visitor_ids = set()  # Will be reset every hour
daily_hourly_visitors = {}  # Format: {date_str: {hour: count}}
current_hour = datetime.datetime.now().hour
current_date = datetime.datetime.now().date()

def capture_screen():
    # Capture screen (adjust coordinates to your surveillance area)
    # Format should be (left, top, right, bottom)
    screen = np.array(ImageGrab.grab(bbox=(264, 342, 1051, 868)))
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    return screen

def is_new_visitor(track_id, cooldown_minutes=30):
    current_time = time.time()
    
    # Check if we've seen this ID recently
    if track_id in visitor_records:
        last_seen = visitor_records[track_id]
        if current_time - last_seen < (cooldown_minutes * 60):
            # Update time and return False (not new)
            visitor_records[track_id] = current_time
            return False
    
    # New visitor or one we haven't seen in a while
    visitor_records[track_id] = current_time
    return True

def update_csv_file():
    """Update the data.csv file with current visitor counts"""
    csv_file = "data.csv"
    
    # Define all hours for columns (9am to 10pm)
    hours = list(range(9, 22))
    
    # Get all dates we have data for
    all_dates = list(daily_hourly_visitors.keys())
    all_dates.sort()  # Sort dates chronologically
    
    # Create/update CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header row with hours
        header = ['Date'] + [f"{hour}:00" for hour in hours]
        writer.writerow(header)
        
        # Write each date's data
        for date_str in all_dates:
            row = [date_str]
            hourly_data = daily_hourly_visitors[date_str]
            
            # Add count for each hour (or 0 if no data)
            for hour in hours:
                count = hourly_data.get(hour, 0)
                row.append(count)
            
            writer.writerow(row)
    
    print(f"CSV file updated: {csv_file} - Hourly visitor counts saved")

# Load existing data if available
try:
    with open("data.csv", 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)  # Try to skip header
            
            for row in reader:
                if len(row) >= 2:  # Date plus at least one hour
                    date_str = row[0]
                    hourly_data = {}
                    
                    # Parse hours (starting from column 1)
                    for i, count in enumerate(row[1:]):
                        if i < 13:  # We have 13 hours (9-21)
                            hour = i + 9  # Hours start at 9
                            try:
                                hourly_data[hour] = int(count)
                            except ValueError:
                                hourly_data[hour] = 0
                    
                    daily_hourly_visitors[date_str] = hourly_data
            print("Loaded existing data from data.csv")
        except StopIteration:
            print("CSV file exists but is empty, will initialize with header")
except FileNotFoundError:
    print("No existing data.csv found, will create new file")

# Load the YOLO model
print("Loading YOLOv8 model...")
model = YOLO("yolov8n.pt")  # Load the small YOLO model
print("Model loaded successfully")

# Main processing loop
visitor_records = {}  # {track_id: last_seen_timestamp}

# Flag to track if we're currently in the operating hours
in_operating_hours = False
# Date when we last cleared the visitor IDs for a new operating day
last_operating_day = None
# Last time we displayed a status message
last_status_time = time.time()

try:
    while True:
        try:
            # Get current time
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            
            # Initialize data structure for today if needed
            if date_str not in daily_hourly_visitors:
                daily_hourly_visitors[date_str] = {}
            
            # Check if date has changed
            if now.date() != current_date:
                update_csv_file()
                current_date = now.date()
                print(f"Date changed to {date_str}")
            
            # Check if hour has changed
            if now.hour != current_hour:
                # If we were in operating hours, save the previous hour's count
                if in_operating_hours:
                    daily_hourly_visitors[date_str][current_hour] = len(visitor_ids)
                    update_csv_file()
                
                # Reset for new hour
                current_hour = now.hour
                
                # Reset visitor IDs at the start of each hour
                visitor_ids = set()
                visitor_records = {}  # Also reset the visitor records
                print(f"Reset visitor count for new hour: {current_hour}:00")
                
                # If we're starting a new operating day, update the tracking
                if current_hour == 9 and now.date() != last_operating_day:
                    last_operating_day = now.date()
                    print(f"Starting a new operating day: {date_str}")
            
            # Check if we're in operating hours (9am-10pm)
            currently_in_operating_hours = 9 <= now.hour < 22
            
            # Detect transitions in/out of operating hours
            if currently_in_operating_hours and not in_operating_hours:
                print(f"Entering operating hours at {now.hour}:00")
                # Reset visitor tracking when entering operating hours
                visitor_ids = set()
                visitor_records = {}
            elif not currently_in_operating_hours and in_operating_hours:
                print(f"Exiting operating hours at {now.hour}:00")
                # Save the final count for the last operating hour
                daily_hourly_visitors[date_str][current_hour] = len(visitor_ids)
                update_csv_file()
            
            # Update our operating hours flag
            in_operating_hours = currently_in_operating_hours
            
            # Only track visitors during operating hours
            if in_operating_hours:
                # Capture and process frame
                frame = capture_screen()
                results = model.track(frame, persist=True, classes=0)  # 0 = person
                
                # Process tracking results
                if results and results[0].boxes.id is not None:
                    for box, track_id in zip(results[0].boxes.xyxy, results[0].boxes.id):
                        track_id = int(track_id)
                        
                        # Check if this is a new visitor
                        if is_new_visitor(track_id):
                            visitor_ids.add(track_id)
                            print(f"New visitor detected! Current count: {len(visitor_ids)}")
                
                # Optional: visualize (can be disabled for background operation)
                annotated_frame = results[0].plot()
                cv2.imshow("Tracking", annotated_frame)
                
                # Save current hour's data periodically (every minute)
                if now.second == 0:
                    daily_hourly_visitors[date_str][current_hour] = len(visitor_ids)
                    update_csv_file()
            else:
                # Outside operating hours, just show a waiting screen
                # Print status message periodically (every 5 minutes)
                current_time = time.time()
                if current_time - last_status_time > 300:  # 300 seconds = 5 minutes
                    print(f"Waiting for operating hours... Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                    last_status_time = current_time
                
                # We still need a basic window to capture keyboard input
                blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank_frame, "Outside operating hours", (20, 240), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)
                cv2.putText(blank_frame, f"Time: {now.strftime('%H:%M:%S')}", (20, 280), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Tracking", blank_frame)
                
                # Sleep longer outside operating hours to reduce resource usage
                time.sleep(1)  # Check once per second instead of 20 times
            
            # Check for quit key (q) - but keep this just for debugging/manual stopping
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Manual stop requested - saving data before exit")
                if in_operating_hours:
                    daily_hourly_visitors[date_str][current_hour] = len(visitor_ids)
                update_csv_file()
                cv2.destroyAllWindows()
                # Don't break here - just let the program continue after closing windows
                
        except Exception as e:
            # Log any errors but don't stop the program
            print(f"Error occurred: {e}")
            print("Continuing to run...")
            time.sleep(5)  # Wait a bit before continuing

except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    print("\nKeyboard interrupt detected. Saving data before exit...")
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    if in_operating_hours:
        daily_hourly_visitors[date_str][current_hour] = len(visitor_ids)
    update_csv_file()
    cv2.destroyAllWindows()
    print("Final data saved. Program exited safely.")