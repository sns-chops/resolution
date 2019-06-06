# Setup

Need my pychop
$ rsync -av analysis.sns.gov:dv/PyChop PyChop

conda env
$ conda create -n dash python=3
$ conda activate dash
$ conda config --add channels conda-forge
$ conda config --add channels mcvine
$ conda install dash dash-daq scipy matplotlib pyyaml histogram waitress

And need this repo
$ git clone git@github.com:sns-chops/resolution
$ git checkout dash-ui