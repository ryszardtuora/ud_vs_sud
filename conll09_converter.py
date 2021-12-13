import conllu
import os
import argparse

# MATE seems to cut conll09 up to first 13 columns, so additional annotations are pointless

def from_conllu_to_09(filename):
    sent_list = []

    with open(filename, 'r', encoding='utf-8') as f:
        for s in conllu.parse_incr(f):
            sent_list.append(s)

    out = []
    for sent in sent_list:
        sent_chunk = []
        for tok in sent:
            if type(tok["id"]) == tuple:
                continue
            feats = "_"
            if tok['feats'] != None:
                feats = "|".join(["{}={}".format(k,v) for k, v in tok["feats"].items()])

            upos = tok["upostag"]
            tag = tok["upostag"]
                    
            token_columns = [str(tok['id']), #1 ID
                     tok['form'], #2 FORM
                     tok['lemma'], #3 LEMMA
                     '_', #4 PredictedLEMMA
                     tag, #5 POS
                     '_', #6 PredictedPOS
                     feats, #7 FEAT
                     '_', #8 PredictedFEAT
                     str(tok['head']), #9 HEAD
                     '_', #10 PredictedHEAD
                     tok['deprel'], #11 DEPREL
                     '_', #12 PredictedDEPREL
                     '_', #13 FILLPRED
                     '_', #14 PRED
                     upos, #15 APRED we save UPOS tags here
                     ]
            tokenstring = "\t".join(token_columns)
            sent_chunk.append(tokenstring)

        sentstring = "\n".join(sent_chunk)
        out.append(sentstring)

    outstring = "\n\n".join(out)+"\n\n"
    with open(filename[:filename.index(".conllu")] + ".conll09", 'w', encoding='utf-8') as f:
     f.write(outstring)

def from_09_to_conllu(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    sents = text.split("\n\n")[:-1]
    sent_strings = []
    for sent in sents:
        toks = sent.split("\n")
        tok_strings = []

        for tok in toks:
            columns = tok.split("\t")
            
            id = columns[0]
            form = columns[1]
            lemma = columns[2]
            xpos = columns[4]
            upos = columns[4]
            #upos = columns[14]
            feats = columns[6]

            head = columns[8]
            if columns[9] != "_":
                head = columns[9]
            
            deprel = columns[10]
            if columns[11] != "_":
                deprel = columns[11] 
           
            deps = "_"
            misc = "_"
            tok_string = "\t".join([id,
                                    form,
                                    lemma,
                                    upos,
                                    xpos,
                                    feats,
                                    head,
                                    deprel,
                                    deps,
                                    misc
                                   ])
            tok_strings.append(tok_string)

        sent_string = "\n".join(tok_strings)
        sent_strings.append(sent_string)

    out_string = "\n\n".join(sent_strings) + "\n\n"
    with open(filename[:filename.index(".conll09")] + '_conv_back.conllu', 'w', encoding='utf-8') as f:
        f.write(out_string)



parser = argparse.ArgumentParser(description='Converter between .conllu and .conll09 formats')
parser.add_argument('input', metavar='INPUT', type=str,
                    help='filepath for the file to be converted, conversion direction will be induced automatically')

if __name__ == "__main__":
    args = parser.parse_args()
    file_in = args.input
  
    if file_in.endswith(".conllu"):
        from_conllu_to_09(file_in)
    elif file_in.endswith(".conll09"):
        from_09_to_conllu(file_in)
    else:
        print("Wrong file format!")

