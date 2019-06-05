import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


import numpy as np
import arcsmodel
E = np.arange(-20, 100., 2.)
res = arcsmodel.res_vs_E(E)

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

app.layout = html.Div(children=[
    html.H1(children='ARCS resolution'),

    html.Div(children='''
        This application calculates energy resolution for the ARCS instrument
    '''),

    html.Table([
        html.Tr([
            html.Td(Ei_widget_elements),
            html.Td(FC_widget_elements, style=dict(width="20em"))
        ])
    ]),

    html.Div([
        dcc.Graph(
            id='arcs-res_vs_E',
            figure={
                'data': [
                    {'x': E, 'y': res, 'type': 'point', 'name': 'resolution'},
                ],
                'layout': {
                    'title': ''
                }
            }
        ),
    ], style=dict(width="40em")),

    html.Div(id='status', children=''),    
])

@app.callback(
    [dd.Output(component_id='arcs-res_vs_E', component_property='figure'),
     dd.Output(component_id='status', component_property='children'),
    ],
    [dd.Input(component_id='chopper_select', component_property='value'),
     dd.Input(component_id='chopper_freq', component_property='value'),
     dd.Input(component_id='Ei_input', component_property='value'),
    ]
    )
def update_output_div(chopper_select, chopper_freq, Ei):
    E = np.linspace(-Ei*.2, Ei*.95, 100)
    try:
        res = arcsmodel.res_vs_E(E, chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
    except Exception as e:
        status = str(e)
        curve = {}
    else:
        curve = {
            'data': [
                {'x': E, 'y': res, 'type': 'point', 'name': 'resolution'},
            ],
            'layout': {
                'title': 'ARCS resolution'
            }
        }
        status = ''
    return curve, status

if __name__ == '__main__':
    app.run_server(debug=True)
