import dearpygui.dearpygui as dpg       # for GUI
from tkinter import filedialog as fd    # for file selection
import sounddevice as sd                # to play .wav files
import soundfile as sf                  # to play .wav files
import math
import time
import collections
import threading
import pdb

# GUI documentation:    https://dearpygui.readthedocs.io/en/latest/index.html
# File Selection:       https://dearpygui.readthedocs.io/en/latest/documentation/file-directory-selector.html


# for input file name
global fname
fname = ''
global text
global buttons

#for the graph of audio output
nsamples = 100 #make number of samples as a parameter in the gui

# for input file
global input_wav_data
global input_wav_fs

# for envelope
global envelope
envelope = 1
envs = ["default","triangle","bell","untouched","complex"]

"""
def prep_data():
    global nsamples
    sample_table = []
    with open("yeat.txt", "r") as f:
        for thing, line in enumerate(f.readlines()):
            sample_table.append(float(line.strip()))
    f.close()
    nsamples = len(sample_table)
    indexes = list(range(0,nsamples+1))
    return sample_table, indexes
        
"""

def resize_in():
    dpg.fit_axis_data("y_axis") 
    dpg.fit_axis_data("x_axis")

def update_in_display():
    global nsamples
    sample_table = []
    for x in range(0, 100):
        sample_table.append(x)
    nsamples = len(sample_table)
    indexes = list(range(0,nsamples))
    dpg.set_value('input_line', [indexes, sample_table])
    resize_in()

# initial input graph display  
def prep_in_display():
    global nsamples
    sample_table = []
    for x in range(0, 100):
        sample_table.append(0)
    nsamples = len(sample_table)
    indexes = list(range(0,nsamples+1))
    return sample_table, indexes
        
def play_input():
    if fname == '':
        dpg.set_value(msg_box, "Message Box: No Input")
    else: 
        try:
            print(fname)
            sd.play(input_wav_data, input_wav_fs)
            status = sd.wait() 
        except:
            dpg.set_value(msg_box, "Message Box: Input Playback Failure")


def save_callback():
    print("Save Clicked")

def callback(sender, app_data):
    print('OK was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)

def cancel_callback(sender, app_data):
    print('Cancel was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)

def select_file():
    global fname
    global input_wav_data
    global input_wav_fs
    try:
        fname = fd.askopenfilename(filetypes=(("Audio Files", ".wav"),   ("All Files", "*.*")))
        t = fname.split("/").pop()
        dpg.set_value(text,"File Name: "+t)
        input_wav_data, input_wav_fs = sf.read(fname, dtype='float32') 
    except:
        dpg.set_value(msg_box, "Message Box: File Selection Failed")

def update_envelope(sender, app_data, user_data):
    state, enabled_theme, disabled_theme = user_data
    # Apply the appropriate theme
    dpg.bind_item_theme(sender, enabled_theme)
    if sender == "default":
        dpg.set_value(env_text,"Envelope type: Default")
        envelope = 1
    elif sender == "triangle":
        dpg.set_value(env_text,"Envelope type: Triangle")
        envelope = 2
    elif sender == "bell":
        dpg.set_value(env_text,"Envelope type: Bell")
        envelope = 3
    elif sender == "untouched":
        dpg.set_value(env_text,"Envelope type: Untouched")
        envelope = 4
    else:
        dpg.set_value(env_text,"Envelope type: Complex")
        envelope = 5

    for env in envs:
        if sender != env:
            dpg.bind_item_theme(env, disabled_theme)
            dpg.set_item_user_data(env, (False, enabled_theme, disabled_theme,))
        else:
            dpg.set_item_user_data(env, (True, enabled_theme, disabled_theme,))

# below replaces, start_dearpygui()
dpg.create_context()

# for button selection highlight
with dpg.theme() as enabled:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button,(42,91,128), category=dpg.mvThemeCat_Core)

with dpg.theme() as disabled:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button,(51,51,55), category=dpg.mvThemeCat_Core)

with dpg.window(tag="GS", label="GS", width=800, height=300):
    # Message Box
    msg_box = dpg.add_text("Message Box :")

    # Input file selection
    with dpg.group(horizontal=True):
        dpg.add_button(label="Preview Input", callback=play_input)
        dpg.add_button(label="Select File", callback=select_file)
    text = dpg.add_text("File Name: "+fname)
    
    # Grain specification
    dpg.add_input_float(label="Grain Duration (ms)", width=200, default_value=50)
    dpg.add_slider_float(label="Grain Duration Variation",width=200, default_value=0, max_value = 100)
    
    # Cloud specification
    dpg.add_input_float(label="Cloud Density (ms/sec)", width=200, default_value=50)
    dpg.add_slider_float(label="Cloud Density Variation",width=200, default_value=0, max_value = 100)

    dpg.add_slider_float(label="Cloud Center (% of input)", default_value=50, max_value=100, width=200)
    dpg.add_slider_float(label="Cloud Size (% of input)", default_value=100, max_value=100, width=200)

    dpg.add_slider_float(label="Cloud Center (% of input)", default_value=50, max_value=100, width=200)
    dpg.add_slider_float(label="Cloud Size (% of input)", default_value=100, max_value=100, width=200)

    # Envelope specification
    env_text = dpg.add_text("Envelope type: Default")
    with dpg.group(horizontal=True):
        dpg.add_button(tag="default", label="Default", width=70, callback=update_envelope, user_data=(True, enabled, disabled,))
        dpg.add_button(tag="triangle", label="Triangle", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        dpg.add_button(tag="bell", label="Bell", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        dpg.add_button(tag="untouched", label="Untouched", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        dpg.add_button(tag="complex", label="Complex", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        
    with dpg.plot(label='Input Sample', height=-1, width=-1, tag="input_plot"):
        
        # series belong to a y axis. Note the tag name is used in the update
        # function update_data

        samples, indexes = prep_in_display()
        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="y_axis")

        # series belong to a y axis
        dpg.add_line_series(indexes, samples, label="Audio Sample", parent="x_axis", tag="input_line")
    
    dpg.add_button(tag="resize_in", label="Resize Graph", width=140, callback=resize_in)
        
    dpg.add_button(tag="do_thing",label="Synthesize", width=140)#callback will be running the synthesizer code
    
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    
dpg.bind_item_theme("default", enabled)
# Update the user_data associated with the button

dpg.create_viewport(title='Granular Synthesis', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("GS", True)
dpg.start_dearpygui()
dpg.destroy_context()