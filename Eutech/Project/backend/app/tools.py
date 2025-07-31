import os
import io
import json
import pandas as pd
from contextlib import redirect_stdout
from thefuzz import process, fuzz

# Define the path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def _load_and_prepare_data() -> pd.DataFrame:

    """Retrieves the the JSON dataset in the data folder.

    Args:
        None

    Returns:
        pd.DataFrame: A dataframe containing the room sensor data for all the rooms.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'df' key with the dataframe object.
              If 'error', includes an 'error_message' key.
    """

    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return None
        
    standardized_data = []
    # These are the standard names we will use for the DataFrame columns.
    standard_columns = ['Timestamp', 'CO2', 'Relative Humidity', 'Temperature']

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.ndjson'):
            # Create a clean room name, e.g., 'sensor_data_room 1.txt' -> 'Room 1'
            room_name = filename.split('.')[0].replace('_', '')[-6:].title()
            file_path = os.path.join(DATA_DIR, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        # Skip empty or whitespace-only lines
                        if not line.strip():
                            continue
                        
                        try:
                            # Load the JSON object from the line
                            data_dict = json.loads(line)
                            
                            # Get values in their insertion order (works in Python 3.7+)
                            values = list(data_dict.values())
                            
                            # Validate that we have the expected number of fields
                            if len(values) != 4:
                                print(f"Warning: Skipping malformed line {i+1} in {filename} (expected 4 fields, got {len(values)}).")
                                continue

                            # Create a standardized dictionary by zipping keys and values
                            record = dict(zip(standard_columns, values))
                            record['Room'] = room_name  # Add the room name
                            standardized_data.append(record)
                            
                        except (json.JSONDecodeError, IndexError) as e:
                            print(f"Warning: Skipping corrupted line {i+1} in {filename}. Error: {e}")
                            continue

            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                continue
                
    if not standardized_data:
        print("Error: No data could be loaded. Check file contents and paths.")
        return None

    # Create the DataFrame from our list of standardized records
    df = pd.DataFrame(standardized_data)
    
    # Convert relevant columns to the correct data types, coercing errors
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    for col in ['CO2', 'Relative Humidity', 'Temperature']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop any rows where critical data conversion failed
    df.dropna(subset=['Timestamp', 'CO2', 'Relative Humidity', 'Temperature'], inplace=True)

    return df

