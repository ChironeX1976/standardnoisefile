from dash import dash, Input, Output, State
from layout import layout_dash
from data import data_init, saveas_standard_csv_in_data_dir
import webbrowser


# ######################################################################################
# # #########                 BUILD DASHBOARD                                  #########
# ######################################################################################
app = dash.Dash(__name__)
app.layout = layout_dash()
# ######################################################################################
# # #########                 CALLBACKS                                        #########
# ######################################################################################
@app.callback(
    Output("cl_hlp_save", "children"),
    Input("cl_btn_save", "n_clicks"),
    State ("cl_store_df","data"),
    State("cl_path", "value"),
    prevent_initial_call=True)
def save_output(n_clicks,dict_df,targetpath):
    if len(dict_df) != 0: saveas_standard_csv_in_data_dir (dict_df, targetpath)
    return f"saveButton clicked {n_clicks} times"

@app.callback(
    Output("cl_filestatus", "children"),
    Output("cl_store_df", "data"),
    Input('cl_upload01', 'contents'),
    State('cl_upload01', 'filename'),
    State('cl_audiofolder',"value"), prevent_initial_call=True)
def load_data(contents, filenames, audiofolder):
    """laad de data,
    :param filenames and contents of the uploaded files
    :returns
        if input was valid or not and
        a dictionary of the dataframe"""
    #always make a list of geüploaded files, even if it is only one file
    if not isinstance(contents, list):
        contents = [contents]
        filenames = [filenames]
    geldigheid, dict_df = data_init(contents,filenames, audiofolder)
    return geldigheid,dict_df

if __name__ == '__main__':
    app.run(debug=True)
