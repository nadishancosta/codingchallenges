
def process_iaq_query(df):
    """
    Calculates the average CO2 level in Room 1.

    Args:
        df (pandas DataFrame): DataFrame containing IAQ data with columns:
                                ['Timestamp', 'CO2', 'Relative Humidity', 'Temperature', 'Room']

    Returns:
        dict: A JSON-compatible dictionary containing the result.
    """

    room = "Room 1"
    df_room1 = df[df['Room'] == room]
    average_co2 = df_room1['CO2'].mean()

    return {"type": "text", "data": f"The average CO2 level in {room} was {average_co2:.2f} ppm."}