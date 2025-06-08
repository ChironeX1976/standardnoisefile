from dash import dash, Input, Output, State
from layout import layout_dash
from data import data_init, saveas_standard_csv_in_data_dir
import webbrowser

# # Pad naar Microsoft Edge (pas aan indien nodig)
# edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
#
# # Registreer Edge als browser
# webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
#
# # Open met Edge
# webbrowser.get('edge').open_new("http://127.0.0.1:8050/")

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
    State('cl_upload01', 'filename'), prevent_initial_call=True)
def load_data(contents, filenames):
    #maak altijd een lijst van de geüploade bestanden, ook als het er maar één is
    if not isinstance(contents, list):
        contents = [contents]
        filenames = [filenames]
    geldigheid, dict_df = data_init(contents,filenames)
    return geldigheid,dict_df

if __name__ == '__main__':
    app.run(debug=True)
