from panda3d.core import loadPrcFile
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter, GeomNode, NodePath
import numpy as np

# load config file
loadPrcFile("config/conf.prc")

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        # create a GeomVertexData object
        vertex_data = GeomVertexData('sphere', GeomVertexFormat().getV3n3c4(), Geom.UHDynamic)

        # create Geom Vertex Writers
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')
        normal_writer = GeomVertexWriter(vertex_data, 'normal')
        color_writer = GeomVertexWriter(vertex_data, 'color')

        # set sphere properties
        radius = 5
        slices = 16
        stacks = 16

        # generate vertices based on the above properties
        for i in range(stacks+1):
            # calculate angle in the y-z plane for a full circle
            phi = np.pi * (i/stacks)
            # calculate z cartesian coordinate
            z = radius * np.sin(phi)
            for j in range(slices+1):
                # calculate angle in the x-y plane
                theta = np.pi * (j/slices)
                # calculate x and y, remember rcos(theta) is the stack radius
                x = (radius*np.cos(phi))*np.cos(theta)
                y = (radius*np.cos(phi))*np.sin(theta)
                # add vertiex and normal
                print('x,y,z=',x,y,z)
                vertex_writer.addData3f(x,y,z)
                normal_writer.addData3f(x,y,z)

        # set sphere color
        color_writer.addData4f(1,0,0,1)

        # create a geom object
        sphereGeom = Geom(vertex_data)

        # create a geomNode
        sphereNode = GeomNode('sphere')
        sphereNode.addGeom(sphereGeom)

        # create a node path and put it in scene graph
        sphereNodePath = NodePath(sphereNode)
        sphereNodePath.reparentTo(self.render)


inst1 = MyGame()
inst1.run()