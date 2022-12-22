import dearpygui.dearpygui as dpg
import math
import time
import collections
import threading
import pdb

#https://www.reddit.com/r/DearPyGui/comments/t8bq2h/how_to_make_a_graph_autoadjust_to_show_newly/

nsamples = 100 #make number of samples as a parameter in the gui

global data_y
global data_x

#circular buffers to hold our indexes/samples
data_y = [0.0] * nsamples
data_x = [0.0] * nsamples

def update_data():
    sample = 1
    t0 = time.time()
    frequency=1.0
    while True: #adjust to while next index of samples is not empty

        t = time.time() - t0 #change time to be a counter to equal the index of the sample table
        y = math.sin(2.0 * math.pi * frequency * t) #y to be the value of the audio at the sample table
        data_x.append(t)
        data_y.append(y)
        
        #set the series x and y to the last nsamples
        dpg.set_value('series_tag', [list(data_x[-nsamples:]), list(data_y[-nsamples:])])          
        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')
        
        time.sleep(0.01)
        sample=sample+1
           


dpg.create_context()
with dpg.window(label='Tutorial', tag='win',width=800, height=600):

    with dpg.plot(label='Line Series', height=-1, width=-1):

        # REQUIRED: create x and y axes, set to auto scale.
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis')
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis')


        # series belong to a y axis. Note the tag name is used in the update
        # function update_data
        dpg.add_line_series(x=list(data_x),y=list(data_y), 
                            label='Temp', parent='y_axis', 
                            tag='series_tag')
        
            
                            
dpg.create_viewport(title='Custom Title', width=850, height=640)

dpg.setup_dearpygui()
dpg.show_viewport()

thread = threading.Thread(target=update_data)
thread.start()
dpg.start_dearpygui()

dpg.destroy_context()