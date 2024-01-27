#! /usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from ament_index_python.packages import get_package_share_directory
from shapely import wkt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import time
import PySimpleGUI as sg
debug = sg.Print

PLAN_PATH = str(get_package_share_directory('planner')) + '/data/final_path.txt'
MAP_PATH = str(get_package_share_directory('planner')) + '/data/map.txt'

def update_figure(current_ax, current_fig):
    time.sleep(0.5)
    color = np.random.rand(3,)
    current_ax.plot(PLAN_PATH[2:,0], PLAN_PATH[2:,1], color=color, linewidth=2.0)
    current_fig.canvas.draw()
    return current_ax, current_fig

def plot_map_and_path():
    time.sleep(0.5)
    start = PLAN_PATH[0]
    end = PLAN_PATH[1]
    fig, ax = plt.subplots()
    geom = wkt.loads(open(MAP_PATH, 'r').read())
    xs, ys = geom.exterior.xy
    xs = np.array(xs)
    ys = np.array(ys)
    verts = np.array([xs, ys]).T
    polygon = Polygon(verts,closed=True, color='grey', edgecolor='k')
    ax.add_patch(polygon)
    for hole in geom.interiors:
        # plot holes for each polygon
        xh, yh = hole.xy
        xh = np.array(xh)
        yh = np.array(yh)
        verts = np.array([xh, yh]).T
        polygon = Polygon(verts,closed=True, color='k')
        ax.add_patch(polygon)
        # ax.plot(xh, yh, '-k', lw=4)

    ax.scatter(start[0], start[1], marker='o', color='green')
    ax.scatter(end[0], end[1], marker='o', color='red')
    ax.plot(PLAN_PATH[2:,0], PLAN_PATH[2:,1], 'b-', linewidth=2.0)
    ax.axis("equal")
    return ax, fig


if __name__ == "__main__":
    
    plot_map_and_path()