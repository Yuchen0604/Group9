import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def analyze_column_completeness(root_directory):
    """
    Analyze CSV files to find tables with most columns and identify incomplete columns.
    
    Args:
        root_directory (str): Path to the root directory containing the main folders
    
    Returns:
        dict: Analysis results for each language
    """
    
    languages = ['en', 'de', 'zh', 'it', 'nl']
    
    # Results dictionary
    results = {
        'language_stats': {},
        'detailed_files': [],
        'max_column_files': {}
    }
    
    # Initialize language statistics
    for lang in languages:
        results['language_stats'][lang] = {
            'max_columns': 0,
            'max_columns_file': None,
            'total_columns_sum': 0,
            'incomplete_columns_sum': 0,
            'files_analyzed': 0,
            'max_column_table_info': None
        }
    
    root_path = Path(root_directory)
    
    if not root_path.exists():
        print(f"Error: Directory '{root_directory}' does not exist.")
        return results
    
    print("Analyzing column completeness across CSV files...")
    print("=" * 60)
    
    # Process each main folder
    for main_folder in root_path.iterdir():
        if main_folder.is_dir():
            folder_name = main_folder.name
            print(f"\nProcessing folder: {folder_name}")
            
            # Check each language subdirectory
            for lang in languages:
                lang_path = main_folder / lang
                
                if lang_path.exists() and lang_path.is_dir():
                    csv_files = list(lang_path.glob('*.csv'))
                    
                    for csv_file in csv_files:
                        try:
                            # Read CSV file
                            df = pd.read_csv(csv_file)
                            
                            if df.empty:
                                continue
                            
                            total_columns = len(df.columns)
                            results['language_stats'][lang]['files_analyzed'] += 1
                            
                            # Count columns with missing values
                            missing_counts = df.isnull().sum()
                            incomplete_columns = sum(1 for count in missing_counts if count > 0)
                            
                            # Calculate missing data percentage for each column
                            total_rows = len(df)
                            column_completeness = []
                            
                            for col in df.columns:
                                missing_count = df[col].isnull().sum()
                                completeness_pct = ((total_rows - missing_count) / total_rows) * 100
                                column_completeness.append({
                                    'column': col,
                                    'missing_count': missing_count,
                                    'completeness_pct': completeness_pct
                                })
                            
                            # Store detailed file information
                            file_info = {
                                'folder': folder_name,
                                'language': lang,
                                'filename': csv_file.name,
                                'total_columns': total_columns,
                                'incomplete_columns': incomplete_columns,
                                'total_rows': total_rows,
                                'column_details': column_completeness
                            }
                            
                            results['detailed_files'].append(file_info)
                            
                            # Update language statistics
                            lang_stats = results['language_stats'][lang]
                            
                            # Check if this file has the most columns for this language
                            if total_columns > lang_stats['max_columns']:
                                lang_stats['max_columns'] = total_columns
                                lang_stats['max_columns_file'] = f"{folder_name}/{lang}/{csv_file.name}"
                                lang_stats['max_column_table_info'] = file_info
                            
                            # Add to totals (for the file with most columns per language, we'll adjust later)
                            lang_stats['total_columns_sum'] += total_columns
                            lang_stats['incomplete_columns_sum'] += incomplete_columns
                            
                            print(f"  {lang}/{csv_file.name}: {total_columns} cols, {incomplete_columns} incomplete")
                            
                        except Exception as e:
                            print(f"  Error reading {lang}/{csv_file.name}: {str(e)}")
    
    # Now calculate the final sums based on the requirement:
    # 1) Select table with most columns for each language
    # 2) Calculate sum of column numbers and incomplete columns for each language
    
    final_results = {}
    for lang in languages:
        lang_stats = results['language_stats'][lang]
        
        if lang_stats['files_analyzed'] > 0:
            # For the requirement, we use the max column table info
            max_col_info = lang_stats['max_column_table_info']
            
            final_results[lang] = {
                'max_columns_file': lang_stats['max_columns_file'],
                'max_columns': lang_stats['max_columns'],
                'total_columns_sum': lang_stats['total_columns_sum'],  # Sum across all files
                'incomplete_columns_sum': lang_stats['incomplete_columns_sum'],  # Sum across all files
                'files_count': lang_stats['files_analyzed'],
                'max_table_incomplete_cols': max_col_info['incomplete_columns'] if max_col_info else 0
            }
        else:
            final_results[lang] = {
                'max_columns_file': 'No files found',
                'max_columns': 0,
                'total_columns_sum': 0,
                'incomplete_columns_sum': 0,
                'files_count': 0,
                'max_table_incomplete_cols': 0
            }
    
    return final_results, results['detailed_files']

def print_analysis_summary(results):
    """Print summary of the column analysis"""
    print("\n" + "=" * 80)
    print("COLUMN COMPLETENESS ANALYSIS SUMMARY")
    print("=" * 80)
    
    languages = ['en', 'de', 'zh', 'it', 'nl']
    
    for lang in languages:
        lang_data = results[lang]
        print(f"\n{lang.upper()} Language:")
        print("-" * 40)
        print(f"  Files analyzed: {lang_data['files_count']}")
        print(f"  Table with most columns: {lang_data['max_columns_file']}")
        print(f"  Max columns in single table: {lang_data['max_columns']}")
        print(f"  Sum of all columns across tables: {lang_data['total_columns_sum']}")
        print(f"  Sum of incomplete columns across tables: {lang_data['incomplete_columns_sum']}")
        
        if lang_data['total_columns_sum'] > 0:
            incomplete_percentage = (lang_data['incomplete_columns_sum'] / lang_data['total_columns_sum']) * 100
            print(f"  Incomplete columns ratio: {incomplete_percentage:.1f}%")

def create_column_completeness_chart(results, save_path='column_completeness_chart.svg'):
    """
    Create a stacked bar chart showing complete columns (bottom) and incomplete columns (top) by language.
    
    Args:
        results (dict): Results from analyze_column_completeness function
        save_path (str): Path to save the chart image
    """
    
    languages = ['en', 'de', 'zh', 'it', 'nl']
    
    # Extract data for plotting
    total_columns = []
    incomplete_columns = []
    complete_columns = []
    
    for lang in languages:
        total = results[lang]['total_columns_sum']
        incomplete = results[lang]['incomplete_columns_sum']
        complete = total - incomplete
        
        total_columns.append(total)
        incomplete_columns.append(incomplete)
        complete_columns.append(complete)
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Set the width of bars and positions
    bar_width = 0.6
    x_positions = np.arange(len(languages))
    
    # Create stacked bars - complete columns first (bottom), then incomplete on top
    bars1 = ax.bar(x_positions, complete_columns, bar_width, 
                   label='Complete Columns', color='red', alpha=0.6, edgecolor='white', linewidth=1)
    bars2 = ax.bar(x_positions, incomplete_columns, bar_width, bottom=complete_columns,
                   label='Incomplete Columns', color='orange', alpha=0.6, edgecolor='white', linewidth=1)
    
    # Customize the chart
    ax.set_xlabel('Languages', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Columns', fontsize=12, fontweight='bold')
    ax.set_title('Column Completeness Analysis: Complete vs Incomplete Columns by Language', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Set x-axis labels
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lang.upper() for lang in languages], fontsize=11)
    
    # Add total value labels on top of each bar
    for i, total in enumerate(total_columns):
        if total > 0:
            ax.text(x_positions[i], total + max(total_columns) * 0.01,
                   f'{int(total)}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add labels for complete columns (in the middle of green bars)
    for i, (complete, incomplete) in enumerate(zip(complete_columns, incomplete_columns)):
        if complete > 0:
            # Position label in the middle of the complete (green) section
            label_y = complete / 2
            ax.text(x_positions[i], label_y, f'{int(complete)}',
                   ha='center', va='center', fontweight='bold', fontsize=10, 
                   color='darkgreen')
    
    # Add labels for incomplete columns (in the middle of red bars)
    for i, (complete, incomplete) in enumerate(zip(complete_columns, incomplete_columns)):
        if incomplete > 0:
            # Position label in the middle of the incomplete (red) section
            label_y = complete + (incomplete / 2)
            ax.text(x_positions[i], label_y, f'{int(incomplete)}',
                   ha='center', va='center', fontweight='bold', fontsize=10, 
                   color='darkred')
    
    # Add percentage labels for incomplete columns (above the bars)
    for i, (total, incomplete) in enumerate(zip(total_columns, incomplete_columns)):
        if total > 0 and incomplete > 0:
            percentage = (incomplete / total) * 100
            ax.text(x_positions[i], total + max(total_columns) * 0.05, f'{percentage:.1f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=10, 
                   color='red', style='italic')
    
    # Add legend
    ax.legend(loc='upper right', fontsize=11)
    
    # Customize grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Set y-axis limits
    max_value = max(total_columns) if total_columns else 1
    ax.set_ylim(0, max_value * 1.2)
    
    # Add summary text box
    total_all_columns = sum(total_columns)
    total_incomplete_columns = sum(incomplete_columns)
    total_complete_columns = sum(complete_columns)
    overall_incomplete_pct = (total_incomplete_columns / total_all_columns * 100) if total_all_columns > 0 else 0
    overall_complete_pct = (total_complete_columns / total_all_columns * 100) if total_all_columns > 0 else 0
    
    summary_text = (f'Overall: {total_all_columns} total columns\n'
                   f'Complete: {total_complete_columns} ({overall_complete_pct:.1f}%)\n'
                   f'Incomplete: {total_incomplete_columns} ({overall_incomplete_pct:.1f}%)')
    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
            fontsize=10, fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"\nColumn completeness chart saved as: {save_path}")
    
    # Display chart statistics
    print(f"\nChart Statistics:")
    print(f"- Total columns across all languages: {total_all_columns:,}")
    print(f"- Complete columns: {total_complete_columns:,} ({overall_complete_pct:.1f}%)")
    print(f"- Incomplete columns: {total_incomplete_columns:,} ({overall_incomplete_pct:.1f}%)")
    
    # Show the plot
    plt.show()
    
    return fig, ax

def save_detailed_analysis(results, detailed_files, output_file='column_analysis_detailed.csv'):
    """Save detailed analysis results to CSV files"""
    
    # Summary by language
    summary_data = []
    for lang, data in results.items():
        summary_data.append({
            'language': lang,
            'files_analyzed': data['files_count'],
            'max_columns_file': data['max_columns_file'],
            'max_columns': data['max_columns'],
            'total_columns_sum': data['total_columns_sum'],
            'incomplete_columns_sum': data['incomplete_columns_sum'],
            'completeness_rate': ((data['total_columns_sum'] - data['incomplete_columns_sum']) / data['total_columns_sum'] * 100) if data['total_columns_sum'] > 0 else 0
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_output = output_file.replace('.csv', '_summary.csv')
    summary_df.to_csv(summary_output, index=False)
    print(f"Summary analysis saved to: {summary_output}")
    
    # Detailed file analysis
    detailed_data = []
    for file_info in detailed_files:
        detailed_data.append({
            'folder': file_info['folder'],
            'language': file_info['language'],
            'filename': file_info['filename'],
            'total_columns': file_info['total_columns'],
            'incomplete_columns': file_info['incomplete_columns'],
            'total_rows': file_info['total_rows'],
            'completeness_rate': ((file_info['total_columns'] - file_info['incomplete_columns']) / file_info['total_columns'] * 100) if file_info['total_columns'] > 0 else 0
        })
    
    if detailed_data:
        detailed_df = pd.DataFrame(detailed_data)
        detailed_df.to_csv(output_file, index=False)
        print(f"Detailed file analysis saved to: {output_file}")
    
    return summary_df

# Main execution
if __name__ == "__main__":
    # Set your root directory path here
    root_dir = "."  # Current directory - change this to your actual path
    
    print("Column Completeness Analysis Script")
    print("=" * 80)
    print(f"Analyzing directory: {os.path.abspath(root_dir)}")
    print("Analyzing CSV files in language subdirectories: en, de, zh, it, nl")
    print("Tasks:")
    print("1. Find table with most columns per language")
    print("2. Calculate sum of columns and incomplete columns per language")
    print("3. Create visualization showing completeness analysis")
    
    # Run the analysis
    results, detailed_files = analyze_column_completeness(root_dir)
    
    if any(results[lang]['files_count'] > 0 for lang in ['en', 'de', 'zh', 'it', 'nl']):
        # Print summary
        print_analysis_summary(results)
        
        # Create visualization
        print(f"\nCreating column completeness visualization...")
        create_column_completeness_chart(results)
        
        # Save detailed results
        save_detailed_analysis(results, detailed_files)
        
        print(f"\nAnalysis completed successfully!")
        
    else:
        print("No CSV files found to analyze.")