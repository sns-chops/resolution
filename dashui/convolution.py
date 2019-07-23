import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
import widget_utils as wu


def create(instrument='arcs'):
    "return interface builder and callback builder"
    upload_widget_id = '%s-convolution-upload' % instrument
    plot_widget_id = '%s-convolution-plot' % instrument
    def interface_builder(app):
        return convolution_panel(upload_widget_id, plot_widget_id)
    def callback_builder(app):
        return build_callbacks(app, upload_widget_id, plot_widget_id)
    return interface_builder, callback_builder


def convolution_panel(upload_widget_id, plot_widget_id):
    return html.Div([
        html.Details([
            html.Summary('Convolution'),
            html.Div("Upload a 2-col ascii file for the I vs E curve, and calculate the curve with instrument broadening"),
            ]),
        
        dcc.Upload(
            id=upload_widget_id,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a file')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),

        # plot
        html.Div(id=plot_widget_id, style=dict(width="40em", margin='.3em')),
    ])

def build_callbacks(app, upload_widget_id, plot_widget_id):
    # convolution
    @app.callback(dd.Output(plot_widget_id, component_property='children'),
                  [dd.Input(upload_widget_id, 'contents')],
                  [dd.State(upload_widget_id, 'filename'),
                   dd.State(upload_widget_id, 'last_modified')])
    def handle_convolution_upload(uploaded_contents, uploaded_filename, uploaded_last_modified):
        if uploaded_contents is None: return []
        # load data
        try:
            E, I = dataarr_from_uploaded_ascii(uploaded_contents).T
        except Exception as e:
            return [html.P("Failed to load %s as 2-col ascii" % uploaded_filename,
                           style={'color': 'red', 'fontSize': 12})]
            import traceback as tb
            return [html.Pre(tb.format_exc(), style={'color': 'red', 'fontSize': 14})]
        # plot
        curve = {
            'data': [
                {'x': E, 'y': I, 'type': 'point', 'name': 'Without resolution'},
            ],
            'layout': {
                'title': 'I(E) curve',
                'xaxis':{
                    'title':'E (meV)'
                },
                'yaxis':{
                    'title':'Intensity (arb. unit)'
                }
            }
        }
        return [dcc.Graph(figure=curve)]
    return


def dataarr_from_uploaded_ascii(uploaded_contents):
    content_type, content_string = uploaded_contents.split(',')
    import base64; decoded = base64.b64decode(content_string)
    from StringIO import StringIO
    tmp = StringIO(decoded);
    return np.loadtxt(tmp)
