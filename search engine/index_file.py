import csv
import json
import sys



def make_json(csvFilePath, jsonFilePath):
    f1 = open(csvFilePath, encoding='utf-8-sig')
    f1Reader = csv.DictReader(f1)
    doc_id = 1
    new_row = {}
    for rows in f1Reader:
        ################################################
        ##### Choose indexing documents or queries #####
        ################################################
        new_row["id"] = doc_id
        new_row["contents"] = rows.pop("text").strip()
        print(new_row["contents"])
        readability = rows.pop("label")
        string = str(new_row["id"])
        if readability == 'A1' or readability == 'A2':
            new_row["id"] = readability + '-' + string
        elif readability == 'B1' or readability == 'B2':
            new_row["id"] = readability + '-' + string
        elif readability == 'C1' or readability == 'C2':
            new_row["id"] = readability + '-' + string
        else:
            print('other redability label found')
            return
        path = jsonFilePath + str(new_row["id"]) + ".jsonl"
        f2 = open(path, 'w', encoding='utf-8')
        f2.write(json.dumps(new_row))
        f2.close()
        doc_id += 1
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