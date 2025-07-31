
import pandas as pd
import numpy as np

def process_iaq_query(df):
    """
    Calculates the average temperature of each room in mornings and evenings.

    Args:
        df (pd.DataFrame): DataFrame with IAQ data, including 'Timestamp', 'Temperature', and 'Room' columns.

    Returns:
        dict: A JSON-compatible dictionary containing the average temperature for each room in the morning and evening.
    """

    # Convert Timestamp to datetime objects
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Define morning and evening time ranges
    morning_start = 6
    morning_end = 12
    evening_start = 18
    evening_end = 24

    # Create morning and evening columns
    df['Morning'] = ((df['Timestamp'].dt.hour >= morning_start) & (df['Timestamp'].dt.hour < morning_end))
    df['Evening'] = ((df['Timestamp'].dt.hour >= evening_start) & (df['Timestamp'].dt.hour < evening_end))

    # Calculate average temperature for each room in the morning
    morning_temps = df[df['Morning']].groupby('Room')['Temperature'].mean().reset_index()
    morning_temps = morning_temps.rename(columns={'Temperature': 'Avg_Morning_Temp'})

    # Calculate average temperature for each room in the evening
    evening_temps = df[df['Evening']].groupby('Room')['Temperature'].mean().reset_index()
    evening_temps = evening_temps.rename(columns={'Temperature': 'Avg_Evening_Temp'})

    # Merge the results
    merged_temps = pd.merge(morning_temps, evening_temps, on='Room', how='outer')

    # Handle cases where there is no morning or evening data for a room
    merged_temps['Avg_Morning_Temp'] = merged_temps['Avg_Morning_Temp'].fillna(np.nan)
    merged_temps['Avg_Evening_Temp'] = merged_temps['Avg_Evening_Temp'].fillna(np.nan)

    # Convert to a list of lists for the table
    data = merged_temps.values.tolist()
    headers = ['Room', 'Avg_Morning_Temp', 'Avg_Evening_Temp']

    return {"type": "table", "data": {"headers": headers, "rows": data}}