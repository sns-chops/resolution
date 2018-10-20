#Program to load Vanadium or empty Can powder files and perform a constant-Q cut along the middle Q to look at energy resolution and intensity.
import matplotlib.pyplot as plt
from mantid import plots
from mantid.simpleapi import Load, ConvertToMD, BinMD, ConvertUnits, Rebin
from matplotlib.colors import LogNorm
import numpy as np

# RunNumbers=range(102669,102699)+range(102742,102892)
# Bad Runs 102706,709,702,718,701,713,722,665,666,714,726,730,729,711,700,704,712,705,716,708 did not run
# RunNumbers=range(107970,108193) #FC2Runs3

# FC2
# RunNumbers=range(108245,108317) #Various Runs with 360Hz FC1 and FC2 and also changing T0 and energy
RunNumbers=range(107476,107648)+range(108331,108457) # FC1
print RunNumbers
IPTS=21387
PlotTag=0
datadir="/SNS/ARCS/IPTS-"+str(IPTS)+"/shared/autoreduce/"
overallArray=[]

for RunNumber in RunNumbers:
    
    try:
        w=CreateSingleValuedWorkspace()
        #LoadNexusLogs(w,"/SNS/ARCS/IPTS-"+str(IPTS)+"/data/ARCS_"+str(RunNumber)+'_event.nxs')
        LoadNexusLogs(w,"/SNS/ARCS/IPTS-"+str(IPTS)+"/nexus/ARCS_"+str(RunNumber)+'.nxs.h5')
        RunParams=w.getRun()
        Energy=RunParams["BL18:Chop:Skf0:EnergyUserReq"].getStatistics().mean
        #print Energy
        Chopperpos=RunParams["chtrans"].getStatistics().mean
        #print Chopperpos
        Chopper1=RunParams["Speed1"].getStatistics().mean
        Chopper2=RunParams["Speed2"].getStatistics().mean
        Chopper3=RunParams["Speed3"].getStatistics().mean
        if Chopperpos>400: 
            Chopper=2 
        elif Chopperpos<1: 
            Chopper=1 
        else: 
            Chopper=0

        
        # generate a nice 2D multi-dimensional workspace
        data = LoadNXSPE(datadir+'ARCS_'+str(RunNumber)+'_autoreduced.nxspe')
        values=ConvertToMDMinMaxLocal('data',QDimensions='|Q|', dEAnalysisMode='Direct')
        minQ,minE=values.MinValues
        maxQ,maxE=values.MaxValues
        
        md = ConvertToMD(InputWorkspace=data, QDimensions='|Q|', dEAnalysisMode='Direct')
        sqw = BinMD(InputWorkspace=md,
                    AlignedDim0='|Q|,'+str(minQ)+','+str(maxQ)+',100',
                    AlignedDim1='DeltaE,'+ str(minE) +',' +str(maxE*0.8) +',100')

        #2D plot
        if PlotTag==1:
            fig, ax = plt.subplots(subplot_kw={'projection':'mantid'})
            c = ax.pcolormesh(sqw, vmin=0., vmax=0.5e-3)
            cbar=fig.colorbar(c)
            cbar.set_label('Intensity (arb. units)') #add text to colorbar
            ax.set_title('Run '+str(RunNumber)+',Ei='+str(Energy)+'meVChoppers=['+str(Chopper1)+','+str(Chopper2)+','+str(Chopper3)+']')
            fig.show()


        # generate a 1D multi-dimensional workspace


        sqw_line= BinMD(InputWorkspace=md,
                    AlignedDim0='|Q|,' +str((minQ+maxQ)/3-0.01*maxQ) +','+ str((minQ+maxQ)/3+0.01*maxQ) +',1',
                    AlignedDim1='DeltaE,'+ str(minE) +',' +str(maxE*0.8) +',100')

        sqw_line_Hist=ConvertMDHistoToMatrixWorkspace('sqw_line', Normalization='NumEventsNormalization')
        result=Fit(Function='name=Gaussian,Height=1,PeakCentre=-'+str(0.01*Energy)+',Sigma='+str(0.1*Energy), InputWorkspace='sqw_line_Hist', Output='sqw_line_Hist', OutputCompositeMembers=True)

        # plots 1D multi-dimensional workspace
        if PlotTag==1:
            fig, ax = plt.subplots(subplot_kw={'projection':'mantid'})
            c = ax.errorbar(sqw_line_Hist,label='Data')
            ax.plot(result.OutputWorkspace,'r-',wkspIndex=1, label='Fit')
            ax.legend()
            ax.set_title('Run '+str(RunNumber)+',Ei='+str(Energy)+'meV,|Q|=[' +str((minQ+maxQ)/3-0.01*maxQ) +','+ str((minQ+maxQ)/3+0.01*maxQ) +']' )
            fig.show()

        handle=mtd['sqw_line_Hist_Parameters']
        RunParams2=data.getRun()
        Ei=RunParams2["Ei"].value
        Height=handle.row(0).values()[1]
        Center=handle.row(1).values()[1]
        Sigma=handle.row(2).values()[1]
        dHeight=handle.row(0).values()[2]
        dCenter=handle.row(1).values()[2]
        dSigma=handle.row(2).values()[2]
        Q=(minQ+maxQ)/3
        array=[0,RunNumber, Energy, Ei, Chopper, round(Chopper1), round(Chopper2), round(Chopper3), Height, dHeight, Center, dCenter, Sigma, dSigma, Q]
        if dHeight*3>Height:
            String1=', Fit= Error: Fit errors too high'
        elif abs(Center)>abs(dCenter)*3:
            String1=', Fit= Error: Bragg peak not at E=0'
        else:
            String1=', Fit= OK'
        print "Run=",RunNumber,", Energy=",Energy,"meV, Chopper=",Chopper,"ChopperPosition=",Chopperpos,String1
        #print array
        overallArray.append(array)
        
    except:
        print RunNumber,": Errors, either file not in directory or some syntax, or fitting / plot errors"


print overallArray
toPrint=np.c_[overallArray]
np.savetxt("/SNS/ARCS/IPTS-"+str(IPTS)+"/shared/Arnab_Vanadium/File_FC1_allRuns1.dat",toPrint,header='RunNumber Energy Ei Chopper Chopper1 Chopper2 Chopper3 Height dHeight Center dCenter Sigma dSigma Q')