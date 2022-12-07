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

    def createExternalNode(self, fileName):
        externalNode = Node()
        externalNode.htmls[fileName] += 1
        return externalNode

    def createEndChildNode(self, word, remainString, fileName):
        child = Node()
        child.value[remainString[0]] = remainString
        child.isEnd = True
        child.children[word] = self.createExternalNode(fileName)
        return child


    def insert(self, word, fileName):
        currNode = self.root
        i = 0

        while i < len(word) and word[i] in currNode.value:
            j = 0
            firstLetter = word[i]
            value = currNode.value[firstLetter]

            while j < len(value) and i < len(word) and value[j] == word[i]:
                i += 1
                j += 1
            
            if (j == len(value) and i == len(word)):
                # case 1, the matched word = current node's value
                # check the current node's isEnd
                if currNode.isEnd:
                    # if True, update the external node's htmls dict
                    externalNode = currNode.children[word]
                    externalNode.htmls[fileName] += 1
                else:
                    # if False, create a new external node
                    currNode.children[word] = self.createExternalNode(fileName)
            elif (j == len(value) and i < len(word)):
                # case 2, the current node's value ends but the matched word not yet
                # check the current node's children
                if remainString[0] in currNode.children:
                    # if the first remaining letter is a key in children dict, traverse
                    # down the trie and update the current node
                    currNode = currNode.children[remainString[0]]
                else:
                    # if not, create a new child internal node with the remaining
                    # unmatched string and the external node, then break the loop
                    remainString = word[i:]
                    currNode.children[remainString[0]] = self.createEndChildNode(word, remainString, fileName)
                    break
            elif (j < len(value) and i == len(value)):
                # case 3, the matched word ends but the current node's value not yet
                # it means the word is a new word ending at the current node
                # we need to:
                # (1) divide the current node's value
                preString = value[:j]
                postString = value[j:]
                # (2) update the current node's value to be divided preString, isEnd = True
                currNode.value[firstLetter] = preString
                currNode.isEnd = True
                # (3) create a new child node with the value as postString
                newChild = Node()
                newChild.value[postString[0]] = postString
                # (4) move the current node's children to be the newChild's children
                newChild.children = currNode.children
                # (5) create a new external node for the word
                newExternal = self.createExternalNode(fileName)
                # (6) update the current node's children
                currNode.children = {}
                currNode.children[word] = newExternal
                currNode.children[postString[0]] = newChild
                break






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