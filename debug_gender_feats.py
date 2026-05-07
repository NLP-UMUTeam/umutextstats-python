import pandas as pd
from collections import Counter

from umutextstats.nlp import annotate_dataframe_with_stanza
from umutextstats.dimensions.pos_tagging_tag import POSTaggingTag


texts = [
    "Hoy voy al cine.",
    "Mañana trabajaremos.",
    "Ayer llovió mucho.",
    "Siempre llegas tarde.",
    "Luego hablamos.",
]

df = pd.DataFrame({"text_norm": texts})

df = annotate_dataframe_with_stanza(
    df,
    input_path="debug_gender_feats.py",
    use_cache=False,
)

print("\nTAGGED POS")
print(df["tagged_pos"].to_string(index=False))

gender_values = Counter()

for tagged in df["tagged_pos"]:
    items = POSTaggingTag(key="debug")._parse_tagged_pos(tagged)

    for item in items:
        feats = item["feats"]

        for feat in feats.split("|"):
            if feat.startswith("Gender="):
                gender_values[feat] += 1

print("\nGENDER VALUES")
print(gender_values)

for universal in ["Gender=Masc", "Gender=Fem", "Gender=Neut", "Gender=Com"]:
    dim = POSTaggingTag(
        key=universal,
        postagger_universal=universal,
    )

    print(f"\n{universal}")
    print(dim.compute(df).to_string(index=False))
    
    
print("\nADV WORDS")

for tagged in df["tagged_pos"]:
    items = POSTaggingTag(key="debug")._parse_tagged_pos(tagged)

    for item in items:
        print (item)
