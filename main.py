import dearpygui.dearpygui as dpg
from tkinter import filedialog as fd

# GUI documentation:    https://dearpygui.readthedocs.io/en/latest/index.html
# File Selection:       https://dearpygui.readthedocs.io/en/latest/documentation/file-directory-selector.html

# for input file name
global fname
fname = ''
global text
global buttons

# for envelope
global envelope
envelope = 1
envs = ["default","triangle","bell","untouched","complex"]

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
    fname = fd.askopenfilename(filetypes=(("Audio Files", ".wav"),   ("All Files", "*.*")))
    dpg.set_value(text,"File Name: "+fname)

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

with dpg.theme() as enabled:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button,(42,91,128), category=dpg.mvThemeCat_Core)

with dpg.theme() as disabled:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button,(51,51,55), category=dpg.mvThemeCat_Core)

with dpg.window(tag="GS", label="GS", width=800, height=300):
    # Input file selection
    dpg.add_button(label="Select File", callback=select_file)
    text = dpg.add_text("File Name: "+fname)
    
    dpg.add_input_float(label="Grain Duration (ms)", width=200, default_value=50)
    dpg.add_slider_float(label="Grain Duration Variation",width=200, default_value=0, max_value = 100)
    
    dpg.add_input_float(label="Cloud Density (ms/sec)", width=200, default_value=50)
    dpg.add_slider_float(label="Cloud Density Variation",width=200, default_value=0, max_value = 100)

    env_text = dpg.add_text("Envelope type: Default")
    with dpg.group(horizontal=True):
        dpg.add_button(tag="default", label="Default", width=70, callback=update_envelope, user_data=(True, enabled, disabled,))
        dpg.add_button(tag="triangle", label="Triangle", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        dpg.add_button(tag="bell", label="Bell", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        dpg.add_button(tag="untouched", label="Untouched", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        dpg.add_button(tag="complex", label="Complex", width=70, callback=update_envelope, user_data=(False, enabled, disabled,))
        
    dpg.add_slider_float(label="Cloud Center (% of input)", default_value=50, max_value=100, width=200)
    dpg.add_slider_float(label="Cloud Size (% of input)", default_value=100, max_value=100, width=200)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    
dpg.bind_item_theme("default", enabled)
# Update the user_data associated with the button

dpg.create_viewport(title='Granular Synthesis', width=500, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("GS", True)
dpg.start_dearpygui()
