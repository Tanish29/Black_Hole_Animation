from ursina import *
import numpy as np

''' Script below creates an animation of a rotating black hole
Note: s
'sphere' refers to as the black hole
'''

# create app
app = Ursina()

# create a sphere
sphere_scale = tuple(i*5 for i in (1,1,1))
sphere = Entity(model='sphere', color=color.black, scale=sphere_scale, position=(0,0,0), dz=1e+35)
square = Entity(model='quad', color=color.red, scale=sphere_scale, position=(0,0,0))

def update():
    # add sphere rotation; a black rotates on the axis of symmetry
    sphere.rotation_z += sphere.dz
    # sphere.rotate(value=np.array([1,1,1])*1e+35)

# make free view available
EditorCamera()

app.run()