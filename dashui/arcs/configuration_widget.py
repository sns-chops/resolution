import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash_core_components as dcc
import dash_html_components as html

# chopper freqs
chopper_freqs = range(60, 601, 60)
chopper_freq_opts = [dict(label=str(f), value=f) for f in chopper_freqs]

def create(id_prefix=''):
    # select Ei
    Ei_widget_elements = [
        html.Label('Incident energy (meV)'),
        dcc.Input(id=id_prefix+'arcs_Ei_input', type='number', value=100.),
    ]

    # select FC
    FC_widget_elements = [
        html.Label('Fermi chopper'),
        dcc.Dropdown(
            id=id_prefix+'arcs_chopper_select',
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
        dcc.Dropdown(id=id_prefix+'arcs_chopper_freq', value=600, options=chopper_freq_opts),
    ]


    # input fields
    widget = html.Table([
        html.Tr([
            html.Td(Ei_widget_elements, style=dict(width="14em", border="none")),
            html.Td(FC_widget_elements, style=dict(width="14em", border="none")),
        ])
    ])

    return widget
