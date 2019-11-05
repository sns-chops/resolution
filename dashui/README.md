# Setup

Need Jiao's pychop

```
  $ rsync -av analysis.sns.gov:~lj7/dv/PyChop PyChop
```
and make sure it is in PYTHONPATH

conda env

```
  $ conda create -n dash python=2
  $ conda activate dash
  $ conda config --add channels conda-forge
  $ conda config --add channels mcvine
  $ conda config --add channels mantid
  $ conda install dash dash-daq scipy matplotlib plotly=3.10 pyyaml waitress pandas mcvine tqdm multiphonon
```

Activate conda environment

```
  $ conda activate dash
```

Install dgsres

```
  $ git clone git@github.com:mcvine/dgsres.git
  $ cd dgsres
  $ python setup.py install
```

And need this repo

```
  $ cd ~/dv/
  $ git clone git@github.com:sns-chops/resolution
```
