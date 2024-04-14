import typing as tp
import joblib
from utils import split_text_into_sentences
from sentiment_prediction import prepocess_text
from utils import split_news_on_companies
from utils import get_all_tickers, get_dictionaries
import os
import pandas as pd

EntityScoreType = tp.Tuple[int, float]  # (entity_id, entity_score)
MessageResultType = tp.List[
    EntityScoreType
]  # list of entity scores,
#    for example, [(entity_id, entity_score) for entity_id, entity_score in entities_found]


def score_texts(
    messages: tp.Iterable[str], *args, **kwargs
) -> tp.Iterable[MessageResultType]:
    """
    Main function (see tests for more clarifications)
    Args:
        messages (tp.Iterable[str]): any iterable of strings (utf-8 encoded text messages)

    Returns:
        tp.Iterable[tp.Tuple[int, float]]: for any messages returns MessageResultType object
    -------
    Clarifications:
    # >>> assert all([len(m) < 10 ** 11 for m in messages]) # all messages are shorter than 2048 characters
    """

    cur_dir = os.getcwd()
    parent_directory = os.path.dirname(cur_dir)
    df, dictionary_companies, dictionary_companies_by_ticker, companies = get_dictionaries()
    all_tickers = get_all_tickers(df)
    clf = joblib.load(parent_directory + '/data/svс_model_weights.pkl')
    vectorizer = joblib.load(parent_directory + '/tfidf_vectorizer.pkl')
    result = []

    for i in range(len(messages)):
        text = messages[i]
        sentences, companies_by_index = split_news_on_companies(text, dictionary_companies, all_tickers, dictionary_companies_by_ticker)

        comp_ids_to_text = dict()
        for key in companies_by_index:
            value = companies_by_index[key]
            for company_ids in value:
                if company_ids in comp_ids_to_text:
                    comp_ids_to_text[company_ids] += sentences[key]
                else:
                    comp_ids_to_text[company_ids] = sentences[key]

        for key in companies_by_index:
            value = companies_by_index[key]
            for company_ids in value:

                if company_ids in comp_ids_to_text:
                    comp_ids_to_text[company_ids] += sentences[key]
                else:
                    comp_ids_to_text[company_ids] = sentences[key]
        buf = []
        for ind_com in comp_ids_to_text:
            text = comp_ids_to_text[ind_com]
            text = prepocess_text(text)
            vectors = vectorizer.transform([text])
            pred = clf.predict(vectors)
            tuple = (ind_com, float(pred[0]))
            buf.append(tuple)

        result.append(buf)
    return result


#%%

#%%

#%%
