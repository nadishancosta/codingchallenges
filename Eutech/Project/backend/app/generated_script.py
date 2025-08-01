
import pandas as pd

def process_iaq_query(df):
    """
    Analyzes CO2 variation by day of the week for each room in the IAQ data.

    Args:
        df (pandas DataFrame): DataFrame with columns 'Timestamp', 'CO2', 'Room'.

    Returns:
        dict: JSON-compatible dictionary containing CO2 statistics by day of the week for each room.
    """

    try:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['DayOfWeek'] = df['Timestamp'].dt.day_name()

        result = {}
        for room in df['Room'].unique():
            room_data = df[df['Room'] == room]
            co2_by_day = room_data.groupby('DayOfWeek')['CO2'].agg(['mean', 'median', 'std']).to_dict('index')
            result[room] = co2_by_day

        # Flatten the structure for table representation
        headers = ['Room', 'DayOfWeek', 'Mean CO2', 'Median CO2', 'Std CO2']
        rows = []
        for room, day_data in result.items():
            for day, co2_stats in day_data.items():
                rows.append([room, day, co2_stats['mean'], co2_stats['median'], co2_stats['std']])

        return {"type": "table", "data": {"headers": headers, "rows": rows}}

    except Exception as e:
        return {"type": "text", "data": f"Error processing query: {str(e)}"}