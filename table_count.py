import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def count_csv_files_and_rows(root_directory):
    """
    Count CSV files (tables) and their rows in language subdirectories (en/de/zh/it/nl)
    under each main folder, with focus on table distribution.
    
    Args:
        root_directory (str): Path to the root directory containing the main folders
    
    Returns:
        dict: Summary statistics for each folder and language
    """
    
    # Language subdirectories to look for
    languages = ['en', 'de', 'zh', 'it', 'nl']
    
    # Dictionary to store results
    results = {}
    
    # Convert to Path object for easier handling
    root_path = Path(root_directory)
    
    if not root_path.exists():
        print(f"Error: Directory '{root_directory}' does not exist.")
        return {}
    
    # Iterate through each main folder
    for main_folder in root_path.iterdir():
        if main_folder.is_dir():
            folder_name = main_folder.name
            results[folder_name] = {}
            
            print(f"\nProcessing folder: {folder_name}")
            
            # Check each language subdirectory
            for lang in languages:
                lang_path = main_folder / lang
                
                if lang_path.exists() and lang_path.is_dir():
                    csv_files = list(lang_path.glob('*.csv'))
                    csv_count = len(csv_files)
                    total_rows = 0
                    file_details = []
                    
                    # Process each CSV file
                    for csv_file in csv_files:
                        try:
                            df = pd.read_csv(csv_file)
                            rows = len(df)
                            total_rows += rows
                            file_details.append({
                                'filename': csv_file.name,
                                'rows': rows,
                                'columns': len(df.columns)
                            })
                            print(f"  {lang}/{csv_file.name}: {rows} rows, {len(df.columns)} columns")
                        except Exception as e:
                            print(f"  Error reading {lang}/{csv_file.name}: {str(e)}")
                            file_details.append({
                                'filename': csv_file.name,
                                'rows': 'Error',
                                'columns': 'Error'
                            })
                    
                    results[folder_name][lang] = {
                        'csv_count': csv_count,
                        'total_rows': total_rows,
                        'files': file_details
                    }
                    
                    print(f"  {lang}: {csv_count} tables, {total_rows} total rows")
                else:
                    results[folder_name][lang] = {
                        'csv_count': 0,
                        'total_rows': 0,
                        'files': []
                    }
                    print(f"  {lang}: No tables found")
    
    return results

def print_summary(results):
    """Print a summary of the results with focus on table distribution"""
    print("\n" + "="*80)
    print("TABLE DISTRIBUTION SUMMARY")
    print("="*80)
    
    total_csv_files = 0
    total_rows = 0
    language_totals = {'en': 0, 'de': 0, 'zh':0, 'it': 0, 'nl': 0}
    
    for folder_name, folder_data in results.items():
        print(f"\nFolder: {folder_name}")
        print("-" * 50)
        
        folder_csv_count = 0
        folder_row_count = 0
        folder_lang_counts = {}
        
        for lang, lang_data in folder_data.items():
            csv_count = lang_data['csv_count']
            row_count = lang_data['total_rows']
            
            folder_csv_count += csv_count
            folder_row_count += row_count
            folder_lang_counts[lang] = csv_count
            language_totals[lang] += csv_count
            
            print(f"  {lang:2}: {csv_count:3} tables, {row_count:8} rows")
        
        # Calculate percentages for this folder
        if folder_csv_count > 0:
            print(f"\n  Distribution in {folder_name}:")
            for lang in ['en', 'de', 'zh', 'it', 'nl']:
                count = folder_lang_counts[lang]
                percentage = (count / folder_csv_count) * 100
                print(f"    {lang}: {count:3} tables ({percentage:5.1f}%)")
        
        print(f"\n  Folder Total: {folder_csv_count:3} tables, {folder_row_count:8} rows")
        
        total_csv_files += folder_csv_count
        total_rows += folder_row_count
    
    # Overall distribution
    print("\n" + "="*80)
    print("OVERALL DISTRIBUTION ACROSS ALL FOLDERS")
    print("="*80)
    
    for lang in ['en', 'de', 'zh', 'it', 'nl']:
        count = language_totals[lang]
        percentage = (count / total_csv_files) * 100 if total_csv_files > 0 else 0
        print(f"{lang:2}: {count:4} tables ({percentage:5.1f}%)")
    
    print("\n" + "="*80)
    print(f"GRAND TOTAL: {total_csv_files} tables, {total_rows:,} rows")
    print("="*80)

def save_results_to_csv(results, output_file='table_distribution_analysis.csv'):
    """Save results to a CSV file focusing on table distribution"""
    
    # Create summary data for each folder
    summary_rows = []
    detailed_rows = []
    
    for folder_name, folder_data in results.items():
        folder_total = sum(lang_data['csv_count'] for lang_data in folder_data.values())
        folder_row_total = sum(lang_data['total_rows'] for lang_data in folder_data.values())
        
        # Summary row for the folder
        summary_row = {
            'folder': folder_name,
            'total_tables': folder_total,
            'total_rows': folder_row_total,
            'en_tables': folder_data['en']['csv_count'],
            'de_tables': folder_data['de']['csv_count'],
            'zh_tables': folder_data['zh']['csv_count'],
            'it_tables': folder_data['it']['csv_count'],
            'nl_tables': folder_data['nl']['csv_count']
        }
        
        # Add percentages
        if folder_total > 0:
            summary_row.update({
                'en_percent': round((folder_data['en']['csv_count'] / folder_total) * 100, 1),
                'de_percent': round((folder_data['de']['csv_count'] / folder_total) * 100, 1),
                'zh_percent': round((folder_data['zh']['csv_count'] / folder_total) * 100, 1),
                'it_percent': round((folder_data['it']['csv_count'] / folder_total) * 100, 1),
                'nl_percent': round((folder_data['nl']['csv_count'] / folder_total) * 100, 1)
            })
        else:
            summary_row.update({
                'en_percent': 0, 'de_percent': 0, 'zh_percent': 0, 
                'it_percent': 0, 'nl_percent': 0 
            })
        
        summary_rows.append(summary_row)
        
        # Detailed rows for individual files
        for lang, lang_data in folder_data.items():
            for file_info in lang_data['files']:
                detailed_rows.append({
                    'folder': folder_name,
                    'language': lang,
                    'filename': file_info['filename'],
                    'rows': file_info['rows'],
                    'columns': file_info['columns']
                })
    
    # Save summary
    summary_df = pd.DataFrame(summary_rows)
    summary_output = output_file.replace('.csv', '_summary.csv')
    summary_df.to_csv(summary_output, index=False)
    print(f"\nTable distribution summary saved to: {summary_output}")
    
    # Save detailed results
    if detailed_rows:
        detailed_df = pd.DataFrame(detailed_rows)
        detailed_output = output_file.replace('.csv', '_detailed.csv')
        detailed_df.to_csv(detailed_output, index=False)
        print(f"Detailed file list saved to: {detailed_output}")
    
    return summary_df

def create_distribution_barchart(results, save_path='table_distribution_chart.svg'):
    """
    Create a stacked bar chart showing table distribution across languages,
    with different colors for each folder.
    
    Args:
        results (dict): Results from count_csv_files_and_rows function
        save_path (str): Path to save the chart image
    """
    
    # Prepare data for plotting
    languages = ['en', 'de', 'zh', 'it', 'nl']
    folders = list(results.keys())
    
    # Create a matrix of table counts: folders x languages
    data_matrix = []
    for folder in folders:
        folder_counts = []
        for lang in languages:
            count = results[folder][lang]['csv_count']
            folder_counts.append(count)
        data_matrix.append(folder_counts)
    
    # Convert to numpy array for easier manipulation
    data_matrix = np.array(data_matrix)
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Define colors for each folder (using a colormap for variety)
    colors = plt.cm.Set3(np.linspace(0, 1, len(folders)))
    
    # Create the stacked bar chart
    bar_width = 0.8
    x_positions = np.arange(len(languages))
    
    # Initialize bottom values for stacking
    bottoms = np.zeros(len(languages))
    
    # Plot each folder as a stack
    bars = []
    for i, folder in enumerate(folders):
        folder_data = data_matrix[i]
        # Only plot if folder has any tables
        if folder_data.sum() > 0:
            bar = ax.bar(x_positions, folder_data, bar_width, 
                        bottom=bottoms, label=folder, color=colors[i],
                        alpha=0.8, edgecolor='white', linewidth=0.5)
            bars.append(bar)
            bottoms += folder_data
    
    # Customize the chart
    ax.set_xlabel('Languages', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Tables', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Wikipedia Tables Across Languages', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Set x-axis labels
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lang.upper() for lang in languages], fontsize=11)
    
    # Add value labels on top of each bar
    totals_by_language = bottoms
    for i, total in enumerate(totals_by_language):
        if total > 0:
            ax.text(i, total + 0.5, str(int(total)), 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Add legend
    if len(folders) <= 15:  # Only show legend if not too many folders
        ax.legend(bbox_to_anchor=(0.55, 1), loc='upper left', 
                 title='Sources', title_fontsize=11, fontsize=9)
    else:
        # If too many folders, add a note about colors
        ax.text(0.02, 0.98, f'Note: {len(folders)} folders represented by different colors', 
                transform=ax.transAxes, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=9)
    
    # Customize grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Set y-axis to start from 0
    ax.set_ylim(0, max(totals_by_language) * 1.1 if max(totals_by_language) > 0 else 1)
    
    # Adjust layout to prevent legend cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"\nBar chart saved as: {save_path}")
    
    # Display some statistics about the chart
    print(f"\nChart Statistics:")
    print(f"- Total folders plotted: {len([f for f in folders if sum(results[f][lang]['csv_count'] for lang in languages) > 0])}")
    print(f"- Languages with tables: {sum(1 for total in totals_by_language if total > 0)}")
    print(f"- Most tables in language: {languages[np.argmax(totals_by_language)]} ({int(max(totals_by_language))} tables)")
    
    # Show the plot
    plt.show()
    
    return fig, ax

# Main execution
if __name__ == "__main__":
    # Set your root directory path here
    root_dir = "."  # Current directory - change this to your actual path
    
    print("Table Distribution Analysis Script")
    print("="*80)
    print(f"Analyzing directory: {os.path.abspath(root_dir)}")
    print("Counting CSV tables in language subdirectories: en, de, zh, it, nl")
    
    # Run the analysis
    results = count_csv_files_and_rows(root_dir)
    
    if results:
        # Print summary with distribution
        print_summary(results)
        
        # Save detailed results to CSV
        summary_df = save_results_to_csv(results)
        
        # Create visualization
        print(f"\nCreating bar chart visualization...")
        create_distribution_barchart(results)
        
        # Additional analysis
        print(f"\nQuick Analysis:")
        total_folders = len(results)
        folders_with_tables = sum(1 for folder_data in results.values() 
                                 if sum(lang_data['csv_count'] for lang_data in folder_data.values()) > 0)
        
        print(f"- Found {total_folders} main folders")
        print(f"- {folders_with_tables} folders contain CSV tables")
        print(f"- {total_folders - folders_with_tables} folders have no tables")
        
    else:
        print("No results to display.")