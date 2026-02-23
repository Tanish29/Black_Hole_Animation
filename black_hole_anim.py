import os
import sys

import numpy as np
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.particles.ForceGroup import ForceGroup
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Geom,
    GeomLinestrips,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    LColor,
    LPoint3,
    LVector3,
    NodePath,
    TextNode,
    loadPrcFile,
)
from panda3d.physics import LinearSinkForce

sys.path.append(os.getcwd())

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


class BlackHoleAnimation(ShowBase):
    """Black hole animation using Panda3D.

    Notes:
        1) Axis (positive): Right = X/Pitch, back = -Y/Roll, up = Z/Heading.
    """

    def __init__(self):
        super().__init__()

        # scene properties
        self.bh_rad = 5
        self.photon_rad = self.bh_rad + 0.1
        self.adisk_rad = self.bh_rad + 1
        self.photon_thickness = 5
        self.position = LPoint3(25, -5, 0)
        self.pool_size = 9000

        # background
        background_path = "images/galaxy_background.jpg"
        self.loadBackground(background_path)

        # black hole geometry
        self.createBlackHole()
        self.createPhotonRing()

        # particle systems
        base.enableParticles()
        self.pe_acc_z = self.createAccretionDisk("acc disk")
        self.pe_acc_y = self.createAccretionDisk(
            "top acc disk", birth_rate=1e-4, lifespan_base=2.0, tilt=90, show=False
        )
        self.pe_star = self.createStarParticles("star")

        # star model
        # This work is based on "Sun with 2K Textures"
        # (https://sketchfab.com/3d-models/sun-with-2k-textures-bac9e8f95040484bb86f1deb9bd6fe95)
        # by ayushcodemate (https://sketchfab.com/ayushcodemate)
        # licensed under CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/)
        star_path = "star_model/source/Sun.glb"
        self.loadStar(star_path)

        # camera
        self.useDrive()

        # key bindings
        self.accept("1", self.changeColor)
        self.accept("2", self.changeColor, [LColor(0.99, 0.39, 0, 1)])
        self.accept("3", self.changeRenderer, [3])
        self.accept("4", self.changeRenderer, [4])
        self.accept("5", self.changeRenderer, [5])

        self.events = OnscreenText(
            text=HELP_TEXT,
            parent=base.a2dTopLeft,
            style=1,
            fg=(1, 1, 1, 1),
            pos=(0.06, -0.06),
            align=TextNode.ALeft,
            scale=0.05,
        )

    # -------------------------------------------------------------------------
    # Scene setup helpers
    # -------------------------------------------------------------------------

    def createTaskChains(self, name: str) -> str:
        """Set up a single-threaded task chain and return its name.

        Args:
            name: Identifier used for both the chain name and the return value.

        Returns:
            The supplied name string, ready to pass to taskMgr.add().
        """
        self.taskMgr.setupTaskChain(chainName=f"{name}Chain", numThreads=1)
        return name

    def loadBackground(self, imagepath: str):
        """Load a full-screen background image rendered behind all 3D models.

        Panda3D exposes two 2-D renderers (render2d / render2dp). By attaching
        the image to render2dp and setting a negative sort order on its camera
        we ensure it is drawn before everything else.

        Args:
            imagepath: Path to the background image file.
        """
        self.background = OnscreenImage(parent=self.render2dp, image=imagepath)
        self.background.setPos(0, 0, 0)
        base.cam2dp.node().getDisplayRegion(0).setSort(-20)

    def loadStar(self, path: str):
        """Load the star model, place it in the scene, and begin its spin task.

        Args:
            path: Path to the star GLTF model file.
        """
        star = self.loader.loadModel(path)

        # Create a parent node to act as the rotation pivot point
        star_pivot = self.render.attachNewNode("star_pivot")
        star_pivot.setPos(-20, -10, 0)

        # Attach the star to the pivot
        star.reparentTo(star_pivot)

        # Scale FIRST before calculating bounds
        star.setScale(LVector3(30, 30, 30))

        # Now center the star model on the pivot based on its scaled bounds
        bounds = star.getTightBounds()
        if bounds:
            min_point, max_point = bounds
            center = (min_point + max_point) / 2
            star.setPos(-center)

        self.taskMgr.add(
            funcOrTask=self.spinStar,
            name="spinStar",
            taskChain=self.createTaskChains("spinStar"),
        )
        # Store the pivot node so we rotate it instead of the star directly
        self.starNode = star_pivot

    def createBlackHole(self):
        """Procedurally generate the black hole sphere and add it to the scene.

        The sphere is built from scratch using Panda3D's low-level geometry
        API (GeomVertexData / GeomTriangles) and painted solid black to
        represent the event horizon / shadow.
        """
        vertex_data = GeomVertexData(
            "sphere", GeomVertexFormat().getV3n3c4(), Geom.UHDynamic
        )
        vertex_writer = GeomVertexWriter(vertex_data, "vertex")
        # normal_writer kept for future lighting work
        GeomVertexWriter(vertex_data, "normal")

        radius = self.bh_rad
        slices = 30
        stacks = 30

        for i in range(stacks + 1):
            # angle in the y-z plane
            phi = (2 * np.pi) * (i / stacks)
            z = radius * np.sin(phi)
            for j in range(slices + 1):
                # angle in the x-y plane
                theta = (2 * np.pi) * (j / slices)
                x = (radius * np.cos(phi)) * np.cos(theta)
                y = (radius * np.cos(phi)) * np.sin(theta)
                vertex_writer.addData3f(x, y, z)

        triangles = GeomTriangles(Geom.UHStatic)
        for i in range(stacks):
            for j in range(slices):
                K1 = i * (slices + 1) + j
                K2 = (i + 1) * (slices + 1) + j
                K1_1 = i * (slices + 1) + (j + 1)
                K2_1 = (i + 1) * (slices + 1) + (j + 1)
                triangles.addVertices(K1, K2, K1_1)
                triangles.addVertices(K1_1, K2, K2_1)

        hole_geom = Geom(vertex_data)
        hole_geom.addPrimitive(triangles)

        hole_node = GeomNode("sphere")
        hole_node.addGeom(hole_geom)

        self.HoleNodePath = NodePath(hole_node)
        self.HoleNodePath.setPos(self.position)
        self.HoleNodePath.setColor(r=0, g=0, b=0, a=1)
        self.HoleNodePath.reparentTo(self.render)

        self.taskMgr.add(
            funcOrTask=self.spinHole,
            name="spinHoleTask",
            taskChain=self.createTaskChains("spinHole"),
        )

    def createPhotonRing(self):
        """Build the photon ring as a circle linestrip and add it to the scene.

        The circle is constructed by iterating over x values and computing the
        corresponding positive and negative z values to form a closed loop.
        """
        vertex_data = GeomVertexData(
            "circle", GeomVertexFormat().getV3c4(), Geom.UHDynamic
        )
        vertex_writer = GeomVertexWriter(vertex_data, "vertex")

        radius = self.photon_rad
        x_vals = np.linspace(-radius, radius, 500)
        neg_z_vals = {}

        for x in x_vals:
            z = np.sqrt(radius**2 - x**2)
            vertex_writer.addData3f(x, 0, z)
            neg_z_vals[x] = -z

        for x in reversed(x_vals):
            vertex_writer.addData3f(x, 0, neg_z_vals[x])

        circle_lines = GeomLinestrips(Geom.UHDynamic)
        circle_lines.addConsecutiveVertices(
            start=0, num_vertices=vertex_data.getNumRows()
        )
        circle_lines.closePrimitive()

        circle_geom = Geom(vertex_data)
        circle_geom.addPrimitive(circle_lines)

        circle_node = GeomNode("circle")
        circle_node.addGeom(circle_geom)

        self.circleNodePath = NodePath(circle_node)
        self.circleNodePath.setPos(self.position)
        self.circleNodePath.setColor(r=0.99, g=0.39, b=0, a=1)
        self.circleNodePath.setRenderModeThickness(self.photon_thickness)
        self.circleNodePath.reparentTo(self.render)

    # -------------------------------------------------------------------------
    # Particle systems
    # -------------------------------------------------------------------------

    def createAccretionDisk(
        self,
        name: str,
        birth_rate: float = 1e-5,
        lifespan_base: float = 3.0,
        tilt: float = 0,
        show: bool = True,
    ) -> ParticleEffect:
        """Create an accretion disk particle system around the black hole.

        A TangentRingEmitter gives particles an orbital velocity, while a
        LinearSinkForce with inverse-square falloff pulls them inward to
        simulate gravity.

        Args:
            name:          Base name used for the particles, force group, and
                           particle effect objects.
            birth_rate:    Seconds between each particle birth event.
            lifespan_base: Base lifespan of each particle in seconds.
            tilt:          Rotation around the P axis (degrees) to orient the
                           disk plane (0 = horizontal, 90 = vertical).
            show:          Whether to start the particle effect immediately.

        Returns:
            The configured ParticleEffect instance.
        """
        p = Particles(f"{name} particles")
        p.setPoolSize(self.pool_size + 10000)
        p.setBirthRate(birth_rate)
        p.setLitterSize(10000)
        p.setLitterSpread(1)
        p.setSystemGrowsOlderFlag(False)
        p.setLocalVelocityFlag(False)

        # factory
        p.setFactory("PointParticleFactory")
        p.factory.setLifespanBase(lifespan_base)
        p.factory.setLifespanSpread(1.0)
        p.factory.setTerminalVelocityBase(12)
        p.factory.setTerminalVelocitySpread(1)
        p.factory.setMassBase(1)
        p.factory.setMassSpread(0.25)

        # emitter
        p.setEmitter("TangentRingEmitter")
        p.emitter.setEmissionType(p.emitter.ET_CUSTOM)
        p.emitter.setAmplitude(10)
        p.emitter.setAmplitudeSpread(1.0)
        p.emitter.setRadius(self.adisk_rad)

        # renderer
        p.setRenderer("LineParticleRenderer")
        p.renderer.setAlphaMode(p.renderer.PR_ALPHA_OUT)
        p.renderer.setHeadColor(LColor(0.99, 0.39, 0, 1))
        p.renderer.setTailColor(LColor(0.99, 0.39, 0, 1))

        # gravitational sink force
        fg = ForceGroup(f"{name} forces")
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R_SQUARED)
        force.setForceCenter(LPoint3(0, 0, 0))
        force.setRadius(self.adisk_rad - 1)
        force.setMassDependent(True)
        force.setAmplitude(55)
        force.setActive(1)
        fg.addForce(force)

        pe = ParticleEffect(f"{name} particle effect")
        pe.addForceGroup(fg)
        pe.addParticles(p)
        pe.setPos(self.position)
        pe.setP(tilt)

        if show:
            pe.start(self.render)

        return pe

    def createStarParticles(self, name: str) -> ParticleEffect:
        """Create the particle system that streams material from the star to the black hole.

        A SphereSurfaceEmitter radiates particles outward from the star's
        surface, while a LinearSinkForce pulls them toward the black hole.

        Args:
            name: Base name used for the particles, force group, and particle
                  effect objects.

        Returns:
            The configured ParticleEffect instance.
        """
        p = Particles(f"{name} particles")
        p.setPoolSize(self.pool_size)
        p.setBirthRate(1e-5)
        p.setLitterSize(10000)
        p.setLitterSpread(1)
        p.setSystemGrowsOlderFlag(False)
        p.setLocalVelocityFlag(False)

        # factory
        p.setFactory("PointParticleFactory")
        p.factory.setLifespanBase(4.0)
        p.factory.setLifespanSpread(1.0)
        p.factory.setTerminalVelocityBase(12)
        p.factory.setTerminalVelocitySpread(1)
        p.factory.setMassBase(5)
        p.factory.setMassSpread(2)

        # emitter
        p.setEmitter("SphereSurfaceEmitter")
        p.emitter.setEmissionType(p.emitter.ET_RADIATE)
        p.emitter.setRadiateOrigin(LPoint3(0, 0, 0))
        p.emitter.setAmplitude(0.25)
        p.emitter.setAmplitudeSpread(2)
        p.emitter.setRadius(self.adisk_rad)
        p.emitter.setOffsetForce(LPoint3(0, 0, 0))

        # renderer
        p.setRenderer("LineParticleRenderer")
        p.renderer.setAlphaMode(p.renderer.PR_ALPHA_OUT)
        p.renderer.setHeadColor(LColor(0.99, 0.39, 0, 1))
        p.renderer.setTailColor(LColor(0.99, 0.39, 0, 1))

        # gravitational sink force (center is relative to the black hole position)
        fg = ForceGroup(f"{name} forces")
        force = LinearSinkForce()
        force.setFalloffType(force.FT_ONE_OVER_R)
        force.setForceCenter(LPoint3(33, 1.5, 0))
        force.setRadius(self.adisk_rad - 1)
        force.setMassDependent(True)
        force.setAmplitude(self.bh_rad / 1.5)
        force.setActive(1)
        fg.addForce(force)

        pe = ParticleEffect(f"{name} particle effect")
        pe.addForceGroup(fg)
        pe.addParticles(p)
        pe.start(self.render)
        pe.setPos(LPoint3(-20, -10, 0))

        return pe

    # -------------------------------------------------------------------------
    # Color and renderer controls
    # -------------------------------------------------------------------------

    def changeColor(self, col: LColor = None):
        """Change the color of the photon ring, star, and all particle systems.

        Args:
            col: Target color. If None, a random color is generated.
        """
        if col is None:
            vals = np.float16(np.append(np.random.uniform(0, 1, 3), 1))
            col = LColor(vals[0], vals[1], vals[2], vals[3])

        self.circleNodePath.setColor(col)
        self.starNode.setColorScale(col)

        crend = (
            self.pe_acc_z.getParticlesNamed("acc disk particles")
            .getRenderer()
            .__repr__()
        )

        if crend == "SpriteParticleRenderer":
            self.changeRenderer(3, col)
        elif crend == "LineParticleRenderer":
            self.changeRenderer(4, col)
        elif crend == "PointParticleRenderer":
            self.changeRenderer(5, col)

    def changeRenderer(self, val: int, ccol: LColor = None):
        """Switch the particle renderer type across all particle systems.

        Args:
            val:  Renderer type identifier (3 = Sprite, 4 = Line, 5 = Point).
            ccol: Color to carry over. If None, the current color is read from
                  the active renderer.
        """
        crend = (
            self.pe_acc_z.getParticlesNamed("acc disk particles")
            .getRenderer()
            .__repr__()
        )

        if ccol is None:
            renderer = self.pe_acc_z.getParticlesNamed(
                "acc disk particles"
            ).getRenderer()
            if crend == "SpriteParticleRenderer":
                ccol = renderer.getColor()
            elif crend == "LineParticleRenderer":
                ccol = renderer.getHeadColor()
            elif crend == "PointParticleRenderer":
                ccol = renderer.getStartColor()

        if val == 3:
            self.updateToSprite(ccol)
        elif val == 4:
            self.updateToLine(ccol)
        elif val == 5:
            self.updateToPoint(ccol)

    def updateToSprite(self, ccol: LColor):
        """Switch all particle systems to the sprite renderer.

        Args:
            ccol: Color to apply to every sprite renderer instance.
        """

        def _apply(p, x_init, x_final, y_init, y_final):
            p.setRenderer("SpriteParticleRenderer")
            p.renderer.setTexture(self.loader.loadTexture("images/steam.png"))
            p.renderer.setColor(ccol)
            p.renderer.setXScaleFlag(True)
            p.renderer.setYScaleFlag(True)
            p.renderer.setAnimAngleFlag(True)
            p.renderer.setInitialXScale(x_init)
            p.renderer.setFinalXScale(x_final)
            p.renderer.setInitialYScale(y_init)
            p.renderer.setFinalYScale(y_final)

        p = self.pe_acc_z.getParticlesNamed("acc disk particles")
        _apply(p, 5e-3, 1e-4, 1e-3, 1e-4)
        self.pe_acc_z.getParticlesDict()["acc disk particles"] = p

        p = self.pe_acc_y.getParticlesNamed("top acc disk particles")
        _apply(p, 1e-3, 1e-4, 5e-3, 1e-4)
        self.pe_acc_y.getParticlesDict()["top acc disk particles"] = p

        p = self.pe_star.getParticlesNamed("star particles")
        _apply(p, 5e-3, 5e-3, 1e-3, 1e-3)
        self.pe_star.getParticlesDict()["star particles"] = p

    def updateToLine(self, ccol: LColor):
        """Switch all particle systems to the line renderer.

        Args:
            ccol: Color to apply to every line renderer instance.
        """

        def _apply(p):
            p.setRenderer("LineParticleRenderer")
            p.renderer.setHeadColor(ccol)
            p.renderer.setTailColor(ccol)

        p = self.pe_acc_z.getParticlesNamed("acc disk particles")
        _apply(p)
        self.pe_acc_z.getParticlesDict()["acc disk particles"] = p

        p = self.pe_acc_y.getParticlesNamed("top acc disk particles")
        _apply(p)
        self.pe_acc_y.getParticlesDict()["top acc disk particles"] = p

        p = self.pe_star.getParticlesNamed("star particles")
        _apply(p)
        self.pe_star.getParticlesDict()["star particles"] = p

    def updateToPoint(self, ccol: LColor):
        """Switch all particle systems to the point renderer.

        Args:
            ccol: Color to apply to every point renderer instance.
        """

        def _apply(p):
            p.setRenderer("PointParticleRenderer")
            p.renderer.setPointSize(100.0)
            p.renderer.setStartColor(ccol)
            p.renderer.setEndColor(ccol)
            p.renderer.setBlendType(p.renderer.PP_BLEND_VEL)
            p.renderer.setBlendMethod(p.renderer.PP_BLEND_CUBIC)

        p = self.pe_acc_z.getParticlesNamed("acc disk particles")
        _apply(p)
        self.pe_acc_z.getParticlesDict()["acc disk particles"] = p

        p = self.pe_acc_y.getParticlesNamed("top acc disk particles")
        _apply(p)
        self.pe_acc_y.getParticlesDict()["top acc disk particles"] = p

        p = self.pe_star.getParticlesNamed("star particles")
        _apply(p)
        self.pe_star.getParticlesDict()["star particles"] = p

    # -------------------------------------------------------------------------
    # Per-frame tasks
    # -------------------------------------------------------------------------

    def spinStar(self, task):
        """Continuously rotate the star around its heading axis.

        Args:
            task: Panda3D task object.

        Returns:
            task.cont to keep the task running every frame.
        """
        self.starNode.setH(self.starNode.getH() + 0.25)
        return task.cont

    def spinHole(self, task):
        """Continuously rotate the black hole sphere around its roll axis.

        Args:
            task: Panda3D task object.

        Returns:
            task.cont to keep the task running every frame.
        """
        self.HoleNodePath.setR(self.HoleNodePath.getR() + 2)
        return task.cont
