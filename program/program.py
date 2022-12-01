import nltk
nltk.download('punkt')
nltk.download('stopwords')
from bs4 import BeautifulSoup
import pathlib
import os
import re
import collections
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# if the node is an end of a word, the isEnd attribute shoule be True
# it should has at least one child node that is an external node whose len(self.htmls) > 0
class Node():
    def __init__(self):
        self.value = {} # the node of a compressed trie may store a string rather than a char
        self.isEnd = False # a boolean indicates that the node is an end of a word
        self.children = {} # children nodes of the node
        self.htmls = collections.defaultdict(int) # {file_name: freq of the word in the html}, for ranking


class Trie():
    def __init__(self):
        self.root = Node()

    def insert(self, word, fileName):
        """
        4 cases:
        case 1: A brandnew word
        case 2: A word with common prefix with an existing word
        case 3: A word extending an existing word
        case 4: A word as same as an existing word
        """
        currNode = self.root
        i = 0

        while i < len(word) and word[i] in currNode.value:
            j = 0
            value = currNode.value[word[i]]

            while j < len(value) and i < len(word) and value[j] == word[i]:
                i += 1
                j += 1
            
            # # case 4
            # if j == len(value) and i == len(word):
            #     currNode = 


        # case 1
        if i < len(word):
            currNode.value[word[i]] = word[i:]
            currNode.isEnd = True

            # create an external node as the child node
            child = Node()
            child.htmls[fileName] += 1
            currNode.children[word] = child

        return


def main():
    html_path = str(pathlib.Path(__file__).parent.parent.resolve()) + '/Inputs'
    os.chdir(html_path)
    trie = Trie()
    for file in os.listdir():
        if file.endswith(".html"):
            # 1. open a html file
            file_path = f"{html_path}/{file}"
            with open(file_path, 'r') as fp:
                soup = BeautifulSoup(fp, 'html.parser')

            # 2. import the stop words set
            stop_words = set(stopwords.words('english'))

            # 3. extract all texts from the input html
            all_text = soup.get_text()
            
            # 4. tokenize all extracted texts
            word_tokens = word_tokenize(all_text)

            # 5. iterate all tokens, if the token is not a stop word, then it can be splitted by non-alpha
            # after splitting, if the splitted word is not empty, append each splotted word to the filtered text list
            filtered_text = []
            for token in word_tokens:
                if token not in stop_words:
                    splitted_token = re.split('[^a-zA-Z]', token)
                    for splitted_word in splitted_token:
                        if splitted_word:
                            filtered_text.append(splitted_word.lower())

            print(file_path)
            print(filtered_text)


if __name__ == '__main__':
    main()