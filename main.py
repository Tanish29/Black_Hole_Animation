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
# point = Entity(model='line', color=color.blue, scale = (1,1,1), position=(5,0,0))
# add bottom arcs/black hole's underside
bottomArcs = []
arcRadius = radius/1.5
# create n arcs
n = 200
for numArcs in range(n):
    # generates points
    vertices = []
    # loop through a set of possible y values of a circle
    for y in np.linspace(arcRadius, -arcRadius):
        x = np.sqrt((arcRadius**2) - (y)**2)
        # positive square root answer
        vertices.append([x, y, 0])
    # add negative square root answers
    for i in reversed(vertices.copy()):
        vertices.append([i[j]*-1 if j==0 else i[j] for j in range(len(i))])
    # convert to a tuple
    vertices = tuple([tuple(i) for i in vertices])
    bottomArcs.append(Entity(model=Mesh(vertices=vertices, mode='line'), color=color.orange, scale=1))
    # increase arc radius using a nonlinear spaced vector of numbers
    if numArcs != round(n/1.1):
        arcRadius += (n/10000)*(np.linspace(0,1,n)**2)[numArcs]
    else:
        # significantly increase arc radius to make it look more like a black hole
        arcRadius += 0.1

def rotate_sphere():
    # add sphere rotation; a black rotates on the axis of symmetry
    sphere.rotation_z += sphere.dz
    # sphere.rotate(value=np.array([1,1,1])*1e+35)
sphere.update = rotate_sphere

# make free view available
EditorCamera()

app.run()