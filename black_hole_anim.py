import numpy as np
from panda3d.core import loadPrcFile
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, \
                         GeomTriangles, Geom, GeomNode, GeomLinestrips
from panda3d.core import NodePath
from panda3d.core import LPoint3, LColor, LVector3, LVector4
from panda3d.physics import ParticleSystem, PointParticleFactory, PointEmitter, BaseParticleEmitter, \
                            PointParticleRenderer, ParticleSystemManager, GeomParticleRenderer, BaseParticleRenderer, PhysicalNode
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

from direct.particles.ForceGroup import ForceGroup
from panda3d.physics import LinearNoiseForce, DiscEmitter, Physical


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
        self.bh_rad = 5
        self.photon_rad = 5.1
        self.adisk_rad = 6

        self.setBackGroundColor()
        # create basic aspects (singularity/shadow and ring)
        self.createBlackHole()
        self.createPhotonRing()
        # enable particles
        base.enableParticles()
        self.createParticleSystem()

        # some function may need to be ran in parallel so need to create task chains
        # self.createTaskChains()
        # add tasks or updates
        # self.taskMgr.add(funcOrTask=self.spinHole, name="spinHoleTask", taskChain='spinHoleChain',
        #                  extraArgs=[hole_path], appendTask=True)

    def createTaskChains(self):
        self.taskMgr.setupTaskChain(chainName='spinHoleChain', numThreads=1)

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
        HoleNodePath.setPos(0,30,0)
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
        circleNodePath.setPos(0,30,0)
        circleNodePath.setColor(r=0.99, g=0.39, b=0, a=1)
        circleNodePath.setRenderModeThickness(4)
        circleNodePath.reparentTo(self.render)

        self.circleNodePath = circleNodePath

    def createParticleSystem(self):
        # particle effect system
        pe = ParticleEffect()

        # Particles
        p = Particles("event horizon")
        # max number of particles
        p.setPoolSize(100000)
        # time (s) between each particle birth
        p.setBirthRate(0.001)
        # num particles created at birth
        p.setLitterSize(50000)
        # variation in litter birth
        p.setLitterSpread(20000)
        p.setSystemGrowsOlderFlag(False)
        # only if system grows older
        # p.setSystemLifespan(10.0)
        # p.setActiveSystemFlag(True)
        # whether velocities are absolute or not
        p.setLocalVelocityFlag(False)

        # factory - child of baseParticleFactory
        # parent parameters
        p.setFactory("ZSpinParticleFactory")
        p.factory.setLifespanBase(5.0)
        p.factory.setLifespanSpread(2.0)
        p.factory.setTerminalVelocityBase(10.0)
        p.factory.setTerminalVelocitySpread(3.0)
        # child parameters
        p.factory.setInitialAngle(0.0)
        p.factory.setFinalAngle(0.0)

        # emitter - child of baseParticleEmitter
        p.setEmitter("TangentRingEmitter")
        # parent parameters
        p.emitter.setEmissionType(p.emitter.ET_CUSTOM)
        # p.emitter.setExplicitLaunchVector(LVector3(0, 0, 1))
        # p.emitter.setRadiateOrigin(LPoint3(0, 0, 0))
        p.emitter.setAmplitude(2.0)
        p.emitter.setAmplitudeSpread(1.0)
        # child parameters
        p.emitter.setRadius(self.adisk_rad)

        # renderer - child of baseParticleRenderer
        p.setRenderer("PointParticleRenderer")
        # parent parameters
        p.renderer.setAlphaMode(p.renderer.PR_ALPHA_OUT)
        # p.renderer.setUserAlpha(1)
        # child parameters
        # sprite renderer
        # p.renderer.setTexture(loader.loadTexture('photon.png'))
        # p.renderer.setColor(LColor(255,255,255,1))
        # p.renderer.setXScaleFlag(True)
        # p.renderer.setYScaleFlag(True)
        # p.renderer.setAnimAngleFlag(True)
        # p.renderer.setInitialXScale(1e-4)
        # p.renderer.setFinalXScale(5e-7)
        # p.renderer.setInitialYScale(1e-4)
        # p.renderer.setFinalYScale(5e-7)

        # sparkle particle renderers
        # p.renderer.setCenterColor(LColor(0.99,0.39,0,1))
        # p.renderer.setEdgeColor(LColor(0,0,0,1))
        # p.renderer.setBirthRadius(0.005)
        # p.renderer.setDeathRadius(0.001)
        # p.renderer.setLifeScale(p.renderer.SP_SCALE)

        # point particle renderer
        p.renderer.setPointSize(100.0)
        p.renderer.setStartColor(LColor(0.99,0.39,0, 1))
        p.renderer.setEndColor(LColor(0, 0, 0, 1))
        p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
        p.renderer.setBlendMethod(BaseParticleRenderer.PP_BLEND_CUBIC)

        fg = ForceGroup('vertex')
        # Force parameters
        force = LinearNoiseForce(0.1500, 0)
        force.setActive(1)
        fg.addForce(force)

        # pe.addForceGroup(fg)
        pe.addParticles(p)
        pe.start(self.render)
        pe.setPos(0,30,0)


    def setBackGroundColor(self):
        # set background color
        self.setBackgroundColor(0,0,0)

    def loadModel(self):
        # load a model
        box = self.loader.loadModel("models/box")
        box.setPos(0,10,0)
        box.reparentTo(self.render)

    # -- Update functions/tasks --
    def spinHole(self, path:NodePath, task):
        # rotate hole smoothly
        path.setHpr(0, 0, path.getR()-1e-3)
        return task.cont
