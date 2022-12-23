# useful imports
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
from helpers.load import load_interventions
from dateutil.relativedelta import relativedelta
from helpers.vars import helper_langs, interventions_helper, int_c, int_ls
from dash import Dash, dcc, html, Input, Output
from helpers.plot import set_size, plot_dates, plot_intervention, plot_cumm_diff

pd.options.mode.chained_assignment = None  # default='warn'
import math
from statsmodels.stats import diagnostic
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from helpers import Wiki
import jupyterlab_dash
import plotly
import plotly.graph_objects as go
import plotly.io as pio


def wiki_query(code, language):
    """
    Will return a dataframe of the Wikipedia articles falling within a certain
    category with the associated genre for a given language
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
        PREFIX bd: <http://www.bigdata.com/rdf#>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>

    select  ?objet ?objectLabel ?genreLabel ?url
    where {
        ?object wdt:P31 wd:{}.
        ?object wdt:P136 ?genre.
        SERVICE wikibase:label {
        bd:serviceParam wikibase:language {}.
        }
    }
    """.format(code, language))
    sparql.setReturnFormat(JSON)
    books_result = sparql.query().convert()
    book_genre_df = pd.json_normalize(books_result['results']['bindings'])
    return book_genre_df


def get_monthly_count(code, name, start_date, end_date):
    """
    Will return a dataframe of the monthly count-views of an article for the period given and a chosen language
    """

    url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{}.wikipedia/all-access/all-agents/{' \
          '}/monthly/{}/{}'.format(code, name, start_date, end_date)
    response = urlopen(url)
    data_json = json.loads(response.read())
    df = pd.json_normalize(data_json['items'])
    return df


def get_daily_count(code, name, start_date, end_date):
    """
    Will return a dataframe of the monthly count-views of an article for the period given and a chosen language
    """

    url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{}.wikipedia/all-access/all-agents/{' \
          '}/daily/{}/{}'.format(code, name, start_date, end_date)
    response = urlopen(url)
    data_json = json.loads(response.read())
    df = pd.json_normalize(data_json['items'])
    return df


def min_max_scaling(df):
    # copy the dataframe
    df_norm = df.copy()
    # apply min-max scaling
    for column in df_norm.columns[0:-2]:
        df_norm[column] = (df_norm[column] - df_norm[column].min()) / (df_norm[column].max() - df_norm[column].min())

    return df_norm


def concatenate_results(code):
    en = pd.read_csv('data/{}_en.csv'.format(code))
    fr = pd.read_csv('data/{}_fr.csv'.format(code))
    it = pd.read_csv('data/{}_it.csv'.format(code))
    ja = pd.read_csv('data/{}_ja.csv'.format(code))
    data = [en, fr, it, ja]


    for l in range(len(data)):
        data[l].pop('Unnamed: 0')


    enn = pd.melt(en, id_vars=['dates', 'lang'], value_vars=en.columns, value_name='count')
    frr = pd.melt(fr, id_vars=['dates', 'lang'], value_vars=fr.columns, value_name='count')
    itt = pd.melt(it, id_vars=['dates', 'lang'], value_vars=it.columns, value_name='count')
    jaa = pd.melt(ja, id_vars=['dates', 'lang'], value_vars=ja.columns, value_name='count')

    frames = [enn, frr, itt, jaa]
    result = pd.concat(frames)
    result.to_csv('data/{}_concat.csv'.format(code))

    return result, data


def dist_from_normality(code):
    en = pd.read_csv('data/{}_en.csv'.format(code))
    fr = pd.read_csv('data/{}_fr.csv'.format(code))
    it = pd.read_csv('data/{}_it.csv'.format(code))
    ja = pd.read_csv('data/{}_ja.csv'.format(code))
    data = [en, fr, it, ja]


    for l in range(len(data)):
        data[l].pop('Unnamed: 0')


    en_2019 = en.loc[0:364]
    fr_2019 = fr.loc[0:364]
    it_2019 = it.loc[0:364]
    ja_2019 = ja.loc[0:364]

    normality_dist_en = en
    normality_dist_en.iloc[:, 0:-2] = abs(normality_dist_en.iloc[:, 0:-2] - en_2019.iloc[:, 0:-2].mean())
    normality_dist_fr = fr
    normality_dist_fr.iloc[:, 0:-2] = abs(normality_dist_fr.iloc[:, 0:-2] - fr_2019.iloc[:, 0:-2].mean())
    normality_dist_it = it
    normality_dist_it.iloc[:, 0:-2] = abs(normality_dist_it.iloc[:, 0:-2] - it_2019.iloc[:, 0:-2].mean())
    normality_dist_ja = ja
    normality_dist_ja.iloc[:, 0:-2] = abs(normality_dist_ja.iloc[:, 0:-2] - ja_2019.iloc[:, 0:-2].mean())

    enn = pd.melt(normality_dist_en, id_vars=['dates', 'lang'], value_vars=en.columns, value_name='count')
    frr = pd.melt(normality_dist_fr, id_vars=['dates', 'lang'], value_vars=fr.columns, value_name='count')
    itt = pd.melt(normality_dist_it, id_vars=['dates', 'lang'], value_vars=it.columns, value_name='count')
    jaa = pd.melt(normality_dist_ja, id_vars=['dates', 'lang'], value_vars=ja.columns, value_name='count')

    frames = [enn, frr, itt, jaa]
    result_concat = pd.concat(frames)
    result_concat.to_csv('data/{}_normality_dist.csv'.format(code))

    return result_concat, [normality_dist_en,normality_dist_fr,normality_dist_it,normality_dist_ja]

def dist_from_normality2(code):
    en = pd.read_csv('data/{}_en.csv'.format(code))
    fr = pd.read_csv('data/{}_fr.csv'.format(code))
    it = pd.read_csv('data/{}_it.csv'.format(code))
    ja = pd.read_csv('data/{}_ja.csv'.format(code))
    data = [en, fr, it, ja]


    for l in range(len(data)):
        data[l].pop('Unnamed: 0')


    en_2019 = en.loc[0:364]
    fr_2019 = fr.loc[0:364]
    it_2019 = it.loc[0:364]
    ja_2019 = ja.loc[0:364]

    normality_dist_en = en
    normality_dist_en.iloc[:, 0:-2] = abs(normality_dist_en.iloc[:, 0:-2] - stats.gmean(en_2019.iloc[:, 0:-2],axis=0))/stats.gmean(en_2019.iloc[:, 0:-2],axis=0)
    normality_dist_fr = fr
    normality_dist_fr.iloc[:, 0:-2] = abs(normality_dist_fr.iloc[:, 0:-2] - stats.gmean(fr_2019.iloc[:, 0:-2],axis=0))/stats.gmean(fr_2019.iloc[:, 0:-2],axis=0)
    normality_dist_it = it
    normality_dist_it.iloc[:, 0:-2] = abs(normality_dist_it.iloc[:, 0:-2] - stats.gmean(it_2019.iloc[:, 0:-2],axis=0))/stats.gmean(it_2019.iloc[:, 0:-2],axis=0)
    normality_dist_ja = ja
    normality_dist_ja.iloc[:, 0:-2] = abs(normality_dist_ja.iloc[:, 0:-2] - stats.gmean(ja_2019.iloc[:, 0:-2],axis=0))/stats.gmean(ja_2019.iloc[:, 0:-2],axis=0)



    enn = pd.melt(normality_dist_en, id_vars=['dates', 'lang'], value_vars=en.columns, value_name='count')
    frr = pd.melt(normality_dist_fr, id_vars=['dates', 'lang'], value_vars=fr.columns, value_name='count')
    itt = pd.melt(normality_dist_it, id_vars=['dates', 'lang'], value_vars=it.columns, value_name='count')
    jaa = pd.melt(normality_dist_ja, id_vars=['dates', 'lang'], value_vars=ja.columns, value_name='count')

    frames = [enn, frr, itt, jaa]
    result_concat = pd.concat(frames)
    result_concat.to_csv('data/{}_normality_dist.csv'.format(code))

    return result_concat, [normality_dist_en,normality_dist_fr,normality_dist_it,normality_dist_ja]


def plotly_plot_log(df, interventions,title):

    lineplt_fr = px.line(data_frame = df[df["lang"] == 'fr'],
                         x="dates",
                         y="count",
                         color="variable")
    lineplt_fr.update_yaxes(type="log")

    lineplt_en = px.line(data_frame = df[df["lang"] == 'en'],
                         x="dates",
                         y="count",
                         color="variable")
    lineplt_en.update_yaxes(type="log")
    lineplt_it = px.line(data_frame = df[df["lang"] == 'it'],
                         x="dates",
                         y="count",
                         color="variable")
    lineplt_it.update_yaxes(type="log")
    lineplt_ja = px.line(data_frame = df[df["lang"] == 'ja'],
                         x="dates",
                         y="count",
                         color="variable")
    lineplt_ja.update_yaxes(type="log")
    lineplt_fr.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="royalblue"),
            name=f"French, Mobility/Normalcy",
            legendgroup="down",
        ))
    lineplt_it.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="seagreen"),
            name=f"Italy, Mobility/Normalcy",
            legendgroup="down",
        ))
    lineplt_en.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="grey"),
            name=f"English, Mobility/Normalcy",
            legendgroup="down",
        ))
    lineplt_ja.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="red"),
            name=f"Japan, Mobility/Normalcy",
            legendgroup="down",)
    )


    ### Your original setup
    lineplt = px.line(data_frame=df[df["lang"] == 'fr'],
                      x="dates",
                      y="count",
                      color="variable")
    lineplt.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=12,color="royalblue"),
            name=f"French, Mobility/Normalcy",
            legendgroup="down"
        ))

    lineplt.add_vrect(x0=interventions['fr']['Normalcy'], x1=interventions['fr']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top left",
                      line_color="royalblue", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['it']['Normalcy'], x1=interventions['it']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top left",
                      line_color="seagreen", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['en']['Normalcy'], x1=interventions['en']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top right",
                      line_color="grey", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['ja']['Normalcy'], x1=interventions['ja']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top right",
                      line_color="red", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['fr']['Mobility'], x1=interventions['fr']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="royalblue", opacity=1, line_width=2,line_dash="dot",name="A")
    lineplt.add_vrect(x0=interventions['en']['Mobility'], x1=interventions['en']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="grey", opacity=0.8, line_width=2,line_dash="dot",name="A")
    lineplt.add_vrect(x0=interventions['it']['Mobility'], x1=interventions['it']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="seagreen", opacity=1, line_width=2,line_dash="dot",name="A")
    lineplt.add_vrect(x0=interventions['ja']['Mobility'], x1=interventions['ja']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="red", opacity=1, line_width=2,line_dash="dot",name="A")

    lineplt.update_yaxes(type="log")

    updatemenus = [
        {'buttons': [
            {
                'method': 'restyle',
                'label': 'Fr',
                'args': [{'y': [dat.y for dat in lineplt_fr.data],'name':[dat.name for dat in lineplt_fr.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_fr.data]}]
            },
            {
                'method': 'restyle',
                'label': 'En',
                'args': [{'y': [dat.y for dat in lineplt_en.data],'name':[dat.name for dat in lineplt_en.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_en.data]}]
            },
            {
                'method': 'restyle',
                'label': 'It',
                'args': [{'y': [dat.y for dat in lineplt_it.data],'name':[dat.name for dat in lineplt_it.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_it.data]}]
            },
            {
                'method': 'restyle',
                'label': 'Ja',
                'args': [{'y': [dat.y for dat in lineplt_ja.data],'name':[dat.name for dat in lineplt_ja.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_ja.data]}]
            }
        ],
            'direction': 'down',
            'showactive': True,
        }
    ]

    lineplt = lineplt.update_layout(
        title_text=f'{title}',
        title_x=0.5,

        xaxis_showgrid=False,
        yaxis_showgrid=False,

        legend=dict(title='variable',
                    x=1.3,
                    y=1,
                    traceorder='normal',
                    xanchor = 'auto'),
        updatemenus=updatemenus
    )
    lineplt = lineplt.update_traces(mode="lines",
                                    selector=dict(mode="markers"),
                                    )
    lineplt.update_yaxes(type="log")
    lineplt.update_annotations()
    return lineplt

def plotly_plot(df, interventions,title):

    lineplt_fr = px.line(data_frame = df[df["lang"] == 'fr'],
                         x="dates",
                         y="count",
                         color="variable")

    lineplt_en = px.line(data_frame = df[df["lang"] == 'en'],
                         x="dates",
                         y="count",
                         color="variable")

    lineplt_it = px.line(data_frame = df[df["lang"] == 'it'],
                         x="dates",
                         y="count",
                         color="variable")

    lineplt_ja = px.line(data_frame = df[df["lang"] == 'ja'],
                         x="dates",
                         y="count",
                         color="variable")

    lineplt_fr.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="royalblue"),
            name=f"French, Mobility/Normalcy",
            legendgroup="down",
        ))
    lineplt_it.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="seagreen"),
            name=f"Italy, Mobility/Normalcy",
            legendgroup="down",
        ))
    lineplt_en.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="grey"),
            name=f"English, Mobility/Normalcy",
            legendgroup="down",
        ))
    lineplt_ja.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="red"),
            name=f"Japan, Mobility/Normalcy",
            legendgroup="down",)
    )


    ### Your original setup
    lineplt = px.line(data_frame=df[df["lang"] == 'fr'],
                      x="dates",
                      y="count",
                      color="variable")
    lineplt.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=12,color="royalblue"),
            name=f"French, Mobility/Normalcy",
            legendgroup="down"
        ))

    lineplt.add_vrect(x0=interventions['fr']['Normalcy'], x1=interventions['fr']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top left",
                      line_color="royalblue", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['it']['Normalcy'], x1=interventions['it']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top left",
                      line_color="seagreen", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['en']['Normalcy'], x1=interventions['en']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top right",
                      line_color="grey", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['ja']['Normalcy'], x1=interventions['ja']['Normalcy'], row="all", col=1,
                      annotation_text='N', annotation_position="top right",
                      line_color="red", opacity=1, line_width=2,line_dash="dot")
    lineplt.add_vrect(x0=interventions['fr']['Mobility'], x1=interventions['fr']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="royalblue", opacity=1, line_width=2,line_dash="dot",name="A")
    lineplt.add_vrect(x0=interventions['en']['Mobility'], x1=interventions['en']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="grey", opacity=0.8, line_width=2,line_dash="dot",name="A")
    lineplt.add_vrect(x0=interventions['it']['Mobility'], x1=interventions['it']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="seagreen", opacity=1, line_width=2,line_dash="dot",name="A")
    lineplt.add_vrect(x0=interventions['ja']['Mobility'], x1=interventions['ja']['Mobility'], row="all", col=1,
                      annotation_text='M', annotation_position="top left",
                      line_color="red", opacity=1, line_width=2,line_dash="dot",name="A")


    updatemenus = [
        {'buttons': [
            {
                'method': 'restyle',
                'label': 'Fr',
                'args': [{'y': [dat.y for dat in lineplt_fr.data],'name':[dat.name for dat in lineplt_fr.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_fr.data]}]
            },
            {
                'method': 'restyle',
                'label': 'En',
                'args': [{'y': [dat.y for dat in lineplt_en.data],'name':[dat.name for dat in lineplt_en.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_en.data]}]
            },
            {
                'method': 'restyle',
                'label': 'It',
                'args': [{'y': [dat.y for dat in lineplt_it.data],'name':[dat.name for dat in lineplt_it.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_it.data]}]
            },
            {
                'method': 'restyle',
                'label': 'Ja',
                'args': [{'y': [dat.y for dat in lineplt_ja.data],'name':[dat.name for dat in lineplt_ja.data],'hovertemplate':[dat.hovertemplate for dat in lineplt_ja.data]}]
            }
        ],
            'direction': 'down',
            'showactive': True,
        }
    ]

    lineplt = lineplt.update_layout(
        title_text=f'{title}',
        title_x=0.5,

        xaxis_showgrid=False,
        yaxis_showgrid=False,

        legend=dict(title='variable',
                    x=1.3,
                    y=1,
                    traceorder='normal',
                    xanchor = 'auto'),
        updatemenus=updatemenus
    )
    lineplt = lineplt.update_traces(mode="lines",
                                    selector=dict(mode="markers"),
                                    )
    lineplt.update_annotations()
    return lineplt

def diff_in_diff(langue,df,interventions,scenario,variable):
    if scenario == 'a':
        m = interventions[langue]['Mobility']
        date_m_20 = datetime.strptime(m, "%Y-%m-%d")
        start_20 = date_m_20 - timedelta(days=20)
        end_20 = date_m_20 + timedelta(days=20)
        start_19 = start_20 - relativedelta(years=1)
        end_19 = end_20 - relativedelta(years=1)
        date_19 = date_m_20 - relativedelta(years=1)

        df2 = df.loc[df["dates"].between(start_20.strftime("%Y-%m-%d"), end_20.strftime("%Y-%m-%d"))| df["dates"].between(start_19.strftime("%Y-%m-%d"), end_19.strftime("%Y-%m-%d"))]
        df2['year'] = df2.dates.str.contains('2020')
        df2['year'] = df2['year'].replace({True: 1, False: 0})
        df2['period'] = 0
        df2.loc[df2.dates.between(date_19.strftime("%Y-%m-%d"), end_19.strftime("%Y-%m-%d"))| df2.dates.between(date_m_20.strftime("%Y-%m-%d"), end_20.strftime("%Y-%m-%d")),'period'] =1
        df2.iloc[:,0:-4]=np.log(df2.iloc[:,0:-4])

    if scenario == 'b':
        m = interventions[langue]['Mobility']
        n = interventions[langue]['Normalcy']
        date_m_20 = datetime.strptime(m, "%Y-%m-%d")
        date_n_20 = datetime.strptime(n, "%Y-%m-%d")
        end_m_20 = date_m_20 + timedelta(days=20)
        end_n_20 = date_n_20 + timedelta(days=20)
        start_m_19 = date_m_20 - relativedelta(years=1)
        end_m_19 = end_m_20 - relativedelta(years=1)
        start_n_19 = date_n_20 - relativedelta(years=1)
        end_n_19 = end_n_20 - relativedelta(years=1)

        df2 = df.loc[df["dates"].between(date_m_20.strftime("%Y-%m-%d"), end_m_20.strftime("%Y-%m-%d"))| df["dates"].between(date_n_20.strftime("%Y-%m-%d"), end_n_20.strftime("%Y-%m-%d"))| df["dates"].between(start_m_19.strftime("%Y-%m-%d"), end_m_19.strftime("%Y-%m-%d"))| df["dates"].between(start_n_19.strftime("%Y-%m-%d"), end_n_19.strftime("%Y-%m-%d"))]
        df2['year'] = df2.dates.str.contains('2020')
        df2['year'] = df2['year'].replace({True: 1, False: 0})
        df2['period'] = 0
        df2.loc[df2.dates.between(date_n_20.strftime("%Y-%m-%d"), end_n_20.strftime("%Y-%m-%d"))| df2.dates.between(start_n_19.strftime("%Y-%m-%d"), end_n_19.strftime("%Y-%m-%d")),'period'] =1
        df2.iloc[:,0:-4]=np.log(df2.iloc[:,0:-4])

    if scenario == 'c':
        m = interventions[langue]['Mobility']
        n = interventions[langue]['Normalcy']
        date_m_20 = datetime.strptime(m, "%Y-%m-%d")
        date_n_20 = datetime.strptime(n, "%Y-%m-%d")
        start_m_20 = date_m_20 - timedelta(days=20)
        end_n_20 = date_n_20 + timedelta(days=20)
        start_m_19 = start_m_20 - relativedelta(years=1)
        end_m_19 = date_m_20 - relativedelta(years=1)
        start_n_19 = date_n_20 - relativedelta(years=1)
        end_n_19 = end_n_20 - relativedelta(years=1)

        df2 = df.loc[df["dates"].between(start_m_20.strftime("%Y-%m-%d"), date_m_20.strftime("%Y-%m-%d"))| df["dates"].between(date_n_20.strftime("%Y-%m-%d"), end_n_20.strftime("%Y-%m-%d"))| df["dates"].between(start_m_19.strftime("%Y-%m-%d"), end_m_19.strftime("%Y-%m-%d"))| df["dates"].between(start_n_19.strftime("%Y-%m-%d"), end_n_19.strftime("%Y-%m-%d"))]
        df2['year'] = df2.dates.str.contains('2020')
        df2['year'] = df2['year'].replace({True: 1, False: 0})
        df2['period'] = 0
        df2.loc[df2.dates.between(date_n_20.strftime("%Y-%m-%d"), end_n_20.strftime("%Y-%m-%d"))| df2.dates.between(start_n_19.strftime("%Y-%m-%d"), end_n_19.strftime("%Y-%m-%d")),'period'] =1
        df2.iloc[:,0:-4]=np.log(df2.iloc[:,0:-4])

    mod = smf.ols(formula=f'{variable} ~ year*period', data=df2)
    res = mod.fit()

    return res

def bootstrapping(df,langue,interventions,value):
    #Bootstrapping

    baseline_lockdown = []
    baseline_normality = []
    lockdown_normality = []

    m = interventions[langue]['Mobility']
    date_m_20 = datetime.strptime(m, "%Y-%m-%d")
    start_20 = date_m_20 - timedelta(days=35)
    end_20 = date_m_20 + timedelta(days=35)
    n = interventions[langue]['Normalcy']
    date_n_20 = datetime.strptime(n, "%Y-%m-%d")
    end_n_20 = date_n_20 + timedelta(days=35)



    for i in range(0, 1000):
        sample_lockdown = df.loc[df["dates"].between(date_m_20.strftime("%Y-%m-%d"), end_20.strftime("%Y-%m-%d"))][value]
        sample_baseline = df.loc[df["dates"].between('2019-01-01', start_20.strftime("%Y-%m-%d"))][value]
        sample_normality = df.loc[df["dates"].between(date_n_20.strftime("%Y-%m-%d"), end_n_20.strftime("%Y-%m-%d"))][value]

        sample_baseline = sample_baseline.sample(n=10, replace=True)
        sample_lockdown = sample_lockdown.sample(n=10, replace=True)
        sample_normality = sample_normality.sample(n=10, replace=True)

        baseline_normality.append(sample_normality.mean() / sample_baseline.mean() - 1)
        lockdown_normality.append(sample_normality.mean() / sample_lockdown.mean() - 1)
        baseline_lockdown.append(sample_lockdown.mean() / sample_baseline.mean() - 1)

    baseline_lockdown.sort()
    lockdown_normality.sort()
    baseline_normality.sort()

    print('All games Baseline -> Lockdown 95% Confidence interval : [' + format(baseline_lockdown[25], '.2f') + ', ' + format(baseline_lockdown[975],'.2f') + ']')
    print('All games Baseline -> Normality 95% Confidence interval : [' + format(baseline_normality[25], '.2f') + ', ' + format(baseline_normality[975],'.2f') + ']')
    print('All games Lockdown -> Normality 95% Confidence interval : [' + format(lockdown_normality[25], '.2f') + ', ' + format(lockdown_normality[975],'.2f') + ']')

    baseline_lockdown_interval = [baseline_lockdown[25],baseline_lockdown[975]]
    baseline_normality_interval = [baseline_normality[25],baseline_normality[975]]
    lockdown_normality_interval = [lockdown_normality[25],lockdown_normality[975]]

    intervals = [baseline_lockdown_interval,baseline_normality_interval,lockdown_normality_interval]
    return intervals