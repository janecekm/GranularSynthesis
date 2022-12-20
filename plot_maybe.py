import dearpygui.dearpygui as dpg
data_x=[0:10]
data_y=[0:10]
dpg.create_context()
with dpg.window(label='Tutorial', tag='win',width=800, height=600):

    with dpg.plot(label='Line Series', height=-1, width=-1):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes, set to auto scale.
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis')
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis')


        # series belong to a y axis. Note the tag name is used in the update
        # function update_data
        dpg.add_line_series(x=list(data_x),y=list(data_y), 
                            label='Temp', parent='y_axis', 
                            tag='series_tag')