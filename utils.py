import os
import pickle
import re
import numpy as np
import pandas as pd
import torch
import math
import nltk


# словарь новость - компании
def create_dict_mes_ids(df: pd.DataFrame) -> dict:
    dic = dict()
    for i in range(len(df)):
        if df.iloc[i].messageid in dic:
            dic[df.iloc[i].messageid].append(df.iloc[i].issuerid)
        else:
            dic[df.iloc[i].messageid] = [df.iloc[i].issuerid]
    return dic


# возвращает дата фрейм комапний, словарь айди компании:
# данные, словарь тикер компании: индекс компании, сет всех компаний
def get_dictionaries(
        path=os.path.dirname(os.getcwd()) + '/data/issuers_modified.xlsx') -> \
        (pd.DataFrame, dict, dict, list):
    df = pd.read_excel(path)
    dictionary_companies = df.set_index('issuerid').to_dict(orient='index')
    dictionary_companies_by_ticker = dict()
    companies = set()
    for key in dictionary_companies:
        names = dictionary_companies[key]["EMITENT_FULL_NAME"]
        names_splitted = re.findall(r'"([^"]*)"', names)
        dictionary_companies[key]["EMITENT_FULL_NAME"] = names_splitted
        tickers = [dictionary_companies[key]['BGTicker']] + [
            dictionary_companies[key]['OtherTicker']]
        tickers = [x.split()[0] for x in tickers if
                   not isinstance(x, float) or not math.isnan(x)]

        for ticker in tickers:
            dictionary_companies_by_ticker[ticker] = key

        for x in names_splitted:
            companies.add(x.lower())

    return df, dictionary_companies, dictionary_companies_by_ticker, companies


# словарь индекс сообщения: список индексов компаний
def create_dict_mes_to_index(ms_to_copm: list, df: pd.DataFrame) -> dict:
    dic = dict()

    for ms_id in ms_to_copm:
        index = df.index[df['messageid'] == ms_id]
        dic[ms_id] = index[0]
    return dic


def get_all_tickers(df: pd.DataFrame) -> set:
    df1 = df.dropna(subset=['BGTicker'])
    df2 = df.dropna(subset=['OtherTicker'])

    t1 = ' '.join(df1['BGTicker']).split()
    t2 = ' '.join(df2['OtherTicker']).split()

    all_tickers = (set(t1) | set(t2)) - set(['RX', 'LI'])
    return all_tickers


def extract_words(text: str) -> list[str]:
    word_pattern = re.compile(r'[а-яА-я]+\b')
    words = word_pattern.findall(text)
    words = [w.lower() for w in words]
    return words


def find_company_name(text: str, dic: dict) -> list:
    tickers = []
    words = extract_words(text)

    for comp_id in dic:
        names = dic[comp_id]['EMITENT_FULL_NAME']
        names = [n.lower() for n in names]

        flag = True in [find_word_in_sentence(n, text) for n in names]

        # если нашли то добавить тикер
        if len(set(words) & set(names)) > 0 or flag:
            tickers.append(dic[comp_id]['BGTicker'])
            tickers.append(dic[comp_id]['OtherTicker'])
    tickers = [x.split()[0] for x in tickers if
               not isinstance(x, float) or not math.isnan(x)]

    return tickers


def is_one_letter_different(word1: str, word2: str) -> bool:
    if abs(len(word1) - len(word2)) > 1:
        return False

    if len(word1) > len(word2):
        if word1[:-1] == word2:
            return True
        else:
            return False

    elif len(word1) < len(word2):
        if word1 == word2[:-1]:
            return True
        else:
            return False

    return word1[:-1] == word2[:-1]


def find_word_in_sentence(word: str, sentence: str) -> bool:
    for word2 in sentence.split():
        if len(word2) > 3:
            if is_one_letter_different(word, word2):
                return True

    return False


# Splitting Text into Sentences
def split_text_into_sentences(test_text: str) -> list[str]:
    nltk.download('punkt')
    test_text = ' '.join([w.lower() for w in test_text.split()])
    sentences = nltk.sent_tokenize(test_text)
    return sentences


def split_news_on_companies(text: str, dictionary_companies: dict,
                            all_tickers: list,
                            dictionary_companies_by_ticker: dict) -> (
        list[str], dict):
    sentences = split_text_into_sentences(text)
    companies_by_index = dict()
    for i in range(len(sentences)):

        sentence = sentences[i]
        sentence = re.sub('[,;:"\>!]', '', sentence)
        for company_ind in dictionary_companies:
            for comp_name in dictionary_companies[company_ind][
                'EMITENT_FULL_NAME']:
                if find_word_in_sentence(comp_name.lower(), sentence):
                    # print(i, comp_name)
                    if i in companies_by_index:
                        companies_by_index[i].add(company_ind)

                    else:
                        companies_by_index[i] = {company_ind}

        for ticker in all_tickers:

            if ticker.lower() in sentence:
                if i in companies_by_index:
                    companies_by_index[i].add(
                        dictionary_companies_by_ticker[ticker])

                else:
                    companies_by_index[i] = {
                        dictionary_companies_by_ticker[ticker]}
    return sentences, companies_by_index
