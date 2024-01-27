import os
import sys
import signal
import subprocess
import psutil
import time

import numpy as np
import PySimpleGUI as sg
from plotter import plot_map_and_path, update_figure
from ament_index_python.packages import get_package_share_directory as share_dir


import matplotlib
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')


DEBUG_GRAPHICS = False  # wether to activate buttons effect or not
CMD_SIMULATION = "ros2 launch projects victims.launch.py"

# sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
debug = sg.Print



def draw_figure(canvas):
    # plot map
    canvas.delete("all")
    current_ax, current_fig  = plot_map_and_path()
    figure_canvas_agg = FigureCanvasTkAgg(current_fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return current_ax,current_fig, figure_canvas_agg

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')
    
def kill_gazebo():
    for proc in psutil.process_iter():
        # check whether the process name matches
        # if proc.name() == "gzserver":
        #     print('Killing gzserver')
        #     proc.kill()
        # if proc.name() == "gzclient":
        #     print('Killing gzclient')
        #     proc.kill()
        pass

def main():
    CMD_PLANNER = "ros2 launch planner rrt_star_dubins.launch.py"
    def kill_process(p):
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            kill_gazebo()

    def signal_handler(sig, frame):
        if 'p0' in locals():
            kill_process(p0)
            kill_gazebo()
        if 'p1' in locals():
            kill_process(p1)
        kill_gazebo()
        sys.exit(0)
    
    # intercept ctrl+c
    signal.signal(signal.SIGINT, signal_handler) 
       
    layout = [[sg.Text('Select the planner and click "Launch Planner". \n' +
                       'Your ros workspace must be sourced in this terminal!', key='title')],
              [sg.Canvas(key='-CANVAS-', size=(1000, 800)),
               sg.Output(size=(15, 10))],          # an output area where all print output will go
              [sg.Button('Launch Gazebo Simulation', key='sim', button_color=(
                  'white', 'green')), sg.Button('Clear plots', key='clear', button_color=('white', 'red'), disabled=True),
               sg.Button('Exit'),],
              [sg.Text('Select Planner:'),
               sg.Drop(values=['RRT', 'RRT*', 'RRT* Dubins', 'Voronoi'],
                       key='dropdown', enable_events=True),
               sg.Button('Launch Planner', key='planner', button_color=('white', 'green'), disabled=True)]]    # a couple of buttons
    window = sg.Window('Planning algorithm test', layout, font='Helvetica 18',icon="ico.png")

    env_running = False
    waiting_result = False
    is_planning = False
    fig_canvas_agg = None
    first_map_plot = True
    try:
        while True:

            if waiting_result:
                if first_map_plot:
                    while (not os.path.exists(share_dir('planner') + '/data/final_path.txt')):
                        pass
                    current_ax, current_fig, fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas)
                    waiting_result = False
                    window['clear'].update(disabled=False)
                    first_map_plot = False
                else:
                    while (not os.path.exists(share_dir('planner') + '/data/final_path.txt')):
                        pass
                    current_ax,current_fig = update_figure(current_ax, current_fig)
                    waiting_result = False
                    
            event, values = window.Read()
            # Show planning results if available

            if event in (None, 'Exit'):         # checks if user wants to exit
                if (env_running):
                    kill_process(p0)
                    kill_gazebo()
                if 'p1' in locals():
                    kill_process(p1)
                print('Exiting')
                break
            # Planners selection:
            if event == 'clear':
                # clear canvas
                if fig_canvas_agg is not None:
                    delete_fig_agg(fig_canvas_agg)
                    window['clear'].update(disabled=True)
                    first_map_plot = True
                
            if event == 'dropdown':
                print("Planner selected: " + str(values['dropdown']))
                window['planner'].update(disabled=False)
                if values['dropdown'] == 'RRT':
                    CMD_PLANNER = "ros2 launch planner rrt.launch.py"
                elif values['dropdown'] == 'RRT*':
                    CMD_PLANNER = "ros2 launch planner rrt_star.launch.py"
                elif values['dropdown'] == 'RRT* Dubins':
                    CMD_PLANNER = "ros2 launch planner rrt_star_dubins.launch.py"
                else:
                    CMD_PLANNER = "ros2 launch planner voronoi.launch.py"
                continue
            # Simulation button
            if event == 'sim':
                # Launch simulation
                if not env_running:
                    if not DEBUG_GRAPHICS:
                        p0 = subprocess.Popen(
                            CMD_SIMULATION, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
                    window['sim'].update('    Kill simulation           ')
                    window['sim'].update(button_color=('white', 'red'))
                    env_running = True
                    print('Simulation launched')
                    continue
                # Kill simulation
                else:
                    window['sim'].update('Launch Gazebo Simulation')
                    window['sim'].update(button_color=('white', 'green'))
                    kill_gazebo()
                    if not DEBUG_GRAPHICS:
                        kill_process(p0)
                    env_running = False
                    # clear canvas
                    if fig_canvas_agg is not None:
                        delete_fig_agg(fig_canvas_agg)
                        window['clear'].update(disabled=True)
                        first_map_plot = True
                    print('Simulation killed')
                    continue
            # Planner button
            if event == 'planner':
                if not is_planning:
                    # Launch planner
                    print('Launching planner')
                    if os.path.exists(share_dir('planner') + '/data/final_path.txt'):
                        os.remove(share_dir('planner') +
                                  '/data/final_path.txt')
                    window['planner'].update('Kill planner')
                    window['planner'].update(button_color=('white', 'red'))
                    if not DEBUG_GRAPHICS:
                        p1 = subprocess.Popen(
                            CMD_PLANNER, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)

                    print('Planner launched')
                    waiting_result = True
                    is_planning = True

                else:
                    # Kill planner
                    window['planner'].update('Launch Planner')
                    window['planner'].update(button_color=('white', 'green'))
                    if not DEBUG_GRAPHICS:
                        kill_process(p1)
                    print('Planner killed')
                    waiting_result = False
                    is_planning = False
                    continue

        window.Close()
    except Exception as e:
        if 'p0' in locals():
            kill_process(p0)
            kill_gazebo()
        if 'p1' in locals():
            kill_process(p1)
        sg.popup_error_with_traceback(
            f'An error happened.  Here is the info:', e)
    # if env_running:
    #     p.kill()
    #     os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    if 'p0' in locals():
        kill_process(p0)
        kill_gazebo()
    if 'p1' in locals():
        kill_process(p1)


if __name__ == '__main__':
    main()
