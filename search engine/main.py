from rankers import BM25Ranker
from rankers import PivotedLengthNormalizatinRanker
from rankers import CustomRanker
from pyserini.index import IndexReader
from tqdm import tqdm, trange
import sys
import csv
import ast
import string
from pyserini.search import SimpleSearcher
import pandas as pd

num_of_docs = 0
num_of_queries = 0

# stoplist = open("stoplist.txt", "r")
# stopwords = stoplist.readlines()
# stopwords = [e.rstrip() for e in stopwords]
# stoplist.close()
# stopwords = []

def run_test(ranker, searcher, fileName, query_index_reader, query_id_list=None):
    
    score_list = []
    f = open(fileName, 'w', encoding='utf-8', newline='')
    writer = csv.writer(f)
    writer.writerow(["QueryId", "DocumentId"])
    f.close()
    
    query_ids = range(num_of_queries)
    if query_id_list != None:
        query_ids = query_id_list
    for j in query_ids:
        readability = -1
        string = j.split('-')[0]
        if string == 'ele':
            readability = 0
        elif string == 'int':
            readability = 1
        else:
            readability = 2
        query = ast.literal_eval(query_index_reader.doc_raw(str(j)))['contents'].split()
        analyzed_query = []
        for q in query:
            analyzed = query_index_reader.analyze(q)
            for i in analyzed:
                analyzed_query.append(i)
        print(analyzed_query)
        print("round", j, "before loop")
        rank_score = ranker.score(analyzed_query, readability)
        #############################################################
        ## Choose whether you want the first 10 or 5 highest score ##
        #############################################################
#         top = sorted(rank_score.items(), key=lambda x: x[1], reverse=True)[:10]
        top = sorted(rank_score.items(), key=lambda x: x[1], reverse=True)[:10]
        print("round", j, "before fwrite")
        with open(fileName, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for e in top:
                line = [str(j), str(e[0])]
                writer.writerow(line)
        print("round", j, "after fwrite")


if __name__ == '__main__':
    
    #############################
    ###### example input ########
    #############################
    '''
    python main.py index_tree_covid_title index_tree_covid_query tree_covid.csv tree_covid/sample_submission.csv

    python main.py index_gaming_title index_gaming_query gaming.csv gaming/gaming_query_sample_submission.csv
    
    python main.py index_android_title index_android_query android.csv android/android_query_sample_submission.csv

    '''

    if len(sys.argv) != 5:
        print("usage: python algorthm_test.py path/to/index_file; also include the output file name, the query index directory name and the path/to/sample_query_submission.csv")
        exit(1)


    # NOTE: You should already have used pyserini to generate the index files
    # before calling main
    index_fname = sys.argv[1]
    index_reader = IndexReader(index_fname)  # Reading the indexes
    
    out_fname = sys.argv[3]
    query_index_reader = IndexReader(sys.argv[2])
    num_of_docs = index_reader.stats()['documents']
    num_of_queries = query_index_reader.stats()['documents']
    searcher = SimpleSearcher(index_fname)
    
    query_word_list = []
    query_ids = []
#     with open('gaming/gaming_query_sample_submission.csv', 'r') as f:
    with open(sys.argv[4], 'r') as f:
        fReader = csv.DictReader(f)
        for rows in fReader:
            qid = rows.pop("QueryId")
            if qid not in query_ids:
                query_ids.append(qid)
        print(query_ids)
        for qid in query_ids:
            query = ast.literal_eval(query_index_reader.doc_raw(str(qid)))['contents'].split()
            for w in query:
                analyzed = index_reader.analyze(w)
                for i in analyzed:
                    query_word_list.append(i)


    # Print some basic stats
    print("Loaded dataset with the following statistics: " + str(index_reader.stats()))

    # NOTE: You can extend this code to have the program read a list of queries
    # and generate rankings for each.    
    sample_query = "the"  # sample Query to check
    
    print("Initializing Ranker")
    # Choose which ranker class you want to use
#     ranker = PivotedLengthNormalizatinRanker(index_reader, searcher, query_word_list)
    ranker = BM25Ranker(index_reader, searcher, query_word_list)
#     ranker = CustomRanker(index_reader, searcher, query_word_list)
#     # new
#     ranker = BM25Ranker(index_reader, searcher)

    print("Tesing Ranker!")
    run_test(ranker, searcher, out_fname, query_index_reader, query_ids)
