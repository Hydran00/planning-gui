#! /usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from ament_index_python.packages import get_package_share_directory
from shapely import wkt

def plot_map_and_path():
    # clear current figure
    # plt.clf()
    path = np.loadtxt(str(get_package_share_directory('planner')) + '/data/dubins_path.txt', delimiter=',')
    start = path[0]
    end = path[1]
    fig, ax = plt.subplots()
    map_path = str(get_package_share_directory('planner')) + '/data/map.txt'
    geom = wkt.loads(open(map_path, 'r').read())
    xs, ys = geom.exterior.xy
    ax.plot(xs, ys, '-ok', lw=4)
    for hole in geom.interiors:
        # plot holes for each polygon
        xh, yh = hole.xy
        ax.plot(xh, yh, '-ok', lw=4)
        # plot the voronoi edges
    ax.scatter(start[0], start[1], marker='o', color='green')
    ax.scatter(end[0], end[1], marker='o', color='red')
    ax.plot(path[2:,0], path[2:,1], 'b-', linewidth=2.0)
    ax.axis("equal")
    return fig
    # plt.show()


if __name__ == "__main__":
    plot_map_and_path()