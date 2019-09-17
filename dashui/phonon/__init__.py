#!/usr/bin/env python

import numpy as np, os, sys, glob, shutil, tempfile
import threading
lock = threading.RLock()


def SQE_from_FCzip(Qaxis, Eaxis, zippath, Ei, max_det_angle, T=300., qgrid_dim=31, Nqpoints=1e5):
    qgrid_dim = min(qgrid_dim, 51)
    Nqpoints = min(Nqpoints, 1e6)
    zippath = os.path.abspath(zippath)
    # create work dir
    workdir = tempfile.mkdtemp()
    # cd
    lock.acquire()
    saved = os.path.abspath(os.curdir)
    os.chdir(workdir)
    # unzip
    cmd = 'unzip %r' % zippath
    if os.system(cmd): raise IOError("failed to unzip %r" % zippath)
    #
    rt = SQE_from_ForceConstants(Qaxis, Eaxis, workdir, Ei, max_det_angle, T=300, qgrid_dim=qgrid_dim, Nqpoints=Nqpoints)
    # cleanup
    shutil.rmtree(workdir)
    # restore
    os.chdir(saved)
    lock.release()
    return rt


def SQE_from_ForceConstants(Qaxis, Eaxis, datadir, Ei, max_det_angle, T=300, qgrid_dim=31, Nqpoints=1e5):
    """datadir should contain POSCAR, SPOSCAR, FORCE_CONSTANTS
    datadir should be writable, and will be used as work directory
    """
    workdir = datadir
    # move to work dir
    os.chdir(workdir)

    #
    from mcvine.phonon.from_phonopy import idf, make_all
    print "calculating phonons"
    make_all(
        qgrid_dims=[qgrid_dim,qgrid_dim,qgrid_dim],
        fix_pols_phase=True,
        force_constants='FORCE_CONSTANTS', poscar='POSCAR', sposcar='SPOSCAR'
    )

    # SQE
    import mcvine.phonon.powderSQE.IDF as psidf
    print "reading dispersion"
    disp = psidf.disp_from_datadir('.')
    from mccomponents.sample import phonon as mcphonon
    print "reading dos"
    doshist = mcphonon.read_dos.dos_fromidf('DOS').doshist
    print "calculate SQE"
    IQE, mphIQE = psidf.from_data_dir(
        datadir='.',
        disp=disp, 
        N = int(Nqpoints),
        Q_bins=Qaxis, E_bins=Eaxis,
        doshist=doshist,
        T=T, Ei=Ei, max_det_angle=max_det_angle,
        include_multiphonon=True,
    )
    return IQE + mphIQE
