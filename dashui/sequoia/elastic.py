import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as sequoiamodel, exp


min_flux = 10

good_Eis = exp.good_Eis

# interface
def build_interface(app):
    # select Ei
    Ei_select = dcc.Dropdown(
        id='sequoia_Ei_select',
        value=95.,
        options = [dict(label=str(_), value=_) for _ in good_Eis],
    )
    Ei_widget_elements = [
        html.Label('Select incident energy (meV)'),
        Ei_select,
    ]
    # 
    return html.Div(children=[
        html.Div(Ei_widget_elements, style=dict(width="15em")),
        html.Div([
            dcc.Graph(id='sequoia-flux_vs_fwhm'),
            dcc.Graph(id='sequoia-fwhm_vs_freq'),
            dcc.Graph(id='sequoia-flux_vs_freq'),
        ], style=dict(width="50em")),
    ])


# exp Flux vs FWHM
extra_info = dict(
    chopper_freqs = ('nu', '%sHz'),
    RunNumber = ('Run no.', '%d'),
    FWHM_percentages = ('Resolution percentage', '%.1f%%')
)
max_res_percentage = 55.
plot_opts = dict(extra_info=extra_info, max_res_percentage=max_res_percentage)

def getFlux_vs_FWHMdata(data, Ei, name, chopper_index):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition = ((data.intensity>min_flux)&(data.vdata.chopper_choice==chopper_index)))
    plot =  data.createPlotXY(Ei, 'FWHM', 'intensity', **plot_opts1)
    plot.name = 'Experimental: '  + name
    return plot

def getFlux_vs_freq_data(data, Ei, name, chopper_index):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition = ((data.intensity>min_flux)&(data.vdata.chopper_choice==chopper_index)))
    plot =  data.createPlotXY(Ei, 'chopper_freqs', 'intensity', **plot_opts1)
    plot.name = 'Experimental: '  + name
    return plot

def getFWHM_vs_freq_data(data, Ei, name, chopper_index):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition = ((data.intensity>min_flux)&(data.vdata.chopper_choice==chopper_index)))
    plot =  data.createPlotXY(Ei, 'chopper_freqs', 'FWHM', **plot_opts1)
    plot.name = 'Experimental: '  + name
    return plot

def build_callbacks(app):
    @app.callback(
        [
            dd.Output(component_id='sequoia-flux_vs_fwhm', component_property='figure'),
            dd.Output(component_id='sequoia-fwhm_vs_freq', component_property='figure'),
            dd.Output(component_id='sequoia-flux_vs_freq', component_property='figure'),
        ],
        [dd.Input('sequoia_Ei_select', 'value'),
        ],
    )
    def update_figure(Ei):
        Ei = float(Ei)
        data = [
            getFlux_vs_FWHMdata(exp.alldata, Ei, 'High resolution', 0),
            getFlux_vs_FWHMdata(exp.alldata, Ei, 'High flux', 1),
        ]
        data2 = [
            getFWHM_vs_freq_data(exp.alldata, Ei, 'High resolution', 0),
            getFWHM_vs_freq_data(exp.alldata, Ei, 'High flux', 1),
        ]
        data3 = [
            getFlux_vs_freq_data(exp.alldata, Ei, 'High resolution', 0),
            getFlux_vs_freq_data(exp.alldata, Ei, 'High flux', 1),
        ]
        return [
            {
                'data': data,
                'layout': dict(
                    title = 'Flux vs resolution',
                    showlegend=True,
                    xaxis=dict(
                        title='FWHM (meV)',
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title='Flux (counts/s/cm^2/MW)',
                        showspikes=True,
                    ),
                ),
            },
            {
                'data': data2,
                'layout': dict(
                    title = 'FWHM vs Chopper Frequency',
                    showlegend=True,
                    xaxis=dict(
                        title='Chopper frequency (Hz)',
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title='FWHM (meV)',
                        showspikes=True,
                    ),
                ),
            },
            {
                'data': data3,
                'layout': dict(
                    title = 'Flux vs Chopper Frequency',
                    showlegend=True,
                    xaxis=dict(
                        title='Chopper frequency (Hz)',
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title='Flux (counts/s/cm^2/MW)',
                        showspikes=True,
                    ),
                ),
            },
        ]
    return
