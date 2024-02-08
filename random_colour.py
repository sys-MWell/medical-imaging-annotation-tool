# random_colour.py
from imports import *


class RandomColourGenerator:
    def __init__(self):
        self.used_colours = set()
        # Predefined colour mapping
        self.colour_mapping_margin = {
            'Indistinct': '#20f75a',
            'Angular': '#f7a820',
            'Microlobulated': '#be20f7',
            'Spiculated': '#20f7c8',
        }

        self.colour_mapping_echo = {
            'Anechoic': '#20def7',
            'Hyperechoic': '#7620f7',
            'Complex cystic and solid': '#f720be',
            'Hypoechoic': '#f72059',
            'Isoechoic': '#a5e359',
            'Heterogeneous': '#0954d6',
        }

    def predefined_colour(self, label):
        # Check if the label has a predefined colour in the margin mapping
        margin_color = self.colour_mapping_margin.get(label)
        if margin_color:
            return margin_color

        # Check if the label has a predefined colour in the echo mapping
        echo_color = self.colour_mapping_echo.get(label)
        if echo_color:
            return echo_color

        # Else return green
        return 'green'

    def random_hex_colour(self):
        while True:
            # Generate a random RGB color
            rgb = [random.randint(0, 255) for _ in range(3)]

            # Convert RGB to hex
            hex_colour = "#{:02x}{:02x}{:02x}".format(*rgb)

            # Check if the colour is not black, white, greyscale, or already used
            if self.is_valid_color(hex_colour):
                self.used_colours.add(hex_colour)
                return hex_colour

    def is_valid_color(self, hex_colour):
        # Exclude black, white, greyscale, and previously used colours
        return (
                hex_colour not in {"#000000", "#FFFFFF"}
                and self.calculate_greyscale_intensity(hex_colour) > 0.1
                and hex_colour not in self.used_colours
        )

    def calculate_greyscale_intensity(self, hex_colour):
        # Calculate greyscale intensity (0.0 for black, 1.0 for white)
        rgb = tuple(int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
        return sum(rgb) / (255 * 3)
