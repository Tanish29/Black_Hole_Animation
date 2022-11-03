from ursina import *
import numpy as np

''' Script below creates an animation of a rotating black hole
Note: 
'sphere' refers to as the black hole
'''

# create app
app = Ursina()

# set background color
window.color = color.black

# create a sphere
radius = 5 # scale factor
sphere_scale = tuple(i*radius for i in (1,1,1))
sphere = Entity(model='sphere', color=color.black, scale=sphere_scale, position=(0,0,0), dz=1e+35)
# create photon ring
circle = Entity(model='circle', color=color.rgba(243,216,192,100), scale=tuple(i+0.05 for i in sphere_scale), position=(0,0,0))
# add bottom arcs/black hole's underside
bottomArcs = []
arcRadius = radius
# create 10 arcs
for numArcs in range(50):
    # generates points
    vertices = []
    # loop through a set of possible y values of a circle
    for y in np.linspace(0, -arcRadius):
        x = np.sqrt((arcRadius**2) - (y)**2)
        # positive square root answer
        vertices.append([x, y, 0])
    # add negative square root answers
    for i in reversed(vertices.copy()):
        vertices.append([i[j]*-1 if j==0 else i[j] for j in range(len(i))])
    # convert to a tuple
    vertices = tuple([tuple(i) for i in vertices])
    bottomArcs.append(Entity(model=Mesh(vertices=vertices, mode='line'), color=color.orange, scale=1))
    # increase arc radius
    arcRadius += 0.1

def rotate_sphere():
    # add sphere rotation; a black rotates on the axis of symmetry
    sphere.rotation_z += sphere.dz
    # sphere.rotate(value=np.array([1,1,1])*1e+35)
sphere.update = rotate_sphere

# make free view available
EditorCamera()

app.run()