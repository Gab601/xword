#!/usr/bin/env python3

import copy
import sys
import time
import argparse


def get_word_starts(filename, size, min_size):
    '''
    Find all words from wordlist of the appropriate size range
    Return a list of sets of initial substrings of the words
    i.e. If word sizes could be 2 or 3, and we had
            "aaa", "aab", "ab", and "baaa" as our word list
            we would return [(""), ("a"), ("aa", "ab"), ("aaa", "aab")]
    '''
    with open(filename, "r") as file:
        all_words = [a[:-1] for a in file.readlines()]

    words = []

    #find words of appropriate size
    for word in all_words:
        if len(word) == size:
            words.append(word)
        elif len(word) < size and len(word) >= min_size:
            words.append(word + " "*(size-len(word)))
            words.append(" "*(size-len(word)) + word)

    word_starts_list = [[] for _ in range(size+1)]
    word_starts = []

    #loop through lengths of substrings
    for start_length in range(size+1):
        #create list of substrings of that length
        for word in words:
            if word[:start_length] not in word_starts_list[start_length]:
                word_starts_list[start_length].append(word[:start_length])

        #convert to set and add to output list
        word_starts.append(set(word_starts_list[start_length]))
    return word_starts, word_starts_list



class Crossword:
    def __init__(self, size, board = None, next_across = 0, next_down = 0, used_words = []):
        self.size = size
        if board == None:
            self.board = [[None for _ in range(size)] for _ in range(size)]
        else:
            self.board = board
        self.next_across = next_across
        self.next_down = next_down
        self.used_words = used_words

    def pretty_print(self):
        for col in self.board:
            print("".join(["-" if x==None else x for x in col]))
        print("")

    def find_all_children(self):
        '''
        Recursive generator function that finds all crosswords matching the current partially filled crossword
        Fills in words in order of top across -> left down -> next across -> next down -> etc
        '''

        #if crossword is fully filled in and valid
        if self.next_across == self.size and "".join([self.board[i][self.size - 1] for i in range(self.size)]).strip() not in self.used_words:
            yield self

        #if a word needs to be filled in across
        elif self.next_across <= self.next_down:

            #get the filled in letters of the word we are trying to fill in
            word_start = ""
            for j in range(self.next_down):
                word_start += self.board[self.next_across][j]

            #look for words in word list that match the filled in letters and has not already been used in the crossword
            for word in word_starts[self.size]:
                if word[:len(word_start)] == word_start and word.strip() not in self.used_words:

                    #check if filling the word in would result in any "down" word beginnings to not have any valid words
                    possible = True
                    for j in range(self.next_down, self.size):
                        col_start = ""
                        for i in range(self.next_across):
                            col_start += self.board[i][j]
                        col_start += word[j]

                        word_possible = col_start in word_starts[self.next_across + 1]

                        if not word_possible:
                            possible = False
                            break

                    #if word works, fill it in and recurse with a new board containing the word
                    if possible:
                        new_board = copy.deepcopy(self.board)
                        for j in range(self.size):
                            new_board[self.next_across][j] = word[j]
                        yield from Crossword.find_all_children(Crossword(self.size, new_board, self.next_across + 1, self.next_down, self.used_words + [word.strip()]))

        #if a word needs to be filled in down
        #TODO: Join this else with the elif case since they are indentical except for row/col swap
        #all parts work identically to above case, so comments are omitted here
        else:
            word_start = ""
            for i in range(self.next_across):
                word_start += self.board[i][self.next_down]
            for word in word_starts[self.size]:
                if word[:len(word_start)] == word_start and word.strip() not in self.used_words:

                    possible = True
                    for i in range(self.next_across, self.size):
                        col_start = ""
                        for j in range(self.next_down):
                            col_start += self.board[i][j]
                        col_start += word[i]
                        word_possible = col_start in word_starts[self.next_down + 1]
                        if not word_possible:
                            possible = False
                            break

                    if possible:
                        new_board = copy.deepcopy(self.board)
                        for i in range(self.size):
                            new_board[i][self.next_down] = word[i]
                        yield from Crossword.find_all_children(Crossword(self.size, new_board, self.next_across, self.next_down + 1, self.used_words + [word.strip()]))

if __name__ == "__main__":

    #parse command line arguments
    parser = argparse.ArgumentParser(description='Generates small crosswords of a given size.')
    parser.add_argument('size', type=int, help='Overall dimension of crossword board.')
    parser.add_argument("-m", "--min", type=int, help="Minimum allowable word size")
    parser.add_argument("-f", "--first", type=str, help="First word of crossword")
    args = parser.parse_args()
    size = args.size
    min_size = size
    if args.min:
        min_size = args.min
    hint = None
    if args.first:
        hint = args.first

    #get word list
    filename = "./words.txt"
    word_starts, word_starts_list = get_word_starts(filename, size, min_size)

    #generate board, using hint if available
    board = Crossword(size)
    if hint:
        for j in range(size):
            board.board[0][j] = hint[j]
        board.next_across = 1
        board.used_words += [hint.strip()]

    #run program
    for crossword in board.find_all_children():
        crossword.pretty_print()
