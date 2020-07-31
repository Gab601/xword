#!/usr/bin/env python3

import copy
import sys
import time
import argparse


def get_word_starts(filename, size, min_size):
    with open(filename, "r") as file:
        all_words = [a[:-1] for a in file.readlines()]

    words = []
    for word in all_words:
        if len(word) == size:
            words.append(word)
        elif len(word) < size and len(word) >= min_size:
            words.append(word + " "*(size-len(word)))
            words.append(" "*(size-len(word)) + word)

    word_starts_list = [[] for _ in range(size+1)]
    word_starts = []
    for start_length in range(size+1):
        for word in words:
            if word[:start_length] not in word_starts_list[start_length]:
                word_starts_list[start_length].append(word[:start_length])
        word_starts.append(set(word_starts_list[start_length]))
    return word_starts, word_starts_list



class Crossword:
    def __init__(self, size):
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.size = size
        self.next_across = 0
        self.next_down = 0
        self.used_words = []

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

    def find_all_children(self, timing = True):
        if self.next_across == self.size and "".join([self.board[i][self.size - 1] for i in range(self.size)]).strip() not in self.used_words:
            yield self

        elif self.next_across <= self.next_down:
            word_start = ""
            for j in range(self.next_down):
                word_start += self.board[self.next_across][j]
            for word in word_starts[self.size]:
                if word[:len(word_start)] == word_start and word.strip() not in self.used_words:

                    st = time.time()

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

                    et = time.time()
                    times[2] += et - st

                    if possible:
                        new_board = copy.deepcopy(self.board)
                        for j in range(self.size):
                            new_board[self.next_across][j] = word[j]
                        yield from Crossword.find_all_children(Crossword(self.size, new_board, self.next_across + 1, self.next_down, self.used_words + [word.strip()]))

        else:
            word_start = ""
            for i in range(self.next_across):
                word_start += self.board[i][self.next_down]
            for word in word_starts[self.size]:
                if word[:len(word_start)] == word_start and word.strip() not in self.used_words:

                    st = time.time()

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

                    et = time.time()
                    times[3] += et - st

                    if possible:
                        new_board = copy.deepcopy(self.board)
                        for i in range(self.size):
                            new_board[i][self.next_down] = word[i]
                        yield from Crossword.find_all_children(Crossword(self.size, new_board, self.next_across, self.next_down + 1, self.used_words + [word.strip()]))
    #print(words)

if __name__ == "__main__":
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
    filename = "./words.txt"
    word_starts, word_starts_list = get_word_starts(filename, size, min_size)
    #print(word_starts)
    board = Crossword(size)
    if hint:
        for j in range(size):
            board.board[0][j] = hint[j]
        board.next_across = 1
        board.used_words += [hint.strip()]
    times = [0, 0, 0, 0, 0]
    for crossword in board.find_all_children():
        crossword.pretty_print()
        #print(times)
