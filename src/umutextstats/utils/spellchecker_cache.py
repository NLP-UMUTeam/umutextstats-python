class CachedSpellChecker:
    def __init__(self, language: str = "es"):
        try:
            from spellchecker import SpellChecker
        except ImportError:
            self.spellchecker = None
            return

        self.spellchecker = SpellChecker(language=language)
        self._known_cache = {}
        self._correction_cache = {}

    def available(self) -> bool:
        return self.spellchecker is not None

    def is_known(self, word: str) -> bool:
        word = word.lower()

        if word not in self._known_cache:
            self._known_cache[word] = word in self.spellchecker

        return self._known_cache[word]

    def correction(self, word: str) -> str | None:
        word = word.lower()

        if word not in self._correction_cache:
            self._correction_cache[word] = self.spellchecker.correction(word)

        return self._correction_cache[word]


_SPELLCHECKERS: dict[str, CachedSpellChecker] = {}

def get_cached_spellchecker(language: str = "es") -> CachedSpellChecker:
    if language not in _SPELLCHECKERS:
        _SPELLCHECKERS[language] = CachedSpellChecker(language=language)

    return _SPELLCHECKERS[language]