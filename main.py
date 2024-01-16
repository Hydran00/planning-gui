import time
import os
import subprocess
import sys
import numpy as np
import signal
import PySimpleGUI as sg
import psutil
from plotter import plot_map_and_path
from ament_index_python.packages import get_package_share_directory as share_dir


import matplotlib
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')


DEBUG_GRAPHICS = False  # wether to activate buttons effect or not
CMD_SIMULATION = "ros2 launch projects victims.launch.py"
CMD_PLANNER = "ros2 launch planner rrt_star_dubins.launch.py"

# sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
debug = sg.Print


def draw_figure(canvas):
    # plot map
    canvas.delete("all")
    figure = plot_map_and_path()
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')
    
def kill_gazebo():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "gzserver":
            print('Killing gzserver')
            proc.kill()
        if proc.name() == "gzclient":
            print('Killing gzclient')
            proc.kill()


def main():
    CMD_PLANNER = "ros2 launch planner rrt_star_dubins.launch.py"

    # os.system(". ~/shelfino_ws/install/setup.zsh")
    # sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
    layout = [[sg.Text('Select the planner and click "Launch Planner" ', key='title')],
              [sg.Canvas(key='-CANVAS-', size=(500, 400)),
               sg.Output(size=(15, 10))],          # an output area where all print output will go
              [sg.Button('Launch Gazebo Simulation', key='sim', button_color=(
                  'white', 'green')), sg.Button('Clear plots', key='clear', button_color=('white', 'red'), disabled=True),
               sg.Button('Exit'),],
              [sg.Text('Select Planner:'),
               sg.Drop(values=['RRT', 'RRT*', 'RRT* Dubins', 'Voronoi'],
                       key='dropdown', enable_events=True, default_value='RRT* Dubins'),
               sg.Button('Launch Planner', key='planner', button_color=('white', 'green'), disabled=False)]]    # a couple of buttons
    window = sg.Window('Planning algorithm test', layout, font='Helvetica 18')

    env_running = False
    waiting_result = False
    is_planning = False
    fig_canvas_agg = None
    try:
        while True:

            if waiting_result:
                while (not os.path.exists(share_dir('planner') + '/data/dubins_path.txt')):
                    pass
                fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas)
                waiting_result = False
                window['clear'].update(disabled=False)
                window.Refresh()

            event, values = window.Read()
            # Show planning results if available

            if event in (None, 'Exit'):         # checks if user wants to exit
                if (env_running):
                    os.killpg(os.getpgid(p0.pid), signal.SIGTERM)
                    kill_gazebo()
                if 'p2' in locals():
                    os.killpg(os.getpgid(p2.pid), signal.SIGTERM)
                print('Exiting')
                break
            # Planners selection:
            if event == 'clear':
                # clear canvas
                if fig_canvas_agg is not None:
                    delete_fig_agg(fig_canvas_agg)
                    window['clear'].update(disabled=True)
                
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
                        os.killpg(os.getpgid(p0.pid), signal.SIGTERM)
                    env_running = False
                    print('Simulation killed')
                    continue
            # Planner button
            if event == 'planner':
                if not is_planning:
                    # Launch planner
                    print('Launching planner')
                    if os.path.exists(share_dir('planner') + '/data/dubins_path.txt'):
                        os.remove(share_dir('planner') +
                                  '/data/dubins_path.txt')
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
                        os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
                    print('Planner killed')
                    waiting_result = False
                    is_planning = False
                    continue

        window.Close()
    except Exception as e:
        sg.popup_error_with_traceback(
            f'An error happened.  Here is the info:', e)
    # if env_running:
    #     p.kill()
    #     os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    if 'p1' in locals():
        os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
    if 'p2' in locals():
        os.killpg(os.getpgid(p2.pid), signal.SIGTERM)
    kill_gazebo()


if __name__ == '__main__':
    main()
