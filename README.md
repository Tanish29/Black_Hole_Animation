# Black_Hole_Animation

Black_Hole_Animation is a simple animation of a black hole in python using the Panda3D Library. It was created for the sole purpose of passion.

The aim was to create the animation through programming therefore, this animation only contains one model (star) and the black hole is created using primitive shapes. The light/mass around the black hole is created using Panda3D's particle physics system.

If you are intereted in viewing the animation here is the link to the video: ...

## Instructions

### Clone
Create a local copy of this repository on your machine and `cd Black_Hole_Animation` into it.

**nb:** It may help to clone the repo where the name of the parent folder is lower case with no special characters as sometimes some of the models do not load properly.

### Python Envirnoment
It is recommended to create a python virtual envirnoment using either pyenv or conda. However, it is not required if you do not wish to.

### Modules
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the necessary requirements.

```bash
pip install -r requirements.txt
```

For a faster installation of the modules you can use uv, follow the steps below.
1. Install uv: `pip install uv`
2. Install the modules: `uv pip install -r requirements.txt`

### Run
To view the animation simply run `main.py`, or if you are on windows run the `run.bat` file.

This will open a new window with a black or different background. Simply zoom out to see the animation (if you are using a touchpad then double click and hold at the bottom center of the new window until the black hole appears). There are also additional options in the top left corner for the user to use.

## Contributing
Pull requests and feedback are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)