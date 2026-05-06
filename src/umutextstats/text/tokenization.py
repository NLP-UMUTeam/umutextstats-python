from functools import lru_cache

from umutextstats.text.patterns import LEXICAL_TOKEN_REGEX, SYLLABIFIABLE_WORD_REGEX


@lru_cache(maxsize=50_000)
def get_lexical_tokens(text: str, lowercase: bool = True) -> tuple[str, ...]:
    text = "" if text is None else str(text)
    tokens = LEXICAL_TOKEN_REGEX.findall(text)

    if lowercase:
        tokens = [token.lower() for token in tokens]

    return tuple(tokens)


@lru_cache(maxsize=50_000)
def get_syllabifiable_words(text: str, lowercase: bool = True) -> tuple[str, ...]:
    text = "" if text is None else str(text)
    words = SYLLABIFIABLE_WORD_REGEX.findall(text)

    if lowercase:
        words = [word.lower() for word in words]

    return tuple(words)