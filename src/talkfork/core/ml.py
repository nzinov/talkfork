import nltk
from nltk.corpus import wordnet as wn
from nltk.metrics.distance import edit_distance
import scipy.cluster.hierarchy as sch
import math
import numpy as np
from collections import Counter
from matplotlib import pyplot as plt


def size_cond(size):
    n = size
    r = 2
    f = math.factorial
    return int(f(n) // f(r) // f(n-r))


def word_similarity(word_1, word_2):
    max_sim = 0
    synsets_1 = wn.synsets(word_1)
    synsets_2 = wn.synsets(word_2)
    if len(synsets_1) == 0 or len(synsets_2) == 0:
        return word_1 == word_2
    else:
        max_sim = 0
        for synset_1 in synsets_1:
            for synset_2 in synsets_2:
                sim = wn.path_similarity(synset_1, synset_2)
            if sim and sim > max_sim:
                max_sim = sim
        return max_sim


def similarity(s1, s2):
    words_1 = nltk.word_tokenize(s1)
    words_2 = nltk.word_tokenize(s2)
    words_1 = [el for el in words_1 if el not in nltk.corpus.stopwords.words("english")]
    words_2 = [el for el in words_2 if el not in nltk.corpus.stopwords.words("english")]
    if not words_1 or not words_2:
        return 0
    pairwise = np.array([[word_similarity(a, b) for a in words_1] for b in words_2])
    best_1 = np.max(np.apply_along_axis(np.max, 1, pairwise))
    best_2 = np.max(np.apply_along_axis(np.max, 0, pairwise))
    return np.max([best_1, best_2])


class ML:
    def __init__(self, users):
        self.users = users[:]

    def convert_graph(self, graph):
        data = []
        for i in range(len(self.users)):
            for j in range(i + 1, len(self.users)):
                data.append({"source": j, "target": i, "link_distance": 30 / (np.arctanh(2 - graph[i][j]) + 0.1)})
        return data

    def get_graph(self, messages):
        messages = [el for el in messages if el["text"] != '-']
        for i, message in enumerate(messages):
            message["time"] = i
        graph = np.array([[0 for el2 in self.users] for el in self.users], dtype="float")
        for message in messages:
            from_id = self.users.index(message["user"])
            for to_user in message["recipients"]:
                to_id = self.users.index(to_user)
                if to_id < from_id:
                    from_id, to_id = to_id, from_id
                graph[from_id][to_id] += 0.99**(messages[-1]["time"] - message["time"] + 1)
        message_graph = np.array([[0 for el2 in self.users] for el in self.users], dtype="float")
        counts = np.array([[0 for el2 in self.users] for el in self.users])
        for i in range(len(messages)):
            for j in range(i + 1, len(messages)):
                a, b = [self.users.index(messages[pos]["user"]) for pos in [i, j]]
                if a == b:
                    continue
                if b < a:
                    a, b = b, a
                message_graph[a][b] += similarity(messages[i]["text"],  messages[j]["text"]) \
                    * 0.99**(messages[-1]["time"] - messages[i]["time"] + 1) \
                    * 0.99**(messages[-1]["time"] - messages[j]["time"] + 1)
                counts[a][b] += 1
        for i in range(len(self.users)):
            for j in range(len(self.users)):
                if counts[i][j]:
                    graph[i][j] = (graph[i][j]**2 + (message_graph[i][j] / counts[i][j]**0.7)**2)**0.5
        return 2 - np.tanh(graph)

    def get_clusters(self, matrix):
        dists_cond = np.zeros(size_cond(len(matrix)))
        idx = 0
        for r in range(len(matrix)-1):
            dists_cond[idx:idx+len(matrix)-r-1] = matrix[r, r+1:]
            idx += len(matrix)-r-1
        linkage = sch.linkage(dists_cond, method="single")
        sch.dendrogram(linkage)
        plt.savefig("test.png")
        plt.gcf().clear()
        clusters = sch.cut_tree(linkage, height=0.7*np.max(dists_cond))
        print(clusters)
        counter = Counter(clusters.flatten())
        cluster = counter.most_common(2)
        if cluster[1][1] >= 2:
            users = []
            for i in range(len(self.users)):
                if clusters[i] == cluster[0][0]:
                    users.append(self.users[i])
            return users
        return False

    def get_clusters_and_graph(self, messages):
        matrix = self.get_graph(messages)
        return self.get_clusters(matrix), self.convert_graph(matrix)
