import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
file_path = "aggregated_columns_by_language.csv"
df = pd.read_csv(file_path)

# Choose multilingual models
models = {
    "mT5-small": SentenceTransformer("sentence-transformers/LaBSE"),  # Multilingual (replacement for mT5 embedding)
    "XLM-R": SentenceTransformer("xlm-r-bert-base-nli-stsb-mean-tokens"),
    "BLOOM": SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")  # Proxy for BLOOM
}

# Prepare language-wise column header lists
language_columns = {}
for index, row in df.iterrows():
    lang = row['Directory']
    columns = [str(col).strip() for col in row[1:].dropna()]
    language_columns[lang] = columns

# Create embeddings and similarity matrices
for model_name, model in models.items():
    print(f"\n=== Using model: {model_name} ===")
    
    # Compute averaged embedding per language (pooled from column headers)
    lang_embeddings = {}
    for lang, headers in language_columns.items():
        embeddings = model.encode(headers)
        lang_embeddings[lang] = np.mean(embeddings, axis=0)

    # Compute cosine similarity matrix
    languages = list(lang_embeddings.keys())
    sim_matrix = np.zeros((len(languages), len(languages)))

    for i, lang1 in enumerate(languages):
        for j, lang2 in enumerate(languages):
            sim_matrix[i][j] = cosine_similarity(
                [lang_embeddings[lang1]], [lang_embeddings[lang2]]
            )[0][0]

    # Create heatmap
    sim_df = pd.DataFrame(sim_matrix, index=languages, columns=languages)
    print(sim_df)

    plt.figure(figsize=(10, 8))
    sns.heatmap(sim_df, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title(f"Column Header Similarity Across Languages ({model_name})")
    plt.tight_layout()
    plt.show()
