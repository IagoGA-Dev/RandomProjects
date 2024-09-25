import pyautogui
import tkinter as tk
from tkinter import colorchooser
from threading import Thread
import keyboard
import time

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Aimbot")

        self.color = None
        self.region = None  # Stores the selected region as (left, top, width, height)
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        self.color_button = tk.Button(self.root, text="Select Color", command=self.select_color)
        self.color_button.pack(pady=10)

        self.pick_color_button = tk.Button(self.root, text="Pick Color from Screen", command=self.pick_color_from_screen)
        self.pick_color_button.pack(pady=10)

        self.color_label = tk.Label(self.root, text="No color selected")
        self.color_label.pack(pady=5)

        self.region_button = tk.Button(self.root, text="Select Region", command=self.select_region)
        self.region_button.pack(pady=10)

        self.region_label = tk.Label(self.root, text="Region: Full Screen")
        self.region_label.pack(pady=5)

        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(pady=5)

        self.start_button = tk.Button(self.root, text="Start (F8)", command=self.start_autoclicker)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop (F9)", command=self.stop_autoclicker)
        self.stop_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start a separate thread to listen for key presses
        self.listener_thread = Thread(target=self.key_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def select_color(self):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code[0]:
            self.color = color_code[0]  # RGB tuple
            self.color_label.config(text=f"Selected Color: {self.color}")

    def pick_color_from_screen(self):
        self.root.withdraw()  # Hide the root window
        time.sleep(0.2)  # Allow time for the window to hide

        # Create a fullscreen transparent window
        self.overlay = tk.Tk()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.config(bg='grey')

        canvas = tk.Canvas(self.overlay, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)

        canvas.bind("<ButtonPress-1>", self.on_color_pick)
        canvas.bind("<Escape>", lambda event: self.exit_color_pick())

        self.overlay.mainloop()

    def on_color_pick(self, event):
        x = self.overlay.winfo_pointerx()
        y = self.overlay.winfo_pointery()
        self.overlay.destroy()
        self.root.deiconify()

        # Get the color at the clicked position
        screenshot = pyautogui.screenshot()
        pixel_color = screenshot.getpixel((x, y))
        self.color = pixel_color  # RGB tuple
        self.color_label.config(text=f"Selected Color: {self.color}")

    def exit_color_pick(self):
        self.overlay.destroy()
        self.root.deiconify()

    def select_region(self):
        self.root.withdraw()  # Hide the root window
        time.sleep(0.2)  # Allow time for the window to hide

        # Create a fullscreen transparent window
        self.overlay = tk.Tk()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.config(bg='grey')
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect = None

        canvas = tk.Canvas(self.overlay, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)

        canvas.bind("<ButtonPress-1>", self.on_button_press)
        canvas.bind("<B1-Motion>", self.on_move_press)
        canvas.bind("<ButtonRelease-1>", self.on_button_release)
        canvas.bind("<Escape>", lambda event: self.exit_region_pick())

        self.overlay.mainloop()

    def exit_region_pick(self):
        self.overlay.destroy()
        self.root.deiconify()

    def on_button_press(self, event):
        # Save the starting point
        self.start_x = self.overlay.winfo_pointerx()
        self.start_y = self.overlay.winfo_pointery()
        self.rect = None

    def on_move_press(self, event):
        canvas = event.widget
        # Delete the previous rectangle
        if self.rect:
            canvas.delete(self.rect)
        # Draw a new rectangle
        curX, curY = (self.overlay.winfo_pointerx(), self.overlay.winfo_pointery())
        self.rect = canvas.create_rectangle(self.start_x, self.start_y, curX, curY, outline='red')

    def on_button_release(self, event):
        # Capture the ending point
        self.end_x = self.overlay.winfo_pointerx()
        self.end_y = self.overlay.winfo_pointery()

        # Calculate the region
        left = min(self.start_x, self.end_x)
        top = min(self.start_y, self.end_y)
        right = max(self.start_x, self.end_x)
        bottom = max(self.start_y, self.end_y)
        width = right - left
        height = bottom - top

        self.region = (left, top, width, height)
        self.region_label.config(text=f"Region: {self.region}")

        # Close the overlay and show the root window
        self.overlay.destroy()
        self.root.deiconify()

    def start_autoclicker(self):
        if self.color is None:
            self.status_label.config(text="Please select a color first.")
            return
        if not self.running:
            self.running = True
            self.status_label.config(text="Status: Running")
            self.autoclicker_thread = Thread(target=self.autoclicker)
            self.autoclicker_thread.daemon = True
            self.autoclicker_thread.start()

    def stop_autoclicker(self):
        if self.running:
            self.running = False
            self.status_label.config(text="Status: Stopped")

    def autoclicker(self):
        while self.running:
            if self.region:
                screenshot = pyautogui.screenshot(region=self.region)
                offset_x, offset_y = self.region[0], self.region[1]
            else:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0

            width, height = screenshot.size
            target_color = self.color

            found = False
            for x in range(0, width, 5):  # Skip pixels for efficiency
                for y in range(0, height, 5):
                    current_color = screenshot.getpixel((x, y))
                    if self.colors_match(current_color, target_color):
                        screen_x = x + offset_x
                        screen_y = y + offset_y
                        pyautogui.moveTo(screen_x, screen_y)
                        pyautogui.click()
                        time.sleep(0.01)
                        found = True
                        break
                if found:
                    break  # Break outer loop if clicked
            time.sleep(0.1)  # Wait before next iteration

    def colors_match(self, color1, color2, tolerance=20):
        return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))

    def key_listener(self):
        while True:
            if keyboard.is_pressed('F8'):
                self.start_autoclicker()
                time.sleep(0.5)  # Debounce delay
            if keyboard.is_pressed('F9'):
                self.stop_autoclicker()
                time.sleep(0.5)  # Debounce delay
            time.sleep(0.1)

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
