import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as cncsmodel, exp


chopper_modes = [
    'High Resolution',
    'Intermediate',
    'High Flux',
]

# interface
def build_interface(app):
    # select chopper mode
    chopper_mode = dcc.Dropdown(
        id='cncs_chopper_mode',
        value='High Resolution',
        options = [dict(label=str(_), value=_) for _ in chopper_modes+['all']],
    )
    return html.Div(children=[
        html.Div([
            chopper_mode, 
            dcc.Graph(
                id='cncs-fwhm_vs_Ei',
            ),
            dcc.Graph(
                id='cncs-flux_vs_Ei',
            ),
        ], style=dict(width="50em")),
    ])


# plot
def sorted_xy_byx(x,y):
    s = np.argsort(x)
    return np.array(x)[s], np.array(y)[s]
extra_info = dict(
    RunNumber = ('Run number', '%d'),
    FWHM_percentages = ('Resolution percentage', '%.1f%%')
)
def getFWHM_vs_Ei(chopper_mode):
    data = exp.data[chopper_mode]
    expplot = data.createPlotXY_on_condition(None, 'Energy', 'FWHM', extra_info = extra_info)
    expplot.name = 'Experimental'
    # model
    x,y = sorted_xy_byx(data.Ei_list, data.FWHM)
    y_pychop = [cncsmodel.elastic_res_flux(chopper_mode, _)[0] for _ in x]
    import plotly.graph_objs as go
    modelplot = go.Scatter(x=x,y=y_pychop,mode='lines')
    modelplot.name = 'PyChop'
    return [expplot, modelplot]
def getFlux_vs_Ei(chopper_mode):
    data = exp.data[chopper_mode]
    expplot = data.createPlotXY_on_condition(None, 'Energy', 'intensity', extra_info = extra_info)
    expplot.name = 'Experimental'
    # model
    x,y = sorted_xy_byx(data.Ei_list, data.intensity)
    y_pychop = [cncsmodel.elastic_res_flux(chopper_mode, _)[1] for _ in x]
    import plotly.graph_objs as go
    modelplot = go.Scatter(x=x,y=y_pychop,mode='lines')
    modelplot.name = 'PyChop'
    return [expplot, modelplot]

def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='cncs-fwhm_vs_Ei', component_property='figure'),
         dd.Output(component_id='cncs-flux_vs_Ei', component_property='figure'),
        ],
        [dd.Input('cncs_chopper_mode', 'value'),
        ],
    )
    def update_figures(chopper):
        if chopper == 'all':
            fwhm_data = sum([getFWHM_vs_Ei(chopper) for chopper in chopper_modes], [])
            flux_data = sum([getFlux_vs_Ei(chopper) for chopper in chopper_modes], [])
        else:
            fwhm_data = getFWHM_vs_Ei(chopper)
            flux_data = getFlux_vs_Ei(chopper)
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
                        title='Flux (arb. unit)',
                        type='log',
                        showspikes=True,
                    ),
                ),
            },
        ]
    return
