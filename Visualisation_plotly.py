import json
import os
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from data_preparation.preparing_data import import_all_data, set_logger, get_ecu_list, parse_config, \
    prepare_all_data
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from resources import dash_reusable_components as drc
from dash_bootstrap_templates import load_figure_template


# Load extra layouts
cyto.load_extra_layouts()


asset_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'assets'
)


load_figure_template('LUX')
app = dash.Dash(__name__, assets_folder=r'C:\Users\LENOVO\PycharmProjects\Pfe_Project\assets', external_stylesheets=[dbc.themes.BOOTSTRAP])


server = app.server
CONFIG_PATH = r"C:\Users\LENOVO\PycharmProjects\Pfe_Project\resources\config.json"
data_path = r"C:\Users\LENOVO\PycharmProjects\Pfe_Project\resources\IPB_data.csv"
ECU_TO_SEARCH = "BCP21_GW"


# parameters readed from the  config fiel
list_of_config, config_value, data_path, coopling_prefix, file_path, file_type, \
default_selected_vlan, default_selected_ecu, workspace, include_ecu_naming_in_coupling = parse_config(config_path=CONFIG_PATH)
print(default_selected_ecu)

# get list of all ecu's
ECU_LIST = get_ecu_list(config_path=CONFIG_PATH, data_path=data_path)

# get all vlan combination
# VLAN_COMBINATION = get_vlan_list(config_path=CONFIG_PATH, data_path=data_path)


# ###################### DATA PREPROCESSING ######################
# Load data

with open(r'C:\Users\LENOVO\PycharmProjects\Pfe_Project\resources\sample_network.txt') as f:
    network_data = f.read().split('\n')

print("network_data:", network_data)  # check the contents of network_data

data = import_all_data(csv_data_path=r"C:\Users\LENOVO\PycharmProjects\Pfe_Project\resources\IPB_data.csv")

edges = network_data
# edges = prepare_all_data(csv_data_path=data_path, ecu_names=ECU_LIST, include_port_switch=[True], config_path=CONFIG_PATH)

hardwarelist = list(set(data['ECU'])) + list(set(data['ECU.1']))
hardwarelist = sorted(hardwarelist)
nodes = pd.DataFrame()
nodes["ecu_name"] = hardwarelist

# print("edges:", edges)
# print("nodes:", nodes)


followers_node_di = {}  # user id -> list of followers (cy_node format)
followers_edges_di = {}  # user id -> list of cy edges ending at user id

cy_edges = []
cy_nodes = []

for edge in edges:
    if " " not in edge:
        continue

    source, target = edge.split(" ")

    cy_edge = {'data': {'id': source+target, 'source': source, 'target': target}}
    cy_target = {"data": {"id": target, "label": str(target)}}
    cy_source = {"data": {"id": source, "label": str(source)}}

    if source not in nodes:
        nodes.add(source)
        cy_nodes.append(cy_source)
    if target not in nodes:
        nodes.add(target)
        cy_nodes.append(cy_target)


    # Process dictionary of followers
    if not followers_node_di.get(target):
        followers_node_di[target] = []
    if not followers_edges_di.get(target):
        followers_edges_di[target] = []

    followers_node_di[target].append(cy_source)
    followers_edges_di[target].append(cy_edge)

    print("cy_nodes:", cy_nodes)
    print("nodes:", nodes)

    print("followers_node_di:", followers_node_di)
    print("followers_edges_di:", followers_edges_di)

# genesis_node = cy_nodes[3]
# genesis_node[3] = "genesis"

default_elements = cy_nodes[:]

default_stylesheet = [
    {
         "selector": 'node',
        'style': {
            "opacity": 0.65,
            'z-index': 9999,
             # "label": "data(label)",

        }
    },
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.45,
            'z-index': 5000
        }
    },
    {
        'selector': '.followerNode',
        'style': {
            'background-color': '#0074D9',
             # "label": "data(label)",
        }
    },
    {
        'selector': '.followerEdge',
        "style": {
            "mid-target-arrow-color": "#11101d",
            "mid-target-arrow-shape": "vee",
            "line-color": "#0074D9",
             # "label": "data(label)",

        }
    },
    {
        'selector': '.followingNode',
        'style': {
            'background-color': '#FF4136',
            # "label": "data(label)",

        }
    },
    {
        'selector': '.followingEdge',
        "style": {
            "mid-target-arrow-color": "red",
            "mid-target-arrow-shape": "vee",
            "line-color": "#FF4136",
        }
    },
    {
        "selector": '.genesis',
        "style": {
            'background-color': '#B10DC9',
            "border-width": 2,
            "border-color": "purple",
            "border-opacity": 1,
            "opacity": 1,

            # "label": "data(label)",
            "color": "#B10DC9",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999
        }
    },
    # {
    #     'selector': ':selected',
    #     "style": {
    #         "border-width": 2,
    #         "border-color": "black",
    #         "border-opacity": 1,
    #         "opacity": 1,
    #          "label": "data(label)",
    #         "color": "black",
    #         "font-size": 12,
    #         'z-index': 9999
    #     }
    # }
]

def generate_cytoscape(ecu_names):
    prepare_all_data(csv_data_path=data_path, ecu_names=ECU_LIST, include_port_switch=[True],
                     config_path=CONFIG_PATH)

    cytoscape = cyto.Cytoscape(
        responsive=True,
        elements=default_elements,
        stylesheet=default_stylesheet,

        style={
            'height': '95vh',
            'width': '100%'
        },

    )
    return cytoscape

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 80px)'}
}
# App layout
app.layout = html.Div([
    html.Div(
        children=[
            html.Link(rel='stylesheet', href='assets/css/navbar.css'),
            html.Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css'),
            html.Div(
                className="navbar",
                children=[
                    # html.Div(
                    #     className="dropdown",
                    #     children=[
                    #         html.Button(
                    #             className="dropbtn",
                    #             id="dropdown-button",
                    #             children=[
                    #                 html.I(className="bi bi-box-arrow-down"),
                    #                 "Save"
                    #             ]
                    #         ),
                    #         html.Div(
                    #             className="dropdown-content",
                    #             id="dropdown-content",
                    #             children=[
                    #                 html.Button("Save all relations as html",className="btn", id='generate_all_pages_btn', n_clicks=0,
                    #                                                 style={"background-color": "#FFFFFF", "color": "##1fbfb8"}),
                    #                 html.Button("Save Specific page as html", className="btn",id='generate_specific_btn', n_clicks=0,
                    #                                                 style={"color": "#1fbfb8", "background": "#FFFFFF"}),
                    #                 html.Button("Save Specific graphiz plot as JPEG", className="btn",id='generate_specific_graphiz_btn', n_clicks=0,
                    #                                                 style={"color": "#1fbfb8", "background": "#FFFFFF"}),
                    #             ]
                    #         )
                    #     ]
                    # )
                ]
            )

        ],
    ),


    html.Div(
        children=[
            html.Link(rel='stylesheet', href='assets/css/styles.css'),
            html.Link(rel='stylesheet', href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css'),
            html.Div(
                className="sidebar close",
                id="sidebar",
                children=[
                    html.Div(
                        className="logo-details",
                        children=[
                            html.I(className='bx bxs-dashboard'),
                            html.Span(className="logo_name", children="Visualisation")
                        ]
                    ),
                    html.Ul(
                        className="nav-links",
                        children=[
                            html.Li(
                                children=[
                                    html.A(
                                        href="#",
                                        children=[
                                            html.I(className='bx bxs-car'),
                                            html.Span(className="link_name", children="Dashboard")
                                        ]
                                    ),
                                ]
                            ),
                            html.Li(
                                children=[
                                    html.Div(
                                        className="icon-link",
                                        children=[
                                            html.A(
                                                href="#",
                                                children=[
                                                    html.I(className='bx bxs-car-wash'),
                                                    html.Span(className="link_name", children="ECU's List")
                                                ]
                                            ),
                                            html.I(className='bx bxs-chevron-down arrow ', id="n-arrow-1")
                                        ]
                                    ),

                                    html.Ul(
                                        className="sub-menu ",
                                        id="submenu-1",
                                        children=[
                                            dbc.Checklist(
                                                id='select-switch',
                                                className="form-switch",
                                                switch=True,
                                                options=[

                                                    {'label': 'Select All', 'value': 'Select All', 'disabled': False}

                                                ],
                                                value=['Select All']
                                            ),

                                            dbc.Checklist(
                                                id='ecu-switch',
                                                className="form-switch",
                                                switch=True,
                                                    options=[
                                                        {'label': ecu, 'value': ecu}
                                                        for ecu in ECU_LIST
                                                    ],
                                                    value=ECU_LIST[0]
                                            ),
                                        ]
                                    )
                                ]
                            ),
                            html.Li(
                                children=[
                                    html.Div(
                                        className="icon-link",
                                        children=[
                                            html.A(
                                                href="#",
                                                children=[
                                                    html.I(className='bx bxs-car-wash'),
                                                    html.Span(className="link_name", children="VLAN's List")
                                                ]
                                            ),
                                            html.I(className='bx bxs-chevron-down arrow', id="n-arrow-2")
                                        ]
                                    ),
                                    # html.Ul(
                                    #     className="sub-menu",
                                    #     id="submenu-2",
                                    #     children=[
                                    #         dbc.Checklist(
                                    #             id='vlan-switch',
                                    #             className="form-switch",
                                    #             switch=True,
                                    #             options=[
                                    #                 {'label': vlan, 'value': vlan, 'disabled': False}
                                    #                 for vlan in VLAN_COMBINATION
                                    #             ],
                                    #             value=VLAN_COMBINATION[0]
                                    #         )
                                    #     ]
                                    # )
                                ]
                            ),
                            html.Li(
                                children=[
                                    html.Div(
                                        className="icon-link",
                                        children=[
                                            html.A(
                                                href="#",
                                                children=[
                                                    html.I(className='bi bi-diagram-3-fill'),
                                                    html.Span(className="link_name", children="View Model")
                                                ]
                                            ),
                                            html.I(className='bx bxs-chevron-down arrow', id="n-arrow-3")
                                        ]
                                    ),
                                    html.Ul(
                                        className="sub-menu",
                                        id="submenu-3",
                                        children=[
                                            html.Li(
                                              id='layout-list',
                                                value='cola',
                                              children=[
                                                html.A('random'),
                                                html.A('grid'),
                                                html.A('circle'),
                                                html.A('concentric'),
                                                html.A('breadthfirst'),
                                                html.A('cose'),
                                                html.A('cose-bilkent'),
                                                html.A('dagre'),
                                                html.A('cola'),
                                                html.A('klay'),
                                                html.A('spread'),
                                                html.A('euler'),

                                              ]
                                            ),

                                            # drc.NamedDropdown(
                                            #     name='Model',
                                            #     id='dropdown-layout',
                                            #     options=drc.DropdownOptionsList(
                                            #         'random',
                                            #         'grid',
                                            #         'circle',
                                            #         'concentric',
                                            #         'breadthfirst',
                                            #         'cose',
                                            #         'cose-bilkent',
                                            #         'dagre',
                                            #         'cola',
                                            #         'klay',
                                            #         'spread',
                                            #         'euler'
                                            #     ),
                                            #     value='cola',
                                            #     clearable=False
                                            # )
                                        ]
                                    )
                                ]
                            ),
                            html.Br(),
                            html.Br(),

                            html.Li(
                                children=[
                                    html.Div(
                                        className="icon-link-btn",
                                        children=[
                                            html.I(className='bi bi-box-arrow-down'),
                                            html.Button("Save page as html", className="btn", id='generate_specific_btn', n_clicks=0),
                                        ]
                                    ),
                                ]
                            ),
                            html.Li(
                                children=[
                                    html.Div(
                                        className="icon-link-btn",
                                        children=[
                                            html.I(className='bi bi-box-arrow-down'),
                                            html.Button("Save graphiz as JPEG", className="btn", id='generate_specific_graphiz_btn', n_clicks=0),
                                        ]
                                    ),
                                ]
                            ),
                            html.Li(
                                children=[
                                    html.Div(
                                        className="icon-link-btn",
                                        children=[
                                            html.I(className=''),
                                            html.Button("Nodes names", className="btn", id='nodes-names-btn', n_clicks=0),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            ),
            html.Section(
                className="home-section",
                children=[
                    html.Div(
                        className="home-content",
                        children=[
                            html.I(className='bx bx-menu', id="sidebar-btn"),
                            html.Span(className="text", children="")
                        ]
                    ),
                    html.Div(
                        className='eight columns',
                        children=[
                            cyto.Cytoscape(
                                id='cytoscape',
                                responsive=True,
                                elements=default_elements,
                                stylesheet=default_stylesheet,

                                style={
                                    'height': '95vh',
                                    'width': '100%'
                                },

                            )
                        ]
                    ),

                ]
            ),

        ]
    ),



])

# @app.callback(Output('cytoscape', 'layout'),
#               [Input('layout-list', 'value')])
# def update_cytoscape_layout(layout):
#     return {'name': layout}

# @app.callback(Output('cytoscape', 'layout'),
#               [Input('layout-list', 'n_clicks')])
# def update_cytoscape_layout(n_clicks):
#     if n_clicks is None:
#         # Aucun clic n'a encore eu lieu
#         return {'name': 'cola'}  # Layout par défaut
#     else:
#         # Un clic a eu lieu, vous pouvez mettre en œuvre la logique de mise à jour du layout ici
#         layout = 'cola'  # Layout par défaut
#         # Effectuer une logique pour déterminer le layout sélectionné en fonction de n_clicks
#         # Assigner le layout sélectionné à la clé 'name' du dictionnaire de layout
#         return {'name': layout}

@app.callback(
    Output('cytoscape', 'stylesheet'),
    [Input('nodes-names-btn', 'n_clicks')],
    [State('cytoscape', 'stylesheet')]
)
def show_node_labels(n_clicks, stylesheet):
    print("clicks:", n_clicks)
    if n_clicks is None :
        return stylesheet

    if n_clicks % 2 == 1:
        global default_stylesheet
        default_stylesheet = stylesheet.copy() if stylesheet else []
        default_stylesheet.append(
            {
            "selector": 'node',
            'style': {"label": "data(label)"}
            }
        )
        return default_stylesheet
    else:
        if default_stylesheet:
            # Remove the label style for nodes
            default_stylesheet = [
                style for style in default_stylesheet
                if style.get('selector') != 'node' or 'label' not in style.get('style', {})
            ]
        return default_stylesheet

    return stylesheet



@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-btn", "n_clicks")]
)
def toggle_sidebar(n_clicks):
    if n_clicks is None or n_clicks % 2 == 0:
        return "sidebar"
    else:
        return "sidebar close"


@app.callback(
    Output("submenu-1", "style"),
    [Input("n-arrow-1", "n_clicks")]
)
def toggle_submenu_1(n_clicks):
    if n_clicks is None:
        return {"display": "none"}
    elif n_clicks % 2 == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}

# @app.callback(
#     Output("submenu-2", "style"),
#     [Input("n-arrow-2", "n_clicks")]
# )
# def toggle_submenu_2(n_clicks):
#     if n_clicks is None:
#         return {"display": "none"}
#     elif n_clicks % 2 == 1:
#         return {"display": "block"}
#     else:
#         return {"display": "none"}

@app.callback(
    Output("submenu-3", "style"),
    [Input("n-arrow-3", "n_clicks")]
)
def toggle_submenu_3(n_clicks):
    if n_clicks is None:
        return {"display": "none"}
    elif n_clicks % 2 == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


# ############################## CALLBACKS ####################################
@app.callback(Output('cytoscape', 'elements'),
              [Input('cytoscape', 'id')])
def generate_elements(_):
    elements = default_elements

    for node_id in followers_node_di:
        followers_nodes = followers_node_di[node_id]
        followers_edges = followers_edges_di[node_id]

        if followers_nodes:
            for node in followers_nodes:
                node['classes'] = 'followerNode'
            elements.extend(followers_nodes)

        if followers_edges:
            for follower_edge in followers_edges:
                follower_edge['classes'] = 'followerEdge'
            elements.extend(followers_edges)

    return elements

if __name__ == '__main__':
    logger = set_logger()

    app.run_server(port=8051, debug=True)
