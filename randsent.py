#!/usr/bin/env python3
"""
601.465/665 — Natural Language Processing
Assignment 1: Designing Context-Free Grammars

Assignment written by Jason Eisner
Modified by Kevin Duh
Re-modified by Alexandra DeLucia

Code template written by Alexandra DeLucia,
based on the submitted assignment with Keith Harrigian
and Carlos Aguirre Fall 2019
"""
import os, re
import sys
import random
import argparse

# Want to know what command-line arguments a program allows?
# Commonly you can ask by passing it the --help option, like this:
#     python randsent.py --help
# This is possible for any program that processes its command-line
# arguments using the argparse module, as we do below.
#
# NOTE: When you use the Python argparse module, parse_args() is the
# traditional name for the function that you create to analyze the
# command line.  Parsing the command line is different from parsing a
# natural-language sentence.  It's easier.  But in both cases,
# "parsing" a string means identifying the elements of the string and
# the roles they play.

def parse_args():
    """
    Parse command-line arguments.

    Returns:
        args (an argparse.Namespace): Stores command-line attributes
    """
    # Initialize parser
    parser = argparse.ArgumentParser(description="Generate random sentences from a PCFG")
    # Grammar file (required argument)
    parser.add_argument(
        "-g",
        "--grammar",
        type=str, required=True,
        help="Path to grammar file",
    )
    # Start symbol of the grammar
    parser.add_argument(
        "-s",
        "--start_symbol",
        type=str,
        help="Start symbol of the grammar (default is ROOT)",
        default="ROOT",
    )
    # Number of sentences
    parser.add_argument(
        "-n",
        "--num_sentences",
        type=int,
        help="Number of sentences to generate (default is 1)",
        default=1,
    )
    # Max number of nonterminals to expand when generating a sentence
    parser.add_argument(
        "-M",
        "--max_expansions",
        type=int,
        help="Max number of nonterminals to expand when generating a sentence",
        default=450,
    )
    # Print the derivation tree for each generated sentence
    parser.add_argument(
        "-t",
        "--tree",
        action="store_true",
        help="Print the derivation tree for each generated sentence",
        default=False,
    )
    return parser.parse_args()


class Grammar:
    def __init__(self, grammar_file):
        """
        Context-Free Grammar (CFG) Sentence Generator

        Args:
            grammar_file (str): Path to a .gr grammar file
        
        Returns:
            self
        """
        # Parse the input grammar file
        self.rules = {}
        self._load_rules_from_file(grammar_file)
        self.exit = False
        self.expansion_num = 0

    def sample(self, derivation_tree, max_expansions, start_symbol):
        """
        Sample a random sentence from this grammar
        Args:
            derivation_tree (bool): if true, the returned string will represent 
                the tree (using bracket notation) that records how the sentence 
                was derived
                               
            max_expansions (int): max number of nonterminal expansions we allow
            start_symbol (str): start symbol to generate from
        Returns:
            str: the random sentence or its derivation tree
        """

        self.exit = False
        self.expansion_num = 0

        return self.expand(derivation_tree, max_expansions, start_symbol)
    
    def _load_rules_from_file(self, grammar_file):
        with open(grammar_file, "r") as outfile:
            data = outfile.readlines()

            for line in data:
                if line[0] == "#" or line[0] == '\n':
                    continue

                # Remove comments from the line
                line = re.sub(r'\s*#.*', '', line)

                if "\t" in line:
                    line = line.replace("\t", " ")

                try:
                    prob, rest = line.split(" ", 1)
                    rest = rest.strip()
                    LHS, rest = rest.split(" ", 1)
                    rest = rest.strip()
                    RHS = ' '.join(rest.split())
                    # prob, LHS, RHS = line.rstrip().split("\t")
                except:
                    print("ERROR: ", line.rstrip(), ":", prob, LHS, RHS)

                if LHS in self.rules:
                    self.rules[LHS].append((RHS, float(prob)))
                else:
                    self.rules[LHS] = [(RHS, float(prob))]

        # import json
        # print(json.dumps(self.rules, indent=4))
        # print("-----------")

    def expand(self, derivation_tree, max_expansions, start_symbol):
        subS = start_symbol

        if subS not in self.rules:
            return subS

        if self.exit:
            return "..."

        if self.expansion_num >= max_expansions:
            self.exit = True
            return "..."

        LHS_dist = self.rules[subS]

        if len(LHS_dist) == 1:
            subS = LHS_dist[0][0]
        else:
            RHSs = []
            probs = []

            for val in LHS_dist:
                RHSs.append(val[0])
                probs.append(val[1])

            subS = random.choices(RHSs, weights=probs, k=1)[0]

        stream = list(subS.split(" "))
        out = []

        self.expansion_num += 1

        if derivation_tree:
            for val in stream:
                out.append(self.expand(derivation_tree, max_expansions, start_symbol=val))
                # if val not in self.rules:
                #     out.append(self.expand(derivation_tree, max_expansions, start_symbol=val))
                # else:
                #     out.append(f"({val} {self.expand(derivation_tree, max_expansions, start_symbol=val)})")
            if start_symbol != start_symbol.upper():
                return ' '.join(out)
            return f"({start_symbol} {' '.join(out)})"
        
        else:
            for val in stream:
                out.append(self.expand(derivation_tree, max_expansions, start_symbol=val))
            return " ".join(out)


####################
### Main Program
####################
def main():
    # Parse command-line options
    args = parse_args()

    # Initialize Grammar object
    grammar = Grammar(args.grammar)

    # Generate sentences
    for i in range(args.num_sentences):
        # Use Grammar object to generate sentence
        sentence = grammar.sample(
            derivation_tree=args.tree,
            max_expansions=args.max_expansions,
            start_symbol=args.start_symbol
        )

        # Print the sentence with the specified format.
        # If it's a tree, we'll pipe the output through the prettyprint script.
        if args.tree:
            prettyprint_path = os.path.join(os.getcwd(), 'prettyprint')

            t = os.system(f"echo '{sentence}' | perl {prettyprint_path}")
        else:
            print(sentence)

        # print(sentence)


if __name__ == "__main__":
    main()
