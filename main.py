import dearpygui.dearpygui as dpg

# GUI documentation:    https://dearpygui.readthedocs.io/en/latest/index.html
# File Selection:       https://dearpygui.readthedocs.io/en/latest/documentation/file-directory-selector.html

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

# below replaces, start_dearpygui()
dpg.create_context()

with dpg.window(tag="GS", label="GS", width=800, height=300):
    with dpg.group(horizontal=True):
        dpg.add_button(label="lol")
        dpg.add_button(label="asdfasdf")
    dpg.add_file_dialog(directory_selector=True, show=False, callback=callback, tag="file_dialog_id",cancel_callback=cancel_callback)
    dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog_id"))

    dpg.add_button(label="Save", callback=save_callback)

    dpg.add_slider_float(label="Volume", default_value=3, max_value=11)


    #Generate graph
    


    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

dpg.create_viewport(title='Granular Synthesis', width=800, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("GS", True)
dpg.start_dearpygui()