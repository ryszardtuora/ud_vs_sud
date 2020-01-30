class Sentence:
  def __init__(self, token_list, tree):
    # these should be created using token_list and tree objects from the conllu module
    self.token_list = token_list
    self.tree = tree

  def __getitem__(self, index):
    # returns the token corresponding to the given index
    # indexing starts with 1 as in conllu

    match = [t for t in self.token_list if t["id"] == index][0]
    return match

  def get_subtree(self, token, tree = None):
    # returns the subtree spanned by the given token
    if tree = None:
      tree = self.tree
    if tree.token == token:
      return self.tree:
    else:
      subtrees = [self.get_subtree(token, stree) for stree in tree.children]
      for stree in subtrees:
        if stree.token == token:
          return stree
    return None

  def flatten_subtree(self, subtree):
    # returns the list of all elements of the given tree
    if subtree.children == []:
      return subtree.token
    else:
      return [self.flatten_subtree(c) for c in subtree.children]

  def get_tokens(self):
    # returns the list of all base tokens (i.e. including the subword tokens
    # but excluding the tokens spanning over them, and created by merging these)
    return [t for t in self.token_list if type(t["id"]) == int]

  def get_non_puncts(self):
    # returns the list of tokens which are not punctuation
    return [t for t in self.get_tokens() if t["upostag"] != "PUNCT"]
  # Sentence parameters
                    
  def __len__(self):
    # returns the length of the sentence
    # this is done via the max id of the token
    # so that merged tokens are not counted
    return max([t['id'] for t in self.get_full_tokens()])

  def avg_dep_length(self):
    # returns the average dependency length, excluding the arc from root to dummy token 0
    # the root token is counted when calculating the average though
    non_roots = [t for t in self.get_tokens() if t["deprel"] != "root"
    dep_lengths = [abs(t["id"] - self.get_token(t["head"])["id"]) for t in non_roots]
    return sum(dep_lengths) / len(self)

  def avg_token_depth(self):
    # returns the average depth of the token in the dependency tree
    # depth of root is equal to 0
    # the root token is counted when calculating the average though
    depths = []
    for t in self.get_tokens():
      deprel = t['deprel']
      depth = 0
      curr_t = t
      while deprel!='root':
        curr_t = self.get_token(curr_t['head'])
        deprel = curr_t['deprel']
        depth += 1
      depths.append(depth)
    return sum(depths) / len(self)

  def contains_coordination(self):
    for t in self.token_list:
      if t['deprel']=='conj':
        return True
    return False

  #def no_of_coord_structures(self):
  #  return len(self.get_coord_subtrees())

    
    
    #def errors(self, gold_standard):
    #    # zwraca parę (uas_errors, las_errors, %uas, %las)
        # ilości złych strzałek, i złych etykiet w zdaniu względem gold_standard
    #    uas_errors=0
    #    las_errors=0
    #    for (t, gt) in zip(self.token_list, gold_standard.token_list):
    #        uas_errors+=1-UAS(gt,t)
    #        las_errors+=1-LAS(gt,t)
    #    return (uas_errors, las_errors, 1-uas_errors/self.get_len(), 1-las_errors/self.get_len())

  # Token features

  def root_dist(self, token):
    # calculates the distance from root token, counting both punctuation and subword tokens
    # zwraca odległość tokena od root, liczy każdy token po drodze, i.e. również przecinki i morfemy takie jak '-bym'
    return abs(self.tree.token['id'] - token['id'])

  def dep_length(self, head_token, subordinate_token):
    # calculates the dependency length from subordinate token to its head
    return abs(subordinate_token['id'] - head_token['id'])


    #def in_a_coord_phrase(self, token):
     #   for f in [self.flatten_subtree(st) for st in self.get_coord_subtrees()]:
      #      if token in f:
       #         return True
       # return False

    #def hd_of_coord_phrase(self, token):
     #   sts = [st.token for st in self.get_coord_subtrees()]
     #   return token in sts
