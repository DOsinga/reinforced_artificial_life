import math
import numpy as np

# The number of looking/moving directions
SLICES = 12

def cart2pol(x, y):
    """Converts coords to angle and distance. Angle origin is at negative x-axis"""
    phi = np.pi-np.arctan2(y, x)
    dist = np.sqrt(x**2 + y**2)
    return(phi, dist)

def pol2cart(phi, dist):
    """Converts angle and distance to cathesian coords. Angle origin is at negative x-axis"""
    x = dist * np.cos(np.pi-phi)
    y = dist * np.sin(np.pi-phi)
    return(x, y)

def cart2slice(x, y, max_slices):
    """Converts coords to slice index based on max_angles pie slices. Angle origin is at negative x-axis"""
    phi, dist = cart2pol( x,y )
    return math.floor(phi / 2 / np.pi * max_slices)

def slice2pol( slice, max_slices ):
    """Returns the angle of a slice when the circle is split into max_slices slices"""
    return (slice+0.5) / max_slices * 2 * np.pi

def slice2cart( slice, max_slices, dist ):
    """Returns dx,dy based on a slice and a distance"""
    phi = (slice+0.5) / max_slices * 2 * np.pi
    return pol2cart(phi, dist )
