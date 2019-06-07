# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ARCS inelastic resolution"

import numpy as np
import arcsmodel

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
    html.H1(children='ARCS inelastic resolution'),

    dcc.Markdown('''
This application calculates energy resolution (FWHM) as a function of energy transfer for the ARCS instrument
using [PyChop](https://docs.mantidproject.org/nightly/interfaces/PyChop.html).
The sample was assumed to be a plate of 2mm thickness and 48mm width and height.
    '''),

    # input fields
    html.Table([
        html.Tr([
            html.Td(Ei_widget_elements),
            html.Td(FC_widget_elements, style=dict(width="14em")),
        ])
    ]),

    # calculate button
    html.Div([html.Button('Calculate', id='calculate-button')], style=dict(padding='1em')),
    # status
    html.Div(id='status', children='', style=dict(padding='1em', color='red')),

    # info
    dcc.Markdown('', id='info'),

    # plot
    dcc.Markdown('''
### Plot
The plot below is an interactive plot.ly plot.

* You can drag a rectangle to zoom in
* There are several icons near the top-right corner on each plot.ly plot as you hover your mouse on top of the plot, including an icon to zoom out
* Hover the mouse over any data point to show more information related to the data point
    '''),
    html.Div([
        dcc.Graph(
            id='arcs-res_vs_E',
        ),
    ], style=dict(width="40em")),

    # download button
    html.A(html.Button('Download', id='download-button'), id='download-link'),

    # 
])

@app.callback(
    [dd.Output(component_id='arcs-res_vs_E', component_property='figure'),
     dd.Output(component_id='status', component_property='children'),
     dd.Output('download-link', 'href'),
     dd.Output('info', 'children'),
    ],
    [dd.Input('calculate-button', 'n_clicks'),
     ],
    [
     dd.State(component_id='chopper_select', component_property='value'),
     dd.State(component_id='chopper_freq', component_property='value'),
     dd.State(component_id='Ei_input', component_property='value'),
    ]
    )
def update_output_div(n_clicks, chopper_select, chopper_freq, Ei):
    try:
        E, res = get_data(chopper_select, chopper_freq, Ei)
    except Exception as e:
        status = str(e)
        curve = {}
        downloadlink = ''
        info = ''
    else:
        curve = {
            'data': [
                {'x': E, 'y': res, 'type': 'point', 'name': 'resolution'},
            ],
            'layout': {
                # 'title': '',
                'xaxis':{
                    'title':'E (meV)'
                },
                'yaxis':{
                    'title':'FWHM (meV)'
                }
            }
        }
        if (res!=res).any():
            status = "No transmission"
            downloadlink = ''
            info = ''
        else:
            status = ''
            downloadlink = '/download?chopper_select=%s&chopper_freq=%s&Ei=%s' % (
                chopper_select, chopper_freq, Ei)
            elastic_res = arcsmodel.res_vs_E([0.], chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)[0]
            info = info_format_str.format(el_res=elastic_res, el_res_percentage=elastic_res/Ei*100., Ei=Ei)
    return curve, status, downloadlink, info

info_format_str = '''
### Basics

* Incident energy: {Ei} meV
* Elastic resolution: {el_res:.5f} meV
* Elastic resolution percentage: {el_res_percentage:.2f}%
'''

def get_data(chopper_select, chopper_freq, Ei):
    E = np.linspace(-Ei*.2, Ei*.95, 100)
    res = arcsmodel.res_vs_E(E, chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
    return E, res

@app.server.route('/download')
def download_csv():
    d = {}
    keys = ['chopper_select', 'chopper_freq', 'Ei']
    for k in keys:
        value = flask.request.args.get(k)
        try: value = float(value)
        except: pass
        d[k] = value
    E, res = get_data(**d)
    filename = "arcs_res_{chopper_select}_{chopper_freq}_Ei_{Ei}.csv".format(**d)
    return send_file(np.array([E,res]).T, filename)
    

def send_file(nparr, filename):
    str_io = io.StringIO()
    np.savetxt(str_io, nparr, delimiter=',')
    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('utf-8'))
    mem.seek(0)
    str_io.close()
    return flask.send_file(
        mem,
        mimetype='text/csv',
        attachment_filename=filename,
        as_attachment=True)


def main():
    import sys
    if len(sys.argv)>1 and sys.argv[1] == 'debug':
        app.run_server(debug=True)
    else:
        from waitress import serve
        serve(app.server, host='0.0.0.0', port=8050)
    
if __name__ == '__main__': main()

