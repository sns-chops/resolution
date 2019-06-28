import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
# from . import model as hyspecmodel
from . import exp

operation_modes = [
    'HU',
    'PG',
]

# interface
def build_interface(app):
    # select chopper mode
    operation_mode = dcc.Dropdown(
        id='hyspec_operation_mode',
        value='HU',
        options = [dict(label=str(_), value=_) for _ in operation_modes],
    )
    return html.Div(children=[
        html.Div([
            operation_mode, 
            dcc.Graph(
                id='hyspec-fwhm_vs_Ei',
            ),
            dcc.Graph(
                id='hyspec-flux_vs_Ei',
            ),
        ], style=dict(width="50em")),
    ])


# plot
def sorted_xy_byx(x,y):
    s = np.argsort(x)
    return np.array(x)[s], np.array(y)[s]
extra_info = {
    'Run': ('Run number', '%s'),
    'FWHM_percentages': ('Resolution percentage', '%.1f%%'),
    'Fermi': ('Fermi chopper frequency', '%.0f'),
}
def getFWHM_vs_Ei(operation_mode):
    data = exp.data[operation_mode]
    expplot = data.createPlotXY_on_condition(None, 'energy_plus_freq', 'FWHM', extra_info = extra_info)
    expplot.name = 'Experimental'
    return [expplot,]
def getFlux_vs_Ei(operation_mode):
    data = exp.data[operation_mode]
    expplot = data.createPlotXY_on_condition(None, 'energy_plus_freq', 'flux', extra_info = extra_info)
    expplot.name = 'Experimental'
    return [expplot]

def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='hyspec-fwhm_vs_Ei', component_property='figure'),
         dd.Output(component_id='hyspec-flux_vs_Ei', component_property='figure'),
        ],
        [dd.Input('hyspec_operation_mode', 'value'),
        ],
    )
    def update_figures(mode):
        fwhm_data = getFWHM_vs_Ei(mode)
        flux_data = getFlux_vs_Ei(mode)
        return [
            {
                'data': fwhm_data,
                'layout': dict(
                    title = 'Resolution vs incident energy',
                    showlegend=True,
                    xaxis=dict(
                        title='Ei (meV)',
                        type='log',
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title='FWHM (meV)',
                        type='log',
                        showspikes=True,
                    ),
                ),
            },
            {
                'data': flux_data,
                'layout': dict(
                    title = 'Flux vs incident energy',
                    showlegend=True,
                    xaxis=dict(
                        title='Ei (meV)',
                        type='log',
                        showspikes=True,
                    ),
                    yaxis=dict(
                        # title='Flux (counts/s/cm^2/MW)',
                        title='Flux (arb. unit)',
                        type='log',
                        showspikes=True,
                    ),
                ),
            },
        ]
    return
