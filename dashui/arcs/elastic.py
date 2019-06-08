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

# data
import resolution_plot
fc1data = resolution_plot.ExpData(os.path.join(here, '../../ARCS//V_Cali_Int_Res_FC1_2018_v2.dat'))
fc2data = resolution_plot.ExpData(os.path.join(here, '../../ARCS/V_Cali_Int_Res_FC2_2018_v2.dat'))
fc1_highres_data = resolution_plot.ExpData(os.path.join(here, '../../ARCS/V_Cali_Int_Res_FC1_HighRes_2018_v2.dat'))
vscatt_scale = 2.6e4
vscatt_scale *=60./1.4
vscatt_scale *= 1.5/2
fc1data.intensity *= vscatt_scale
fc2data.intensity *= vscatt_scale
fc1_highres_data.intensity *= vscatt_scale
min_flux = 10000

unique_nominal_Eis = set( list(fc1data.Ei_list) + list(fc2data.Ei_list) + list(fc1_highres_data.Ei_list) )
unique_nominal_Eis = sorted(list(unique_nominal_Eis))


# interface
def build_interface(app):
    # select Ei
    Ei_select = dcc.Dropdown(
        id='Ei_select',
        value=100.,
        options = [dict(label=str(_), value=_) for _ in unique_nominal_Eis],
    )
    Ei_widget_elements = [
        html.Label('Select incident energy (meV)'),
        Ei_select,
    ]
    # 
    return html.Div(children=[
        html.Div(Ei_widget_elements, style=dict(width="15em")),
        html.Div([
            dcc.Graph(
                id='arcs-flux_vs_fwhm',
            ),
        ], style=dict(width="50em")),
    ])


# exp Flux vs FWHM
extra_info = dict(
        chopper_freqs = ('nu', '%sHz'),
        FWHM_percentages = ('Resolution percentage', '%.1f%%')
    )
max_res_percentage = 15.
plot_opts = dict(extra_info=extra_info, max_res_percentage=max_res_percentage)

def getFlux_vs_FWHMdata(data, Ei, name):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition = (data.intensity>min_flux))
    plot =  data.createPlotXY(Ei, 'FWHM', 'intensity', **plot_opts1)
    plot.name = 'Experimental: '  + name
    return plot

def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='arcs-flux_vs_fwhm', component_property='figure'),
        ],
        [dd.Input('Ei_select', 'value'),
        ],
    )
    def update_figure(Ei):
        Ei = float(Ei)
        
        data = [
            getFlux_vs_FWHMdata(fc1data, Ei, 'ARCS-700-1.5'),
            getFlux_vs_FWHMdata(fc2data, Ei, 'ARCS-100-1.5'),
            getFlux_vs_FWHMdata(fc1_highres_data, Ei, 'ARCS-700-0.5'),
        ]
        return {
            'data': data,
            'layout': dict(
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
    return
