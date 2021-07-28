import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly_express as px

from gensim import corpora
import gensim
import pyLDAvis
import nltk

from nltk import pos_tag, word_tokenize
import spacy
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from spacy import displacy
nlp = spacy.load("en_core_web_sm")


# containers
header = st.beta_container()
dataset = st.beta_container()
interactive = st.beta_container()


#SIDE BARS
TM = st.sidebar.checkbox('Topic Modelling')
NER = st.sidebar.checkbox('NER: Named Entity Recognition')

# data sets functions
@st.cache
def get_data(filename):
    data = pd.read_csv(filename)
    return data


with header:
    st.title("NLP for Quantified-Self Forum")
    st.subheader("This project will give an overview of Forum's interactions and offer an interactive dashboard"
                 " to discover topics discussed about")

    st.image('Data_Viz/qs_wordcloud.png')
    st.sidebar.title("Side Menu")
    st.sidebar.write("-----------")
    st.sidebar.write("**Visualizations:** ")


with dataset:
    st.header('QS forum dataset')
    st.text('The dataset was extracted from QS website using Python to parse the JSON files')

    qs_data = get_data('https://media.githubusercontent.com/media/KaoutarLanjri/large_files/master/global_df.csv')
    st.write(qs_data.head())

    st.subheader('Distribution of Yearly Created Posts')
    docs_list = pd.DataFrame(qs_data['date_year'].value_counts())
    st.bar_chart(docs_list)

with interactive:
    st.title('Closer look into the data')

    fig = go.Figure(data=go.Table(
                columnwidth=[1, 1, 3, 3],
                header=dict(values=list(qs_data[['topic_id', 'creation_date', 'noHTML_text', 'lemmat_text']].columns),
                fill_color='#FD8E72',
                align='center'),
                cells=dict(values=[qs_data.topic_id, qs_data.creation_date, qs_data.noHTML_text, qs_data.lemmat_text])))

    fig.update_layout(margin=dict(l=5, r=5, b=10, t=10))
    st.write(fig)

    # LINE CHART for Word occurence over time*

# ALL TIME
    words_freq = get_data(
        'https://raw.githubusercontent.com/KaoutarLanjri/quantified-self-forums/main/datasets/words_df.csv')

    fig = px.line(words_freq, x=words_freq.creation_year, y=words_freq.columns[0:30],
                  title="Word Dispersion over time 2011 to 2021")

    fig.update_xaxes(type='category')
    st.write(fig)

# 2021
    words21_freq = get_data(
        'https://raw.githubusercontent.com/KaoutarLanjri/quantified-self-forums/main/datasets/words_df_2021.csv')

    fig = px.line(words21_freq, x=words21_freq.creation_date, y=words21_freq.columns[0:30],
                  title="Word Dispersion over the year 2021")

    fig.update_xaxes(type='category')
    st.write(fig)

    # TOPIC MODELLING

# Tokenize Text
def tokenize_text(text):
    filtered_text = []
    words = word_tokenize(text)

    for word in words:
        filtered_text.append(word)
    return filtered_text
#
df = qs_data.copy()

df['no_sw_LDA_text'] = df['no_sw_LDA_text'].astype('str')

df = df.groupby(['topic_id'], as_index = False).agg({('no_sw_LDA_text'): ' '.join})


