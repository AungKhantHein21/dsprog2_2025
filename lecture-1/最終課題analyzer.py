import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_tokyodev():
    conn = sqlite3.connect("tokyodev_jobs.db")
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()

    if df.empty:
        print("No data! Run scraper first.")
        return

    print("--- Data Loaded ---")
    print(df.groupby('japanese_level')['salary_min'].mean())

    # Create a nice Boxplot
    plt.figure(figsize=(10, 6))
    
    # Order the levels logically
    order = ["None", "Conversational", "Business", "Fluent"]
    
    sns.boxplot(x='japanese_level', y='salary_min', data=df, order=order, palette="viridis")
    
    plt.title('Impact of Japanese Requirement on Tech Salaries in Tokyo')
    plt.ylabel('Minimum Annual Salary (JPY)')
    plt.xlabel('Japanese Level Required')
    
    # Format Y axis to normal numbers
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    plt.savefig('tokyodev_analysis.png')
    print("Graph saved as tokyodev_analysis.png")

if __name__ == "__main__":
    analyze_tokyodev()