import time
import os
import subprocess
import sys
import numpy as np
import signal
import PySimpleGUI as sg
import psutil
from plotter import plot_map_and_path

import matplotlib
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')


DEBUG_GRAPHICS = False
CMD_SIMULATION = "ros2 launch projects victims.launch.py"
CMD_PLANNER = "ros2 launch planner rrt_star_dubins.launch.py"

# sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
debug = sg.Print


def draw_figure(canvas):
    figure = plot_map_and_path()
    # plot map
    
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


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
    # os.system(". ~/shelfino_ws/install/setup.zsh")
    # sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
    layout = [[sg.Text('Select the planner and click "Launch Planner" ', key='title')],
              [sg.Canvas(key='-CANVAS-', size=(500, 400)),
               sg.Output(size=(15, 10))],          # an output area where all print output will go
              [sg.Button('Launch Gazebo Simulation', key='sim', button_color=(
                  'white', 'green')), sg.Button('Exit')],   # a couple of buttons
              [sg.Text('Select Planner:'),
               sg.Drop(values=['RRT', 'RRT*', 'RRT* Dubins', 'Voronoi'], key='dropdown', enable_events=True),
               sg.Button('Launch Planner', key='planner', button_color=('white', 'green'), disabled=True)]]    # a couple of buttons
    window = sg.Window('Planning algorithm test', layout, font='Helvetica 18')

    env_running = False
    already_showed = False
    try:
        while True:             # Event Loop
            event, values = window.Read()

            # if env_running:
            #     output = ''
            #     print('Reading output')
            #     i = 0
            #     for line in p.stdout.readlines():
            #         line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
            #         output += line
            #         # debug(line)
            #         # debug(i)
            #         sg.Print(line, do_not_reroute_stdout=False)
            #         # sys.stdout.flush()
            #         i += 1
            #         if i>2:
            #             break
            # for stdout_line in iter(popen.stdout.readline, ""):
            #     yield stdout_line
            # popen.stdout.close()

            if event in (None, 'Exit'):         # checks if user wants to exit
                if (env_running):
                    os.killpg(os.getpgid(p0.pid), signal.SIGTERM)
                    os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
                    kill_gazebo()
                print('Exiting')
                break
            
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

            if event == 'sim':
                if not env_running:
                    if not DEBUG_GRAPHICS:
                        p0 = subprocess.Popen(
                            CMD_SIMULATION, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
                    window['sim'].update('    Kill simulation           ')
                    window['sim'].update(button_color=('white', 'red'))
                    env_running = True
                    print('Simulation launched')
                    continue
                else:
                    window['sim'].update('Launch Gazebo Simulation')
                    window['sim'].update(button_color=('white', 'green'))
                    kill_gazebo()
                    if not DEBUG_GRAPHICS:
                        os.killpg(os.getpgid(p0.pid), signal.SIGTERM)
                    env_running = False
                    print('Simulation killed')
                    continue

            if event == 'planner':
                if not already_showed:
                    print('Launching planner')
                    window['planner'].update('Kill planner')
                    window['planner'].update(button_color=('white', 'red'))
                    if not DEBUG_GRAPHICS:
                        p1 = subprocess.Popen(
                            CMD_PLANNER, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)

                    print('Planner launched')
                    # fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
                    # t = np.arange(0, 3, .01)
                    # fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
                    time.sleep(10)
                    fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas)
                    already_showed = True

                    # window.Refresh() if window else None        # yes, a 1-line if, so shoot me
                else:
                    window['planner'].update('Launch Planner')
                    window['planner'].update(button_color=('white', 'green'))
                    if not DEBUG_GRAPHICS:
                        os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
                    already_showed = False
                    print('Planner killed')
                    already_showed = False
                    continue

        window.Close()
    except Exception as e:
        sg.popup_error_with_traceback(
            f'An error happened.  Here is the info:', e)
    # if env_running:
    #     p.kill()
    #     os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    kill_gazebo()


if __name__ == '__main__':
    main()
