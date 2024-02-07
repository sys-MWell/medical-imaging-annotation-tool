# imports.py

import copy
import os
import shutil
import uuid
import matplotlib
import numpy as np
from PIL import ImageTk, Image
from matplotlib import backend_bases, patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as mlines
import tkinter as tk
from tkinter import Scale
from tkinter import filedialog
from tkinter import ttk, font
import tkinter.messagebox as messagebox
import json
import random
from sklearn.cluster import KMeans

from matplotlib.patches import FancyArrow

# import file data
from constants import *
from image_info import ImageInfo
from user_cache import UserCache
from random_colour import RandomColourGenerator
from tooltip import CreateToolTip
from rads_loaded_status import RadsLoadStatus
from load_rads_data import LoadRadsData
from pen_checker import PenTypeFileManager

#from annotation_page_combine import AnnotationPage
from rads_page_functionality import RadsFunctionality
from annotation_page_functionality import PageFunctionality

matplotlib.use("TkAgg")