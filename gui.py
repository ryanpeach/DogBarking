import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
from main import Recorder, Player

app = dash.Dash()

def transform_value(value):
    return 10. ** value

def inv_transform_value(value):
    return np.log10(value)

default_chunk = 10240
default_fs = 44100
default_freq = 17000
default_dur = .1
default_thresh = .01

slider_style = {'margin-top': 20,
                'margin-left': 20,
                'margin-right': 20,
                'padding-left': 20,
                'padding-right': 20,
                'width': "50%"}

slider_div_style = {'margin-top': 20}

options_slider_style = {'margin-top': 20,
                        'margin-left': 20,
                        'margin-right': 20,
                        'padding-left': 20,
                        'padding-right': 20,
                        'width': "50%"}
options_slider_div_style = {'margin-top': 20}
row_header_style = {}
app.layout = html.Div([

    html.Table(id="options_table", children=[

        # Tone Frequency
        html.Tr([
            html.Td("Tone Frequency:", style=row_header_style),
            html.Td([
                    dcc.Slider(
                        id='slider-tone-frequency',
                        marks={i: "{0:.0f}".format(10 ** i) for i in np.linspace(inv_transform_value(default_freq/100), inv_transform_value(default_freq*100), 4)},
                        max=inv_transform_value(default_freq*100),
                        min=inv_transform_value(default_freq/100),
                        value=inv_transform_value(default_freq),
                        step=0.01,
                        updatemode='drag'
                    ),
                ],
                style=options_slider_style),
            html.Td(
                html.Div(id='updatemode-output-tone-frequency', style=options_slider_div_style)
            ),
            html.Td(
                html.Button(id='button-play-tone', n_clicks=0, children='Play Tone')
            )
        ]),

        # Tone Duration
        html.Tr([
            html.Td("Tone Duration:", style=row_header_style),
            html.Td([
                    dcc.Slider(
                        id='slider-tone-duration',
                        marks={i: "{0:.4f}".format(10 ** i) for i in np.linspace(inv_transform_value(default_dur/100), inv_transform_value(default_dur*100), 4)},
                        max=inv_transform_value(default_dur*100),
                        min=inv_transform_value(default_dur/100),
                        value=inv_transform_value(default_dur),
                        step=0.01,
                        updatemode='drag'
                    ),
                ],
                style=options_slider_style),
            html.Td(
                html.Div(id='updatemode-output-tone-duration', style=options_slider_div_style)
            )
            # html.Td(
            #     html.Button(id='button-play-tone', n_clicks=0, children='Play Tone')
            # )
        ]),

        # RMS Threshold
        html.Tr([
            html.Td("RMS Threshold:", style=row_header_style),
            html.Td([
                    dcc.Slider(
                        id='slider-rms-threshold',
                        marks={i: "{0:.4f}".format(10 ** i) for i in np.linspace(inv_transform_value(default_thresh/100), inv_transform_value(default_thresh*100), 4)},
                        max=inv_transform_value(default_thresh*100),
                        min=inv_transform_value(default_thresh/100),
                        value=inv_transform_value(default_thresh),
                        step=0.01,
                        updatemode='drag'
                    ),
                ],
                style=options_slider_style),
            html.Td(
                html.Div(id='updatemode-output-rms-threshold', style=options_slider_div_style)
            )
            # html.Td(
            #     html.Button(id='button-play-tone', n_clicks=0, children='Play Tone')
            # )
        ]),
    ]),

    # Sampling Settings
    html.Table(id="sampling_table", children=[

        # Column Headers
        html.Tr([
            html.Td("Chunk Size:"),
            html.Td("Sample Frequency (Hz):")
        ]),

        # Sliders
        html.Tr([
            # Chunk Size
            html.Td(
                dcc.Slider(
                    id='slider-chunk',
                    marks={i: "{0:.2f}".format(10 ** i) for i in np.linspace(inv_transform_value(default_chunk/100), inv_transform_value(default_chunk*100), 4)},
                    max=inv_transform_value(default_chunk*100),
                    min=inv_transform_value(default_chunk/100),
                    value=inv_transform_value(default_chunk),
                    step=0.01,
                    updatemode='drag'
                ),
                style=slider_style
            ),

            # Sampling Frequency
            html.Td(
                dcc.Slider(
                    id='slider-fs',
                    marks={i: "{0:.2f}".format(10 ** i) for i in np.linspace(inv_transform_value(default_fs/100), inv_transform_value(default_fs*100), 4)},
                    max=inv_transform_value(default_fs*100),
                    min=inv_transform_value(default_fs/100),
                    value=inv_transform_value(default_fs),
                    step=0.01,
                    updatemode='drag',
                ),
                style=slider_style
            ),

            # Update Button
            html.Td(
                html.Button(id='button-update-sampling', n_clicks=0, children='Update')
            )
        ]),

        # Value Display
        html.Tr([
            html.Td(
                html.Div(id='updatemode-output-chunk', style=slider_div_style)
            ),
            html.Td(
                html.Div(id='updatemode-output-fs', style=slider_div_style)
            )
        ])
    ]),

    # Sampling Interval
    dcc.Interval(
            id='interval-component',
            interval=int(default_chunk/default_fs*1000/2), # in milliseconds
            n_intervals=0
        )
])

# Value Displays
# Chunck Value
@app.callback(Output('updatemode-output-chunk', 'children'),
              [Input('slider-chunk', 'value')])
def display_chunk(value):
    return 'Value: {:0.2f}'.format(transform_value(value))


# Sampling Freqency Value
@app.callback(Output('updatemode-output-fs', 'children'),
              [Input('slider-fs', 'value')])
def display_fs(value):
    return 'Value: {:0.2f} Hz'.format(transform_value(value))

# Freqency Value
@app.callback(Output('updatemode-output-tone-frequency', 'children'),
              [Input('slider-tone-frequency', 'value')])
def display_freq(value):
    return 'Value: {:0.0f} Hz'.format(transform_value(value))

# Duration Value
@app.callback(Output('updatemode-output-tone-duration', 'children'),
              [Input('slider-tone-duration', 'value')])
def display_dur(value):
    return 'Value: {:0.4f} sec'.format(transform_value(value))

# Duration Value
@app.callback(Output('updatemode-output-rms-threshold', 'children'),
              [Input('slider-rms-threshold', 'value')])
def display_thresh(value):
    return 'Value: {:0.4f} RMS'.format(transform_value(value))

# Global Options
# Sampling Interval
@app.callback(Output('interval-component', 'interval'),
              [Input('button-update-sampling', 'n_clicks')],
              [State('slider-chunk', 'value'),
               State('slider-fs', 'value')])
def update_interval(n_clicks, chunk, fs):
    return int(float(chunk)/float(fs)*1000/2)

if __name__ == '__main__':
    app.run_server(debug=True)
