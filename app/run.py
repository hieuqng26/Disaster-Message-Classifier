import json
import plotly
import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from sklearn.externals import joblib
from sqlalchemy import create_engine


app = Flask(__name__)


def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('DisasterResponse', engine)

# load model
model = joblib.load("../models/nbsvm.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():

    #############
    ### PLOT 1 ##
    #############
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)

    data1 = [
        Bar(
            x=genre_names,
            y=genre_counts
        )
    ]

    layout1 = {
        'title': 'Distribution of Message Genres',
        'yaxis': {
            'title': "Count"
        },
        'xaxis': {
            'title': "Genre"
        }
    }

    #############
    ### PLOT 2 ##
    #############
    # Grouped Bar chart by genres for most classified categories
    numeric_df = df.drop(['id', 'message', 'original'], axis=1)
    by_genre = numeric_df.groupby('genre').aggregate('sum')

    # Find labels that are classified most oftern
    top_labels = by_genre.sum().sort_values(ascending=False)[:5].index
    ext_genre = by_genre[top_labels]
    categories = ext_genre.index

    data2 = []
    for col in ext_genre.columns:
        data2.append(Bar(
            x=categories,
            y=ext_genre[col].values,
            name=col
        ))

    layout2 = {
        'barmode': 'group',
        'title': 'Top Message Categories by Genres',

        'yaxis': {
            'title': "Count"
        },

        'xaxis': {
            'title': "Genre"
        }
    }

    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': data1,
            'layout': layout1
        },

        {
            'data': data2,
            'layout': layout2
        }
    ]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    # image = return_image(df)

    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '')

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file.
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
