# Setup

Need my pychop

```
  $ rsync -av analysis.sns.gov:dv/PyChop PyChop
```
and make sure it is in PYTHONPATH

conda env

```
  $ conda create -n dash python=3
  $ conda activate dash
  $ conda config --add channels conda-forge
  $ conda config --add channels mcvine
  $ conda config --add channels mantid
  $ conda install dash dash-daq scipy matplotlib pyyaml waitress pandas mcvine
```

And need this repo

```
  $ git clone git@github.com:sns-chops/resolution
```
