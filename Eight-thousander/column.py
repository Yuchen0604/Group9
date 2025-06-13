import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    base_dir = os.getcwd()
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    results = []
    column_summary = []

    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        csv_files = [f for f in os.listdir(subdir_path) if f.endswith('.csv')]
        
        if not csv_files:
            continue
        
        total_columns = 0
        all_columns = set()

        for csv_file in csv_files:
            file_path = os.path.join(subdir_path, csv_file)
            try:
                df = pd.read_csv(file_path)
                total_columns += len(df.columns)
                all_columns.update(df.columns)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        results.append({
            'Directory': subdir,
            'Total Columns': total_columns,
            'Table Numbers': len(csv_files)
        })

        column_summary.append({
            'Directory': subdir,
            'Columns': ', '.join(sorted(all_columns))
        })
    
    if not results:
        print("No CSV files found.")
        return
    
    df_results = pd.DataFrame(results)
    df_column_summary = pd.DataFrame(column_summary)

    print(df_results)

    # Save main summary table to Markdown
    with open('statistics.md', 'w') as f:
        f.write('# Column Statistics\n\n')
        f.write(df_results.to_markdown(index=False))
        f.write('\n')

    # Save aggregated column names to CSV
    df_column_summary.to_csv('aggregated_columns_by_language.csv', index=False)

    # Plot with different colors for each bar
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df_results['Directory'], df_results['Total Columns'], color=plt.cm.tab10.colors[:len(df_results)])
    plt.xlabel('Directory')
    plt.ylabel('Total Number of Columns')
    plt.title('Total Number of Columns per Directory')
    plt.tight_layout()
    plt.savefig('column_count_plot.png')
    plt.show()

if __name__ == '__main__':
    main()
