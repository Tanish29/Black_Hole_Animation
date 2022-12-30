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
        vertex_data = GeomVertexData('sphere', GeomVertexFormat().getV3c4(), Geom.UHDynamic)

        # create Geom Vertex Writers
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')
        color_writer = GeomVertexWriter(vertex_data, 'color')

        # set sphere properties
        radius = 5

        # generate vertices, cartesian equation for a sphere - x^2 + y^2 + z^2 = R^2
        for x in np.arange(0, radius):
            print('x=',x)
            y = np.sqrt(radius**2-x**2)
            print('y=',y)
            z = np.sqrt(radius**2-x**2-y**2)
            print('z=',z)
            # write data
            vertex_writer.addData3f(x,y,z)

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