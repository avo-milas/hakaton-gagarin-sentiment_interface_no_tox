import pickle
import re
import numpy as np
import pandas as pd
import torch
import math

#словарь новость - компании
def create_dict_mes_ids(df):
    dic = dict()
    for i in range(len(df)):
        if df.iloc[i].messageid in dic:
            dic[df.iloc[i].messageid].append(df.iloc[i].issuerid)
        else:
            dic[df.iloc[i].messageid] = [df.iloc[i].issuerid]
    return dic

#возвращает дата врейм комапний, словарь айди компании: данные, словарь тикер компании: индекс компании, сет всех компаний
def get_dictionaries(path = 'sentiment_dataset/issuers_modified.xlsx'):
    df = pd.read_excel(path)
    dictionary_companies = df.set_index('issuerid').to_dict(orient='index')
    dictionary_companies_by_ticker = dict()
    companies = set()
    for key in dictionary_companies:
        names = dictionary_companies[key]["EMITENT_FULL_NAME"]
        names_splitted = re.findall(r'"([^"]*)"', names)
        dictionary_companies[key]["EMITENT_FULL_NAME"] = names_splitted
        tickers = [dictionary_companies[key]['BGTicker']] + [dictionary_companies[key]['OtherTicker']]
        tickers = [x.split()[0] for x in tickers if not isinstance(x, float) or not math.isnan(x)]

        for ticker in tickers:
            dictionary_companies_by_ticker[ticker] = key

        for x in names_splitted:
            companies.add(x.lower())

    return df, dictionary_companies, dictionary_companies_by_ticker, companies

#словарь индекс сообщения: список индексов компаний
def create_dict_mes_to_index(ms_to_copm, df):
    dic = dict()

    for ms_id in ms_to_copm:
        index = df.index[df['messageid'] == ms_id]
        dic[ms_id] = index[0]
    return dic

def get_all_tickers(df):
    df1 = df.dropna(subset=['BGTicker'])
    df2 = df.dropna(subset=['OtherTicker'])

    t1 = ' '.join(df1['BGTicker']).split()
    t2 = ' '.join(df2['OtherTicker']).split()

    all_tickers = (set(t1) | set(t2)) - set(['RX', 'LI'])
    return all_tickers

def extract_words(text):

    word_pattern = re.compile(r'[а-яА-я]+\b')
    words = word_pattern.findall(text)
    words = [w.lower() for w in words]
    return words


def find_company_name(text, dic):
    tickers = []
    words = extract_words(text)

    for comp_id in dic:
        names = dic[comp_id]['EMITENT_FULL_NAME']
        names = [n.lower() for n in names]

        #если нашли то добавить тикер
        if len(set(words) & set(names)) > 0:
            tickers.append(dic[comp_id]['BGTicker'])
            tickers.append(dic[comp_id]['OtherTicker'])
    tickers = [x.split()[0] for x in tickers if not isinstance(x, float) or not math.isnan(x)]

    return tickers
