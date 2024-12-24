import threading
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

from voting_aid_methods import get_topics_and_descriptions, get_parties_context_of_political_positions

app = dash.Dash(__name__)

party_colors = {
    "afd": "#009EE0",
    "bsw": "#4B0082",
    "fdp": "#FFED00",
    "gruene": "#64A12D",
    "linke": "#BE3075",
    "spd": "#E3000F",
    "union": "#000000"
}

app.layout = html.Div([
    html.H1("VotingAid"),
    dcc.Textarea(
        id='political-position-input',
        placeholder='Please explain your political positions...',
        style={'width': '100%', 'height': 200},
    ),
    html.Button('Analyze', id='analyze-button', n_clicks=0),
    html.Div(id='topics-positions-container'),
    html.Button('Add Topic and Position', id='add-topic-position-button', n_clicks=0),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='final-score-output')
])

@app.callback(
    Output('topics-positions-container', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('political-position-input', 'value')
)
def analyze_political_position(n_clicks, political_position):
    if n_clicks == 0:
        return []

    if not political_position: # To make debugging easier

        political_position = ("Für mich ist der Zugang zu einem starken Gesundheitssystem ein Grundpfeiler einer gerechten Gesellschaft. "
                              "Jeder Mensch sollte unabhängig von Einkommen oder Wohnort eine qualitativ hochwertige medizinische Versorgung erhalten. "
                              "Daher halte ich es für notwendig, dass die Politik stärker in öffentliche Gesundheitsstrukturen investiert und den Zugang zu Präventionsmaßnahmen wie Impfungen oder regelmäßigen Untersuchungen erleichtert. "
                              "Besonders wichtig ist mir hierbei auch die mentale Gesundheit, die oft vernachlässigt wird und dringend mehr Aufmerksamkeit erfordert. "
                              "Bildung ist für mich das wichtigste Mittel, um Chancengleichheit zu schaffen. Ein freier und gleicher Zugang zu Bildung sollte für alle Menschen selbstverständlich sein, angefangen bei der frühkindlichen Förderung bis hin zu lebenslangem Lernen. "
                              "Ich glaube, dass wir dringend mehr in Schulen, Lehrpersonal und digitale Infrastruktur investieren müssen, um sicherzustellen, dass Kinder und Jugendliche die bestmögliche Ausbildung erhalten, unabhängig von ihrem sozialen Hintergrund. "
                              "Ein weiteres Thema, das mir wichtig ist, ist der öffentliche Verkehr. Ich bin der Überzeugung, dass eine bessere Infrastruktur im Nah- und Fernverkehr nicht nur unsere Lebensqualität verbessert, sondern auch die Umwelt schützt. "
                              "Der Ausbau von Schienenverkehr und emissionsfreien Verkehrsmitteln sollte daher im Mittelpunkt einer nachhaltigen Verkehrspolitik stehen. "
                              "Gleichzeitig müssen Tickets erschwinglicher werden, um den öffentlichen Verkehr für alle attraktiv zu machen.")

    topics, positions = get_topics_and_descriptions(political_position)

    topics_positions_inputs = [
        html.Div([
            dcc.Markdown(f"**Topic:**"),
            dcc.Textarea(
                id={'type': 'topic-input', 'index': i},
                value=topic,
                style={'width': '100%', 'height': 50}
            ),
            dcc.Markdown(f"**Position:**"),
            dcc.Textarea(
                id={'type': 'position-input', 'index': i},
                value=position,
                style={'width': '100%', 'height': 100}
            )
        ], style={'border': '1px solid black', 'padding': '10px', 'margin-bottom': '10px'})
        for i, (topic, position) in enumerate(zip(topics, positions))
    ]

    return topics_positions_inputs

@app.callback(
    Output('topics-positions-container', 'children', allow_duplicate=True),
    Input('add-topic-position-button', 'n_clicks'),
    State('topics-positions-container', 'children'),
    prevent_initial_call=True
)
def add_topic_position(n_clicks, children):
    new_div = html.Div([
        dcc.Markdown(f"**Topic:**"),
        dcc.Textarea(
            id={'type': 'topic-input', 'index': n_clicks},
            value='',
            style={'width': '100%', 'height': 50}
        ),
        dcc.Markdown(f"**Position:**"),
        dcc.Textarea(
            id={'type': 'position-input', 'index': n_clicks},
            value='',
            style={'width': '100%', 'height': 100}
        )
    ], style={'border': '1px solid black', 'padding': '10px', 'margin-bottom': '10px'})
    children.append(new_div)
    return children

def perform_analysis(parties, topics, positions, max_answer_length, output):
    final_score = get_parties_context_of_political_positions(parties, topics, positions, max_answer_length)
    output.append(final_score)

@app.callback(
    Output('final-score-output', 'children'),
    Input('submit-button', 'n_clicks'),
    State({'type': 'topic-input', 'index': dash.dependencies.ALL}, 'value'),
    State({'type': 'position-input', 'index': dash.dependencies.ALL}, 'value')
)
def submit_analysis(n_clicks, topics, positions):
    if n_clicks == 0:
        return ""

    parties = ["spd", "union", "gruene", "fdp", "afd", "linke", "bsw"]
    max_answer_length = 600
    output = []
    analysis_thread = threading.Thread(target=perform_analysis,
                                       args=(parties, topics, positions, max_answer_length, output))
    analysis_thread.start()
    analysis_thread.join()

    final_score = output[0]

    final_score = dict(sorted(final_score.items(), key=lambda item: item[1]['total'], reverse=True))
    party_boxes = []
    for party, scores in final_score.items():
        party_box = html.Div([
            html.Div([
                html.H3(party, style={'display': 'inline-block'}),
                html.H3(f"Total: {scores['total']:.2f}", style={'display': 'inline-block', 'float': 'right'})
            ]),
            html.Div([
                html.Div([
                    html.H4(topic),
                    html.P(f"Rating: {details['rating']}"),
                    html.P(details['detailed_answer'])
                ], style={'border': '1px solid black', 'padding': '10px', 'margin-bottom': '10px'})
                for topic, details in scores.items() if topic != 'total'
            ])
        ], style={'border': f'2px solid {party_colors[party]}', 'padding': '10px', 'margin-bottom': '10px'})
        party_boxes.append(party_box)

    return party_boxes

if __name__ == '__main__':
    try:
        app.run_server(debug=True)
    except OSError as e:
        print(f"An error occurred: {e}")