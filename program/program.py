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
        if word[0] in currNode.children:
            currNode = currNode.children[word[0]]
        else:
            currNode.children[word[0]] = self.createEndChildNode(word, word, fileName)
            return

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
                    # if False, create a new external node, and isEnd = True
                    currNode.children[word] = self.createExternalNode(fileName)
                    currNode.isEnd = True
            elif (j == len(value) and i < len(word)):
                # case 2, the current node's value ends but the matched word not yet
                # check the current node's children
                unmatched = word[i:]
                if unmatched[0] in currNode.children:
                    # if the first unmatched letter is a key in children dict, traverse
                    # down the trie and update the current node
                    currNode = currNode.children[unmatched[0]]
                else:
                    # if not, create a new endChild node with the remaining
                    # unmatched string and the external node, then break the loop
                    currNode.children[unmatched[0]] = self.createEndChildNode(word, unmatched, fileName)
                    return
            elif (j < len(value) and i == len(word)):
                # case 3, the matched word ends but the current node's value not yet.
                # it means the word is a new word ending at the current node
                # we need to:
                # (1) divide the current node's value
                matched = value[:j]
                unmatched = value[j:]
                # (2) update the current node's value to be divided matched
                currNode.value[firstLetter] = matched
                # (3) create a new child node with the value as unmatched
                newChild = Node()
                newChild.value[unmatched[0]] = unmatched
                # (4) move the current node's children to be the newChild's children, and copy isEnd status
                newChild.children = currNode.children
                newChild.isEnd = currNode.isEnd
                # (5) create a new external node for the word
                newExternal = self.createExternalNode(fileName)
                # (6) update the current node's children, isEnd = True
                currNode.children = {}
                currNode.children[word] = newExternal
                currNode.children[unmatched[0]] = newChild
                currNode.isEnd = True
                return
            elif (j < len(value) and i < len(word)):
                # case 4, both don't end
                # we need to:
                # (1) divide the word and the current node's value 
                matched = value[:j]
                unmatchedOfValue = value[j:]
                unmatchedOfWord = word[i:]
                # (2) update the current node's value to be divided matched
                currNode.value[firstLetter] = matched
                # (3) create a new child node with the value as unmatchedOfValue
                newChild = Node()
                newChild.value[unmatchedOfValue[0]] = unmatchedOfValue
                # (4) move the current node's children to be the newChild's children, and copy isEnd status
                newChild.children = currNode.children
                newChild.isEnd = currNode.isEnd
                # (5) create a new endChild node for the word
                newEndChild = self.createEndChildNode(word, unmatchedOfWord, fileName)
                # (6) update the current node's children, isEnd = False
                currNode.children = {}
                currNode.children[unmatchedOfValue[0]] = newChild
                currNode.children[unmatchedOfWord[0]] = newEndChild
                currNode.isEnd = False
                return
        return


    def search(self, word):
        currNode = self.root
        i = 0

        if word[i] in currNode.children:
            currNode = currNode.children[word[i]]
        else:
            return {}

        while i < len(word) and word[i] in currNode.value:
            j = 0
            firstLetter = word[i]
            value = currNode.value[firstLetter]

            while j < len(value) and i < len(word) and value[j] == word[i]:
                i += 1
                j += 1

            if j < len(value):
                return {}
            
            if i == len(word) and word in currNode.children:
                return currNode.children[word].htmls
            elif i < len(word) and word[i] in currNode.children:
                currNode = currNode.children[word[i]]
            else:
                return {} # the case i == len(word) but there is no word in currNode.children
        return {}


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
            # print(word_tokens)
            # 5. iterate all tokens, if the token is not a stop word, then it can be splitted by non-alpha
            # after splitting, if the splitted word is not empty, append each splotted word to the filtered text list
            filtered_text = []
            for token in word_tokens:
                splitted_token = re.split('[^a-zA-Z0-9]', token)
                for splitted_word in splitted_token:
                    if splitted_word.lower() not in stop_words and len(splitted_word) > 1:
                        if splitted_word:
                            trie.insert(splitted_word.lower(), file)
                            filtered_text.append(splitted_word.lower())
    
    runProgram = True
    while runProgram:
        selection = input("\nEnter 1 to do search\nEnter 2 to end the program\n")
        if selection == '1':
            keywords = input("\nPlease enter keywords to search\n!!Please enter multiple keywords with spaces!!\n").split()
            finalResult = {}
            for i, keyword in enumerate(keywords):
                if i == 0:
                    finalResult = trie.search(keyword.lower())
                else:
                    currResult = trie.search(keyword.lower())
                    preResult = finalResult
                    finalResult = {}
                    finalResult = {k : preResult[k] + currResult[k] for k in preResult if k in currResult}
                

            if not len(finalResult):
                print("\nYour search did not match any document, please try different keywords\n")
                continue

            rankedResult = dict(sorted(finalResult.items(), key=lambda item : item[1], reverse=True))
            print("\nThe search result is:\n")
            for k, v in rankedResult.items():
                print("The page '" + k + "' has all keywords with total " + str(v) + " occurence\n")

        elif selection == '2':
            runProgram = False
        else:
            print("\n!!!Please enter 1 or 2!!!\n")

    return


if __name__ == '__main__':
    main()