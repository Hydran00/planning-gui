import PySimpleGUI as sg
import time
import os
import subprocess
import sys
print = sg.Print

def main():
    # os.system(". ~/shelfino_ws/install/setup.zsh")
    # sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
    layout = [  [sg.Text('Welcome to the best planning algorithm GUI ever written :)')],
                # [sg.Input(key='_IN_')],             # input field where you'll type command
                # [sg.Output(size=(60,15))],          # an output area where all print output will go
                [sg.Button('Launch Gazebo Simulation', key='sim', button_color=('white', 'green') ), sg.Button('Exit')] ]     # a couple of buttons

    window = sg.Window('Planning algorithm test', layout)

    env_running = False
    try:
        while True:             # Event Loop
            event, values = window.Read()
            if event in (None, 'Exit'):         # checks if user wants to exit
                if(env_running):
                    p.kill()
                print('Exiting')
                break
            if event == 'sim' and not env_running: # the two lines of code needed to get button and run command
                # cmd = "ros2 launch projects victims.launch.py"
                cmd = "cat tmp"
                # runCommand(cmd=values['_IN_'], window=window)
                p = p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                env_running = True
                window['sim'].update('Kill simulation')
                # window['sim'].update(disabled=True)
                window['sim'].update(button_color=('white', 'red'))
                print('Simulation launched')
                continue

            if event == 'sim' and env_running:
                p.kill()
                env_running = False
                window['sim'].update('Launch Gazebo Simulation')
                window['sim'].update(button_color=('white', 'green'))
                print('Simulation killed')
                continue
            
            if env_running:
                output = ''
                for line in p.stdout:
                    line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
                    output += line
                    print(line)
                    window.Refresh() if window else None        # yes, a 1-line if, so shoot me
            

        window.Close()
    except Exception as e:
        sg.popup_error_with_traceback(f'An error happened.  Here is the info:', e)

if __name__ == '__main__':
    main()