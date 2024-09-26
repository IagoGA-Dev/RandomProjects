import pyautogui
import customtkinter as ctk
from tkinter import colorchooser
from threading import Thread
import keyboard
import time
from utils import colors_match, rgb_to_hex

class AutoClicker:
    def __init__(self, root):
        self.root = root

        # Set the appearance mode and theme
        ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
        ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

        self.color = None
        self.region = None
        self.use_fullscreen = True  # Variable to track fullscreen usage
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(master=self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title label
        title_label = ctk.CTkLabel(
            main_frame,
            text="Pixel AutoClicker",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Color selection frame
        color_frame = ctk.CTkFrame(master=main_frame)
        color_frame.pack(pady=10, padx=10, fill="x")

        # Color buttons
        self.color_button = ctk.CTkButton(
            color_frame, text="Select Color", command=self.select_color
        )
        self.color_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.pick_color_button = ctk.CTkButton(
            color_frame, text="Pick Color from Screen", command=self.pick_color_from_screen
        )
        self.pick_color_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Configure grid weights
        color_frame.columnconfigure((0, 1), weight=1)

        # Color display frame
        color_display_frame = ctk.CTkFrame(master=main_frame)
        color_display_frame.pack(pady=5)

        # Color label
        self.color_label = ctk.CTkLabel(color_display_frame, text="No color selected")
        self.color_label.pack(side="left", padx=5)

        # Color preview box
        self.color_preview = ctk.CTkFrame(
            color_display_frame,
            width=50,
            height=25,
            fg_color="#D3D3D3",  # Light gray for no color selected
            corner_radius=5
        )
        self.color_preview.pack(side="left", padx=5)

        # Region selection frame
        region_frame = ctk.CTkFrame(master=main_frame)
        region_frame.pack(pady=10, padx=10, fill="x")

        # Region button
        self.region_button = ctk.CTkButton(
            region_frame, text="Select Region", command=self.select_region
        )
        self.region_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Use Fullscreen button
        self.fullscreen_button = ctk.CTkButton(
            region_frame, text="Use Fullscreen", command=self.toggle_fullscreen
        )
        self.fullscreen_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Configure grid weights
        region_frame.columnconfigure((0, 1), weight=1)

        # Region label
        self.region_label = ctk.CTkLabel(main_frame, text="Region: Full Screen")
        self.region_label.pack(pady=5)

        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame, text="Status: Stopped", font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=(20, 10))

        # Control frame
        control_frame = ctk.CTkFrame(master=main_frame)
        control_frame.pack(pady=10, padx=10, fill="x")

        # Start and Stop buttons
        self.start_button = ctk.CTkButton(
            control_frame, text="Start (F8)", command=self.start_autoclicker
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(
            control_frame, text="Stop (F9)", command=self.stop_autoclicker
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Configure grid weights
        control_frame.columnconfigure((0, 1), weight=1)

        # Appearance mode selector
        settings_frame = ctk.CTkFrame(master=main_frame)
        settings_frame.pack(pady=10, padx=10, fill="x")

        self.mode_option = ctk.CTkOptionMenu(
            settings_frame,
            values=["System", "Light", "Dark"],
            command=self.change_mode
        )
        self.mode_option.set("System")
        self.mode_option.pack(pady=5, padx=10, fill="x")

        # Footer label
        footer_label = ctk.CTkLabel(
            main_frame,
            text="Use F8 to Start and F9 to Stop the autoclicker.",
            font=ctk.CTkFont(size=12)
        )
        footer_label.pack(pady=(20, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start key listener thread
        self.listener_thread = Thread(target=self.key_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def toggle_fullscreen(self):
        self.use_fullscreen = not self.use_fullscreen
        if self.use_fullscreen:
            self.region = None
            self.region_label.configure(text="Region: Full Screen")
            self.fullscreen_button.configure(text="Use Selected Region")
        else:
            if self.region:
                self.region_label.configure(text=f"Region: {self.region}")
            else:
                self.region_label.configure(text="Region: Not Selected")
            self.fullscreen_button.configure(text="Use Fullscreen")

    def change_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    def select_color(self):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code[0]:
            # Ensure RGB values are integers
            self.color = tuple(map(int, color_code[0]))
            self.color_label.configure(text=f"Selected Color: {self.color}")
            hex_color = rgb_to_hex(self.color)
            self.color_preview.configure(fg_color=hex_color)

    def pick_color_from_screen(self):
        self.root.withdraw()
        time.sleep(0.2)
        self.overlay = ctk.CTk()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.config(bg='grey')

        self.canvas = ctk.CTkCanvas(self.overlay, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        # Variables to hold the circle
        self.color_indicator = None

        self.canvas.bind("<ButtonPress-1>", self.on_color_pick)
        self.canvas.bind("<Escape>", lambda event: self.exit_color_pick())
        self.canvas.bind("<Motion>", self.update_color_indicator)

        self.overlay.mainloop()

    def update_color_indicator(self, event):
        x = self.overlay.winfo_pointerx()
        y = self.overlay.winfo_pointery()

        # Get the color at the current position
        try:
            pixel_color = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
            hex_color = rgb_to_hex(pixel_color)
        except Exception:
            hex_color = "#FFFFFF"

        # Remove the previous indicator
        if self.color_indicator:
            self.canvas.delete(self.color_indicator)

        # Draw the circle near the cursor
        radius = 15
        indicator_x = event.x + 20
        indicator_y = event.y + 20

        self.color_indicator = self.canvas.create_oval(
            indicator_x - radius,
            indicator_y - radius,
            indicator_x + radius,
            indicator_y + radius,
            fill=hex_color,
            outline="black"
        )

    def on_color_pick(self, event):
        x = self.overlay.winfo_pointerx()
        y = self.overlay.winfo_pointery()
        self.overlay.destroy()
        self.root.deiconify()

        # Get the color at the clicked position
        pixel_color = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
        self.color = pixel_color
        self.color_label.configure(text=f"Selected Color: {self.color}")
        hex_color = rgb_to_hex(self.color)
        self.color_preview.configure(fg_color=hex_color)

    def exit_color_pick(self):
        self.overlay.destroy()
        self.root.deiconify()

    def select_region(self):
        self.root.withdraw()
        time.sleep(0.2)
        self.overlay = ctk.CTk()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.config(bg='grey')
        self.start_x = self.start_y = self.rect = None

        canvas = ctk.CTkCanvas(self.overlay, cursor="cross")
        canvas.pack(fill="both", expand=True)

        canvas.bind("<ButtonPress-1>", self.on_button_press)
        canvas.bind("<B1-Motion>", self.on_move_press)
        canvas.bind("<ButtonRelease-1>", self.on_button_release)
        canvas.bind("<Escape>", lambda event: self.exit_region_pick())

        self.overlay.mainloop()

    def exit_region_pick(self):
        self.overlay.destroy()
        self.root.deiconify()

    def on_button_press(self, event):
        self.start_x = self.overlay.winfo_pointerx()
        self.start_y = self.overlay.winfo_pointery()
        self.rect = None

    def on_move_press(self, event):
        canvas = event.widget
        if self.rect:
            canvas.delete(self.rect)
        curX = self.overlay.winfo_pointerx()
        curY = self.overlay.winfo_pointery()
        self.rect = canvas.create_rectangle(
            self.start_x, self.start_y, curX, curY, outline='red'
        )

    def on_button_release(self, event):
        end_x = self.overlay.winfo_pointerx()
        end_y = self.overlay.winfo_pointery()

        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)
        width = right - left
        height = bottom - top

        self.region = (left, top, width, height)
        if not self.use_fullscreen:
            self.region_label.configure(text=f"Region: {self.region}")

        self.overlay.destroy()
        self.root.deiconify()

    def start_autoclicker(self):
        if self.color is None:
            self.status_label.configure(text="Please select a color first.")
            return
        if not self.running:
            self.running = True
            self.status_label.configure(text="Status: Running")
            self.autoclicker_thread = Thread(target=self.autoclicker)
            self.autoclicker_thread.daemon = True
            self.autoclicker_thread.start()

    def stop_autoclicker(self):
        if self.running:
            self.running = False
            self.status_label.configure(text="Status: Stopped")

    def autoclicker(self):
        while self.running:
            if self.use_fullscreen or self.region is None:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0
            else:
                screenshot = pyautogui.screenshot(region=self.region)
                offset_x, offset_y = self.region[0], self.region[1]

            width, height = screenshot.size
            target_color = self.color

            found = False
            for x in range(0, width, 5):
                for y in range(0, height, 5):
                    current_color = screenshot.getpixel((x, y))
                    if colors_match(current_color, target_color):
                        screen_x = x + offset_x
                        screen_y = y + offset_y
                        pyautogui.moveTo(screen_x, screen_y)
                        pyautogui.click()
                        time.sleep(0.01)
                        found = True
                        break
                if found:
                    break
            time.sleep(0.1)

    def key_listener(self):
        while True:
            if keyboard.is_pressed('F8'):
                self.start_autoclicker()
                time.sleep(0.5)
            if keyboard.is_pressed('F9'):
                self.stop_autoclicker()
                time.sleep(0.5)
            time.sleep(0.1)

    def on_closing(self):
        self.running = False
        self.root.destroy()
