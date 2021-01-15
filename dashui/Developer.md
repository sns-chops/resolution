# Root web app
`app.py`
* Loads apps of each instrument

# ARCS web app
* `arcs/__init__.py`: skeleton
* `arcs/inelastic.py`: inelastic tab
  - method `get_data`: get a tuple of (energy transfer, resolution)
* `arcs/elastic.py`: elastic tab
* `arcs/model.py`: functions to obtain resolution from pychop model

Web apps for other intruments have similar structure.

# Common utils
`phonon/__init__.py`
* `SQE_from_ForceConstants`: function to calculate S(Q,E) from POSCAR, SPOSCAR, FORCE_CONSTANTS 
* `SQE_from_FCzip`: function to calculate S(Q,E) from a zip file of POSCAR, SPOSCAR, FORCE_CONSTANTS files
