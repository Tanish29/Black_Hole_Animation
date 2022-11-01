from ursina import *

# create app
app = Ursina()

# create a sphere
sphere_scale = tuple(i*5 for i in (1,1,1))
sphere = Entity(model='sphere', color=color.black, scale=sphere_scale, position=(0,0,0))

# make free view available
EditorCamera()

app.run()