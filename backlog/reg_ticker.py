import pickle
import re
import pandas as pd

issuers = pd.read_excel('data/issuers.xlsx')


def re_find_ticker(message: str):
    out = list(set(re.findall(r'(?<=\$)\[A-Z]+|[A-Z]{3,6}', message)))
    if 'IPO' in out:
        out.remove('IPO')
    return out
    # return list(set(re.findall(r'\$[A-Z]+(?:-[A-Z]+)*\b', message)))


def get_ticker(issuer_id: int):
    return str(issuers[issuers["issuerid"] == issuer_id].BGTicker).split()[1]


def count_acc(n):
    correct_count = 0
    with open('data/mentions texts.pickle', 'rb') as f:
        mentions = pickle.load(f)

    for mention in mentions.iloc:
        message = mention.MessageText
        issuer = mention.issuerid

        found = re_find_ticker(message)
        correct = get_ticker(issuer)

        if len(found) == 0:
            correct_count += int(correct == 'Nan')
        if len(found) == 1:
            correct_count += int(found[0] == correct)
        if len(found) > 1:
            correct_count += int(found[min(n, len(found) - 1)] == correct)

    print(n, correct_count / mentions.shape[0])


for i in range(0, 5):
    count_acc(i)
