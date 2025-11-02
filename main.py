from dash import dash, Input, Output, State,dcc
from layout import layout_dash
from data import data_init, check_audio_extensions, saveas_standard_csv_in_data_dir2

# ######################################################################################
# # #########                 BUILD DASHBOARD                                  #########
# ######################################################################################
app = dash.Dash(__name__)
server=app.server # <-- belangrijk voor deployment
app.layout = layout_dash()
# ######################################################################################
# # #########                 CALLBACKS                                        #########
# ######################################################################################
# @app.callback(
#     Output("cl_hlp_save", "children"),
#     Input("cl_btn_save", "n_clicks"),
#     State ("cl_store_df","data"),
#     State("cl_path", "value"),
#     prevent_initial_call=True)
# def save_output(n_clicks,dict_df,targetpath):
#     if len(dict_df) != 0: saveas_standard_csv_in_data_dir (dict_df, targetpath)
#     return f"saveButton clicked {n_clicks} times"

@app.callback(
    Output("cl_divaudiofiles", "children"),
    Output("cl_store_audiofiles", "data"),
    Input('cl_upload_audio', 'filename'), prevent_initial_call=True)
def load_audiodata(audiofilenames):
    """load audiodata
    :param filenames of the uploaded files
    :returns
        filenames"""
    #always make a list of geüploaded files, even if it is only one file
    if not isinstance(audiofilenames, list):
        audiofilenames = [audiofilenames]
    # only wav and mp3 are allowed, else: empty list is returned
    audiofilenames = check_audio_extensions(audiofilenames)
    return audiofilenames, audiofilenames

@app.callback(
    Output("cl_filestatus", "children"),
    Output("cl_store_df", "data"),
    Input('cl_upload01', 'contents'),
    State('cl_upload01', 'filename'),
    State('cl_store_audiofiles', 'data'), prevent_initial_call=True)
def load_data(contents, filenames, lst_audiofiles):
    """laad de data,
    :param filenames and contents of the uploaded files
    :returns
        if input was valid or not and
        a dictionary of the dataframe"""
    #always make a list of geüploaded files, even if it is only one file
    if not isinstance(contents, list):
        contents = [contents]
        filenames = [filenames]
    geldigheid, dict_df = data_init(contents,filenames, lst_audiofiles)
    return geldigheid,dict_df

# --------------------------------------------------------------------------------------
# ------------         SAVE DATA                               ------------
# --------------------------------------------------------------------------------------
@app.callback(Output("cl_download_component", 'data'),
               Input('cl_btn_download', 'n_clicks'),
               State("cl_store_df", 'data'),
#               State('cl_store_c_always', 'data'),
#               State('cl_store_c_markers', 'data'),
#               State('cl_hlp_columnorder', 'children'),
               prevent_initial_call=True)
def save2(n_clicks, dct_df):#, col_always, col_markers, col_order):
     datastring, filename = saveas_standard_csv_in_data_dir2(dct_df) #, col_always, col_markers, col_order)
     return dcc.send_string(datastring, filename)

if __name__ == '__main__':
    app.run(debug=True)
