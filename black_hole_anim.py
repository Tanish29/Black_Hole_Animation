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
from panda3d.physics import LinearSinkForce, LinearVectorForce
from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

import os
import sys
sys.path.append(os.getcwd())
import pathlib

HELP_TEXT = """
1 : Change color
2 : Default color
3 : Sprite particles
4 : Line particles
5 : Point particles
"""

# load config file
config_path = "config/conf.prc"
loadPrcFile(config_path)

class MyGame(ShowBase):
    '''
    Black hole animation using panda3d

    Notes:
        1) axis (positive): Right = X/Pitch, back = -Y/Roll, up = Z/Heading
    '''
    def __init__(self):
        super().__init__()
        # attributes
        self.bh_rad = 5
        self.photon_rad = self.bh_rad + 0.1
        self.adisk_rad = self.bh_rad + 1

        self.photon_thickness = 5
        self.position = LPoint3(25,-5,0)
        self.pool_size = 9000
        self.pe = ParticleEffect()

        # background
        background_path = "images/galaxy_background.jpg"
        # self.setBackGroundColor(background_path)
        self.loadBackground(background_path)

        # create basic aspects (singularity/shadow and ring)
        self.createBlackHole()
        self.createPhotonRing()

        # particle systems
        base.enableParticles()
        self.accreationDiskZ("acc disk")
        self.accreationDiskY("top acc disk", False)
        self.starParticles("star")

        # star
        star_path = "panda3d_model/sun_with_2k_textures/scene.gltf"
        self.loadStar(star_path)

        # camera viewing options
        # self.disableMouse()
        self.useDrive()

        self.accept('1', self.changeColor)
        self.accept('2', self.changeColor, [LColor(0.99,0.39,0,1)])
        self.accept('3', self.changeRenderer, [3])
        self.accept('4', self.changeRenderer, [4])
        self.accept('5', self.changeRenderer, [5])

        self.events = OnscreenText(
            text=HELP_TEXT, parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.06),
            align=TextNode.ALeft, scale=.05)

        # some function may need to be run in parallel so need to create task chains
        # add tasks or updates
        # self.taskMgr.doMethodLater(delayTime=2,funcOrTask=self.addHoleMass, name="addHoleMass",
        #                            taskChain=self.createTaskChains("addHoleMass"), extraArgs=["acc disk particles"],
        #                            appendTask=True)
        # self.taskMgr.add(funcOrTask=self.spinCamera, name='spinCamera', taskChain=self.createTaskChains("spinCamera"))


    def createTaskChains(self, name) -> str:
        self.taskMgr.setupTaskChain(chainName=f'{name}Chain', numThreads=1)
        return name


    def setBackGroundColor(self, name):
        # set background color
        # cm = CardMaker("card")
        # cm.setFrameFullscreenQuad()
        # card = self.render2d.attachNewNode(cm.generate())
        # tex = self.loader.loadTexture(name)
        # card.setTexture(tex)

        self.setBackgroundColor(0,0,0,1)
    

    def loadBackground(self, imagepath):
        ''' Load a background image behind the models '''

        # We use a special trick of Panda3D: by default we have two 2D renderers: render2d and render2dp, the two being equivalent. We can then use render2d for front rendering (like modelName), and render2dp for background rendering.
        self.background = OnscreenImage(parent=self.render2dp, image=imagepath) # Load an image object
        # self.background.setScale(0.5,0.5,0.5)
        self.background.setPos(0,0,0)
        base.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)

        # self.taskMgr.add(self.updateBackground, "update-background-task") 

    # def updateBackground(self, task):
        # ''' Update the background position based on the camera zoom (to follow 3D object) '''
        # # Get the 3D object (cube) position and size
        # obj_pos = self.cube.getPos(self.render)
        # obj_scale = self.cube.getScale()

        # # Set the background to always follow the object, but adjust its position and scale as needed
        # self.background.setPos(obj_pos.x, obj_pos.y - 10, obj_pos.z)  # Keep the background behind the object

        # # Scale the background with the zoom level
        # zoom_level = base.cam.node().getLens().getFov()  # Get the current zoom level
        # self.background.setScale(zoom_level * 2, 1, zoom_level * 2)  # Adjust the background size based on zoom level

        # return task.cont

    def loadStar(self, name):
        # This work is based on "Sun with 2K Textures" (https://sketchfab.com/3d-models/sun-with-2k-textures-bac9e8f95040484bb86f1deb9bd6fe95) by ayushcodemate (https://sketchfab.com/ayushcodemate) licensed under CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/)
        star = self.loader.loadModel(name)
        star.setPos(-20,-10,-8)
        star.setScale(LVector3(30,30,30))
        # star.setTexture(self.LoadTexture("panda3d_model/sun_with_2k_textures/textures/material_diffuse.png"))
        star.reparentTo(self.render)
        # task manager
        self.taskMgr.add(funcOrTask=self.spinStar, name="spinStar", taskChain=self.createTaskChains("spinStar"))
        self.starNode = star


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

        self.taskMgr.add(funcOrTask=self.spinHole, name="spinHoleTask", taskChain=self.createTaskChains("spinHole"))


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


    def accreationDiskZ(self, name):
        # Particles
        p = Particles(f"{name} particles")
        # max number of particles
        p.setPoolSize(self.pool_size+10000)
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
        # line particle renderer
        p.renderer.setHeadColor(LColor(0.99,0.39,0,1))
        p.renderer.setTailColor(LColor(0.99,0.39,0,1))

        # sparkle particle renderers
        # p.renderer.setCenterColor(LColor(0.99,0.39,0,1))
        # p.renderer.setEdgeColor(LColor(0,0,0,1))
        # p.renderer.setBirthRadius(0.005)
        # p.renderer.setDeathRadius(0.001)
        # p.renderer.setLifeScale(p.renderer.SP_SCALE)

        # forces
        fg = ForceGroup(f'{name} forces')
        # gravitational force
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R_SQUARED)
        force.setForceCenter(LPoint3(0,0,0))
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

        self.peZ = pe


    def accreationDiskY(self, name, show):
        # Particles
        p = Particles(f"{name} particles")
        # max number of particles
        p.setPoolSize(self.pool_size+10000)
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
        # line particle renderer
        p.renderer.setHeadColor(LColor(0.99,0.39,0,1))
        p.renderer.setTailColor(LColor(0.99,0.39,0,1))

        # sparkle particle renderers
        # p.renderer.setCenterColor(LColor(0.99,0.39,0,1))
        # p.renderer.setEdgeColor(LColor(0,0,0,1))
        # p.renderer.setBirthRadius(0.005)
        # p.renderer.setDeathRadius(0.001)
        # p.renderer.setLifeScale(p.renderer.SP_SCALE)

        # forces
        fg = ForceGroup(f'{name} forces')
        # gravitational force
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R_SQUARED)
        force.setForceCenter(LPoint3(0,0,0))
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
        pe.setPos(self.position)
        pe.setP(90)

        if show:
            pe.start(self.render)

        self.peY = pe


    def starParticles(self, name):
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
        p.factory.setLifespanBase(4.0)
        p.factory.setLifespanSpread(1.0)
        p.factory.setTerminalVelocityBase(12)
        p.factory.setTerminalVelocitySpread(1)
        p.factory.setMassBase(5)
        p.factory.setMassSpread(2)

        # emitter - child of baseParticleEmitter
        p.setEmitter("SphereSurfaceEmitter")
        # parent parameters
        p.emitter.setEmissionType(p.emitter.ET_RADIATE)
        # p.emitter.setExplicitLaunchVector(LVector3(0, 0, 1))
        p.emitter.setRadiateOrigin(LPoint3(0,0,0))
        p.emitter.setAmplitude(0.25)
        p.emitter.setAmplitudeSpread(2)
        # child parameters
        p.emitter.setRadius(self.adisk_rad)
        p.emitter.setOffsetForce(LPoint3(0,0,0))

        # renderer - child of baseParticleRenderer
        p.setRenderer("LineParticleRenderer")
        # parent parameters
        p.renderer.setAlphaMode(p.renderer.PR_ALPHA_OUT)
        # child parameters
        # line particle renderer
        p.renderer.setHeadColor(LColor(0.99,0.39,0,1))
        p.renderer.setTailColor(LColor(0.99,0.39,0,1))

        # sparkle particle renderers
        # p.renderer.setCenterColor(LColor(0.99,0.39,0,1))
        # p.renderer.setEdgeColor(LColor(0,0,0,1))
        # p.renderer.setBirthRadius(0.005)
        # p.renderer.setDeathRadius(0.001)
        # p.renderer.setLifeScale(p.renderer.SP_SCALE)

        # forces
        fg = ForceGroup(f'{name} forces')
        # gravitational force
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R)
        # relative to ?
        force.setForceCenter(LPoint3(33,1.5,0))
        force.setRadius(self.adisk_rad-1)
        force.setMassDependent(True)
        force.setAmplitude(self.bh_rad/1.5)

        force.setActive(1)
        fg.addForce(force)

        # particle effect system
        pe = ParticleEffect(f"{name} particle effect")
        pe.addForceGroup(fg)
        pe.addParticles(p)
        pe.start(self.render)
        pe.setPos(LPoint3(-20,-10,0))

        self.peSt = pe

    ''' Help Text Methods '''
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


    def changeColor(self, col=None):
        if col is None:
            col = np.float16(np.append(np.random.uniform(0,1,3), 1))
            col = LColor(col[0],col[1],col[2],col[3])

        # change photon ring col
        self.circleNodePath.setColor(col)
        # change star color
        self.starNode.setColorScale(col)

        # change all particle colors
        crend = self.peZ.getParticlesNamed('acc disk particles').getRenderer().__repr__()

        if crend == 'SpriteParticleRenderer':
            self.changeRenderer(3,col)
        elif crend == 'LineParticleRenderer':
            self.changeRenderer(4,col)
        elif crend == 'PointParticleRenderer':
            self.changeRenderer(5,col)


    def changeRenderer(self, val, ccol=None):
        # get renderer name
        crend = self.peZ.getParticlesNamed('acc disk particles').getRenderer().__repr__()

        if ccol is None:
            if crend == 'SpriteParticleRenderer':
                ccol = self.peZ.getParticlesNamed('acc disk particles').getRenderer().getColor()
            elif crend == 'LineParticleRenderer':
                ccol = self.peZ.getParticlesNamed('acc disk particles').getRenderer().getHeadColor()
            elif crend == 'PointParticleRenderer':
                ccol = self.peZ.getParticlesNamed('acc disk particles').getRenderer().getStartColor()

        if val == 3:
            # sprite particle renderer
            self.updateToSprite(ccol)
        elif val == 4:
            # line particle renderer
            self.updateToLine(ccol)
        elif val == 5:
            # point particle renderer
            self.updateToPoint(ccol)


    def updateToSprite(self, ccol: LColor):
        # acc disk
        p = self.peZ.getParticlesNamed('acc disk particles')
        p.setRenderer('SpriteParticleRenderer')
        p.renderer.setTexture(loader.loadTexture('images/steam.png'))
        p.renderer.setColor(ccol)
        p.renderer.setXScaleFlag(True)
        p.renderer.setYScaleFlag(True)
        p.renderer.setAnimAngleFlag(True)
        # the y axis is scaled more to make particles look like horizontal rays
        p.renderer.setInitialXScale(5e-3)
        p.renderer.setFinalXScale(1e-4)
        p.renderer.setInitialYScale(1e-3)
        p.renderer.setFinalYScale(1e-4)
        self.peZ.getParticlesDict()['acc disk particles'] = p

        # top disk
        p = self.peY.getParticlesNamed('top acc disk particles')
        p.setRenderer('SpriteParticleRenderer')
        p.renderer.setTexture(loader.loadTexture('images/steam.png'))
        p.renderer.setColor(ccol)
        p.renderer.setXScaleFlag(True)
        p.renderer.setYScaleFlag(True)
        p.renderer.setAnimAngleFlag(True)
        # the y axis is scaled more to make particles look like horizontal rays
        p.renderer.setInitialXScale(1e-3)
        p.renderer.setFinalXScale(1e-4)
        p.renderer.setInitialYScale(5e-3)
        p.renderer.setFinalYScale(1e-4)
        self.peY.getParticlesDict()['top acc disk particles'] = p

        # star
        p = self.peSt.getParticlesNamed('star particles')
        p.setRenderer('SpriteParticleRenderer')
        p.renderer.setTexture(loader.loadTexture('images/steam.png'))
        p.renderer.setColor(ccol)
        p.renderer.setXScaleFlag(True)
        p.renderer.setYScaleFlag(True)
        p.renderer.setAnimAngleFlag(True)
        # the y axis is scaled more to make particles look like horizontal rays
        p.renderer.setInitialXScale(5e-3)
        p.renderer.setFinalXScale(5e-3)
        p.renderer.setInitialYScale(1e-3)
        p.renderer.setFinalYScale(1e-3)
        self.peSt.getParticlesDict()['star particles'] = p


    def updateToLine(self, ccol: LColor):
        # acc disk
        p = self.peZ.getParticlesNamed('acc disk particles')
        p.setRenderer('LineParticleRenderer')
        p.renderer.setHeadColor(ccol)
        p.renderer.setTailColor(ccol)
        self.peZ.getParticlesDict()['acc disk particles'] = p

        # top disk
        p = self.peY.getParticlesNamed('top acc disk particles')
        p.setRenderer('LineParticleRenderer')
        p.renderer.setHeadColor(ccol)
        p.renderer.setTailColor(ccol)
        self.peY.getParticlesDict()['top acc disk particles'] = p

        # star
        p = self.peSt.getParticlesNamed('star particles')
        p.setRenderer('LineParticleRenderer')
        p.renderer.setHeadColor(ccol)
        p.renderer.setTailColor(ccol)
        self.peSt.getParticlesDict()['star particles'] = p


    def updateToPoint(self, ccol: LColor):
        # acc disk
        p = self.peZ.getParticlesNamed('acc disk particles')
        p.setRenderer('PointParticleRenderer')
        p.renderer.setPointSize(100.0)
        p.renderer.setStartColor(ccol)
        p.renderer.setEndColor(ccol)
        p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
        p.renderer.setBlendMethod(p.renderer.PP_BLEND_CUBIC)
        self.peZ.getParticlesDict()['acc disk particles'] = p

        # top disk
        p = self.peY.getParticlesNamed('top acc disk particles')
        p.setRenderer('PointParticleRenderer')
        p.renderer.setPointSize(100.0)
        p.renderer.setStartColor(ccol)
        p.renderer.setEndColor(ccol)
        p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
        p.renderer.setBlendMethod(p.renderer.PP_BLEND_CUBIC)
        self.peY.getParticlesDict()['top acc disk particles'] = p

        # star
        p = self.peSt.getParticlesNamed('star particles')
        p.setRenderer('PointParticleRenderer')
        p.renderer.setPointSize(100.0)
        p.renderer.setStartColor(ccol)
        p.renderer.setEndColor(ccol)
        p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
        p.renderer.setBlendMethod(p.renderer.PP_BLEND_CUBIC)
        self.peSt.getParticlesDict()['star particles'] = p


    ''' Update functions/tasks '''
    def spinStar(self, task):
        self.starNode.setH(self.starNode.getH()+0.25)
        return task.cont


    def addHoleMass(self, name, task):
        self.pool_size += 500
        self.accreationDiskZ("acc disk")
        # self.pe.getParticlesNamed(name).setPoolSiz`e(self.pool_size)
        # print(f'pool size = {self.pe.getParticlesNamed(name).getPoolSize()}')
        return task.again


    def spinHole(self, task):
        # rotate hole smoothly
        self.HoleNodePath.setR(self.HoleNodePath.getR()+2)
        # print(f"R = {self.HoleNodePath.getR()}")
        return task.cont


