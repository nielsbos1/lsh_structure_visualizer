import dearpygui.dearpygui as dpg
import json
import numpy as np
import uuid

with open('parameter_config_final.json', 'r') as file_:
    list_configuration = json.load(file_)

thresholds = [x for x in {round(item['threshold'], 2) for item in list_configuration}]
num_perm = [x for x in {item['num_perm'] for item in list_configuration}]
amplified_two_stages = [x for x in {item['amplified'] for item in list_configuration}]
thresholds.sort()
num_perm.sort()
amplified_two_stages.sort()

# Write tag
with open('current_drawing_tag.txt', 'w') as file_:
    file_.write('starting_tag')



global current_drawing_tag
current_drawing_tag = None

def save_callback():
    print("Save Clicked")

dpg.create_context()


def retrieve_parameters(list_configuration):
    try:
        threshold = float(dpg.get_value('threshold'))
    except Exception:
        threshold = 0.05
    try:
        num_perm = int(dpg.get_value('num_perm'))
    except Exception:
        num_perm = 16
    try:
        amplified_two_stages = dpg.get_value('amplified')
        if amplified_two_stages == 'Amplified':
            amplified_two_stages = True
        else:
            amplified_two_stages = False
    except Exception:
        amplified_two_stages = True

    # get parameter values
    b, r = next(x['params'] for x in list_configuration if (abs(x['threshold'] - threshold) < 0.01
                                                            and x['num_perm'] == num_perm
                                                            and (x['amplified'] is amplified_two_stages)))
    return b, r

def get_plot_data(b, r):
    _probability = lambda s: 1 - (1 - (1 - (1 - s ** float(r[0])) ** float(b[0])) ** float(r[1])) ** float(b[1])

    # create data
    x_array = list(np.arange(start=0, stop=1 + 0.001, step=0.001))
    y_array = list(np.apply_along_axis(_probability, axis=0, arr=x_array))
    return x_array, y_array

def update_plot():
    b, r = retrieve_parameters(list_configuration)
    x_array, y_array = get_plot_data(b, r)
    dpg.set_value('s_curve', [x_array, y_array])
    dpg.set_item_label('s_curve', f"r_1={r[0]}, b_1={b[0]}, r_2={r[1]}, b_2={b[1]}")
    create_tree(b=b, r=r)


    return x_array, y_array

b, r = retrieve_parameters(list_configuration)
x_array, y_array = get_plot_data(b, r)

with dpg.window(label="Parameter value selector", tag='Primary Window', height=1020):
    dpg.add_text("Change the values!")
    with dpg.tab_bar(label='tabbar'):
        with dpg.tab(label="Threshold", tag="Threshold tab"):
            dpg.add_radio_button(items=thresholds, label='threshold', tag='threshold', callback=update_plot)
        with dpg.tab(tag='num_perm_tab', label="Sketch length"):
            dpg.add_radio_button(items=num_perm, label='num_perm', tag='num_perm',  callback=update_plot)
        with dpg.tab(tag='amplified_tab', label="Amplified"):
            dpg.add_radio_button(items=['Amplified', 'Not amplified'], label='amplified', tag='amplified', callback=update_plot)

    with dpg.plot(label="Line Series", height=550, width=550):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")

        # series belong to a y axis
        dpg.add_line_series(x_array, y_array, label=f"b_1={b[0]}, b_2={b[1]}, r_1={r[0]}, r_2={r[1]}", parent="y_axis", tag="s_curve")

def create_tree(b, r):
    with open('current_drawing_tag.txt', 'r') as file_:
        current_drawing_tag = file_.readline()
    if current_drawing_tag == 'starting_tag':
        # do not delete
        pass
    else:
        dpg.delete_item(item=current_drawing_tag)
    tag_of_drawlist = str(uuid.uuid4())
    current_drawing_tag = tag_of_drawlist

    # Write tag
    with open('current_drawing_tag.txt', 'w') as file_:
        file_.write(current_drawing_tag)

    total_lines = b[0] * b[1] * r[0] * r[1]
    if total_lines <= 16:
        internal_dist = 15
        external_dist = 15
        group_dist = 40
    elif total_lines <= 32:
        internal_dist = 12
        external_dist = 12
        group_dist = 30
    elif total_lines <= 64:
        internal_dist = 10
        external_dist = 10
        group_dist = 25
    elif total_lines <= 128:
        internal_dist = 8
        external_dist = 8
        group_dist = 20
    elif total_lines <= 1024:
        internal_dist = 6
        external_dist = 6
        group_dist = 15

    with dpg.window(label="(Amplified) LSH structure", tag=current_drawing_tag, pos=(560,0)):
        dpg.add_drawlist(width=5000, height=15000)
        start_coordinates = (10, 10)
        # Take into account second layer
        for b_2 in range(b[1]):
            for r_2 in range(r[1]):
                for j in range(0, b[0]):
                    # draw in first layer one band of rows
                    for i in range(0, r[0]):
                        start_line = (start_coordinates[0], start_coordinates[1] + (i + j * r[0]) * internal_dist + j * external_dist)
                        end_line = (start_coordinates[0] + 50, start_coordinates[1] + (i + j * r[0]) * internal_dist + j * external_dist)
                        #print((start_line, end_line))
                        dpg.draw_line(start_line, end_line, color=(255, 0, 0, 255), thickness=1, parent=tag_of_drawlist)
                    # draw connecting line between bands
                    start_vertical_line = (start_coordinates[0] + 50, start_coordinates[1] + j * r[0] * internal_dist + j * external_dist)
                    end_vertical_line = (start_coordinates[0] + 50, start_coordinates[1] + (r[0] - 1 + j * r[0]) * internal_dist + j * external_dist)
                    dpg.draw_line(start_vertical_line, end_vertical_line, color=(255, 0, 0, 255), thickness=1, parent=tag_of_drawlist)
                    middle_vertical_line = (start_coordinates[0] + 50, start_coordinates[1] + ((r[0] - 1) / 2 + j * r[0]) * internal_dist + j * external_dist)
                    end_middle_vertical_line = (start_coordinates[0] + 100, start_coordinates[1] + ((r[0] - 1) / 2 + j * r[0]) * internal_dist + j * external_dist)
                    # print(middle_vertical_line, end_middle_vertical_line)
                    dpg.draw_line(middle_vertical_line, end_middle_vertical_line, color=(0, 200, 255), thickness=1, parent=tag_of_drawlist)
                    if j == 0:
                        start_second_vertical_line = end_middle_vertical_line
                    if j == b[0] - 1:
                        end_second_vertical_line = end_middle_vertical_line
                        start_coordinates = (10, end_line[1] + group_dist)
                dpg.draw_line(start_second_vertical_line, end_second_vertical_line, color=(0, 200, 255), thickness=1, parent=tag_of_drawlist)
                start_third_horizontal_line = (start_second_vertical_line[0], (start_second_vertical_line[1] + end_second_vertical_line[1])/ 2)
                end_third_horizontal_line = (start_third_horizontal_line[0] + 50, start_third_horizontal_line[1])
                dpg.draw_line(start_third_horizontal_line, end_third_horizontal_line, color=(255, 0, 0, 255), thickness=1, parent=tag_of_drawlist)
                end_third_vertical_line = None
                if r_2 == 0:
                    start_third_vertical_line = end_third_horizontal_line
                if r_2 == r[1] - 1:
                    end_third_vertical_line = end_third_horizontal_line
            dpg.draw_line(start_third_vertical_line, end_third_vertical_line, color=(255, 0, 0, 255), thickness=1, parent=tag_of_drawlist)
            start_middle_third_vertical_line = (start_third_vertical_line[0], (start_third_vertical_line[1] + end_third_vertical_line[1]) / 2)
            end_middle_third_vertical_line = (start_third_vertical_line[0] + 50, (start_third_vertical_line[1] + end_third_vertical_line[1]) / 2)
            dpg.draw_line(start_middle_third_vertical_line, end_middle_third_vertical_line, color=(0, 200, 255), thickness=1, parent=tag_of_drawlist)
            if b_2 == 0:
               start_fourth_vertical_line =  end_middle_third_vertical_line
            if b_2 == b[1] - 1:
                end_fourth_vertical_line = end_middle_third_vertical_line
        dpg.draw_line(start_fourth_vertical_line, end_fourth_vertical_line, color=(0, 200, 255), thickness=1, parent=tag_of_drawlist)
dpg.create_viewport(title='Visualization of LSH structures', width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()