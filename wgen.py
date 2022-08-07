import argparse
import ast
import random
from enum import Enum


class Pattern(Enum):
    CV = 1,
    CVk = 2,
    vCV = 3,
    vCVk = 4,
    CVK = 5,
    VCV = 6


class Format(Enum):
    NONE = 0,
    LOWER = 1,
    UPPER = 2,
    NAME = 3


class WordGenerator:
    default_consonants = list("BDFGHJKLMNPRSTVWYZ")
    default_vowels = list("AEIOU")
    default_codas = list("RNK")

    def __init__(self, **kargs):
        self.consonants = WordGenerator.default_consonants if "consonants" not in kargs else kargs["consonants"]
        self.vowels = WordGenerator.default_vowels if "vowels" not in kargs else kargs["vowels"]
        self.codas = WordGenerator.default_codas if "codas" not in kargs else kargs["codas"]

    def generate(self, pattern: Pattern, word_len, fmt=Format.NONE):
        match pattern:
            case Pattern.CV:
                return self.generate_CV(word_len, fmt)
            case Pattern.CVK:
                return self.generate_CVK(word_len, fmt)
            case Pattern.VCV:
                return self.generate_VCV(word_len, fmt)
            case Pattern.vCVk:
                return self.generate_vCVk(word_len, fmt)

    def generate_CV(self, word_len, fmt=Format.NONE):
        word_len = self.__word_length(word_len, 0)
        word = ''
        word_len /= 2
        while word_len > 0:
            word += random.choice(self.consonants) + random.choice(self.vowels)
            word_len -= 1
        return self.__formatted(word, fmt)

    def generate_CVK(self, word_len, fmt=Format.NONE):
        word_len = self.__word_length(word_len, 1)
        word = self.generate_CV(word_len - 1) + random.choice(self.codas)
        return self.__formatted(word, fmt)

    def generate_VCV(self, word_len, fmt=Format.NONE):
        word_len = self.__word_length(word_len, 1)
        word = random.choice(self.vowels) + self.generate_CV(word_len - 1)
        return self.__formatted(word, fmt)

    def generate_vCVk(self, word_len, fmt=Format.NONE):
        if isinstance(word_len, tuple):
            assert word_len[0] <= word_len[1]
            word_len = random.randint(*word_len)
        if word_len % 2 == 0:
            if bool(random.getrandbits(1)) and word_len >= 2:
                word = random.choice(self.vowels) + self.generate_CV(word_len - 2) + random.choice(self.codas)
                return WordGenerator.__formatted(word, fmt)
            return self.generate_CV(word_len, fmt)
        has_coda = bool(random.getrandbits(1))
        if has_coda:
            return self.generate_CVK(word_len, fmt)
        return self.generate_VCV(word_len, fmt)

    @staticmethod
    def __word_length(word_len, odd_or_even: int):
        odd_or_even %= 2
        match word_len:
            case int():
                WordGenerator.__check_word_length(word_len, odd_or_even)
                return word_len
            case tuple():
                min_val = word_len[0]
                max_val = word_len[1]
                if min_val % 2 != odd_or_even:
                    min_val += 1
                if max_val % 2 != odd_or_even:
                    max_val -= 1
                assert min_val <= max_val
                wlen = random.randint(min_val, max_val)
                if wlen % 2 != odd_or_even:
                    wlen -= 1
                return wlen
            case _:
                raise ValueError("word_len must be an int or a tuple of int")

    @staticmethod
    def __check_word_length(word_len, odd_or_even):
        odd_or_even %= 2
        if word_len % 2 != odd_or_even:
            odd_or_even_str = "odd" if odd_or_even == 1 else "even"
            raise ValueError("word_len must be {}! word_len='{}'".format(odd_or_even_str, word_len))

    @staticmethod
    def __formatted(word, fmt: Format):
        match fmt:
            case Format.NONE:
                return word
            case Format.LOWER:
                return word.lower()
            case Format.UPPER:
                return word.upper()
            case Format.NAME:
                return word[0].upper() + word[1:].lower()


def generate(pattern: Pattern, word_len, fmt=Format.NONE, **kargs):
    return WordGenerator(**kargs).generate(pattern, word_len, fmt)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-C', '--consonants', type=str, default=WordGenerator.default_consonants)
    argparser.add_argument('-V', '--vowels', type=str, default=WordGenerator.default_vowels)
    argparser.add_argument('-K', '--codas', type=str, default=WordGenerator.default_codas)
    argparser.add_argument('--lower', action='store_const', const=Format.LOWER)
    argparser.add_argument('--upper', action='store_const', const=Format.UPPER)
    argparser.add_argument('--name', action='store_const', const=Format.NAME)
    argparser.add_argument('-P', '--print', type=str, default="{}")
    argparser.add_argument('--print-sep', type=str, default="\n")
    argparser.add_argument('-N', '--count', type=int, default=1)
    argparser.add_argument('word_length', type=str, help='word length')
    args = argparser.parse_args()

    args.word_length = ast.literal_eval(args.word_length)
    match args.word_length:
        case int():
            pass
        case tuple():
            if len(args.word_length) == 1:
                args.word_length = args.word_length[0]
            else:
                args.word_length = args.word_length[:2]
        case _:
            raise argparse.ArgumentTypeError("Bad word_length type.")

    fmt = Format.NONE
    if args.lower:
        fmt = args.lower
    elif args.upper:
        fmt = args.upper
    elif args.name:
        fmt = args.name

    word_gen = WordGenerator(consonants=args.consonants, vowels=args.vowels, codas=args.codas)
    if args.count > 0:
        for i in range(args.count - 1):
            word = word_gen.generate(Pattern.vCVk, args.word_length, fmt)
            print(args.print.format(word, word=word, index=i), end=args.print_sep)
        word = word_gen.generate(Pattern.vCVk, args.word_length, fmt)
        print(args.print.format(word, word=word, index=args.count - 1))
