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
    word_starts_dict = [{} for _ in range(size)]
    word_starts = []

    #loop through lengths of substrings
    # for start_length in range(size+1):
    #     #create list of substrings of that length
    #     for word in words:
    #         if word[:start_length] not in word_starts_list[start_length]:
    #             word_starts_list[start_length].append(word[:start_length])
    #             if (start_length != size):
    #                 word_starts_dict[start_length][word[:start_length]] = [word]
    #         elif (start_length != size):
    #             word_starts_dict[start_length][word[:start_length]].append(word)

    #     #convert to set and add to output list
    #     word_starts.append(set(word_starts_list[start_length]))
    # return words, word_starts, word_starts_dict
    return words


class Crossword:
    def __init__(self, size, board = None):
        self.size = size
        if board == None:
            self.board = [[None for _ in range(size)] for _ in range(size)]
        else:
            self.board = board

    def pretty_print(self, filled_rows = None, filled_cols = None):
        if not filled_rows:
            for col in self.board:
                print("".join(["-" if x==None else x for x in col]))
            print("")
        else:
            for col in range(len(self.board)):
                print("".join(["-" if self.board[row][col]==None or not (filled_cols[col] or filled_rows[row]) else self.board[row][col] for row in range(self.size)]))
            print("")

    def row(self, row, next_across, next_down):
        if next_across > row:
            return "".join([self.board[row][x] for x in range(self.size)])
        else:
            return "".join([self.board[row][x] for x in range(next_down)])

    def col(self, col, next_across, next_down):
        if next_down > col:
            return "".join([self.board[x][col] for x in range(self.size)])
        else:
            return "".join([self.board[x][col] for x in range(next_across)])

    def set_row(self, row, word):
        for j in range(self.size):
            self.board[row][j] = word[j]

    def set_col(self, col, word):
        for i in range(self.size):
            self.board[i][col] = word[i]

    def alt_children(self, filled_rows, filled_cols, words_used = []):

        all_true = [True for _ in range(self.size)]
        all_false = [False for _ in range(self.size)]


        # if crossword is filled completely
        if filled_rows == all_true or filled_cols == all_true:
            yield self

        # if crossword is empty
        elif filled_rows == all_false and filled_cols == all_false:
            # fill in the topmost row
            for word in all_words:
                print("Trying top word: ", word)
                self.set_row(0, word)
                new_filled_rows = list(filled_rows)
                new_filled_rows[0] = True
                yield from self.alt_children(new_filled_rows, filled_cols, [word])

        # if only top row is filled in
        elif filled_cols == all_false:
            best_col = 0
            least_options = num_words
            for col in range(self.size):
                if num_with_each_start[self.board[0][col]] < least_options:
                    best_col = col
                    least_options = num_with_each_start[self.board[0][col]]
            for word in words_with_pos_letter[0][self.board[0][best_col]]:
                if word not in words_used:
                    self.set_col(best_col, word)
                    new_filled_cols = list(filled_cols)
                    new_filled_cols[best_col] = True
                    yield from self.alt_children(filled_rows, new_filled_cols, words_used + [word])

        # if both some rows and columns are filled in
        else:
            best_is_col = True
            best_index = 0
            least_options = num_words
            best_possible_words = set()

            for col in range(self.size):
                if not filled_cols[col]:
                    lookup = tuple(self.board[row][col] if filled_rows[row] else "-" for row in range(self.size))
                    if lookup not in words_dict:
                        return
                    possible_words = words_dict[lookup]
                    num_options = len(possible_words)
                    if num_options < least_options:
                        best_index = col
                        least_options = num_options
                        best_possible_words = possible_words
            for row in range(self.size):
                if not filled_rows[row]:
                    lookup = tuple(self.board[row][col] if filled_cols[col] else "-" for col in range(self.size))
                    if lookup not in words_dict:
                        return
                    possible_words = words_dict[lookup]
                    num_options = len(possible_words)
                    if num_options < least_options:
                        best_index = row
                        best_is_col = False
                        least_options = num_options
                        best_possible_words = possible_words

            for word in best_possible_words:
                if word not in words_used:
                    new_words_used = list(words_used)
                    new_words_used.append(word)
                    if best_is_col:
                        self.set_col(best_index, word)
                        new_filled_cols = list(filled_cols)
                        new_filled_cols[best_index] = True
                        yield from self.alt_children(filled_rows, new_filled_cols, new_words_used)
                    else:
                        self.set_row(best_index, word)
                        new_filled_rows = list(filled_rows)
                        new_filled_rows[best_index] = True
                        yield from self.alt_children(new_filled_rows, filled_cols, new_words_used)



    def find_all_children(self, next_across, next_down):
        '''
        Recursive generator function that finds all crosswords matching the current partially filled crossword
        Fills in words in order of top across -> left down -> next across -> next down -> etc
        '''

        if (next_down == 0 and next_across == 1):
            print("Trying top word: ", self.row(0, 1, 0))

        words_used = []
        for i in range(next_across):
            words_used.append(self.row(i, next_across, next_down))
        for i in range(next_down):
            words_used.append(self.col(i, next_across, next_down))

        #if crossword is fully filled in and valid
        if next_across == self.size:
            if "".join([self.board[i][self.size - 1] for i in range(self.size)]).strip() not in words_used:
                yield self

        #if a word needs to be filled in across
        elif next_across <= next_down:

            #get the filled in letters of the word we are trying to fill in
            word_start = ""
            for j in range(next_down):
                word_start += self.board[next_across][j]

            #look for words in word list that match the filled in letters and has not already been used in the crossword
            for word in word_starts_dict[len(word_start)][word_start]:
                if word.strip() not in words_used:

                    #check if filling the word in would result in any "down" word beginnings to not have any valid words
                    possible = True
                    for j in range(next_down, self.size):
                        col_start = ""
                        for i in range(next_across):
                            col_start += self.board[i][j]
                        col_start += word[j]

                        word_possible = col_start in word_starts[next_across + 1]

                        if not word_possible:
                            possible = False
                            break

                    #if word works, fill it in and recurse with a new board containing the word
                    if possible:
                        for j in range(self.size):
                            self.board[next_across][j] = word[j]
                        yield from self.find_all_children(next_across + 1, next_down)

        #if a word needs to be filled in down
        #TODO: Join this else with the elif case since they are indentical except for row/col swap
        #all parts work identically to above case, so comments are omitted here
        else:
            word_start = ""
            for i in range(next_across):
                word_start += self.board[i][next_down]
            if (len(word_start) == self.size):
                self.pretty_print()
                print(word_start)
                print(len(word_start))
                print(next_across)
            for word in word_starts_dict[len(word_start)][word_start]:
                if word.strip() not in words_used:

                    possible = True
                    for i in range(next_across, self.size):
                        col_start = ""
                        for j in range(next_down):
                            col_start += self.board[i][j]
                        col_start += word[i]
                        word_possible = col_start in word_starts[next_down + 1]
                        if not word_possible:
                            possible = False
                            break

                    if possible:
                        for i in range(self.size):
                            self.board[i][next_down] = word[i]
                        yield from self.find_all_children(next_across, next_down + 1)

if __name__ == "__main__":

    #parse command line arguments
    parser = argparse.ArgumentParser(description='Generates small crosswords of a given size.')
    parser.add_argument('size', type=int, help='Overall dimension of crossword board.')
    parser.add_argument("-m", "--min", type=int, help="Minimum allowable word size. Default equal to size argument.")
    parser.add_argument("-f", "--first", type=str, help="First word of crossword. Default none.")
    parser.add_argument("-w", "--words", type=str, help="Path to txt list of words to use. Default \"./words.txt\"")
    args = parser.parse_args()

    size = args.size
    min_size = size
    if args.min:
        min_size = args.min


    #get word list
    filename = "./words.txt" if not args.words else args.words
    all_words = get_word_starts(filename, size, min_size)
    num_words = len(all_words)
    num_with_each_start = {l : 0 for l in "qwertyuiopasdfghjklzxcvbnm"}
    for word in all_words:
        num_with_each_start[word[0]] += 1
    words_with_pos_letter = [{l : [] for l in "qwertyuiopasdfghjklzxcvbnm"} for _ in range(size)]
    for word in all_words:
        for pos in range(size):
            words_with_pos_letter[pos][word[pos]].append(word)
    for pos in range(size):
        for letter in "qwertyuiopasdfghjklzxcvbnm":
            words_with_pos_letter[pos][letter] = set(words_with_pos_letter[pos][letter])

    words_with_two_pos_letters = [[{l1 : {l2 : [] for l2 in "qwertyuiopasdfghjklzxcvbnm"} for l1 in "qwertyuiopasdfghjklzxcvbnm"} for pos2 in range(pos1+1, size)] for pos1 in range(size-1)]
    for pos1 in range(size-1):
        for pos2 in range(pos1+1, size):
            for letter1 in "qwertyuiopasdfghjklzxcvbnm":
                for letter2 in "qwertyuiopasdfghjklzxcvbnm":
                    words_with_two_pos_letters[pos1][pos2-pos1-1][letter1][letter2] = set.intersection(words_with_pos_letter[pos1][letter1], words_with_pos_letter[pos2][letter2])
    words_dict = {}
    combos = [('{0:0' + str(size) + 'b}').format(x) for x in range(1, 2**size - 1)]
    for word in all_words:
        for combo in combos:
            k = tuple(word[i] if combo[i] == "1" else "-" for i in range(size))
            if k in words_dict:
                words_dict[k].append(word)
            else:
                words_dict[k] = [word]
    words_dict = {k : set(l) for k, l in words_dict.items()}
    print(words_dict[('b', 'a', 'n', 'a', '-', '-', '-')])



    # for word1 in word_starts[size]:
    #     for word2 in word_starts[size]:
    #         valid = True
    #         for x in range(size):
    #             if word1[x] + word2[x] not in word_starts[2]:
    #                 valid = False
    #         if valid:
    #             num_words = [len(word_starts_dict[2][word1[x] + word2[x]]) for x in range(size)]
    #             if (min(num_words) > 100):
    #                 print(num_words, word1, word2)



    #generate board, using hint if available
    board = Crossword(size)
    hint = None
    if args.first:
        hint = args.first
    if hint:
        for j in range(size):
            board.board[0][j] = hint[j]
        board.next_across = 1
        board.used_words += [hint.strip()]

    #run program
    for crossword in board.alt_children([False for _ in range(size)], [False for _ in range(size)]):
        crossword.pretty_print()
