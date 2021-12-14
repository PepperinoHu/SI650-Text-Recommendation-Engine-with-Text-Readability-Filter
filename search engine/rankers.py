from pyserini.index import IndexReader
from tqdm import tqdm, trange
import sys
import numpy as np
import ast
import string

class Ranker(object):
    
    def __init__(self, index_reader):
        self.index_reader = index_reader

    def score(query, doc):        
        rank_score = 0
        return rank_score


class PivotedLengthNormalizatinRanker(Ranker):
    
    def __init__(self, index_reader, searcher, query_word_list):
        super(PivotedLengthNormalizatinRanker, self).__init__(index_reader)
        
        self.N = self.index_reader.stats()['documents']
        self.avg_dl = self.index_reader.stats()['total_terms'] / self.N
        self.dfw = {}
        query_word_listSet = set(query_word_list)
        for w in tqdm(query_word_listSet):
            self.dfw[w], _ = self.index_reader.get_term_counts(w, analyzer=None)
            
        self.doc_ids = {}
        for i in range(searcher.num_docs):
            self.doc_ids[i] = searcher.doc(i).docid()
        self.doc_vector = {}
        for doc_id in self.doc_ids.values():
            doc_vector = self.index_reader.get_document_vector(doc_id)
            self.doc_vector[doc_id] = doc_vector

    def score(self, query, b=0.1):

        rank_score = {}
        
        querySet = set(query)
        N = self.N
        avg_dl = self.avg_dl
        for q in tqdm(querySet):
            postings_list = self.index_reader.get_postings_list(q, analyzer=None)
            if not postings_list:
                continue
            cwq = query.count(q)
            dfw = self.dfw[q]
            for posting in postings_list:
                doc_id = self.doc_ids[posting.docid]
                doc = self.doc_vector[doc_id]
                d = sum(doc.values())
                if doc_id not in rank_score:
                    rank_score[doc_id] = cwq*((1+np.log(1+np.log(posting.tf)))/(1-b+b*(d/avg_dl)))*np.log((N+1)/dfw)
                else:
                    rank_score[doc_id] += cwq*((1+np.log(1+np.log(posting.tf)))/(1-b+b*(d/avg_dl)))*np.log((N+1)/dfw)
                    
            
        return rank_score

    

class BM25Ranker(Ranker):

    def __init__(self, index_reader, searcher, query_word_list):
        super(BM25Ranker, self).__init__(index_reader)
        
        self.N = self.index_reader.stats()['documents']
        self.avg_dl = self.index_reader.stats()['total_terms'] / self.N
        self.dfw = {}
        query_word_listSet = set(query_word_list)
        for w in tqdm(query_word_listSet):
            self.dfw[w], _ = self.index_reader.get_term_counts(w, analyzer=None)
            
        self.doc_ids = {}
        for i in range(searcher.num_docs):
            self.doc_ids[i] = searcher.doc(i).docid()
        self.doc_vector = {}
        for doc_id in self.doc_ids.values():
            doc_vector = self.index_reader.get_document_vector(doc_id)
            self.doc_vector[doc_id] = doc_vector

    def score(self, query, readability, k1=1.2, b=0.5, k3=1.2):
        if readability == -1:
            print('invalid readability')
            return {}
        rank_score = {}
        
        querySet = set(query)
        N = self.N
        avg_dl = self.avg_dl
        for q in tqdm(querySet):
            postings_list = self.index_reader.get_postings_list(q, analyzer=None)
            if not postings_list:
                continue
            cwq = query.count(q)
            dfw = self.dfw[q]
            for posting in postings_list:
                doc_id = self.doc_ids[posting.docid]
                doc = self.doc_vector[doc_id]
                d = sum(doc.values())
                doc_readability_level = -1
                string = doc_id.split('-')[0]
                if string == 'A1' or string == 'A2':
                    doc_readability_level = 0
                elif string == 'B1' or string == 'B2':
                    doc_readability_level = 1
                else:
                    doc_readability_level = 2
                weight = 1/((doc_readability_level - readability)*(doc_readability_level - readability) + 5)
#                 weight = 1
                if doc_id not in rank_score:
                    rank_score[doc_id] = weight*(np.log((N-dfw+0.5)/(dfw+0.5))*(((k1+1)*posting.tf)/(k1*(1-b+b*d/avg_dl)+posting.tf))*(((k3+1)*cwq)/(k3+cwq)))
                else:
                    rank_score[doc_id] += weight*(np.log((N-dfw+0.5)/(dfw+0.5))*(((k1+1)*posting.tf)/(k1*(1-b+b*d/avg_dl)+posting.tf))*(((k3+1)*cwq)/(k3+cwq)))
                    
            
        return rank_score

# class BM25Ranker(Ranker):

#     def __init__(self, index_reader, searcher):
#         super(BM25Ranker, self).__init__(index_reader)
            
#         self.doc_ids = {}
#         for i in range(searcher.num_docs):
#             self.doc_ids[i] = searcher.doc(i).docid()

#     def score(self, query, k1=1.2, b=0.5, k3=1.2):

#         rank_score = {}
        
#         querySet = set(query)
#         for q in tqdm(querySet):
#             for doc_id in self.doc_ids.values():
#                 bm25_score = self.index_reader.compute_bm25_term_weight(doc_id, q, analyzer=None)
#                 if doc_id not in rank_score:
#                     rank_score[doc_id] = bm25_score
#                 else:
#                     rank_score[doc_id] += bm25_score
                    
            
#         return rank_score



    
class CustomRanker(Ranker):
    
    def __init__(self, index_reader, searcher, query_word_list):
        super(CustomRanker, self).__init__(index_reader)
        
        self.N = self.index_reader.stats()['documents']
        self.avg_dl = self.index_reader.stats()['total_terms'] / self.N
        self.dfw = {}
        query_word_listSet = set(query_word_list)
        for w in tqdm(query_word_listSet):
            self.dfw[w], _ = self.index_reader.get_term_counts(w, analyzer=None)
            
        self.doc_ids = {}
        for i in range(searcher.num_docs):
            self.doc_ids[i] = searcher.doc(i).docid()
        self.doc_vector = {}
        for doc_id in self.doc_ids.values():
            doc_vector = self.index_reader.get_document_vector(doc_id)
            self.doc_vector[doc_id] = doc_vector


    def score(self, query, k1=3.3, b=1.2, k3=0.8, a=0.1):

        rank_score = {}
        
        querySet = set(query)
        N = self.N
        avg_dl = self.avg_dl
        for q in tqdm(querySet):
            postings_list = self.index_reader.get_postings_list(q, analyzer=None)
            if not postings_list:
                continue
            cwq = query.count(q)
            dfw = self.dfw[q]
            for posting in postings_list:
                doc_id = self.doc_ids[posting.docid]
                doc = self.doc_vector[doc_id]
                d = sum(doc.values())
                K = min(N-dfw, dfw)
                if doc_id not in rank_score:
                    rank_score[doc_id] = np.log((N-dfw+0.5-a*K)/(dfw+0.5-a*K))*(((k1+1)*np.exp(posting.tf))/(k1*(1-b+b*d/avg_dl)+np.exp(posting.tf)))*(k3*cwq)
                else:
                    rank_score[doc_id] += np.log((N-dfw+0.5-a*K)/(dfw+0.5-a*K))*(((k1+1)*np.exp(posting.tf))/(k1*(1-b+b*d/avg_dl)+np.exp(posting.tf)))*(k3*cwq)
                    
            
        return rank_score