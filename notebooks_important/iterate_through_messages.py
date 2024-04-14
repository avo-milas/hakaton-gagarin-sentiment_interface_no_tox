import re
from utils import find_company_name, split_news_on_companies
import math
import pandas as pd


def iterate(mes_to_ids: list, news_train: pd.DataFrame, mes_to_index: dict,
            dictionary_companies: dict) -> None:
    succes = 0
    i = 0

    # проходим сразу по сообщениям с указанными компаниями
    for mes_id in mes_to_ids:

        i += len(mes_to_ids[mes_id])

        # индекс новсти в табличке
        news = news_train.iloc[mes_to_index[mes_id]]

        # 223 компании вообще нет
        if news.issuerid not in dictionary_companies:
            continue

        company = dictionary_companies[news.issuerid]

        company_tickers = [company['BGTicker']] + [company['OtherTicker']]
        company_tickers = [x.split()[0] for x in company_tickers if
                           not isinstance(x, float) or not math.isnan(x)]
        text = news.MessageText

        matches_tickers = re.findall(r'(?<=\$)\[A-Z]+|[A-Z]{4,6}',
                                     text)  # нашли тикеры
        founded_tickers_by_name = find_company_name(text,
                                                    dictionary_companies)

        matches_tickers = set(matches_tickers) | set(founded_tickers_by_name)

        if len(matches_tickers) > 0:
            companies_ids = mes_to_ids[mes_id]
            if 253 in companies_ids:
                companies_ids.remove(253)
            real_tickers = [dictionary_companies[id]['BGTicker'] for id in
                            companies_ids] + [
                               dictionary_companies[id]['OtherTicker'] for id
                               in
                               companies_ids]
            real_tickers = [x.split()[0] for x in real_tickers if
                            not isinstance(x, float) or not math.isnan(x)]

            succes += len(set(real_tickers) & set(matches_tickers))

        print(succes, i)

    print(succes / len(news_train))


# 66% точности


# не дописал, функция для сентимента (news_train)
def iterare_and_give_sentiments(mes_to_ids: dict, news_train, mes_to_index,
                                dictionary_companies: dict, all_tickers,
                                dictionary_companies_by_ticker: dict) -> None:
    succes = 0
    i = 0

    # проходим сразу по сообщениям с указанными компаниями
    for mes_id in mes_to_ids:
        i += len(mes_to_ids[mes_id])

        # индекс новости в табличке
        news = news_train.iloc[mes_to_index[mes_id]]

        # 223 компании вообще нет
        if news.issuerid not in dictionary_companies:
            continue

        company = dictionary_companies[news.issuerid]

        company_tickers = [company['BGTicker']] + [company['OtherTicker']]
        company_tickers = [x.split()[0] for x in company_tickers if
                           not isinstance(x, float) or not math.isnan(x)]
        text = news.MessageText

        sentences, companies_by_index = split_news_on_companies(text,
                                                                dictionary_companies,
                                                                all_tickers,
                                                                dictionary_companies_by_ticker)

        # sentence - все предложения, companies_by_index - индексы предложений
        # если в 1 предложении 2 компании то гг, отсавляем 2 и прогноз для двух

        # ВАШ КОД ЗДЕСЬ #######################################################

        #######################################################################

        matches_tickers = re.findall(r'(?<=\$)\[A-Z]+|[A-Z]{4,6}',
                                     text)  # нашли тикеры
        founded_tickers_by_name = find_company_name(text,
                                                    dictionary_companies)

        matches_tickers = set(matches_tickers) | set(founded_tickers_by_name)

        if len(matches_tickers) > 0:
            companies_ids = mes_to_ids[mes_id]
            if 253 in companies_ids:
                companies_ids.remove(253)
            real_tickers = [dictionary_companies[id]['BGTicker'] for id in
                            companies_ids] + [
                               dictionary_companies[id]['OtherTicker'] for id
                               in
                               companies_ids]
            real_tickers = [x.split()[0] for x in real_tickers if
                            not isinstance(x, float) or not math.isnan(x)]

            succes += len(set(real_tickers) & set(matches_tickers))

        print(succes, i)

    print(succes / len(news_train))
