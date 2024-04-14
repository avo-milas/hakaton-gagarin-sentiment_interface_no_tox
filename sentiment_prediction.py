from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm.notebook import tqdm
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.metrics import accuracy_score, f1_score
nltk.download('wordnet')
wnl = nltk.WordNetLemmatizer()
def create_dataset_from_splitted_news(sentiment_train, split_news_on_companies):
    X = []
    y = []
    for i in tqdm(range(len(sentiment_train))):
        text = sentiment_train.iloc[i].MessageText
        sentences, companies_by_index = split_news_on_companies(text)

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

        real_comp = sentiment_train.iloc[i].issuerid
        if real_comp in comp_ids_to_text:
            X.append(comp_ids_to_text[real_comp])
            y.append(sentiment_train.iloc[i].SentimentScore)

    return X, y
def prepocess_text(text):
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words('russian'))
    stemmer = SnowballStemmer("russian")
    text = re.sub(r'[0-9,.!;:]', '', text)
    stemmed_words = [stemmer.stem(word) for word in text.split()]
    words_final = ' '.join([word for word in stemmed_words if word not in stopwords])
    return words_final

def final_score(y_test, y_pred):
    f1 = f1_score(y_test, y_pred, average='weighted')
    accuracy = accuracy_score(y_test, y_pred)
    return (f1 + accuracy) / 2

def learn_model(X, y):
    X_good = [prepocess_text(x) for x in X]
    vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=1000) #max_features 10000
    vectors = vectorizer.fit_transform(X_good)
    X_train, X_test, y_train, y_test = train_test_split(vectors, y, test_size=0.2, random_state=69)
    sv = svm.SVC()
    sv.fit(X_train, y_train)

    y_pred = sv.predict(X_test)
    ac = accuracy_score(y_test, y_pred)
    print(final_score(y_test, y_pred))