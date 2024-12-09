# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import os
here = os.path.abspath(os.path.dirname(__file__))

from dash import dcc
import dash.html as html
import dash.dependencies as dd

from .exp import fc1data, fc2data, fc1_highres_data
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
        html.H4("Flux(Intensity) vs Resolution"),
        html.Div(Ei_widget_elements, style=dict(width="15em")),
        html.Div([
            dcc.Graph(id='arcs-flux_vs_fwhm',), # Flux(intensity) vs FWHM
        ], style=dict(width="50em")),
        # <iframe width="800" height="600" frameborder="0" scrolling="no" src="//plot.ly/~mcvine/30.embed"></iframe>
        html.H4("Resolution(FWHM) vs Energy"),
        html.Div([html.Iframe(width="800", height="600", src="//plot.ly/~mcvine/30.embed")]),
        html.H4("Flux(Intensity) vs Energy"),
        html.Div([html.Iframe(width="800", height="600", src="//plot.ly/~mcvine/28.embed")]),
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
    return
