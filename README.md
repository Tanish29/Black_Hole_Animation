# Black Hole Animation

A 3D black hole animation built with Python and Panda3D, featuring procedurally generated geometry, particle physics, and dynamic visual effects.

![Black Hole Animation](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Panda3D](https://img.shields.io/badge/Panda3D-1.10%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

This project demonstrates 3D graphics programming by creating a black hole animation entirely through code. Rather than relying on pre-made models, the black hole is constructed from primitive geometric shapes and enhanced with a sophisticated particle system to simulate the accretion disk and gravitational effects.

### Features

- **Procedurally Generated Black Hole** — The event horizon sphere is built from scratch using low-level Panda3D geometry APIs
- **Photon Ring** — A luminous ring marking the photon sphere where light orbits the black hole
- **Dynamic Accretion Disk** — Particle system with orbital mechanics and gravitational sink forces
- **Star with Particle Stream** — A star model emitting matter that gets pulled toward the black hole
- **Interactive Controls** — Real-time color and particle renderer switching
- **Physics-Based Simulation** — Inverse-square gravitational falloff and mass-dependent forces

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or [uv](https://github.com/astral-sh/uv) (recommended for faster installation)

### Clone the Repository

```bash
git clone https://github.com/yourusername/Black_Hole_Animation.git
cd Black_Hole_Animation
```

**Note:** Avoid parent directories with spaces or special characters, as this may cause issues with model path resolution.

### Set Up Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install Dependencies

**Using pip:**
```bash
pip install -r requirements.txt
```

**Using uv (faster):**
```bash
pip install uv
uv pip install -r requirements.txt
```

## Usage

### Running the Animation

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

**Or directly with Python:**
```bash
python main.py
```

### Controls

When the animation window opens:

1. **Camera Navigation** — Use the mouse to rotate and zoom:
   - Left-click to zoom in/out

2. **Keyboard Shortcuts:**
   - `1` — Randomize color scheme
   - `2` — Reset to default orange color
   - `3` — Switch to Sprite particle renderer
   - `4` — Switch to Line particle renderer (default)
   - `5` — Switch to Point particle renderer

### Initial View

The animation starts with the camera at origin. **Zoom out** to see the full scene including the star and particle effects. If using a touchpad, double-click and hold at the bottom center of the window, then drag downward to zoom out.

## Code Architecture

### `BlackHoleAnimation` Class

The main class inherits from Panda3D's `ShowBase` and orchestrates the entire scene:

- **`createBlackHole()`** — Generates the sphere geometry procedurally
- **`createPhotonRing()`** — Builds a circle linestrip for the photon sphere
- **`createAccretionDisk()`** — Unified method for creating accretion disk particle systems with customizable parameters
- **`createStarParticles()`** — Sets up the particle stream from the star
- **`loadStar()`** — Loads the 3D star model and configures rotation
- **`changeColor()`** — Updates colors across all visual elements
- **`changeRenderer()`** — Switches particle rendering modes

### Key Design Decisions

1. **Procedural Geometry** — Building the black hole from primitives provides educational value and avoids external model dependencies
2. **Unified Accretion Disk Method** — Refactored from two separate methods to reduce code duplication
3. **Task Chains** — Each spinning element (star, black hole) runs in its own task chain for parallel execution
4. **Particle Effect Hierarchy** — Separate `ParticleEffect` instances for independent control

## Development Evolution

This project evolved through multiple iterations:

1. **Initial Prototype** — Built with Ursina engine (see `archive/First-attempt-Ursina.py`)
2. **Migration to Panda3D** — More powerful particle system and geometry control
3. **Refactoring** — Consolidated duplicate code, added docstrings, improved naming conventions
4. **Architecture Improvements** — Better separation of concerns and parameterized methods

## Credits

### Star Model
The star model is based on [Sun with 2K Textures](https://sketchfab.com/3d-models/sun-with-2k-textures-bac9e8f95040484bb86f1deb9bd6fe95) by [ayushcodemate](https://sketchfab.com/ayushcodemate), licensed under [CC-BY-4.0](http://creativecommons.org/licenses/by/4.0/).

### Libraries
- [Panda3D](https://www.panda3d.org/) — 3D game engine
- [NumPy](https://numpy.org/) — Numerical computing
- [Ursina](https://www.ursinaengine.org/) — Used in early prototypes

## Known Issues

- **Texture Loading** — The star's texture may not load properly on some systems due to GLTF material handling
- **Camera Zoom** — Initial camera position requires manual zoom-out to view the full scene

## Future Enhancements

Potential improvements and features:

- [ ] Gravitational lensing effect using shaders
- [ ] Einstein ring visualization
- [ ] Schwarzschild radius calculation overlay
- [ ] Ergosphere for rotating (Kerr) black holes
- [ ] Hawking radiation particle effects
- [ ] VR support for immersive viewing
- [ ] Multiple black hole systems (binary/merging)

## Contributing
Contributions are welcome! Whether it's bug fixes, feature additions, or documentation improvements.

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS
