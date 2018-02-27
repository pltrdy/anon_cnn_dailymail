import re
import hashlib
import sys


def hashhex(s):
    """Returns a heximal formated SHA1 hash of the input string.
        Args:
            s: The string to hash.
        Returns:
        A heximal formatted hash of the input string.
    """
    h = hashlib.sha1()
    h.update(s)
    return h.hexdigest()


def warning(*args, **kwargs):
    print(file=sys.stderr, *args, **kwargs)


def fix_missing_period(line):
    """Adds a period to a line that is missing a period"""
    """credits: https://github.com/abisee/cnn-dailymail/blob/master/make_datafiles.py"""
    dm_single_close_quote = u'\u2019'  # unicode
    dm_double_close_quote = u'\u201d'
    END_TOKENS = ['.', '!', '?', '...', "'", "`", '"', dm_single_close_quote,
                  dm_double_close_quote, ")"]  # acceptable ways to end a sentence

    if "@highlight" in line:
        return line
    if line == "":
        return line
    if line[-1] in END_TOKENS:
        return line
    # print line[-1]
    return line + " ."


def line_to_sentence(line):
    """Remove duplicate whitespace and check sentence ends
    """
    s = " ".join(line.split())
    s = fix_missing_period(s)
    return s


def replace_entity(entity_mapping, text, reverse=True):
    """
        With entity_mapping is {tag: text}
        Reverse replaces part of text by the tag (anonymyze)
        reverse=False unanonymize
    """
    if reverse:
        entity_mapping = {v: k for (k, v) in entity_mapping.items()}

    pattern = re.compile(r'(^|\s)(' + '|'.join(re.escape(key)
                                               for key in entity_mapping.keys()) + r')($|\s)')

    def p(x): return " %s " % entity_mapping["".join(x.group().split())]
    result = pattern.sub(p, text)
    result = " ".join(result.split())
    return result
