import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Load the data
file_path = "aggregated_columns_by_language.csv"
df = pd.read_csv(file_path)

# Create output directory
output_dir = "similarity_outputs"
os.makedirs(output_dir, exist_ok=True)

# Choose multilingual models
models = {
    "mT5-small": SentenceTransformer("sentence-transformers/LaBSE"),  # mT5 replacement
    "XLM-R": SentenceTransformer("xlm-r-bert-base-nli-stsb-mean-tokens"),
    "BLOOM": SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")  # BLOOM proxy
}

# Prepare language-wise column header lists
language_columns = {}
for index, row in df.iterrows():
    lang = row['Directory']
    columns = [str(col).strip() for col in row[1:].dropna()]
    language_columns[lang] = columns

# Analyze using each model
for model_name, model in models.items():
    print(f"\n=== Using model: {model_name} ===")
    
    # Compute averaged embedding per language
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

    # Save similarity matrix as CSV
    sim_df = pd.DataFrame(sim_matrix, index=languages, columns=languages)
    csv_path = os.path.join(output_dir, f"similarity_matrix_{model_name.replace('/', '_')}.csv")
    sim_df.to_csv(csv_path)
    print(f"Saved similarity matrix to: {csv_path}")

    # Visualize similarity matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(sim_df, annot=True, cmap="YlGnBu", fmt=".2f", cbar=True, square=True,
                linewidths=0.5, linecolor='gray')
    plt.title(f"Column Similarity Across Languages ({model_name})", fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f"similarity_matrix_{model_name.replace('/', '_')}.png")
    plt.savefig(plot_path)
    plt.show()
    print(f"Saved heatmap to: {plot_path}")

    # Select example pairs: high similarity (de-nl), low similarity (et-en)
    pair_examples = [('de', 'nl'), ('et', 'en')]
    for lang_a, lang_b in pair_examples:
        print(f"\n--- Column comparison between '{lang_a}' and '{lang_b}' ---")
        cols_a = language_columns.get(lang_a, [])
        cols_b = language_columns.get(lang_b, [])

        max_len = max(len(cols_a), len(cols_b))
        cols_a += [""] * (max_len - len(cols_a))
        cols_b += [""] * (max_len - len(cols_b))

        comparison_df = pd.DataFrame({f'{lang_a}_columns': cols_a, f'{lang_b}_columns': cols_b})
        print(comparison_df.to_string(index=False))

        # Save comparison to CSV
        comparison_path = os.path.join(output_dir, f"column_comparison_{lang_a}_{lang_b}_{model_name.replace('/', '_')}.csv")
        comparison_df.to_csv(comparison_path, index=False)
        print(f"Saved column comparison to: {comparison_path}")
