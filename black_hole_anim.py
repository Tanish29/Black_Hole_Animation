import numpy as np
from panda3d.core import loadPrcFile
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, \
                         GeomTriangles, Geom, GeomNode, GeomLinestrips
from panda3d.core import NodePath
from panda3d.core import LPoint3, LColor, LVector3, LVector4

from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

from direct.particles.ForceGroup import ForceGroup
from panda3d.physics import LinearSinkForce, AngularVectorForce
from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText

HELP_TEXT = """
+ : Increase pool size
- : Decrease pool size
"""

# load config file
loadPrcFile("config/conf.prc")

class MyGame(ShowBase):
    '''
    Black hole animation using panda3d

    Notes:
        1) axis: Right = X/Pitch, forward = Y/Roll, up = Z/Heading
    '''
    def __init__(self):
        super().__init__()
        # attributes
        self.bh_rad = 7
        self.photon_rad = 7.1
        self.adisk_rad = 8

        self.photon_thickness = 3
        self.position = LPoint3(0,0,0)

        # start
        self.setBackGroundColor("images/stars.jpg")
        # create basic aspects (singularity/shadow and ring)
        self.createBlackHole()
        self.createPhotonRing()
        # enable particles
        base.enableParticles()
        self.pe = ParticleEffect()
        self.pool_size = 10000
        self.accreationDiskZ("acc disk")
        self.accreationDiskY("top acc disk")

        # self.accept('+',self.increasePoolSize)
        # self.accept('-',self.decreasePoolSize)

        self.events = OnscreenText(
            text=HELP_TEXT, parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.06),
            align=TextNode.ALeft, scale=.05)

        # some function may need to be run in parallel so need to create task chains
        # add tasks or updates
        self.taskMgr.add(funcOrTask=self.spinHole, name="spinHoleTask", taskChain=self.createTaskChains("spinHole"))
        # self.taskMgr.add(funcOrTask=self.spinCamera, name='spinCamera', taskChain=self.createTaskChains("spinCamera"))

    def createTaskChains(self, name) -> str:
        self.taskMgr.setupTaskChain(chainName=f'{name}Chain', numThreads=1)
        return name

    def setBackGroundColor(self, name):
        # set background color
        # bg_img = OnscreenImage()
        # bg_img.setImage(image=name,parent=self.render)
        self.setBackgroundColor(0,0,0,1)

    def loadModel(self, name):
        # load a model
        box = self.loader.loadModel(name)
        box.setPos(0,0,0)
        box.reparentTo(self.render)

    def createBlackHole(self):
        # create a GeomVertexData object
        vertex_data = GeomVertexData('sphere', GeomVertexFormat().getV3n3c4(), Geom.UHDynamic)

        # create Geom Vertex Writers
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')
        normal_writer = GeomVertexWriter(vertex_data, 'normal')

        # set sphere properties
        radius = self.bh_rad
        slices = 30
        stacks = 30

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
        HoleGeom = Geom(vertex_data)
        HoleGeom.addPrimitive(triangles)

        # create a geom node
        HoleNode = GeomNode('sphere')
        HoleNode.addGeom(HoleGeom)

        # create a node path and put it in scene graph
        HoleNodePath = NodePath(HoleNode)
        HoleNodePath.setPos(self.position)
        HoleNodePath.setColor(r=0, g=0, b=0, a=1)
        HoleNodePath.reparentTo(self.render)
        self.HoleNodePath = HoleNodePath

    def createPhotonRing(self):
        vertex_data = GeomVertexData('circle', GeomVertexFormat().getV3c4(), Geom.UHDynamic)
        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')

        # circle properties
        radius = self.photon_rad

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
        circleNodePath.setPos(self.position)
        circleNodePath.setColor(r=0.99,g=0.39,b=0,a=1)
        circleNodePath.setRenderModeThickness(self.photon_thickness)
        circleNodePath.reparentTo(self.render)

        self.circleNodePath = circleNodePath

    def accreationDiskZ(self,name):
        # Particles
        p = Particles(f"{name} particles")
        # max number of particles
        p.setPoolSize(self.pool_size)
        # time (s) between each particle birth
        p.setBirthRate(1e-5)
        # num particles created at birth
        p.setLitterSize(10000)
        # variation in litter birth
        p.setLitterSpread(1)
        p.setSystemGrowsOlderFlag(False)
        # whether velocities are absolute or not
        p.setLocalVelocityFlag(False)

        # factory - child of baseParticleFactory
        # parent parameters
        p.setFactory("PointParticleFactory")
        p.factory.setLifespanBase(3.0)
        p.factory.setLifespanSpread(1.0)
        p.factory.setTerminalVelocityBase(12)
        p.factory.setTerminalVelocitySpread(1)
        p.factory.setMassBase(1)
        p.factory.setMassSpread(0.25)

        # emitter - child of baseParticleEmitter
        p.setEmitter("TangentRingEmitter")
        # parent parameters
        p.emitter.setEmissionType(p.emitter.ET_CUSTOM)
        # p.emitter.setExplicitLaunchVector(LVector3(0, 0, 1))
        # p.emitter.setRadiateOrigin(LPoint3(0, 0, 0))
        p.emitter.setAmplitude(10)
        p.emitter.setAmplitudeSpread(1.0)
        # child parameters
        p.emitter.setRadius(self.adisk_rad)

        # renderer - child of baseParticleRenderer
        p.setRenderer("LineParticleRenderer")
        # parent parameters
        p.renderer.setAlphaMode(p.renderer.PR_ALPHA_OUT)
        # child parameters
        # sprite particle renderer
        # p.renderer.setTexture(loader.loadTexture('images/photon.png'))
        # # p.renderer.setColor(LColor(0.99,0.39,0,1))
        # p.renderer.setXScaleFlag(True)
        # p.renderer.setYScaleFlag(True)
        # p.renderer.setAnimAngleFlag(True)
        # # the y axis is scaled more to make particles look like horizontal rays
        # p.renderer.setInitialXScale(1e-3)
        # p.renderer.setFinalXScale(1e-4)
        # p.renderer.setInitialYScale(1e-4)
        # p.renderer.setFinalYScale(1e-5)

        # line particle renderer
        p.renderer.setHeadColor(LColor(0.99,0.39,0,1))
        p.renderer.setTailColor(LColor(0.99,0.39,0,1))

        # sparkle particle renderers
        # p.renderer.setCenterColor(LColor(0.99,0.39,0,1))
        # p.renderer.setEdgeColor(LColor(0,0,0,1))
        # p.renderer.setBirthRadius(0.005)
        # p.renderer.setDeathRadius(0.001)
        # p.renderer.setLifeScale(p.renderer.SP_SCALE)

        # point particle renderer
        # p.renderer.setPointSize(100.0)
        # p.renderer.setStartColor(LColor(0.99,0.39,0, 1))
        # p.renderer.setEndColor(LColor(0.99,0.39, 0, 1))
        # p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
        # p.renderer.setBlendMethod(p.renderer.PP_BLEND_CUBIC)

        # forces
        fg = ForceGroup(f'{name} forces')
        # gravitational force
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R_SQUARED)
        force.setForceCenter(self.position)
        force.setRadius(self.adisk_rad-1)
        force.setMassDependent(True)
        force.setAmplitude(55)
        force.setActive(1)

        force.setActive(1)
        fg.addForce(force)

        # particle effect system
        pe = ParticleEffect(f"{name} particle effect")
        pe.addForceGroup(fg)
        pe.addParticles(p)
        pe.start(self.render)
        pe.setPos(self.position)


    def accreationDiskY(self,name):
        # Particles
        p = Particles(f"{name} particles")
        # max number of particles
        p.setPoolSize(self.pool_size + 10000)
        # time (s) between each particle birth
        p.setBirthRate(1e-4)
        # num particles created at birth
        p.setLitterSize(10000)
        # variation in litter birth
        p.setLitterSpread(1)
        p.setSystemGrowsOlderFlag(False)
        # whether velocities are absolute or not
        p.setLocalVelocityFlag(False)

        # factory - child of baseParticleFactory
        # parent parameters
        p.setFactory("PointParticleFactory")
        p.factory.setLifespanBase(2)
        p.factory.setLifespanSpread(1)
        p.factory.setTerminalVelocityBase(12)
        p.factory.setTerminalVelocitySpread(1)
        p.factory.setMassBase(1)
        p.factory.setMassSpread(0.25)

        # emitter - child of baseParticleEmitter
        p.setEmitter("TangentRingEmitter")
        # parent parameters
        p.emitter.setEmissionType(p.emitter.ET_CUSTOM)
        # p.emitter.setExplicitLaunchVector(LVector3(0, 0, 1))
        # p.emitter.setRadiateOrigin(LPoint3(0, 0, 0))
        p.emitter.setAmplitude(10)
        p.emitter.setAmplitudeSpread(1)
        # child parameters
        p.emitter.setRadius(self.adisk_rad)

        # renderer - child of baseParticleRenderer
        p.setRenderer("LineParticleRenderer")
        # parent parameters
        p.renderer.setAlphaMode(p.renderer.PR_ALPHA_OUT)
        # child parameters
        # sprite particle renderer
        # p.renderer.setTexture(loader.loadTexture('images/photon.png'))
        # # p.renderer.setColor(LColor(0.99,0.39,0,1))
        # p.renderer.setXScaleFlag(True)
        # p.renderer.setYScaleFlag(True)
        # p.renderer.setAnimAngleFlag(True)
        # # the y axis is scaled more to make particles look like horizontal rays
        # p.renderer.setInitialXScale(1e-4)
        # p.renderer.setFinalXScale(1e-5)
        # p.renderer.setInitialYScale(1e-3)
        # p.renderer.setFinalYScale(1e-4)

        # line particle renderer
        p.renderer.setHeadColor(LColor(0.99,0.39,0,1))
        p.renderer.setTailColor(LColor(0.99,0.39,0,1))

        # sparkle particle renderers
        # p.renderer.setCenterColor(LColor(0.99,0.39,0,1))
        # p.renderer.setEdgeColor(LColor(0,0,0,1))
        # p.renderer.setBirthRadius(0.005)
        # p.renderer.setDeathRadius(0.001)
        # p.renderer.setLifeScale(p.renderer.SP_SCALE)

        # point particle renderer
        # p.renderer.setPointSize(100.0)
        # p.renderer.setStartColor(LColor(0.99,0.39,0, 1))
        # p.renderer.setEndColor(LColor(0.99,0.39, 0, 1))
        # p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
        # p.renderer.setBlendMethod(p.renderer.PP_BLEND_CUBIC)

        # forces
        fg = ForceGroup(f'{name} forces')
        # gravitational force
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R_SQUARED)
        force.setForceCenter(self.position)
        force.setRadius(self.adisk_rad-1)
        force.setMassDependent(True)
        force.setAmplitude(55)
        force.setActive(1)

        force.setActive(1)
        fg.addForce(force)

        # particle effect system
        pe = ParticleEffect(f"{name} particle effect")
        pe.addForceGroup(fg)
        pe.addParticles(p)
        pe.start(self.render)
        pe.setPos(self.position)
        pe.setP(90)


    # def increasePoolSize(self):
    #     self.pool_size += 1000
    #     print(f"Pool Size = {self.pool_size}")
    #     self.createParticleSystem()

    # def decreasePoolSize(self):
    #     dec = 1000
    #     if self.pool_size <= 1000:
    #         dec = 100
    #     self.pool_size -= dec
    #     print(f"Pool Size = {self.pool_size}")
    #     self.createParticleSystem()

    # -- Update functions/tasks --
    def spinCamera(self,task):
        pass

    def spinHole(self, task):
        # rotate hole smoothly
        self.HoleNodePath.setR(self.HoleNodePath.getR()+10)
        print(f"R = {self.HoleNodePath.getR()}")
        return task.cont

