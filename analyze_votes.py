import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def analyze_votes_from_csv():
    csv_file = 'votes_export.csv'
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    
    # Process into long format
    # Keep 'Question Index' to use as label
    df_long = pd.concat([
        df[['Question', 'Question Index', 'Answer 1 (Type)', 'Vote 1']].rename(columns={'Answer 1 (Type)': 'Type', 'Vote 1': 'Vote'}),
        df[['Question', 'Question Index', 'Answer 2 (Type)', 'Vote 2']].rename(columns={'Answer 2 (Type)': 'Type', 'Vote 2': 'Vote'})
    ])

    # Clean up vote labels
    df_long['Vote'] = df_long['Vote'].apply(lambda x: 'Up' if 'Up' in str(x) else ('Down' if 'Down' in str(x) else None))
    df_long = df_long.dropna(subset=['Vote'])

    # Aggregate counts by Question, Question Index, Type, Vote
    agg = df_long.groupby(['Question', 'Question Index', 'Type', 'Vote']).size().unstack(fill_value=0)

    # Ensure columns exist
    for col in ['Up', 'Down']:
        if col not in agg.columns: agg[col] = 0
    agg = agg[['Up', 'Down']]

    if agg.empty:
        print("No votes found in the CSV.")
        return

    # Sort by Question Index
    agg = agg.sort_index(level='Question Index')

    # Prepare data for grouped-stacked bar plot
    pivot_df = agg.unstack(level='Type')

    fig, ax = plt.subplots(figsize=(20, 10))

    # Get index labels (Question Index) from the sorted dataframe
    q_indices = pivot_df.index.get_level_values('Question Index')
    n_q = len(q_indices)
    ind = np.arange(n_q)
    width = 0.35

    # Plot RAG and LLM as grouped bars, stacked internally
    # RAG bars
    rag_up = pivot_df[('Up', 'RAG')]
    rag_down = pivot_df[('Down', 'RAG')]
    ax.bar(ind - width/2, rag_up, width, color='green', label='RAG Up')
    ax.bar(ind - width/2, rag_down, width, bottom=rag_up, color='red', label='RAG Down')

    # LLM bars
    llm_up = pivot_df[('Up', 'LLM')]
    llm_down = pivot_df[('Down', 'LLM')]
    ax.bar(ind + width/2, llm_up, width, color='lightgreen', label='LLM Up')
    ax.bar(ind + width/2, llm_down, width, bottom=llm_up, color='salmon', label='LLM Down')

    ax.set_ylabel('Count')
    ax.set_title('Up/Down Votes by Question (RAG vs LLM)')
    ax.set_xticks(ind)
    ax.set_xticklabels(q_indices, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.savefig('vote_analysis.png')
    print("Plot saved as vote_analysis.png")


if __name__ == "__main__":
    analyze_votes_from_csv()
