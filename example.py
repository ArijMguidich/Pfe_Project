html.Div(
        children=[
            html.Link(rel='stylesheet', href='assets/css/styles.css'),
            html.Link(rel='stylesheet', href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css'),
            html.Div(
                className="navbar",
                children =[
                    html.Div(
                        html.Button(
                            className="dropbtn",
                            id="button",
                            children=[
                                html.I(className='"bi bi-save-fill"'),
                                html.Span(children="Save")
                            ]
                        ),
                        dcc.Dropdown(
                            id='dropdown',
                            options=[
                                {'label': 'Option 1', 'value': 'option1'},
                                {'label': 'Option 2', 'value': 'option2'},
                                {'label': 'Option 3', 'value': 'option3'}
                            ],
                            value='option1'
                        )
                    ),
                ],

            ),
        ],
),





