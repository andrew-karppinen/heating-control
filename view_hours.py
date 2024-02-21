import PySimpleGUI as pg
from datetime import datetime

def ViewHours(data):
    pg.theme('LightGrey1')  # Set the theme
    
    # Parse timestamp strings into datetime objects
    for item in data:
        item[0] = datetime.fromisoformat(item[0][:-1])
    
    # Sort data based on timestamp
    data.sort(key=lambda x: x[0])
    
    layout = []
    row = []
    row_count = 0
    
    current_datetime = datetime.now()
    current_hour = current_datetime.hour
    current_date = current_datetime.date()
    
    for item in data:
        timestamp = item[0]
        price = item[1]
        boolean_value = item[2]
        boolean_indicator = "True" if boolean_value else "False"
        
        # Determine the background color of the row
        timestamp_hour = timestamp.hour
        timestamp_date = timestamp.date()
        
        background_color = 'lightgreen' if timestamp_hour == current_hour and timestamp_date == current_date else 'lightgrey'
        
        row.append(pg.Text(f"Time: {timestamp}, Price: {price}, Heating on: {boolean_indicator}", background_color=background_color))
        
        row_count += 1
        
        # Split rows into multiple columns if they are too wide
        if row_count == 5:
            layout.append(row)
            row = []
            row_count = 0
    
    # Add any remaining rows
    if row:
        layout.append(row)

    layout.append([pg.Button("Close",key="close")]) #add close button

    window = pg.Window('Data Display Window', layout, resizable=True, finalize=True)
    
    while True:
        event, values = window.read()
        if event == pg.WINDOW_CLOSED:
            break

        elif event == "close":
            break

    window.close()


if __name__ == "__main__":

    # Test the function 
    your_data = [['2024-02-18T01:00:00.000Z', 1.691, True], ['2024-02-18T02:00:00.000Z', 1.7, True], ['2024-02-18T03:00:00.000Z', 3.086, True], ['2024-02-18T04:00:00.000Z', 3.524, True], ['2024-02-18T05:00:00.000Z', 4.139, True], ['2024-02-18T06:00:00.000Z', 4.333, True], ['2024-02-18T07:00:00.000Z', 4.711, True], ['2024-02-18T08:00:00.000Z', 4.912, True], ['2024-02-18T14:00:00.000Z', 4.945, True], ['2024-02-18T13:00:00.000Z', 4.972, True], ['2024-02-18T21:00:00.000Z', 5.005, True], ['2024-02-18T11:00:00.000Z', 5.016, True], ['2024-02-18T12:00:00.000Z', 5.084, True], ['2024-02-18T09:00:00.000Z', 5.177, True], ['2024-02-19T02:00:00.000Z', 5.265, True], ['2024-02-18T15:00:00.000Z', 5.316, True], ['2024-02-19T01:00:00.000Z', 5.325, True], ['2024-02-18T10:00:00.000Z', 5.336, True], ['2024-02-18T22:00:00.000Z', 5.349, True], ['2024-02-18T20:00:00.000Z', 5.349, True], ['2024-02-19T00:00:00.000Z', 5.418, True], ['2024-02-19T04:00:00.000Z', 5.445, True], ['2024-02-19T03:00:00.000Z', 5.482, True], ['2024-02-18T23:00:00.000Z', 5.547, True], ['2024-02-19T05:00:00.000Z', 5.57, True], ['2024-02-18T19:00:00.000Z', 5.71, True], ['2024-02-18T17:00:00.000Z', 5.719, True], ['2024-02-18T16:00:00.000Z', 5.786, True], ['2024-02-18T18:00:00.000Z', 5.799, True], ['2024-02-19T06:00:00.000Z', 6.395, True], ['2024-02-20T00:00:00.000Z', 6.535, True], ['2024-02-19T23:00:00.000Z', 6.63, True], ['2024-02-19T22:00:00.000Z', 6.963, True], ['2024-02-19T21:00:00.000Z', 7.534, True], ['2024-02-19T15:00:00.000Z', 7.983, True], ['2024-02-19T07:00:00.000Z', 8.059, True], ['2024-02-19T16:00:00.000Z', 8.258, True], ['2024-02-19T14:00:00.000Z', 8.479, True], ['2024-02-19T17:00:00.000Z', 8.654, True], ['2024-02-19T13:00:00.000Z', 9.02, True], ['2024-02-19T18:00:00.000Z', 9.295, True], ['2024-02-19T10:00:00.000Z', 9.304, True], ['2024-02-19T20:00:00.000Z', 9.63, True], ['2024-02-19T11:00:00.000Z', 9.769, True], ['2024-02-19T08:00:00.000Z', 9.807, True], ['2024-02-19T12:00:00.000Z', 9.986, True], ['2024-02-19T09:00:00.000Z', 10.396, True], ['2024-02-19T19:00:00.000Z', 11.756, True]]
    ViewHours(your_data)
