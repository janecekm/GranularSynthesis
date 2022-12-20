# https://dearpygui.readthedocs.io/en/latest/documentation/node-editor.html

import dearpygui.dearpygui as dpg
import functionality as f 
#import granularSynthesis as gs

global editor
dpg.create_context()

def link_callback(sender, app_data):
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

def delink_callback(sender, app_data):
    dpg.delete_item(app_data)

def add_node():
    # dpg.add_node(label="dare i say....
    
    with editor:
        with dpg.node(label="Sexy"):
            with dpg.node_attribute(label="Sexyyyy"):
                dpg.add_input_float(label="Duration (s)", width=200, default_value=1)
    

with dpg.window(tag="Tutorial",label="Tutorial", width=800, height=200):
    make_sound = dpg.add_button(label="Make Sound", tag="make_sound", callback=f.some_stuff)
    editor = dpg.node_editor(tag="editor", callback=link_callback, delink_callback=delink_callback)
    make_node = dpg.add_button(label="Add Node", tag="add_node", callback=add_node)
    with editor:
        with dpg.node(label="Output"):
            with dpg.node_attribute(label="Output"):
                dpg.add_slider_float(label="Volume", width=200, default_value=11, max_value=11)
                dpg.add_input_float(label="Duration (s)", width=200, default_value=1)



dpg.create_viewport(title='Granular Synthesis', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Tutorial", True)
dpg.start_dearpygui()






