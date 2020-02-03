from conllu import parse_tree_incr, parse_incr
class Sentence:
  @staticmethod
  def load_trees(filename):
    # loads trees from .conllu formatted file
    data_file=open(filename, "r", encoding="utf-8")
    trees=[]
    for tree in parse_tree_incr(data_file):
      trees.append(tree)
    data_file.close()
    return trees

  @staticmethod
  def load_tokenlists(filename):
    # loads tokenlists from .conllu formatted file
    data_file = open(filename, "r", encoding="utf-8")
    tklists = []
    for tkl in parse_incr(data_file):
      tklists.append(tkl)
    data_file.close()
    return tklists

  @classmethod
  def load_sentences(cls, filename):
    trees = cls.load_trees(filename)
    tokenlists = cls.load_tokenlists(filename)
    sentence_list = [Sentence(tl,tr) for (tl,tr) in zip(tokenlists, trees)]
    return sentence_list 

  def __init__(self, token_list, tree):
    # these should be created using token_list and tree objects from the conllu module
    self.token_list = token_list
    self.tree = tree

  def __getitem__(self, index):
    # returns the token corresponding to the given index
    # indexing starts with 1 as in conllu

    match = [t for t in self.token_list if t["id"] == index][0]
    return match

  def __iter__(self):
    # returns the list of all base tokens (i.e. including the subword tokens
    # but excluding the tokens spanning over them, and created by merging these)
    return iter([t for t in self.token_list if type(t["id"]) == int])

  def get_subtree(self, token, tree = None):
    # returns the subtree spanned by the given token
    if tree == None:
      tree = self.tree
    if tree.token == token:
      return self.tree
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

  def get_non_puncts(self):
    # returns the list of tokens which are not punctuation
    return [t for t in self if t["upostag"] != "PUNCT"]
  # Sentence parameters
                    
  def __len__(self):
    # returns the length of the sentence
    # this is done via the max id of the token
    # so that merged tokens are not counted
    return max([t['id'] for t in self])

  def no_arcs(self):
    # number of arcs is the number of tokens minus 1
    return len(self) - 1

  def avg_dep_length(self):
    # returns the average dependency length, excluding the arc from root to dummy token 0
    non_roots = [t for t in self if t["deprel"] != "root"]
    dep_lengths = [abs(t["id"] - self[t["head"]]["id"]) for t in non_roots]
    return sum(dep_lengths) / self.no_arcs()

  def avg_token_depth(self):
    # returns the average depth of the token in the dependency tree
    # depth of root is equal to 0
    # the root token is counted when calculating the average though
    depths = []
    for t in self:
      deprel = t['deprel']
      depth = 0
      curr_t = t
      while deprel!='root':
        curr_t = self[curr_t['head']]
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

  def are_trans_connected(self, head, subordinate):
    # Verifies whether the subordinate is indeed transitively attached to head
    if head == subordinate:
      return True
    else:
      head_id = subordinate["head"]
      if head_id == 0:
        return False
      else:
        return(self.are_trans_connected(head, self[head_id]))

  def count_nonprojective(self, tree = None):
    # Calculates the number of nonprojective arcs
    if tree is None:	
      # the parameter tree is used in recursive calls
      tree = self.tree
    if tree.children == []:
      # leaves have no nonprojective edges
      return 0
    else:
      head_tok = tree.token
      head_id = head_tok["id"]
      nonprojs = 0
      for c in tree.children:
        # for each arc starting from the present node, we verify whether it is projective

        # Obtaining the indices of all tokens between the head and the subordinate token                
        c_id = c.token["id"]
        span = sorted([c_id, head_id])
        min_id = span[0] + 1 # no need to see whether either the head, or the subordinate token are subordinated
        max_id = span[1]
  
        # verifying whether all of these tokens are transitively subordinate to the head token
        trans_connected = [self.are_trans_connected(head_tok, self[between_id]) for between_id in range(min_id, max_id)]
        nonproj_edge = False in trans_connected
        nonprojs += int(nonproj_edge)
      subtrees = [self.count_nonprojective(ch_tree) for ch_tree in tree.children]
      # We recurrently calculate the nonprojective edges of children nodes and return the sum total 
      return nonprojs + sum(subtrees)

