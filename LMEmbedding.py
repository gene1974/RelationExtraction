import torch
import torch.nn as nn
from allennlp.modules.elmo import Elmo, batch_to_ids
from Utils import logger

'''
allennlp/allennlp/modules/token_embedders/elmo_token_embedder.py 
class ElmoTokenEmbedder(TokenEmbedder):
    Compute a single layer of ELMo representations.
    This class serves as a convenience when you only want to use one layer of
    ELMo representations at the input of your network.  It's essentially a wrapper
    around Elmo(num_output_representations=1, ...)

batch_to_ids: torch: (len(batch), max sentence length, max word length)
'''
class LMEmbedding(nn.Module):
    def __init__(self, lm_emb_dim, num_output_representations = 1, dropout = 0.1):
        super().__init__()
        self.num_output_representations = num_output_representations
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.fine_tune = False

        self.lm_embeds = Elmo(
            options_file = '/data/ELMo/elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json', 
            weight_file = '/data/ELMo/elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5', 
            num_output_representations = 1,
            requires_grad = self.fine_tune,
            dropout = dropout
        )
        if lm_emb_dim != self.lm_embeds.get_output_dim():
            self.use_dense = True
            self.lm_emb_dim = lm_emb_dim
            self.lm_dense = nn.Linear(self.lm_embeds.get_output_dim(), self.lm_emb_dim)
        else:
            self.use_dense = False
            self.lm_emb_dim = self.lm_embeds.get_output_dim()
        
        logger('Load Elmo. fine-tune = {}, Size = {}'.format(self.fine_tune, self.lm_emb_dim))

    def forward(self, text): # text: (list(list))
        char_ids = batch_to_ids(text).to(self.device) # (batch_size, max_sen_len)
        lm_emb = self.lm_embeds(char_ids)['elmo_representations'] # List[torch.Tensor]
        if self.num_output_representations == 1:
            lm_emb = lm_emb[0]
        if self.use_dense:
            lm_emb = self.lm_dense(lm_emb)
        return lm_emb

    def get_emb_dim(self):
        return self.lm_emb_dim

'''
reference:
https://github.com/allenai/allennlp/blob/main/allennlp/modules/elmo.py
https://github.com/allenai/allennlp/blob/main/allennlp/modules/token_embedders/elmo_token_embedder.py
https://zhuanlan.zhihu.com/p/53803919
'''
