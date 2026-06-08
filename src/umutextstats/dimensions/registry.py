from typing import Type

from umutextstats.dimensions.base import BaseDimension

from umutextstats.dimensions.length import (
    LengthDimension, 
    AverageWordLengthDimension, 
    WordLengthDimension
)

from umutextstats.dimensions.count import (
    SentenceCountDimension,
    WordCountDimension, 
    CharacterFrequencyDimension, 
    SyllableCountDimension
)
from umutextstats.dimensions.word_per_dictionary import WordPerDictionary
from umutextstats.dimensions.pattern import PatternDimension
from umutextstats.dimensions.pos_tagging_tag import POSTaggingTag
from umutextstats.dimensions.ner_tagging_tag import NERTaggingTag
from umutextstats.dimensions.enclitics_personal_pronouns import EncliticsPersonalPronounsDictionary
from umutextstats.dimensions.periphrasis import PeriphrasisDimension
from umutextstats.dimensions.error import (
    ErrorCapitalizationStartingWithLowerCaseDimension, 
    ErrorMispellingDimension, 
    ErrorMiscTwoOrMoreEqualWordsDimension, 
    ErrorMispellingAccentsDimension, 
    ErrorStyleSentencesStartingWithNumbers, 
    ErrorStyleSentencesStartingWithTheSameWord
)
from umutextstats.dimensions.grammatical_gender import GrammaticalGenderDimension
from umutextstats.dimensions.language import LanguageDimension
from umutextstats.dimensions.perspicuity import PerspicuityDimension
from umutextstats.dimensions.pos_tagging_expression import POSTaggingExpression
from umutextstats.dimensions.readability import ReadabilityDimension
from umutextstats.dimensions.rtie import (
    RTIEDimension, 
    RTIEDeviationDimension
)
from umutextstats.dimensions.syllable_per_word import SyllablePerWordDimension
from umutextstats.dimensions.verb_per_dictionary import VerbPerDictionary
from umutextstats.dimensions.words_per_sentence import WordPerSentenceDimension
from umutextstats.dimensions.word_unique import WordUniqueDimension
from umutextstats.dimensions.word_case import WordCase
from umutextstats.dimensions.dependency import (
    DependencyTag, 
    DependencyDepthDimension, 
    DependencyDistanceDimension
)
from umutextstats.dimensions.root_pos_tag import RootPOSTagDimension
from umutextstats.dimensions.passive_voice_dependency import PassiveVoiceDependencyDimension
from umutextstats.dimensions.document_structure_paragraphs import ParagraphCountDimension, AverageParagraphLengthDimension, ParagraphLengthDeviationDimension, DialogueParagraphPercentageDimension


# =========================
# Registry
# =========================

DIMENSION_REGISTRY: dict[str, Type[BaseDimension]] = {
    "LengthDimension": LengthDimension,
    "SentenceCountDimension": SentenceCountDimension,
    "SyllableCountDimension": SyllableCountDimension,
    "WordCountDimension": WordCountDimension,
    "WordPerDictionary": WordPerDictionary,
    "PatternDimension": PatternDimension,
    "POSTaggingTag": POSTaggingTag,
    "NERTaggingTag": NERTaggingTag,
    "EncliticsPersonalPronounsDictionary": EncliticsPersonalPronounsDictionary,
    "PeriphrasisDimension": PeriphrasisDimension,
    "CharacterFrequencyDimension": CharacterFrequencyDimension,
    "ErrorCapitalizationStartingWithLowerCaseDimension": ErrorCapitalizationStartingWithLowerCaseDimension,
    "ErrorMispellingDimension": ErrorMispellingDimension,
    "ErrorMiscTwoOrMoreEqualWordsDimension": ErrorMiscTwoOrMoreEqualWordsDimension,
    "ErrorMispellingAccentsDimension": ErrorMispellingAccentsDimension,
    "ErrorStyleSentencesStartingWithNumbers": ErrorStyleSentencesStartingWithNumbers,
    "ErrorStyleSentencesStartingWithTheSameWord": ErrorStyleSentencesStartingWithTheSameWord,
    "GrammaticalGenderDimension": GrammaticalGenderDimension,
    "LanguageDimension": LanguageDimension,
    "PerspicuityDimension": PerspicuityDimension,
    "POSTaggingExpression": POSTaggingExpression,
    "ReadabilityDimension": ReadabilityDimension,
    "RTIEDimension": RTIEDimension,
    "RTIEDeviationDimension": RTIEDeviationDimension,
    "SyllablePerWordDimension": SyllablePerWordDimension,
    "VerbPerDictionary": VerbPerDictionary,
    "WordPerSentenceDimension": WordPerSentenceDimension,
    "WordUniqueDimension": WordUniqueDimension,
    "WordCase": WordCase,
    "WordLengthDimension": WordLengthDimension,
    "AverageWordLengthDimension": AverageWordLengthDimension,
    "DependencyTag": DependencyTag,
    "DependencyDepthDimension": DependencyDepthDimension,
    "DependencyDistanceDimension": DependencyDistanceDimension,
    "RootPOSTagDimension": RootPOSTagDimension,
    "PassiveVoiceDependencyDimension": PassiveVoiceDependencyDimension,
    "ParagraphCountDimension": ParagraphCountDimension,
    "AverageParagraphLengthDimension": AverageParagraphLengthDimension,
    "ParagraphLengthDeviationDimension": ParagraphLengthDeviationDimension,
    "DialogueParagraphPercentageDimension": DialogueParagraphPercentageDimension
}


# =========================
# Helpers
# =========================

def normalize_class_name(class_name: str | None) -> str | None:
    """
    Normaliza nombres heredados del XML/PHP.

    Ejemplo:
    UMUTextStats\\Dimensions\\LengthDimension → LengthDimension
    """
    if not class_name:
        return None

    return class_name.replace("\\", "/").split("/")[-1]


def resolve_dimension(class_name: str | None) -> Type[BaseDimension] | None:
    """
    Devuelve la clase Python correspondiente a una dimensión.
    """
    normalized = normalize_class_name(class_name)

    if not normalized:
        return None

    return DIMENSION_REGISTRY.get(normalized)


def list_available_dimensions() -> list[str]:
    """
    Devuelve las dimensiones registradas (debug / info).
    """
    return sorted(DIMENSION_REGISTRY.keys())