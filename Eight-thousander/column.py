import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    base_dir = os.getcwd()
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    results = []
    
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        csv_files = [f for f in os.listdir(subdir_path) if f.endswith('.csv')]
        
        if not csv_files:
            continue
        
        col_counts = []
        for csv_file in csv_files:
            file_path = os.path.join(subdir_path, csv_file)
            try:
                df = pd.read_csv(file_path)
                col_counts.append(len(df.columns))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if col_counts:
            avg_cols = sum(col_counts) / len(col_counts)
            results.append({'Directory': subdir, 'Avg Columns': avg_cols, 'Table Numbers': len(col_counts)})
    
    if not results:
        print("No CSV files found.")
        return
    
    df_results = pd.DataFrame(results)
    print(df_results)
    
    # Save table to Markdown
    with open('statistics.md', 'w') as f:
        f.write('# Column Statistics\n\n')
        f.write(df_results.to_markdown(index=False))
        f.write('\n')

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(df_results['Directory'], df_results['Avg Columns'])
    plt.xlabel('Directory')
    plt.ylabel('Average Number of Columns')
    plt.title('Average Number of Columns per Directory')
    plt.tight_layout()
    plt.savefig('column_count_plot.png')
    plt.show()

if __name__ == '__main__':
    main()

