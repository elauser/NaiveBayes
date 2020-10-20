import tqdm
import math
import string
from tqdm import tqdm, trange
from HW4_util import AI_util
from flask import Flask
from flask_restful import Resource, Api
from flask import request

app = Flask(__name__)
api = Api(app)

def merge(list1, list2):
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list


def init_wordbag(vocab):
    word_bag = {}
    for cat in "business, politics, sport, tech, entertainment".split(', '):
        word_bag[cat] = dict.fromkeys(vocab, 1)
    return word_bag


def fill_wordbag(train_data, train_labels, vocab):
    word_bag = init_wordbag(vocab)
    for i in range(0, len(train_data)):
        article_id, tokens, tf_value = train_data[i]
        merged = merge(vocab, tf_value)
        for voc, amount in merged:
            word_bag[train_labels[i]][voc] += amount
    return word_bag


def get_multipliers(word_bag):
    likelihoods = {}
    total = 0
    word_amount = 0
    for category, freq_dict in word_bag.items():
        total_ca = 0
        for key, value in freq_dict.items():
            total_ca += value - 1
            total += value - 1
            word_amount += value
        likelihoods[category] = total_ca
    for key, value in likelihoods.items():
        likelihoods[key] = value / total
    print(likelihoods)
    return word_amount, likelihoods


def parse_sentence(sentence):
    s = sentence
    s.translate(str.maketrans('', '', string.punctuation))
    words = s.lower().split()
    word_dict = dict.fromkeys(words, 0)
    for word in words:
        word_dict[word] += 1

    return [(word, amount) for word, amount in word_dict.items()]


class Naive_Bayes(AI_util):
    likelihood_bag = {}
    category_likelihoods = {}

    def train(self, train_data=None, test_data=None, train_labels=None, test_labels=None, vocab=None):
        word_bag = fill_wordbag(train_data, train_labels, vocab)
        total_words, category_likelihoods = get_multipliers(word_bag)
        for category, words in word_bag.items():
            for word, amount in words.items():
                word_bag[category][word] = math.log(amount / total_words)

        likelihood_bag = word_bag.copy()
        category_likelihoods = category_likelihoods

    def predict(self, sentence):
        vocab_tf = parse_sentence(sentence)
        lh = self.category_likelihoods.copy()
        categories = "business, politics, sport, tech, entertainment".split(', ')
        for key, value in self.category_likelihoods.items():
            lh[key] = math.log(value)

        for category in categories:
            for word, amount in vocab_tf:
                likelihood = self.likelihood_bag[category][word]
                lh[category] += likelihood * amount

        max_key = max(lh, key=lh.get)
        return max_key


bayes = Naive_Bayes()


class Product(Resource):
    predictions = {}
    test_string = "This is a test string to try to predict a category for this technology"
    predictions[test_string] = bayes.predict(test_string)

    def get(self):
        return self.predictions

    def post(self):
        sentence = request.form['sentence']
        prediction = bayes.predict(sentence)
        self.predictions['sentence'] = prediction



def get_bayes():
    naive_bayes = Naive_Bayes()
    news_data = naive_bayes.Load_Pickle_Data(input_pickle_file_path="HW4_BBC_Data.pickle")
    vocab = naive_bayes.Load_Pickle_Data(input_pickle_file_path="HW4_Vocab.pickle")
    train_data, test_data, train_labels, test_labels = naive_bayes.Split_Train_Test(news_data=news_data)

    naive_bayes.train(train_data=train_data, test_data=test_data,
                      train_labels=train_labels, test_labels=test_labels,
                      vocab=vocab)
    return naive_bayes


if __name__ == "__main__":
    bayes = get_bayes()
    api.add_resource(Product, '/')
    app.run(host='0.0.0.0', port=80, debug=True)