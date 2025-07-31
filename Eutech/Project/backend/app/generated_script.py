
import pandas as pd
import numpy as np

def process_iaq_query(df):
    """
    Calculates the average temperature of each room in the mornings and evenings.

    Args:
        df (pd.DataFrame): DataFrame containing IAQ data with columns:
                           ['Timestamp', 'CO2', 'Relative Humidity', 'Temperature', 'Room'].

    Returns:
        dict: A JSON-compatible dictionary containing the average temperature for each room in the mornings and evenings.
              The dictionary is in the "table" format.
    """

    def categorize_time(timestamp):
        hour = timestamp.hour
        if 6 <= hour < 12:
            return 'Morning'
        elif 18 <= hour < 24:
            return 'Evening'
        else:
            return None

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Time Category'] = df['Timestamp'].apply(categorize_time)

    df_filtered = df[df['Time Category'].isin(['Morning', 'Evening'])]

    if df_filtered.empty:
        return {"type": "text", "data": "No data available for mornings and evenings."}
    
    avg_temp = df_filtered.groupby(['Room', 'Time Category'])['Temperature'].mean().reset_index()

    if avg_temp.empty:
        return {"type": "text", "data": "No data available."}

    headers = ['Room', 'Time Category', 'Average Temperature']
    rows = avg_temp.values.tolist()

    return {"type": "table", "data": {"headers": headers, "rows": rows}}