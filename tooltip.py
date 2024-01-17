# tooltip.py

from imports import *

class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        # Set initial configuration values
        self.waittime = 500     # milliseconds for delay before showing tooltip
        self.wraplength = 180   # maximum width of the tooltip in pixels
        self.widget = widget    # the Tkinter widget to which the tooltip is attached
        self.text = text        # text to be displayed in the tooltip
        # Bind events to widget
        self.widget.bind("<Enter>", self.enter)        # Triggered when mouse enters widget
        self.widget.bind("<Leave>", self.leave)        # Triggered when mouse leaves widget
        self.widget.bind("<ButtonPress>", self.leave)  # Triggered when mouse button is pressed
        self.id = None           # to store the ID of the scheduled task
        self.tw = None           # to store the tooltip window

    def enter(self, event=None):
        # Schedule the display of the tooltip when the mouse enters the widget
        self.schedule()

    def leave(self, event=None):
        # Unschedule the display and hide the tooltip when the mouse leaves the widget
        self.unschedule()
        self.hidetip()

    def schedule(self):
        # Schedule the display of the tooltip after a delay
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        # Unschedule a previously scheduled tooltip display
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        # Display the tooltip at the mouse position
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # Create a Toplevel window for the tooltip
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # Make the window borderless
        self.tw.wm_geometry(f"+{x}+{y}")   # Set window position

        # Create a label inside the window with tooltip text
        label = tk.Label(self.tw, text=self.text, justify='left',
                      background="#ffffff", relief='solid', borderwidth=1,
                      wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        # Hide the tooltip window
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()