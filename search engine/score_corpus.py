import pandas as pd

df = pd.read_csv('Texts_and_queries/processed/cefr_leveled_texts.csv')

# score docs with 20 quries
search_result_df = pd.read_csv('20_queries_results.csv')
# search_result_df = pd.read_csv('test.csv')
for qid in search_result_df['QueryId'].unique():
    df[qid] = 0.0
    count = 1
    for docid in search_result_df.loc[search_result_df['QueryId'] == qid]['DocumentId']:
        index = int(docid.split('-')[1]) - 1
#         df.at[index, qid] = 5 * (100-count+1) / 100
        df.at[index, qid] = 1.0
        count += 1

df['id'] = df.index
df.to_csv('scored_corpus.csv', index=False)