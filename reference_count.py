import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from urllib.parse import quote
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class WikipediaReferencesCounter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Define the sources with their English URLs
        self.sources = [
            {
                'name': 'Seven_Summits',
                'en_url': 'https://en.wikipedia.org/wiki/Seven_Summits'
            },
            {
                'name': 'Eight-thousander', 
                'en_url': 'https://en.wikipedia.org/wiki/Eight-thousander'
            },
            {
                'name': 'List_of_mountains_of_the_Alps_over_4000_metres',
                'en_url': 'https://en.wikipedia.org/wiki/List_of_mountains_of_the_Alps_over_4000_metres'
            },
            {
                'name': 'Lists_of_earthquakes',
                'en_url': 'https://en.wikipedia.org/wiki/Lists_of_earthquakes'
            },
            {
                'name': 'Highest_unclimbed_mountain',
                'en_url': 'https://en.wikipedia.org/wiki/Highest_unclimbed_mountain'
            },
            {
                'name': 'List_of_highest_mountains_on_Earth',
                'en_url': 'https://en.wikipedia.org/wiki/List_of_highest_mountains_on_Earth'
            },
            {
                'name': 'Lakes_of_Titan',
                'en_url': 'https://en.wikipedia.org/wiki/Lakes_of_Titan'
            },
            {
                'name': 'List_of_largest_lakes_of_Europe',
                'en_url': 'https://en.wikipedia.org/wiki/List_of_largest_lakes_of_Europe'
            },
            {
                'name': 'List_of_lakes_by_area',
                'en_url': 'https://en.wikipedia.org/wiki/List_of_lakes_by_area'
            }
        ]
        
        # Languages to check
        self.languages = ['en', 'de', 'zh', 'it', 'nl']
        
    def get_page_title_from_url(self, url):
        """Extract page title from Wikipedia URL"""
        return url.split('/wiki/')[-1]
    
    def build_url_for_language(self, page_title, lang):
        """Build Wikipedia URL for different language"""
        if lang == 'en':
            return f'https://en.wikipedia.org/wiki/{page_title}'
        else:
            return f'https://{lang}.wikipedia.org/wiki/{page_title}'
    
    def get_interlanguage_links(self, page_title, source_lang='en'):
        """Get interlanguage links using Wikipedia API"""
        api_url = f'https://{source_lang}.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'format': 'json',
            'titles': page_title.replace('_', ' '),
            'prop': 'langlinks',
            'lllimit': 'max'
        }
        
        try:
            response = self.session.get(api_url, params=params, timeout=10)
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return {}
                
            page_id = list(pages.keys())[0]
            if page_id == '-1':  # Page not found
                return {}
                
            langlinks = pages[page_id].get('langlinks', [])
            
            # Create mapping of language code to page title
            lang_mapping = {}
            for link in langlinks:
                lang_code = link['lang']
                if lang_code in self.languages:
                    lang_mapping[lang_code] = link['*'].replace(' ', '_')
                    
            return lang_mapping
            
        except Exception as e:
            print(f"Error getting interlanguage links for {page_title}: {e}")
            return {}
    
    def count_references_in_page(self, url, lang):
        """Count references in a Wikipedia page"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return 0
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Count references in References section
            ref_count = 0
            
            # Look for References section
            references_section = soup.find('span', {'id': 'References'}) or \
                               soup.find('span', {'id': 'Références'}) or \
                               soup.find('span', {'id': 'Referenzen'}) or \
                               soup.find('span', {'id': 'Bibliografia'}) or \
                               soup.find('span', {'id': 'Literatuur'}) or \
                               soup.find('span', {'id': '参考文献'}) or \
                               soup.find('span', {'id': '參考資料'})
            
            if references_section:
                # Find the parent heading and get the next elements
                parent = references_section.find_parent()
                if parent:
                    current = parent.find_next_sibling()
                    while current and current.name not in ['h1', 'h2', 'h3']:
                        if current.name == 'ol':
                            ref_count += len(current.find_all('li'))
                        elif current.name == 'div' and 'reflist' in current.get('class', []):
                            ref_count += len(current.find_all('li'))
                        current = current.find_next_sibling()
            
            # Method 2: Count citation elements if no references section found
            if ref_count == 0:
                citations = soup.find_all('sup', class_='reference')
                ref_count = len(citations)
            
            # Method 3: Count reflist items
            if ref_count == 0:
                reflist_divs = soup.find_all('div', class_='reflist')
                for div in reflist_divs:
                    ref_count += len(div.find_all('li'))
            
            return ref_count
            
        except Exception as e:
            print(f"Error counting references for {url}: {e}")
            return 0
    
    def get_references_for_all_languages(self):
        """Get reference counts for all sources across all languages"""
        results = []
        
        for source in self.sources:
            print(f"\nProcessing: {source['name']}")
            page_title = self.get_page_title_from_url(source['en_url'])
            
            # Get interlanguage links
            lang_links = self.get_interlanguage_links(page_title)
            lang_links['en'] = page_title  # Add English
            
            source_results = {'source': source['name']}
            
            for lang in self.languages:
                if lang in lang_links:
                    url = self.build_url_for_language(lang_links[lang], lang)
                    print(f"  Checking {lang}: {url}")
                    ref_count = self.count_references_in_page(url, lang)
                    source_results[lang] = ref_count
                    print(f"    References found: {ref_count}")
                else:
                    source_results[lang] = 0
                    print(f"  {lang}: Page not available")
                
                # Be respectful to Wikipedia servers
                time.sleep(1)
            
            results.append(source_results)
        
        return results
    
    def create_summary_dataframe(self, results):
        """Create a summary DataFrame from results"""
        df = pd.DataFrame(results)
        df = df.set_index('source')
        
        # Add totals
        totals = df.sum()
        totals.name = 'TOTAL'
        df = pd.concat([df, totals.to_frame().T])
        
        return df
    
    def save_to_csv(self, df, filename='wikipedia_references_analysis.csv'):
        """Save results to CSV file with additional formatting"""
        # Create a copy for CSV export
        csv_df = df.copy()
        
        # Add metadata
        metadata = pd.DataFrame({
            'Analysis': ['Wikipedia References Count Analysis'],
            'Date': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Languages': [', '.join([lang.upper() for lang in self.languages])],
            'Total_Sources': [len(self.sources)]
        })
        
        # Save main results
        csv_df.to_csv(filename)
        
        # Save metadata to separate file
        metadata_filename = filename.replace('.csv', '_metadata.csv')
        metadata.to_csv(metadata_filename, index=False)
        
        print(f"Results saved to '{filename}'")
        print(f"Metadata saved to '{metadata_filename}'")
        
        return filename
    
    def create_bar_charts(self, df, save_plots=True):
        """Create comprehensive bar charts for the analysis"""
        # Remove total row for plotting
        plot_df = df.iloc[:-1].copy()
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(figsize=(16, 6))
        fig.suptitle('Wikipedia References Analysis Across Languages', fontsize=16, fontweight='bold')
        
        # # 1. Stacked bar chart - References by source and language
        # ax1 = axes[0, 0]
        # plot_df.plot(kind='bar', stacked=True, ax=ax1, width=0.8)
        # ax1.set_title('References by Source (Stacked)', fontweight='bold')
        # ax1.set_xlabel('Wikipedia Sources')
        # ax1.set_ylabel('Number of References')
        # ax1.legend(title='Languages', bbox_to_anchor=(1.05, 1), loc='upper left')
        # ax1.tick_params(axis='x', rotation=45)
        
        # # 2. Grouped bar chart - Total references by language
        # ax2 = axes[0, 1]
        # language_totals = plot_df.sum()
        # bars = ax2.bar(language_totals.index, language_totals.values, 
        #               color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        # ax2.set_title('Total References by Language', fontweight='bold')
        # ax2.set_xlabel('Languages')
        # ax2.set_ylabel('Total Number of References')
        
        # # Add value labels on bars
        # for bar in bars:
        #     height = bar.get_height()
        #     ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
        #             f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Heatmap - References by source and language
        # ax3 = axes[1, 0]
        sns.heatmap(plot_df.T, annot=True, fmt='d', cmap='YlOrRd', ax=axes, 
                   cbar_kws={'label': 'Number of References'})
        # axes.set_title('References Heatmap (Languages vs Sources)', fontweight='bold')
        axes.set_xlabel('Wikipedia Sources')
        axes.set_ylabel('Languages')
        # Set x-tick labels to be horizontal and wrap long names
        axes.set_xticklabels(
            [ '\n'.join([label[i:i+21] for i in range(0, len(label), 21)]) for label in plot_df.index ],
            rotation=0,
            ha='center',
            fontsize=8  # Set your desired font size here
        )
        axes.set_yticklabels([lang.upper() for lang in self.languages], fontsize=10)

        # # 4. Average references per source by language
        # ax4 = axes[1, 1]
        # avg_refs = plot_df.mean()
        # bars = ax4.bar(avg_refs.index, avg_refs.values,
        #               color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        # ax4.set_title('Average References per Source by Language', fontweight='bold')
        # ax4.set_xlabel('Languages')
        # ax4.set_ylabel('Average Number of References')
        
        # # Add value labels on bars
        # for bar in bars:
        #     height = bar.get_height()
        #     ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
        #             f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('wikipedia_references_analysis.svg', dpi=300, bbox_inches='tight')
            print("Bar charts saved to 'wikipedia_references_analysis.svg'")
        
        plt.show()
        
        return fig
    
    def create_detailed_comparison_chart(self, df, save_plots=True):
        """Create a detailed comparison chart focusing on individual sources"""
        plot_df = df.iloc[:-1].copy()
        
        # Create a larger figure for detailed view
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Create grouped bar chart
        x = np.arange(len(plot_df.index))
        width = 0.15
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, lang in enumerate(self.languages):
            offset = (i - 2) * width
            bars = ax.bar(x + offset, plot_df[lang], width, label=lang.upper(), color=colors[i])
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Only show label if there are references
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        ax.set_xlabel('Wikipedia Sources', fontweight='bold')
        ax.set_ylabel('Number of References', fontweight='bold')
        ax.set_title('References Comparison Across Languages by Source', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([name.replace('_', '\n') for name in plot_df.index], rotation=45, ha='right')
        ax.legend(title='Languages', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('wikipedia_references_detailed_comparison.svg', dpi=300, bbox_inches='tight')
            print("Detailed comparison chart saved to 'wikipedia_references_detailed_comparison.svg'")
        
        plt.show()
        
        return fig
    
    def run_analysis(self):
        """Run the complete analysis"""
        print("Starting Wikipedia References Analysis...")
        print("="*50)
        
        # Get all reference counts
        results = self.get_references_for_all_languages()
        
        # Create summary
        df = self.create_summary_dataframe(results)
        
        print("\n" + "="*50)
        print("RESULTS SUMMARY")
        print("="*50)
        print(df.to_string())
        
        # Save to CSV
        self.save_to_csv(df)
        
        # Create visualizations
        print("\n" + "="*50)
        print("GENERATING VISUALIZATIONS")
        print("="*50)
        
        # Create bar charts
        self.create_bar_charts(df)
        
        # Create detailed comparison
        self.create_detailed_comparison_chart(df)
        
        return df

# Usage
if __name__ == "__main__":
    counter = WikipediaReferencesCounter()
    results_df = counter.run_analysis()
    
    # Additional analysis
    print("\n" + "="*50)
    print("ADDITIONAL STATISTICS")
    print("="*50)
    
    # Exclude total row for stats
    stats_df = results_df.iloc[:-1]
    
    print(f"Average references per source by language:")
    for lang in counter.languages:
        avg_refs = stats_df[lang].mean()
        print(f"  {lang.upper()}: {avg_refs:.1f}")
    
    print(f"\nTotal references by language:")
    for lang in counter.languages:
        total_refs = stats_df[lang].sum()
        print(f"  {lang.upper()}: {total_refs}")
    
    print(f"\nSources with most references:")
    for lang in counter.languages:
        max_source = stats_df[lang].idxmax()
        max_refs = stats_df[lang].max()
        print(f"  {lang.upper()}: {max_source} ({max_refs} refs)")