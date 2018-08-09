# coding: utf-8

import os, numpy as np
# datadir = os.path.expanduser('~/notebooks/ARCS')
datadir = os.path.expanduser('~/dv/sns-chops/resolution/ARCS')


import pandas as pd
import numpy as np
import scipy as sp
import plotly, plotly.plotly as py, plotly.figure_factory as ff, plotly.graph_objs as go

from ipywidgets import widgets
from IPython.display import display, clear_output, Image
from plotly.widgets import GraphWidget


# initialize plotly
plotly.tools.set_credentials_file(username='mcvine', api_key='xPhu0GyBCi4iiEI3unYE')


class ExpData:
    
    def __init__(self, datafile=os.path.join(datadir, './V_Cali_Int_Res_FC1_2018.dat')):
        # read data
        print "reading data. please wait..."
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        vtable = ff.create_table(vdata)
        print "  done"
        self.choppers = choppers = np.array(vdata.Chopper, dtype=int)
        self.chopper_freqs = np.array([getattr(vdata, "Chopper%d"%c)[i] for i, c in enumerate(choppers)])
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.*np.pi)
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.Ei_list = list(vdata.Energy.unique())
        return


    def createPlot(self, Ei):
        condition = np.isclose(self.vdata.Energy, Ei)
        # labels = ['Chopper %s. Freq %s' % (c, f) 
        #          for c,f in zip(self.choppers[condition], self.chopper_freqs[condition])]
        labels = ['Ei=%.2f; nu=%s' % (ei, f) 
                  for ei,f in zip(self.vdata.Ei[condition], self.chopper_freqs[condition])]
        trace = go.Scatter(
            x = self.FWHM[condition],
            # y = self.vdata.Height[condition],
            y = self.intensity[condition],
            mode = 'markers+text',
            text = labels,
            textposition='top center',
        )
        return trace


    def createFigure(self, Ei):
        trace = self.createPlot(Ei)
        data = [trace]
        layout = go.Layout(
            title = 'Flux (peak height) vs elastic resolution (peak width). Ei=%s meV' % Ei,
            showlegend=False,
            xaxis=dict(
                title='Resolution (meV)',
            ),
            yaxis=dict(
                title='Flux (arb. unit)',
            )
        )
        return go.Figure(data=data, layout=layout)


    def createIntResPlot():
        # Plotting widget
        print "preparing widget..."
        g = GraphWidget('https://plot.ly/~mcvine/2')

        # Dropdown list
        Ei_str_list = map(str, self.Ei_list)
        initial_Ei = 100.
        Ei_select = widgets.Dropdown(
            options=Ei_str_list,
            value=str(initial_Ei),
            description='Incident energy',
        )

        def on_Ei_change(_):
            Ei = float(Ei_select.value)
            fig = createFigure(Ei)
            g.plot(fig)

        Ei_select.observe(on_Ei_change)
        print "  done"
        return widgets.VBox([Ei_select, g])
