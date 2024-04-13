import re
from preparations import find_company_name
import math
def iterare(mes_to_ids, news_train, mes_to_index, dictionary_companies):
    succes = 0
    i = 0

    #проходим сразу по сообщениям с указанными компаниями
    for mes_id in mes_to_ids:
        if i > 1000:
            break

        i += len(mes_to_ids[mes_id])

        #индекс новсти в табличке
        news = news_train.iloc[mes_to_index[mes_id]]

        # 223 компании вообще нет
        if news.issuerid not in dictionary_companies:
            continue

        company = dictionary_companies[news.issuerid]
        company_names = company['EMITENT_FULL_NAME']

        company_tickers = [company['BGTicker']] + [company['OtherTicker']]
        company_tickers = [x.split()[0] for x in company_tickers if not isinstance(x, float) or not math.isnan(x)]
        text = news.MessageText


        matches_tickers = re.findall(r'(?<=\$)\[A-Z]+|[A-Z]{4,6}', text) #нашли тикеры
        founded_tickers_by_name = find_company_name(text, dictionary_companies)  # тикеры по названиям

        matches_tickers = set(matches_tickers) | set(founded_tickers_by_name)


        if len(matches_tickers) > 0:
            companies_ids = mes_to_ids[mes_id]
            if 253 in companies_ids:
                companies_ids.remove(253)
            real_tickers = [dictionary_companies[id]['BGTicker'] for id in companies_ids] + [dictionary_companies[id]['OtherTicker']  for id in companies_ids]
            real_tickers = [x.split()[0] for x in real_tickers if not isinstance(x, float) or not math.isnan(x)]

            succes += len(set(real_tickers) & set(matches_tickers))

        print(succes, i)

    print(succes / len(news_train))

#66% точности