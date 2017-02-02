import re
from enum import Enum

class lexer():
    '''
    NUM: made of digits
    NAME: ch+num+_
    TYPE: types defined in language
    '''
    def __init__(self, str_line):
        self.seprators = ['(', ')', ';', '{', '}', '=', '==']
        self.typeWords = ['int', 'char']
        self.line = str_line
        self.wordtype = ['NUM', 'NAME', 'TYPE', 'SEPERATOR', '+', '-', '*', '/']
        self.WordList = []    # saved as [TYPE, CONTENT]
        self.lexStat = Enum('initial', 'process', 'done', 'error')
        print "do lexer: %s" %(self.line)

    # helper functions
    # isalpha/isdigit
    def isalpha(self, ch):
        pattern = re.compile('[A-Za-z]')
        return pattern.match(ch)

    def isdigit(self, ch):
        pattern = re.compile('[+-]*[0-9]+')
        return pattern.match(ch)

    def read_char(self):
        if len(self.line) > 0:
            ch = self.line[0]
            self.line = self.line[1:]
            return ch
        else:
            return '#'

    def push_back(self, ch):
        self.line = (self.line[::-1]+ch)[::-1]
        #print line
        
    def isNUM(self, word):

    def isID(self, word):

    def do_lex(self):
        while len(self.line) > 0:
            word = ''
            status = self.lexStat.initial
            while status is not self.lexStat.done and (status is not self.lexStat.error):
                ch = self.read_char()
                if status is self.lexStat.initial:
                    if self.isalpha(ch):
                        status = self.lexStat.process
                        word = word+ch
                    else:
                        #print 'Not a word'
                        status = self.lexStat.error
                elif status is self.lexStat.process:
                    if self.isalpha(ch) or self.isdigit(ch):
                        status = status
                        word = word+ch
                    else:
                        #print "Found word", word
                        self.push_back(ch)
                        status = self.lexStat.done
            # in outer-while
            if status is self.lexStat.done:
                print "Found word: %s" %(word)
                self.WordList.append(word)

        #print self.WordList
        return 

if __name__ == '__main__':
    line = "int main() here is a-test"
    # keyword = {'int':0, 'if':1, 'else':2, '(':3, ')':4, '{':5, '}':6}
    lex_obj = lexer(line)
    lex_obj.do_lex()
