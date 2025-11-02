import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table

""" 
The components of the dash web-page are created here, web page looks like this:
"""
def c_knoppen():
    """make html-components left on the webpage"""
    #voorbeeldpath = str(get_std_audio_path())
    c = html.Div([html.Img(src="assets/logo.png", width=240),
                  html.H1("Standardize - files tool"),
                  html.H4('Upload the .txt or .csv data in the drag and drop section.'),
                  html.H4('If a .txt or .csv-file is recognized, it will be standardized.'),
                  html.H4('Wait for filestatus to finish.'),
                  html.H4('You can then save the standardized data to a chosen path.'),
                  html.Hr(),
                  html.Br(),
                  html.P('Optional: Add audiofiles', className ="custom-audiotext"),
#
#                 html.P('Optional: associate 01dB-fusion audio-files (.mp3)', className="custom-audiotext"),
#                  html.Div(['Audiofolder path, eg.   ', html.A(voorbeeldpath), ' or no audio'],
#                           className="custom-audiotext"),
#                  dcc.Input(id="cl_audiofolder", type="text",
#                            value=str('no audio'),
#                            className="custom-audiopath"),
                  dcc.Upload(id='cl_upload_audio',
                             children=html.Div(
                                 ['Drag and Drop .wav or .mp3: ', html.A('multiple (01dB) or one (Svantek959)')]),
                             multiple=True,
                             className="custom-audiopath",
                             ),
                  html.Br(),
                  html.Div(id='cl_divaudiofiles', children='...audiofile(s)...', className ="custom-audiotext"),
                  html.Br(),
                  dcc.Upload(id='cl_upload01',
                             children=html.Div(['Drag and Drop or ', html.A('Select (multiple) .csv or .txt Files')]),
                             multiple=True,
                             className="custom-upload",
                             ),

                  html.Br(),
                  html.Div(id='cl_filestatus', children='...filestatus...'),

                  html.Br(),
                  html.Br(),
                  html.Div([
                      html.Button("Download", id="cl_btn_download", n_clicks=0),
                      dcc.Download(id="cl_download_component")]),

                  # html.Button(id="cl_btn_save", children="save to ... " ),
                  # dcc.Input(
                  #     id="cl_path", type="text",
                  #     value=str(get_std_save_path()), placeholder="c:/tmp/standardfile01db.txt", className="custom-saveaspath"),
                  html.P('Output columns (mandatory): isodatetime, laeq1s, exclude, soundpath'),
                  html.P('Output columns (optional): lzeq25Hz -> lzeq20kHz; markercolumns; Lafmin, Lafmax;')

                  ]),
    return c
def c_divhelpfields():
    """ help fields that could be hidden"""
    c = html.Div([
        html.P(children="helpfields"),
        html.Div(id="cl_hlp_save", children="button save not yet used", hidden=False),
        html.Div(id="cl_hlp_filestatus", children="", hidden = False),
        html.Div(id="cl_hlp_columnorder", children=""),
        html.Div(dcc.Store(id='cl_store_df', data=dict())),
        html.Div(dcc.Store(id='cl_store_audiofiles', data=dict()))
    ], hidden=False)
    return c
def layout_dash():
    c = dbc.Container([
        dbc.Row([
            dbc.Col(c_knoppen())]),
        dbc.Row(dbc.Col([c_divhelpfields()]))])
    return c
