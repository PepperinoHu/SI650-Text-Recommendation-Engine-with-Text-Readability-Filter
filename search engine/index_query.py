import csv
import json
import sys



def make_json(csvFilePath, jsonFilePath):
    f1 = open(csvFilePath, encoding='utf-8')
    f1Reader = csv.DictReader(f1)
    count = 0
    new_row = {}
    for rows in f1Reader:
        ################################################
        ##### Choose indexing documents or queries #####
        ################################################
        new_row["id"] = rows.pop("QueryId")
        new_row["contents"] = rows.pop("Query Description")
        readability = rows.pop("Readability").strip()
        string = str(new_row["id"])
        if readability == '0':
            new_row["id"] = 'ele-' + string
        elif readability == '1':
            new_row["id"] = 'int-' + string
        else:
            print(readability)
            new_row["id"] = 'adv-' + string
        path = jsonFilePath + str(new_row["id"]) + ".jsonl"
        f2 = open(path, 'w', encoding='utf-8')
        f2.write(json.dumps(new_row))
#         count += 1
        f2.close()
#         print(json.dumps(new_row))
    f1.close()
    
    
if __name__ == "__main__":
    try:
        csvFilePath = sys.argv[1]
        jsonFilePath = sys.argv[2]
    except:
        print("No proper input")
        
    make_json(csvFilePath, jsonFilePath)
    
###############################################################
##### After indexing, run the pyserini command line code ######
### you can refer to the following example command line code ##
###############################################################
'''
python -m pyserini.index -collection JsonCollection -generator DefaultLuceneDocumentGenerator -threads 1 -input tree_covid/doc_index_jsonl -index index_tree_covid -storePositions -storeDocvectors -storeRaw

python -m pyserini.index -collection JsonCollection -generator DefaultLuceneDocumentGenerator -threads 1 -input tree_covid/query_index_jsonl -index index_tree_covid_query -storePositions -storeDocvectors -storeRaw

'''