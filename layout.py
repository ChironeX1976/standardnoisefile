import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from std_files import get_std_save_path
""" 
The components of the dash web-page are created here, web page looks like this:
"""
def c_knoppen():
    """make html-components left on the webpage"""
    c = html.Div([html.Img(src="assets/logo.png", width=240),
                  html.H1("Standardize - files tool"),
                  html.Div('Upload the data. If file is recognized, then it will be standardized automatically, and you can then save the standardized data to a chosen path:'),
                  dcc.Upload(id='cl_upload01',
                             children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                             multiple=True,
                             className="custom-upload",
                             ),
                  dcc.Input(
                      id="cl_audiofolder", type="text",
                      value=str('C:/py/standardize/testdata/audio/01db'), placeholder="c:/tmp/audio",
                      className="custom-saveaspath"),
                  html.Div(id='cl_filestatus', children='...'),
                  html.Button(id="cl_btn_save", children="save to ... " ),
                  dcc.Input(
                      id="cl_path", type="text",
                      value=str(get_std_save_path()), placeholder="c:/tmp/standardfile.txt", className="custom-audiopath")
                  ])
    return c
def c_divhelpfields():
    """ help fields that could be hidden"""
    c = html.Div([
        html.P(children="helpfields"),
        html.Div(id="cl_hlp_save", children="button save not yet used", hidden=False),
        html.Div(id="cl_hlp_filestatus", children="", hidden = False),
        html.Div(id="cl_hlp_columnorder", children=""),
        html.Div(dcc.Store(id='cl_store_df', data=dict()))
    ], hidden=True)
    return c
def layout_dash():
    c = dbc.Container([
        dbc.Row([
            dbc.Col(c_knoppen())]),
        dbc.Row(dbc.Col([c_divhelpfields()]))])
    return c
