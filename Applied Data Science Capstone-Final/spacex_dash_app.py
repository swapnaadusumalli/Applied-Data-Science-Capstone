# Import required libraries
# Writen By Emmanuel M. Oben, for completion of IBM Data Science Professional Certificate on Coursera September 2021
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
launch_list = [
    ["All Sites", "ALL"], ["CCAFS LC-40", "CCAFS LC-40"], ["VAFB SLC-4E", "VAFB SLC-4E"], 
    ["KSC LC-39A", "KSC LC-39A"], ["CCAFS SLC-40", "CCAFS SLC-40"]
]
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown', 
                                        # Update dropdown values using list comphrehension
                                        options=[{'label': i[0], 'value': i[1]} for i in launch_list],
                                        placeholder="Select a Launch Site here",
                                        searchable=True,
                                        value='ALL'),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                dcc.Graph(id='success-pie-chart'),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000, value=[min_payload, max_payload],
                                    marks={0:'0', 2500:'2500', 5000:'5000', 7500:'7500', 10000: '10000'}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( 
                [Output(component_id='success-pie-chart', component_property='figure')],
                [Input(component_id='site-dropdown', component_property='value')]
            )
# Computation to callback function and return graph
def get_pie(entered_site):
    if entered_site == 'ALL':
        df_site = spacex_df[['Launch Site', 'class']]
        df_site_all = df_site.groupby(['Launch Site']).sum()
        df_site_all["Launch Site"] = df_site_all.index
        df_site_all.reset_index(drop=True, inplace=True)
        #df_site_all.plot(kind='pie', subplots=True, shadow = True, y='class', labels=None,startangle=-180, autopct='%1.1f%%')
        pie_fig = px.pie(df_site_all, values='class', names='Launch Site', title='Total Success Launches By Site')
    else:
        df_site_type = spacex_df[spacex_df['Launch Site'] == entered_site]
        zeros, ones = 0, 0;
        title = "Total Success Launches for site " + entered_site

        for index, row in df_site_type.iterrows():
            if row['class'] == 0: zeros += 1
            else: ones += 1
        df_class = pd.DataFrame({'score': ["0", "1"], 'count': [zeros, ones]})
        pie_fig = px.pie(df_class, values='count', names='score', title = title)

    return [pie_fig]

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( 
                [Output(component_id='success-payload-scatter-chart', component_property='figure')],
                [
                    Input(component_id='site-dropdown', component_property='value'),
                    Input(component_id="payload-slider", component_property="value")
                ]
            )
# Computation to callback function and return graph
def get_scatter(entered_site, payload_mass):
    #spacex_df    Booster Version Category
    def shorten(booster_version):
        return booster_version.split(' ')[1]

    df = spacex_df[['class','Payload Mass (kg)','Booster Version','Launch Site']].rename(columns={'Booster Version': 'Booster Version Category'})
    df['Booster Version Category'] = df['Booster Version Category'].apply(shorten)
    mask = (df['Payload Mass (kg)'] >= payload_mass[0]) & (df['Payload Mass (kg)'] <= payload_mass[1])
    df = df[mask]

    if entered_site == 'ALL':
        scatter_fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                title='Correlation between Payload and Success for all Sites')
    else:
        df2 = df[df['Launch Site'] == entered_site]
        scatter_fig = px.scatter(df2, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                title='Correlation between Payload and Success for site {}'.format(entered_site))

    return [scatter_fig]

# Run the app
if __name__ == '__main__':
    app.run_server()
