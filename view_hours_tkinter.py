from tkinter import *
from datetime import datetime, timedelta, timezone

def ViewHours(data):
    root = Tk()
    root.title("Tuntinäkymä")
    root.geometry("640x480")

    canvas = Canvas(root, width=700, height=410)
    canvas.grid(row=0, column=0, padx=10, pady=1)

    def draw_bar(x, y, width, height, color):
        canvas.create_rectangle(x, y, x + width, y + height, fill=color, width=0)

    def draw_marker(x, y, width=7, height=10, color="black"):
        # pieni kolmio alapuolelle
        canvas.create_polygon(
            x, y,
            x - width // 2, y + height,
            x + width // 2, y + height,
            fill=color
        )

    max_price = max(entry[1] for entry in data) if data else 1
    bar_width = 6      # mahtuu 92 palkkia
    spacing = 0        # pieni rako
    y_base = 350
    chart_left = 45    # palkkien alku x
    scale_left = 25    # hintaskaalan x-koordinaatti
    current_time = datetime.now()

    # Piirrä hintaskaalat vasemmalle (0%, 25%, 50%, 75%, 100%)
    num_levels = 5
    for i in range(num_levels):
        level_price = max_price * i / (num_levels - 1)
        y = y_base - (level_price / max_price * 300)
        canvas.create_line(scale_left, y, scale_left + 5, y, fill="black")  # lyhyt viiva
        canvas.create_text(scale_left - 2, y, text=f"{level_price:.1f}", anchor=E, font=("Arial", 8))

    # Lisää y-akselin teksti
    canvas.create_text(scale_left + 10, y_base - 310, text="snt/kWh", anchor=S, font=("Arial", 10, "bold"))

    # Piirrä palkit
    for i, entry in enumerate(data):
        starttime_str, price, heating_on = entry
        starttime = datetime.fromisoformat(starttime_str.replace("Z", ""))
        endtime = starttime + timedelta(minutes=15)  # oletetaan 15 min per palkki

        x = chart_left + i * (bar_width + spacing)
        bar_height = -price / max_price * 300  # suhteellinen korkeus

        # väri lämmityksen mukaan
        color = "green" if heating_on else "gray"

        draw_bar(x, y_base, bar_width, bar_height, color)

        # merkki nykyiselle ajalle
        if starttime <= current_time < endtime:
            draw_marker(x + bar_width / 2, y_base + 5)

    # Lisää kellonajat alapuolelle
    canvas.create_text(chart_left+20, y_base + 30, text="klo 0.0", anchor=N, font=("Arial", 8, "bold"))
    canvas.create_text(chart_left + len(data) * (bar_width + spacing) -20, y_base + 20, text="klo 24.0", anchor=N, font=("Arial", 8, "bold"))

    # Sulje-nappi
    close_button = Button(root, text="Sulje ikkuna", command=root.destroy, font=("Arial", 20))
    close_button.grid(row=1, column=0, pady=(0, 0))

    root.after(10000, root.destroy)
    root.mainloop()


if __name__ == "__main__":
    # Testidata: 92 varttia (15 min välein)
    start = datetime(2024, 2, 18, 0, 0, tzinfo=timezone.utc)
    test_data = []
    for i in range(92):
        t = start + timedelta(minutes=15*i)
        price = 4 + (i % 12) * 0.5
        heating_on = (i % 3 != 0)
        test_data.append([t.isoformat().replace("+00:00", "Z"), price, heating_on])

    ViewHours(test_data)
