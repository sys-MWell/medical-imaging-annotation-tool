# annotation_page_data_loader.py
from imports import *
import tkinter as tk
from tkinter import ttk


class DoubleSlider(tk.Frame):
    def __init__(self, master, page_functionality, slider_width=421, slider_height=50, bg="white",
                 slider_color="blue", **kwargs):
        self.page_functionality = page_functionality
        self.slider_width = slider_width
        self.slider_height = slider_height
        self.slider_color = slider_color

        tk.Frame.__init__(self, master, **kwargs)

        # Create a frame to contain the canvas with x-padding
        self.canvas_frame = tk.Frame(self, padx=10, pady=10)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Adjust canvas width and height accordingly
        self.canvas = tk.Canvas(self.canvas_frame, width=slider_width + 10, height=slider_height, bg=bg)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.slider1_pos = 0.3
        self.slider2_pos = 0.7

        self.slider1_label = None
        self.slider2_label = None

        self.redraw_sliders()
        self.canvas.bind("<B1-Motion>", self.on_slider_move)

    def redraw_sliders(self):
        # Adjust canvas size based on the modified slider width
        self.canvas.config(width=self.slider_width + 10, height=self.slider_height)

        # Remove any existing sliders and labels
        self.canvas.delete("slider")
        self.canvas.delete("slider_label")

        # Create sliders and labels with adjusted positions
        self.create_slider(self.slider1_pos, 1)
        self.create_slider(self.slider2_pos, 2)
        self.update_labels()  # Create labels

    def create_slider(self, position, tag):
        # Adjust the x-coordinate calculation to start at position 5 and end at position 250
        x = position * self.slider_width + 5
        self.canvas.create_line(x, 0, x, self.slider_height, fill=self.slider_color, width=2, tags=("slider", tag))

    def create_slider_label(self, x, y, value):
        # Adjust the x-coordinate calculation to start at position 5 and end at position 250
        self.canvas.create_text(x, y, text=str(value), tags="slider_label", anchor="n")

    def on_slider_move(self, event):
        x = self.canvas.canvasx(event.x)
        item = self.canvas.find_closest(x, 0)[0]
        tags = self.canvas.gettags(item)
        if "slider" in tags:
            if x < 5:
                x = 5
            elif x > self.slider_width + 5:
                x = self.slider_width + 5
            if item == 5:  # First slider
                if x >= self.slider2_pos * self.slider_width + 5:  # Ensure slider 1 doesn't go above slider 2
                    x = self.slider2_pos * self.slider_width + 4
            elif item == 6:  # Second slider
                if x <= self.slider1_pos * self.slider_width + 5:  # Ensure slider 2 doesn't go below slider 1
                    x = self.slider1_pos * self.slider_width + 6
            self.canvas.coords(item, x, 0, x, self.slider_height)
            if item == 5:  # First slider
                self.slider1_pos = (x - 5) / self.slider_width
            elif item == 6:  # Second slider
                self.slider2_pos = (x - 5) / self.slider_width
            self.update_values()

    def update_values(self):
        self.page_functionality.rgb_value1 = value1 = int(self.slider1_pos * 255)
        self.page_functionality.rgb_value2 = int(self.slider2_pos * 255)
        self.update_labels()

    def update_labels(self):
        value1 = int(self.slider1_pos * 255)
        value2 = int(self.slider2_pos * 255)
        # Delete previous labels
        self.canvas.delete("slider_label")

        # Create new labels
        if value1 > 250:
            slider1_x = self.slider1_pos * self.slider_width - 5
            self.create_slider_label(slider1_x, self.slider_height + 5, int(self.slider1_pos * 255))
        if value2 > 250:
            slider2_x = self.slider2_pos * self.slider_width - 5
            self.create_slider_label(slider2_x, self.slider_height + 5, int(self.slider2_pos * 255))
        if value1 <= 250:
            slider1_x = self.slider1_pos * self.slider_width + 5
            self.create_slider_label(slider1_x, self.slider_height + 5, int(self.slider1_pos * 255))
        if value2 <= 250:
            slider2_x = self.slider2_pos * self.slider_width + 5
            self.create_slider_label(slider2_x, self.slider_height + 5, int(self.slider2_pos * 255))