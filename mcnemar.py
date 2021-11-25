from conll18_ud_eval import load_conllu_file, evaluate
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

def evaluate_wrapper(udvsgold, sudvsgold):
    # Load CoNLL-U files
    """
    gold_ud = load_conllu_file(gold_udfile)
    gold_sud = load_conllu_file(gold_sudfile)
    system_ud = load_conllu_file(sys_ud)
    system_sud= load_conllu_file(sys_sud)
    
    # 3 lists of 0s and 1s corresponding to UAS LAS and CLAS correctness
    sudvsgold=evaluate(gold_sud, system_sud)
    #print([sum(x)/len(x) for x in sudvsgold[:2]]+[sum([t[1] for t in sudvsgold[2] if t[0]==1])/len([t for t in sudvsgold[2] if t[0]==1])])
    #print([sum(x)/len(x) for x in sudvsgold[:2]]+[sum([t[1] for t in sudvsgold[2] if t[0]==True])/len([t for t in sudvsgold[2] if t[0]==True])])
    # 3 lists of 0s and 1s corresponding to UAS LAS and CLAS correctness

    udvsgold=evaluate(gold_ud, system_ud)
    #print([sum(x)/len(x) for x in udvsgold[:2]]+[sum([t[1] for t in udvsgold[2] if t[0]==True])/len([t for t in udvsgold[2] if t[0]==True])]+[sum([t[1] for t in udvsgold[2] if t[0]==True])/len(udvsgold[2])])
    """
    stat_vals=[]
    p_vals = []
    
    ud_uas_error_list = udvsgold["UAS"].error_list
    ud_las_error_list = udvsgold["LAS"].error_list
    sud_uas_error_list = sudvsgold["UAS"].error_list
    sud_las_error_list = sudvsgold["LAS"].error_list
    for (udv,sudv) in zip([ud_uas_error_list, ud_las_error_list],[sud_uas_error_list, sud_las_error_list]):
      a=sum([1 for (u,s) in zip(udv,sudv) if u==1 and s==1])
      b=sum([1 for (u,s) in zip(udv,sudv) if u==1 and s==0])
      c=sum([1 for (u,s) in zip(udv,sudv) if u==0 and s==1])
      d=sum([1 for (u,s) in zip(udv,sudv) if u==0 and s==0])
      #print(a,b,c,d)
      statvalue=((b-c)*(b-c))/(b+c)
      
      data = np.array([[a, b], [c, d]])
      result = mcnemar(data, exact=False, correction=False)
      stat_vals.append(result.statistic)
      p_vals.append(result.pvalue)
    return {'UAS':(stat_vals[0], p_vals[0]), 'LAS':(stat_vals[1], p_vals[1])}
    
  
