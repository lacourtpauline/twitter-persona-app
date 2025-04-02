
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

def compute_engagement(df):
    df = df.copy()
    df['engagement'] = df['favorite_count'] / df['view_count']
    df = df.dropna(subset=['text', 'engagement'])
    return df.sort_values(by='engagement', ascending=False)

def get_engagement_string(df, genai):
    prompt = "Analyze these tweets for what drives engagement:\n\n"
    for _, row in df[['text', 'engagement']].head(30).iterrows():
        prompt += f"Tweet: {row['text']}\nEngagement: {row['engagement']:.4f}\n\n"
    return genai.generate_text(prompt)

def compute_keyword_engagement(df, keyword_string):
    df = df.copy()
    df['engagement'] = df['favorite_count'] / df['view_count']
    keywords = [kw.strip().lower() for kw in keyword_string.split(',')]
    results = []
    for kw in keywords:
        df[f"has_{kw}"] = df['text'].str.lower().str.contains(kw)
        group_true = df[df[f"has_{kw}"]]['engagement']
        group_false = df[~df[f"has_{kw}"]]['engagement']
        if len(group_true) > 1 and len(group_false) > 1:
            t_stat, pval = ttest_ind(group_true, group_false, equal_var=False)
            results.append((kw, pval, group_false.mean(), group_true.mean()))
        else:
            results.append((kw, 1.0, group_false.mean() if len(group_false) > 0 else 0.0,
                                  group_true.mean() if len(group_true) > 0 else 0.0))
    df_results = pd.DataFrame(results, columns=['keyword', 'pvalue', 'engagement_false', 'engagement_true'])
    df_results['pvalue_bh'] = multipletests(df_results['pvalue'], method='fdr_bh')[1]
    return df_results
