from panda3d.core import loadPrcFile
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter, GeomNode, NodePath
from panda3d.core import Vec3
import numpy as np

# load config file
loadPrcFile("config/conf.prc")

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        # create a GeomVertexData object
        vertex_data = GeomVertexData('sphere', GeomVertexFormat().getV3n3c4(), Geom.UHStatic)

        # create Geom Vertex Writers
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')
        normal_writer = GeomVertexWriter(vertex_data, 'normal')
        color_writer = GeomVertexWriter(vertex_data, 'color')

        # set sphere properties
        radius = 5
        slices = 50
        stacks = 50

        # generate vertices based on the above properties
        for i in range(stacks+1):
            # calculate angle in the y-z plane for a full circle
            phi = (2*np.pi) * (i/stacks)
            # calculate z cartesian coordinate
            z = radius * np.sin(phi)
            for j in range(slices+1):
                # calculate angle in the x-y plane
                theta = (2*np.pi) * (j/slices)
                # calculate x and y, remember rcos(theta) is the stack radius
                x = (radius*np.cos(phi))*np.cos(theta)
                y = (radius*np.cos(phi))*np.sin(theta)
                # add vertex and normal
                vertex_writer.addData3f(x,y,z)
                normal_writer.addData3f(x,y,z)
                # set sphere color
                color_writer.addData4f(0,0,0,1)

        # Create the triangles
        triangles = GeomTriangles(Geom.UHStatic)
        for i in range(stacks):
            for j in range(slices):
                # stack index
                K1 = i*(slices+1) + j
                # next stack index
                K2 = (i+1)*(slices+1) + j
                # next slice index
                K1_1 = i*(slices+1) + (j+1)
                # next slice and stack index
                K2_1 = (i+1)*(slices+1) + (j+1)
                triangles.addVertices(K1,K2,K1_1)
                triangles.addVertices(K1_1,K2,K2_1)


        # create a geom object
        sphereGeom = Geom(vertex_data)
        sphereGeom.addPrimitive(triangles)

        # create a geom node
        sphereNode = GeomNode('sphere')
        sphereNode.addGeom(sphereGeom)

        # create a node path and put it in scene graph
        sphereNodePath = NodePath(sphereNode)
        sphereNodePath.setPos(0,30,0)
        sphereNodePath.reparentTo(self.render)

        # load a model
        box = self.loader.loadModel("models/box")
        box.setPos(0,10,0)
        box.reparentTo(self.render)


inst1 = MyGame()
inst1.run()