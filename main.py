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
circle = Entity(model=Circle(resolution=50, radius=radius/2, mode="line", thickness=4),
                color=color.rgb(255,252,236),
                position=(0,0,0))
# add bottom arcs/black hole's underside
bottomArcs = []
arcRadius = radius/1.5
# create n arcs
n = 200
for numArcs in range(n):
    # generates points
    vertices = []
    # loop through a set of possible y values of a circle
    for y in np.linspace(arcRadius, -arcRadius, 2000):
        x = np.sqrt((arcRadius**2) - (y)**2)
        # positive square root answer
        vertices.append([x, y, 0])
    # add negative square root answers
    for i in reversed(vertices.copy()):
        vertices.append([i[j]*-1 if j==0 else i[j] for j in range(len(i))])
    # convert to a tuple
    vertices = tuple([tuple(i) for i in vertices])
    bottomArcs.append(Entity(model=Mesh(vertices=vertices, mode='line'), color=color.rgba(np.linspace(255,237,n)[numArcs],
                                                                                          np.linspace(252,130,n)[numArcs],
                                                                                          np.linspace(236,54,n)[numArcs],
                                                                                          np.linspace(255,120,n)[numArcs])))
    # if you want just a circle (not an arc) use code below
    # bottomArcs.append(Entity(model=Circle(resolution=1000, radius=arcRadius, mode="line", thickness=4),
    #                                 color=color.rgba(np.linspace(255,237,n)[numArcs],
    #                                                  np.linspace(252,130,n)[numArcs],
    #                                                  np.linspace(236,54,n)[numArcs],
    #                                                  255-numArcs),
    #                                 position=(0,0,0)))
    # increase arc radius using a nonlinear spaced vector of numbers
    if numArcs != round(n/1.1):
        arcRadius += (n/10000)*(np.linspace(0,1,n)**2)[numArcs]
    else:
        # significantly increase arc radius to make it look more like a black hole
        arcRadius += 0.08


def update():
    ''' update entities/models

    :return: None
    '''
    # add sphere rotation; a black rotates on the axis of symmetry
    sphere.rotation_z += sphere.dz
    # sphere.rotate(value=np.array([1,1,1])*sphere.dz)
    for bEntity in bottomArcs:
        bEntity.rotation_z += 1

# make free view available
EditorCamera()

app.run()