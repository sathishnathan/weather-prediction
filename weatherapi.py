from tkinter import *
import tkinter as tk
from tkinter import ttk
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import speech_recognition as sr
from tkinter import font as tkfont
import matplotlib.animation as animation
import random

# Function to animate button hover effect with more vibrant effects
def on_enter(e):
    if hasattr(e.widget, 'hover_color'):
        e.widget.configure(bg=e.widget.hover_color, fg='white')
        e.widget.config(relief=RAISED, bd=3)
        current_font = e.widget.cget("font")
        font_size = int(current_font.split()[1])
        e.widget.config(font=(current_font.split()[0], font_size + 1, "bold"))

def on_leave(e):
    if hasattr(e.widget, 'normal_color'):
        e.widget.configure(bg=e.widget.normal_color, fg='white')
        e.widget.config(relief=FLAT, bd=0)
        current_font = e.widget.cget("font")
        font_size = int(current_font.split()[1])
        e.widget.config(font=(current_font.split()[0], font_size - 1, "bold"))

def button_press(e):
    if hasattr(e.widget, 'press_color'):
        e.widget.configure(bg=e.widget.press_color)
        e.widget.config(relief=SUNKEN)

def button_release(e):
    if hasattr(e.widget, 'hover_color'):
        e.widget.configure(bg=e.widget.hover_color)
        e.widget.config(relief=RAISED)

# Animated splash screen with particles
def splash_screen():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("600x400+500+200")
    splash.configure(bg='#0A0A2A')
    
    canvas = Canvas(splash, width=600, height=400, bg='#0A0A2A', highlightthickness=0)
    canvas.pack()
    
    for i in range(40, 0, -1):
        canvas.create_text(300, 150, text="Weather App", 
                         font=("Helvetica", 40, "bold"), 
                         fill=f"#{i:02x}{i:02x}FF")
    
    particles = []
    for _ in range(50):
        x = random.randint(0, 600)
        y = random.randint(0, 400)
        size = random.randint(2, 5)
        speed = random.uniform(0.5, 2)
        color = random.choice(['#FF69B4', '#9370DB', '#FF8C00', '#00BFFF', '#FFD700'])
        particle = canvas.create_oval(x, y, x+size, y+size, fill=color, outline=color)
        particles.append({'id': particle, 'x': x, 'y': y, 'speed': speed, 'size': size})
    
    progress = ttk.Progressbar(splash, orient=HORIZONTAL, length=500, mode='determinate')
    progress.place(x=50, y=300)
    
    def animate_particles():
        try:
            for p in particles:
                canvas.move(p['id'], 0, p['speed'])
                p['y'] += p['speed']
                if p['y'] > 400:
                    canvas.coords(p['id'], p['x'], -10, p['x']+p['size'], -10+p['size'])
                    p['y'] = -10
            splash.after(30, animate_particles)
        except:
            pass
    
    def load():
        for i in range(101):
            time.sleep(0.02)
            progress['value'] = i
            splash.update_idletasks()
        splash.destroy()
        main()
    
    splash.after(100, animate_particles)
    splash.after(100, load)
    splash.mainloop()

# Function to recognize speech
def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for city name...")
        try:
            audio = recognizer.listen(source, timeout=5)
            city = recognizer.recognize_google(audio)
            print(f"City detected: {city}")
            weather_window = tk.Toplevel()
            weather_window.geometry("600x500")
            weather_window.configure(bg='#FFF0F5')
            weather_window.title("Current Weather")
            get_weather_voice(weather_window, city)
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand. Please repeat.")
        except sr.RequestError:
            print("Sorry, the speech service is down.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Weather API Function
def get_weather_voice(weather_window, city=None):
    try:
        api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=f3d2e73f53a5877a8ea389a6d9d6321a"
        json_data = requests.get(api).json()

        if json_data.get('cod') != 200:
            raise ValueError(json_data.get('message', 'Unknown error'))

        condition = json_data['weather'][0]['main']
        temp = int(json_data['main']['temp'] - 273.15)
        min_temp = int(json_data['main']['temp_min'] - 273.15)
        max_temp = int(json_data['main']['temp_max'] - 273.15)
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']
        sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise'] - 21600))
        sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset'] - 21600))

        final_info = f"{condition}\n{temp}°C"
        final_data = (
            f"\nMin Temp: {min_temp}°C\nMax Temp: {max_temp}°C\n"
            f"Pressure: {pressure}\nHumidity: {humidity}\n"
            f"Wind Speed: {wind}\nSunrise: {sunrise}\nSunset: {sunset}"
        )

        f = ("Helvetica", 35, "bold")
        t = ("Helvetica", 15, "bold")

        label1 = tk.Label(weather_window, font=t)
        label1.pack()
        label2 = tk.Label(weather_window, font=f)
        label2.pack()

        label1.config(text=final_info, foreground="#FF1493", bg="#FFF0F5")
        label2.config(text=final_data, foreground="#4B0082", bg="#FFF0F5")

    except Exception as e:
        print(f"Error: {str(e)}")

def predict_rainfall():
    df = pd.read_csv('weatherAUS.csv')
    df['RainTomorrow'].replace({'No': 0, 'Yes': 1}, inplace=True)

    fig = plt.figure(figsize=(8, 5))
    df.RainTomorrow.value_counts(normalize=True).plot(
        kind='bar', color=['#FF69B4', '#BA55D3'], alpha=0.9, rot=0)
    plt.title('RainTomorrow Indicator No(0) and Yes(1)')
    plt.show()

def weather():
    def get_weather(event=None, city=None):
        try:
            city = textField.get()
            api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=f3d2e73f53a5877a8ea389a6d9d6321a"
            json_data = requests.get(api).json()

            if json_data.get('cod') != 200:
                raise ValueError(json_data.get('message', 'Unknown error'))

            condition = json_data['weather'][0]['main']
            temp = int(json_data['main']['temp'] - 273.15)
            min_temp = int(json_data['main']['temp_min'] - 273.15)
            max_temp = int(json_data['main']['temp_max'] - 273.15)
            pressure = json_data['main']['pressure']
            humidity = json_data['main']['humidity']
            wind = json_data['wind']['speed']
            sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise'] - 21600))
            sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset'] - 21600))

            final_info = f"{condition}\n{temp}°C"
            final_data = (
                f"\nMin Temp: {min_temp}°C\nMax Temp: {max_temp}°C\n"
                f"Pressure: {pressure}\nHumidity: {humidity}\n"
                f"Wind Speed: {wind}\nSunrise: {sunrise}\nSunset: {sunset}"
            )

            label1.config(text=final_info, foreground="#FF1493", bg="#FFF0F5")
            label2.config(text=final_data, foreground="#4B0082", bg="#FFF0F5")

        except Exception as e:
            label1.config(text=f"Error: {str(e)}", foreground="red")

    weather_window = tk.Toplevel()
    weather_window.geometry("600x500")
    weather_window.configure(bg='#FFF0F5')
    weather_window.title("Current Weather")

    f = ("Helvetica", 15, "bold")
    t = ("Helvetica", 35, "bold")

    label3 = tk.Label(weather_window, borderwidth=4, font=f)
    label3.pack()
    label3.config(text="\nEnter your city:\n", foreground="#800080", bg="#FFF0F5")

    textField = tk.Entry(weather_window, justify='center', width=20, font=t, foreground="#8A2BE2")
    textField.configure(bg="#FFDAB9", insertbackground='#8A2BE2')
    textField.pack(pady=20)
    textField.focus()
    textField.bind('<Return>', get_weather)

    label1 = tk.Label(weather_window, font=t)
    label1.pack()
    label2 = tk.Label(weather_window, font=f)
    label2.pack()

def analyze():
    data = pd.read_csv("Weather Data in India from 1901 to 2025.csv")
    ax = data[['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
               'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']].mean().plot.bar(
                   width=0.5, linewidth=2, figsize=(16,10), color='#FF69B4')
    plt.xlabel('Month', fontsize=30)
    plt.ylabel('Monthly Rainfall (in mm)', fontsize=30)
    plt.title('Monthly Rainfall in India', fontsize=25)
    ax.tick_params(labelsize=10)
    plt.grid()
    plt.show()

# Main window with animated background
def main():
    root = Tk()
    root.geometry("1000x900")
    root.title("Weather App")
    
    main_frame = Frame(root, bg='#1A1A2E')
    main_frame.pack(fill=BOTH, expand=True)
    
    canvas = Canvas(main_frame, width=1000, height=900, highlightthickness=0, bg='#1A1A2E')
    canvas.pack(fill=BOTH, expand=True)
    
    for i in range(900):
        r = min(10 + i//4, 255)
        g = min(10 + i//6, 255)
        b = min(30 + i//3, 255)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, 1000, i, fill=color)
    
    topFrame = Frame(canvas, bg='#1A1A2E')
    topFrame.place(relx=0.5, rely=0.1, anchor=CENTER, width=800, height=200)
    
    bottomFrame = Frame(canvas, bg='#1A1A2E')
    bottomFrame.place(relx=0.5, rely=0.5, anchor=CENTER, width=800, height=600)
    
    # Title label with static, attractive font
    title_label = Label(topFrame, text="WEATHER REPORT", 
                        borderwidth=1, font=("Helvetica", 40, "bold"), bg='#1A1A2E', fg='#FFD700')
    title_label.pack(pady=20)
    
    # Create buttons with vibrant colors and animations
    buttons = [
        ("Current weather report", weather, '#E94560', '#FF6B6B', '#FF0000'),
        ("Predict rainfall tomorrow", predict_rainfall, '#9370DB', '#BA55D3', '#8A2BE2'),
        ("Analyze average rainfall", analyze, '#00BFFF', '#87CEFA', '#1E90FF'),
        ("Voice Input", voice_input, '#32CD32', '#98FB98', '#00FF7F')
    ]
    
    for i, (text, command, color, hover_color, press_color) in enumerate(buttons):
        btn = Button(bottomFrame, text=text, fg='white', command=command,
                    font=("Helvetica", 15, "bold"), bg=color, activebackground=press_color, 
                    relief='flat', bd=0, width=25, height=2)
        
        btn.normal_color = color
        btn.hover_color = hover_color
        btn.press_color = press_color
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", button_press)
        btn.bind("<ButtonRelease-1>", button_release)
        
        btn.pack(pady=15, padx=50, fill=X)
    
    root.mainloop()

if __name__ == "__main__":
    splash_screen()