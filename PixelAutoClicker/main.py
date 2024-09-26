import customtkinter as ctk
from autoclicker import AutoClicker
from PIL import ImageTk, Image
import os

if __name__ == "__main__":
    # Initialize the main window
    root = ctk.CTk()
    root.title("Pixel AutoClicker")
    root.geometry("400x600")
    root.resizable(False, False)

    # Set the application icon
    icon_path = os.path.join('assets', 'icon.png')
    icon_image = ImageTk.PhotoImage(Image.open(icon_path))
    root.iconphoto(True, icon_image)

    # Create and run the application
    app = AutoClicker(root)
    root.mainloop()
