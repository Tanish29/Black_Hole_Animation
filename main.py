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
sphere_scale = tuple(i*5 for i in (1,1,1))
sphere = Entity(model='sphere', color=color.black, scale=sphere_scale, position=(0,0,0), dz=1e+35)
# square = Entity(model='quad', color=color.red, scale=sphere_scale, position=(0,0,0))
# create photon ring
circle = Entity(model='circle', color=color.rgba(243,216,192,100), scale=tuple(i+0.05 for i in sphere_scale), position=(0,0,0))
# add lines
# line = Entity(model='line', color=color.orange, scale=(8,8), position=(0,-3))
# generate vertices
vertices = []
for y in np.linspace(0,5):
    x = np.sqrt(25-(y**2))
    # positive square root answer
    vertices.append([x, y, 0])

# add negative square root answers

for i in reversed(vertices.copy()):
    vertices.append([i[j]*-1 if j==0 else i[j] for j in range(len(i))])
# vertices.append([[i[j]*-1 if j==0 else i[j] for j in range(len(i))] for i in vertices])
# vertices[-1] = vertices[-1][0]
# convert to a tuple
vertices = tuple([tuple(i) for i in vertices])
line = Entity(model=Mesh(vertices=vertices, mode='line'), color=color.orange, scale=1)

def rotate_sphere():
    # add sphere rotation; a black rotates on the axis of symmetry
    sphere.rotation_z += sphere.dz
    # sphere.rotate(value=np.array([1,1,1])*1e+35)
sphere.update = rotate_sphere

# make free view available
EditorCamera()

app.run()