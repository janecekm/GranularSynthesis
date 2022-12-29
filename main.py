"""
MADELINE JANECEK, BRENDAN PARK
DECEMEBER 2022
COSC 4P98 PROJECT
Implementation of granular synthesis w/ GUI
Code for GUI
"""

import dearpygui.dearpygui as dpg       # for GUI
from tkinter import filedialog as fd    # for file selection
import sounddevice as sd                # to play .wav files
import soundfile as sf                  # to play .wav files
import math
import numpy as np
import synthesis.granularSynthesis as gs

# GUI documentation:    https://dearpygui.readthedocs.io/en/latest/index.html
# File Selection:       https://dearpygui.readthedocs.io/en/latest/documentation/file-directory-selector.html

# for input file name
global fname
fname = ''
global pathname
pathname = ''
global buttons

#for the graph of input audio output
global nsamples
nsamples = 100 #make number of samples as a parameter in the gui
global sample_table
global cloud_minimum
cloud_minimum = 0
global cloud_maximum
cloud_maximum = 100

header_length = 430
button_height = 25


# for input file
global input_wav_data # sample table as numpy.ndarray
global input_wav_fs

# for output file
global output_wav_data
output_wav_data = np.array([])

# for envelope
global envelope
envelope = 1
envs = ["default","triangle","bell","untouched","complex"]

def resize_in():
    dpg.fit_axis_data("y_axis") 
    dpg.fit_axis_data("x_axis")

def resize_out():
    dpg.fit_axis_data("oy_axis") 
    dpg.fit_axis_data("ox_axis")

def update_in_display():
    global nsamples
    global input_wav_data
    nsamples = input_wav_data.size
    indices = []
    for x in range(nsamples):
        indices.append(x)
    dpg.set_value('input_line', [indices, input_wav_data])
    cloud_center()
    resize_in()

def min_update():
    global cloud_minimum
    center = int(nsamples*(dpg.get_value("center_slider")/100))
    x = dpg.get_value("min_slider")
    cloud_minimum = int(center*(x/100))

    indices = [cloud_minimum, cloud_minimum] 
    value = [-1, 1]
    dpg.set_value("cloud_min", [indices, value])

def max_update():
    global cloud_maximum
    center = int(nsamples*(dpg.get_value("center_slider")/100))
    portion = nsamples - center
    x = dpg.get_value("max_slider")
    cloud_maximum = int(portion*(x/100)) + center

    indices = [cloud_maximum, cloud_maximum] 
    value = [-1, 1]
    dpg.set_value("cloud_max", [indices, value])

def disable_buttons():
    dpg.disable_item("synth")
    dpg.disable_item("input_preview")
    dpg.disable_item("output_preview")

def enable_buttons():
    dpg.enable_item("synth")
    dpg.enable_item("input_preview")
    dpg.enable_item("output_preview")

def synthesize():
    disable_buttons()
    dpg.set_value(msg_box, "Generating Output...")
    switch = {
        2: gs.Envelope.TRIANGLE,
        3: gs.Envelope.BELL,
        4: gs.Envelope.UNTOUCHED,
        5: gs.Envelope.COMPLEX
    }

    if fname == '': 
        dpg.set_value(msg_box, "Error: No Input File")
        dpg.set_value(text, "File Name: " + fname)
        return
    if dpg.get_value("out_dur") <= 0:
        dpg.set_value(msg_box, "Error: Ouput Duration must be greater than 0")
        return 
    if dpg.get_value("grain_dur") <= 0:
        dpg.set_value(msg_box, "Error: Grain Duration must be greater than 0")
        return 
    if dpg.get_value("cloud_density") <=0: 
        dpg.set_value(msg_box, "Error: Cloud Density must be greater than 0")
        return 

    output = gs.synthesizeGranularly(fname, input_wav_data, dpg.get_value("out_dur"), switch.get(envelope,gs.Envelope.TRAPEZIUM),
    gs.Selection.NORMAL, dpg.get_value("grain_dur"), dpg.get_value("grain_dur_var")/100,
    dpg.get_value("cloud_density"),dpg.get_value("cloud_density_var")/100,
    dpg.get_value("grain_pitch"),dpg.get_value("grain_pitch_var")/100, int(nsamples*(dpg.get_value("center_slider")/100)), cloud_minimum, cloud_maximum, input_wav_fs)

    global output_wav_data
    output_wav_data = np.array(output)

    # show on graph
    indices = []
    for x in range(output_wav_data.size):
        indices.append(x)
    dpg.set_value('output_line', [indices, output_wav_data])
    resize_out()


    dpg.set_value(msg_box, "Output Generated")
    enable_buttons()

# initial input graph display  
def prep_display():
    global nsamples
    global input_wav_data
    sample_table = []
    for x in range(0, 101):
        sample_table.append(0)
    nsamples = len(sample_table)
    input_wav_data = np.array(sample_table, dtype=np.int8)
    indexes = list(range(0,nsamples))
    return sample_table, indexes

def prep_env_display():
    sample_table = []
    for x in range(0, 15):
        sample_table.append(x/15)
    for x in range(70):
        sample_table.append(1)
    for x in range(1, 16):
        sample_table.append(1 - (x/16))
    indexes = list(range(0,100))
    return sample_table, indexes

def play_input():
    if fname == '':
        dpg.set_value(msg_box, "Error: No Input File")
        dpg.set_value(text, "File Name: " + fname)

    else: 
        try:
            sd.play(input_wav_data, input_wav_fs)
        except:
            dpg.set_value(msg_box, "Error: Input Playback Failure")    

def play_output():
    if output_wav_data.size == 0: 
        dpg.set_value(msg_box, "Error: No Output to Play")   
    else:
        try:
            sd.play(output_wav_data, input_wav_fs)
        except:
            dpg.set_value(msg_box, "Error: Output Playback Failure")  

def save_callback():
    if output_wav_data.size == 0: 
        dpg.set_value(msg_box, "Error: No Ouput to Save")
        return
    if pathname == '':
        dpg.set_value(msg_box, "Error: No File Path Selected")
        return
    f = dpg.get_value("out_name").strip()
    if f == "":
        dpg.set_value(msg_box, "Error: No Output File Name")
        return
    
    try: 
        temp = pathname + "/" + f + ".wav"
        sf.write(temp, output_wav_data, input_wav_fs)
        dpg.set_value(msg_box,  f + ".wav Saved")
    except:
        dpg.set_value(msg_box, "Error: Save Output Failure")  
    
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

        #  update graph display
        update_in_display()
    except:
        dpg.set_value(msg_box, "Error: File Selection Failed")

def select_file_path():
    global pathname
    try: 
        pathname = fd.askdirectory()
        dpg.set_value(file_text, "Folder Name: " + pathname.split("/").pop())
    except:
        dpg.set_value(msg_box, "Error: Path Selection Failed")

def update_envelope(sender, app_data, user_data):
    sample_table = []
    indexes = list(range(0,100))
    state, enabled_theme, disabled_theme = user_data
    # Apply the appropriate theme
    dpg.bind_item_theme(sender, enabled_theme)
    if sender == "default":
        sample_table, indexes = prep_env_display()
        envelope = 1
    elif sender == "triangle":
        for x in range(100):
            if x < 50:
                sample_table.append(x/50)
            else:
                sample_table.append(1 - (x-50)/50)
        envelope = 2
    elif sender == "bell":
        envelope = 3
        for x in range(100):
            cutoff = math.sin(math.pi*x/100)
            sample_table.append(cutoff)
    elif sender == "untouched":
        envelope = 4
        for x in range(100):
            sample_table.append(2)
    else:
        envelope = 5
        for x in range(100):
            bell_cutoff = math.sin(math.pi*x/100)
            sine_cutoff = math.sin(3*math.pi*x/100)
            sample_table.append(min(bell_cutoff, abs(sine_cutoff)))

    for env in envs:
        if sender != env:
            dpg.bind_item_theme(env, disabled_theme)
            dpg.set_item_user_data(env, (False, enabled_theme, disabled_theme,))
        else:
            dpg.set_item_user_data(env, (True, enabled_theme, disabled_theme,))
    
    dpg.set_value("e_line", [indexes, sample_table])

def cloud_center():
    global nsamples
    global input_wav_data
    c = dpg.get_value("center_slider")
    nsamples = input_wav_data.size
    if c == 0:
        c = 1
    indices = [nsamples*(c/100), nsamples*(c/100)] 
    value = [-1, 1]
    dpg.set_value("cloud_center", [indices, value])
    min_update()
    max_update()

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
    with dpg.group(horizontal=True):
        with dpg.child_window(width=header_length, tag="control"):

            dpg.add_button(tag='synth',label='Synthesize', width = 416, height=button_height+15, callback = synthesize)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Play Input", width = 133, height=button_height, callback=play_input, tag = "input_preview")
                dpg.add_button(label="Play Output", width = 133, height=button_height, callback=play_output, tag = "output_preview")
                dpg.add_button(label = "Stop Playback", width = 133, height=button_height, callback=sd.stop)
                        
                # Message Box
            with dpg.child_window(height=35):
                msg_box = dpg.add_text("")
            dpg.add_text("")
            # Input file selection
            with dpg.collapsing_header(label="Input File Selection"):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Select File", callback=select_file)
                    text = dpg.add_text("File Name: "+fname)
            # Output Specification
            with dpg.collapsing_header(label="Output Specifications"):
                dpg.add_input_float(label="Output Duration (s)", default_value=1, width=200, tag="out_dur")
                dpg.add_input_text(width = 200, label="Ouptut File Name", default_value="output_file", tag="out_name")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Select Folder", callback=select_file_path)
                    file_text = dpg.add_text("Folder Name: ")
                dpg.add_button(label="Save", width=418, height=button_height, callback = save_callback)

            # Grain specification
            with dpg.collapsing_header(label="Grain Specifications"):
                dpg.add_input_float(label="Grain Duration (ms)", width=200, default_value=50,tag="grain_dur")
                dpg.add_slider_float(label="Grain Duration Variation (%)",width=200, default_value=0, max_value = 100, tag="grain_dur_var")

            with dpg.collapsing_header(label="Pitch Change Specifications"):
                dpg.add_slider_float(label="Pitch Adjustment (1 for no change)",min_value=0.001, max_value=2, width=160, default_value=1,tag="grain_pitch")
                dpg.add_slider_float(label="Pitch Variation (%)",width=200, default_value=0, max_value = 100, tag="grain_pitch_var")
                
            # Cloud specification
            with dpg.collapsing_header(label="Cloud Specifications"):
                dpg.add_input_float(tag="cloud_density", label="Cloud Density (ms/sec)", width=200, default_value=5)
                dpg.add_slider_float(tag="cloud_density_var", label="Cloud Density Variation (%)",width=200, default_value=0, max_value = 100)

                dpg.add_slider_float(label="Cloud Center (% of input)", default_value=50, min_value = 1, max_value=99, width=200, callback=cloud_center, tag="center_slider")
                dpg.add_slider_float(label="Cloud Minimum", default_value=0, max_value=99, min_value = 0, width=200, callback=min_update, tag="min_slider")
                dpg.add_slider_float(label="Cloud Maximum", default_value=100, max_value=100, min_value = 1, width=200, callback=max_update, tag="max_slider")

            # Envelope specification
            with dpg.collapsing_header(label="Envelope Specifications"):
                with dpg.group(horizontal=True):
                    with dpg.group():
                        dpg.add_button(tag="default", label="Default", width=190, height=button_height, callback=update_envelope, user_data=(True, enabled, disabled,))
                        dpg.add_button(tag="triangle", label="Triangle", width=190, height=button_height,callback=update_envelope, user_data=(False, enabled, disabled,))
                        dpg.add_button(tag="bell", label="Bell", width=190, height=button_height,callback=update_envelope, user_data=(False, enabled, disabled,))
                        dpg.add_button(tag="untouched", label="Untouched", width=190, height=button_height,callback=update_envelope, user_data=(False, enabled, disabled,))
                        dpg.add_button(tag="complex", label="Complex", width=190, height = button_height, callback=update_envelope, user_data=(False, enabled, disabled,))
                    with dpg.plot(label='Envelope', height=141, width=215, tag="e_plot", no_mouse_pos=True):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, tag="ex_axis", no_tick_labels=True, no_tick_marks=True)
                        dpg.set_axis_limits("ex_axis", 0, 100)
                        dpg.add_plot_axis(dpg.mvYAxis, tag="ey_axis", no_tick_labels=True, no_tick_marks=True)
                        dpg.set_axis_limits("ey_axis", -0.25, 1.25)
                            
                        samples, indexes = prep_env_display()
                        dpg.add_line_series(indexes, samples,  parent="ex_axis", tag="e_line")

        with dpg.group():
            # input wave graph
            with dpg.child_window(height = 343):
                with dpg.group(horizontal=True):
                    dpg.add_button(tag="resize_in", label="Recenter Graph", width=140, callback=resize_in)
                    dpg.add_button(label="Fit Data", width=140, callback=lambda: dpg.fit_axis_data("y_axis"))
                with dpg.plot(no_mouse_pos=True, label='Input Sample', height=-1, width=-1, tag="input_plot"):
                    dpg.add_plot_legend()

                    samples, indexes = prep_display()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="y_axis")

                    dpg.add_line_series(indexes, samples, label="Audio Sample", parent="x_axis", tag="input_line")
                    
                    dpg.add_line_series([50, 50], [-1, 1], label="Cloud Center", parent="y_axis", tag="cloud_center")
                    dpg.add_line_series([0, 0], [-1, 1], label="Cloud Min", parent="y_axis", tag="cloud_min")
                    dpg.add_line_series([100, 100], [-1, 1], label="Cloud Max", parent="y_axis", tag="cloud_max")
            
            with dpg.child_window(height = 343):
                # output wave graph
                with dpg.group(horizontal=True):
                    dpg.add_button(tag="resize_out", label="Recenter Graph", width=140, callback=resize_out)
                    dpg.add_button(label="Fit Data", width=140, callback=lambda: dpg.fit_axis_data("oy_axis"))
                with dpg.plot(no_mouse_pos=True, label='Output Sample', height=-1, width=-1, tag="output_plot"):
                    dpg.add_plot_legend()

                    samples, indexes = prep_display()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="ox_axis")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="oy_axis")

                    dpg.add_line_series(indexes, samples, label="Audio Sample", parent="ox_axis", tag="output_line")
                    
                



    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    
dpg.bind_item_theme("default", enabled)
# Update the user_data associated with the button

dpg.create_viewport(title='Granular Synthesis', width=1200, height=750)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("GS", True)
dpg.start_dearpygui()
dpg.destroy_context()