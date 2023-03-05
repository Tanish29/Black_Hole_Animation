from panda3d.core import loadPrcFile
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, \
                         GeomTriangles, Geom, GeomNode, GeomLinestrips
from panda3d.core import NodePath
from panda3d.core import Vec3, LPoint3, LColor
from panda3d.physics import ParticleSystem, BaseParticleFactory, PointParticleFactory, BaseParticleEmitter, PointEmitter, \
                            PointParticleRenderer, BaseParticleRenderer, ParticleSystemManager, PhysicalNode
from direct.task import Task
from direct.particles.ParticleEffect import ParticleEffect
import numpy as np

# load config file
loadPrcFile("config/conf.prc")

class MyGame(ShowBase):
    def createBlackHole(self):
        # create a GeomVertexData object
        vertex_data = GeomVertexData('sphere', GeomVertexFormat().getV3n3c4(), Geom.UHDynamic)

        # create Geom Vertex Writers
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')
        normal_writer = GeomVertexWriter(vertex_data, 'normal')

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
                # normal_writer.addData3f(x,y,z)

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
        sphereNodePath.setColor(r=0, g=0, b=0, a=1)
        sphereNodePath.reparentTo(self.render)
        return sphereNodePath

    def updateBlackHole(self, path, task):
        path.setHpr(Vec3(task.time*50))
        return Task.cont

    def createPhotonRing(self):
        vertex_data = GeomVertexData('circle', GeomVertexFormat().getV3c4(), Geom.UHDynamic)
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')

        # circle properties
        radius = 5.2

        # generate circle vertices
        x_vals = np.linspace(-radius, radius, 500)
        neg_z_vals = {}
        # add positive z values for each x value
        for x in x_vals:
            z = np.sqrt(radius**2 - x**2)
            # write point to data
            vertex_writer.addData3f(x,0,z)
            neg_z_vals[x] = -z
        # add negative z values for each x value
        for x in reversed(x_vals):
            vertex_writer.addData3f(x,0,neg_z_vals[x])

        # create a geom line strip object
        circleLines = GeomLinestrips(Geom.UHDynamic)
        # add all vertices
        circleLines.addConsecutiveVertices(start=0, num_vertices=vertex_data.getNumRows())
        # close line connection
        circleLines.closePrimitive()

        # create a geom object
        circleGeom = Geom(vertex_data)
        circleGeom.addPrimitive(circleLines)

        # create a node to store geom object
        circleNode = GeomNode('circle')
        circleNode.addGeom(circleGeom)

        # create a node path to store geom node
        circleNodePath = NodePath(circleNode)
        circleNodePath.setPos(0,30,0)
        circleNodePath.setColor(r=1, g=0.64, b=0, a=1)
        circleNodePath.setRenderModeThickness(4)
        circleNodePath.reparentTo(self.render)

    def createParticleSystem(self):
        # get system
        particle_system = ParticleSystem(pool_size=1000)
        particle_system.setPoolSize(1000)
        particle_system.setBirthRate(50)
        particle_system.setLitterSize(10)
        # particle_system.setLocalVelocityFlag(True)
        # get factory
        particle_factory = PointParticleFactory()
        # particle_factory.setLifespanBase(5.0)
        # particle_factory.setMassBase(1.0)
        # particle_factory.setTerminalVelocityBase(100.0)
        particle_system.setFactory(particle_factory)
        # # get emitter
        particle_emitter = PointEmitter()
        # particle_emitter.setLocation(LPoint3(0,30,0))
        # particle_emitter.setEmissionType(1)
        # particle_emitter.setRadiateOrigin(LPoint3(0,30,0))
        # particle_emitter.setAmplitude(8.0)
        particle_system.setEmitter(particle_emitter)
        # get renderer
        particle_render = PointParticleRenderer()
        # particle_render.setAlphaMode(1)
        # particle_render.setPointSize(5.0)
        # particle_render.setStartColor(LColor(135,65,255,1))
        particle_system.setRenderer(particle_render)

        # render
        test = PhysicalNode('particles')
        test.addPhysical(particle_system)
        test2 = NodePath(test)
        test2.reparentTo(self.render)

        pass

    def setBackGroundColor(self):
        # set background color
        self.setBackgroundColor(0,0,0)

    def loadModel(self):
        # load a model
        box = self.loader.loadModel("models/box")
        box.setPos(0,10,0)
        box.reparentTo(self.render)

    def __init__(self):
        super().__init__()
        # add tasks
        # self.taskMgr.add(self.updateBlackHole, "RotateBlackHole", extraArgs=[self.createBlackHole()], appendTask=True)
        # add particle system

inst1 = MyGame()
# inst1.createPhotonRing()
# inst1.createParticleSystem()
inst1.run()