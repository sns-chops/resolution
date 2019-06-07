# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as arcsmodel

import resolution_plot
fc1data = resolution_plot.ExpData(os.path.join(here, '../../ARCS//V_Cali_Int_Res_FC1_2018_v2.dat'))

chopper_freqs = range(120, 601, 120)
chopper_freq_opts = [dict(label=str(f), value=f) for f in chopper_freqs]

Ei_widget_elements = [
    html.Label('Incident energy (meV)'),
    dcc.Input(id='Ei_input', type='number', value=100.),
]

FC_widget_elements = [
    html.Label('Fermi chopper'),
    dcc.Dropdown(
        id='chopper_select',
        options = [
            dict(label='ARCS-100-1.5-AST', value='ARCS-100-1.5-AST'),
            dict(label='ARCS-700-1.5-AST', value='ARCS-700-1.5-AST'),
            dict(label='ARCS-700-0.5-AST', value='ARCS-700-0.5-AST'),
            # dict(label='ARCS-100-1.5-SMI', value='ARCS-100-1.5-SMI'),
            # dict(label='ARCS-700-1.5-SMI', value='ARCS-700-1.5-SMI'),
            #dict(label='SEQ-100-2.0-AST', value='SEQ-100-2.0-AST'),
            #dict(label='SEQ-700-3.5-AST', value='SEQ-700-3.5-AST'),
        ],
        value = 'ARCS-100-1.5-AST',
    ),

    html.Label('Fermi chopper frequency'),
    dcc.Dropdown(id='chopper_freq', value=600, options=chopper_freq_opts),
]

def build_interface(app):
    return html.Div(children=[
        html.H1(children='ARCS experimental elastic resolution'),

        dcc.Markdown('''
Experimental data
        '''),

        dcc.Graph(figure={'data': [fc1data.createPlotXY(100., 'FWHM', 'intensity')]}),
    ])


def build_callbacks(app):
    return
