from tkinter import *
from datetime import datetime

def ViewHours(data):
    root = Tk()
    root.title("Tuntinäkymä")

    canvas = Canvas(root, width=800, height=400)
    canvas.pack()

    # Function to draw a bar
    def draw_bar(x, y, width, height, color):
        canvas.create_rectangle(x, y, x + width, y + height, fill=color)

    # Function to convert datetime string to hour
    def get_hour(date_str):
        dt_obj = datetime.fromisoformat(date_str[:-1])  # Convert ISO format to datetime object
        return dt_obj.strftime('%H')

    # Function to convert boolean to "On" or "Off"
    def convert_bool(value):
        return "On" if value else "Off"

    # Colors for bars based on price
    def get_color(price):
        if price < 5:
            return "green"
        elif price < 7:
            return "orange"
        else:
            return "red"

    # Get current hour
    current_hour = datetime.now().strftime('%H')

    # Draw bars
    bar_width = 20
    for i in range(24):
        found = False
        for entry in data:
            hour = int(get_hour(entry[0]))
            price = entry[1]
            status = convert_bool(entry[2])

            if hour == i:
                x = 50 + i * (bar_width + 10)
                y = 350
                bar_height = -price * 20  # Scale the height

                draw_bar(x, y, bar_width, bar_height, get_color(price))
                canvas.create_text(x + bar_width // 2, y + 10, text=hour, anchor=N)
                canvas.create_text(x + bar_width // 2, y + bar_height - 10, text=f"{price:.2f}", anchor=S)
                canvas.create_text(x + bar_width // 2, y + 30, text=status, anchor=N)
                if str(hour) == current_hour:
                    canvas.create_line(x + bar_width // 2, y, x + bar_width // 2, y + bar_height, fill="blue", width=2)
                found = True
                break
        
        if not found:
            x = 50 + i * (bar_width + 10)
            y = 350
            draw_bar(x, y, bar_width, 0, "gray")
            canvas.create_text(x + bar_width // 2, y + 10, text=i, anchor=N)

    root.mainloop()
if __name__ == "__main__":
    # Test the function 
    your_data = [['2024-02-18T01:00:00.000Z', 10, False], ['2024-02-18T02:00:00.000Z', 6, False], ['2024-02-18T03:00:00.000Z', 7, False], ['2024-02-18T04:00:00.000Z', 9, False], ['2024-02-18T05:00:00.000Z', 4.139, True], ['2024-02-18T06:00:00.000Z', 4.333, True], ['2024-02-18T07:00:00.000Z', 4.711, True], ['2024-02-18T08:00:00.000Z', 4.912, True], ['2024-02-18T14:00:00.000Z', 4.945, True], ['2024-02-18T13:00:00.000Z', 4.972, True], ['2024-02-18T21:00:00.000Z', 5.005, True], ['2024-02-18T11:00:00.000Z', 5.016, True], ['2024-02-18T12:00:00.000Z', 5.084, True], ['2024-02-18T09:00:00.000Z', 5.177, True], ['2024-02-19T02:00:00.000Z', 5.265, True], ['2024-02-18T15:00:00.000Z', 5.316, True], ['2024-02-19T01:00:00.000Z', 5.325, True], ['2024-02-18T10:00:00.000Z', 5.336, True], ['2024-02-18T22:00:00.000Z', 5.349, True], ['2024-02-18T20:00:00.000Z', 5.349, True], ['2024-02-19T00:00:00.000Z', 5.418, True], ['2024-02-19T04:00:00.000Z', 5.445, True], ['2024-02-19T03:00:00.000Z', 5.482, True], ['2024-02-18T23:00:00.000Z', 5.547, True], ['2024-02-19T05:00:00.000Z', 5.57, True], ['2024-02-18T19:00:00.000Z', 5.71, True], ['2024-02-18T17:00:00.000Z', 5.719, True], ['2024-02-18T16:00:00.000Z', 5.786, True], ['2024-02-18T18:00:00.000Z', 5.799, True], ['2024-02-19T06:00:00.000Z', 6.395, True], ['2024-02-20T00:00:00.000Z', 6.535, False], ['2024-02-19T23:00:00.000Z', 6.63, False], ['2024-02-19T22:00:00.000Z', 6.963, True], ['2024-02-19T21:00:00.000Z', 7.534, True], ['2024-02-19T15:00:00.000Z', 7.983, True], ['2024-02-19T07:00:00.000Z', 8.059, True], ['2024-02-19T16:00:00.000Z', 8.258, True], ['2024-02-19T14:00:00.000Z', 8.479, True], ['2024-02-19T17:00:00.000Z', 8.654, True], ['2024-02-19T13:00:00.000Z', 9.02, True], ['2024-02-19T18:00:00.000Z', 9.295, True], ['2024-02-19T10:00:00.000Z', 9.304, True], ['2024-02-19T20:00:00.000Z', 9.63, True], ['2024-02-19T11:00:00.000Z', 9.769, True], ['2024-02-19T08:00:00.000Z', 9.807, True], ['2024-02-19T12:00:00.000Z', 9.986, True], ['2024-02-19T09:00:00.000Z', 10.396, True], ['2024-02-19T19:00:00.000Z', 11.756, True]]
    ViewHours(your_data)
