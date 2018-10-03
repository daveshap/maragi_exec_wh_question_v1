import nltk
from nltk.corpus import wordnet
import wikipedia

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')
nltk.download('wordnet')


def get_q_tags(question):
    tokens = nltk.word_tokenize(question)
    pos = nltk.pos_tag(tokens)
    return pos


def get_definition(word):
    syns = wordnet.synsets(word)
    return syns[0].definition()


if __name__ == '__main__':
    #print(nltk.help.upenn_tagset())
    while True:
        a = input('ask me a question!   ')
        if 'what' in a or 'when' in a or 'why' in a or 'where' in a or 'who' in a:
            tagged = get_q_tags(a)
            for word in tagged:
                if 'NN' in word[1]:
                    print(get_definition(word[0]))
        else:
            print("I don't understand the question")