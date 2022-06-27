import torch
from torch import nn, Tensor
# import torch.nn.functional as F
from torch.nn import TransformerEncoder, TransformerEncoderLayer
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
#from transformers import BertTokenizer
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

import math
import csv
import logging

# filename = "D:/Users/thoma/Documents/Python/PoE Appraisal/item_train.csv"
# with open(filename, newline='') as csvfile:
#     cread = csv.reader(csvfile,delimiter='\n')
#     for row in cread:
#         print(row[0])


# smh = nn.Transformer(d_model=5, nhead=1, num_encoder_layers=12)
# out = smh(torch.rand((5, 5, 5)), torch.rand((1, 5, 5)))
# out = smh.forward(torch.rand((5, 5, 5)),torch.rand((1, 5, 5)))

max_vocab = 25000


class ItemPrice(Dataset):
    def __init__(self, ItemPath, PricePath):
        self.samples = []
        max_l = 0

        #Import lists from csv
        with open(ItemPath, newline='') as itfile:
            with open(PricePath, newline='') as prfile:
                itread = csv.reader(itfile,delimiter='\n')
                prread = csv.reader(prfile,delimiter='\n')
                ilist = []
                plist = []
                for i in itread:
                    ilist.append(i[0].split(","))
                    #track padding length req
                    if len(i[0]) > max_l:
                        max_l = len(i[0])
                for p in prread:
                    plist.append([p[0]])

                #Write item-price pairs to tuples
                for x, val in enumerate(ilist):
                    self.samples.append((ilist[x],plist[x]))     

    def __len__(self):
        return len(self.samples)

    def __getitem__(self,idx):
        return self.samples[idx]




logging.basicConfig(level=logging.INFO)

tds = ItemPrice(ItemPath="D:/Users/thoma/Documents/Python/PoE Appraisal/item_train.csv", PricePath="D:/Users/thoma/Documents/Python/PoE Appraisal/price_train.csv")
logging.info("Training set generated")
vds = ItemPrice(ItemPath="D:/Users/thoma/Documents/Python/PoE Appraisal/item_verif.csv", PricePath="D:/Users/thoma/Documents/Python/PoE Appraisal/price_verif.csv")
logging.info("Validation set generated")

#Dataloaders not required?
#tdl = DataLoader(tds, batch_size=50, shuffle=True)
#vdl = DataLoader(vds, batch_size=50, shuffle=True)

#Convert to tokens
vocab = build_vocab_from_iterator([i[0] for i in tds.samples],specials=['<unk>'])
vocab.set_default_index(vocab['<unk>'])
# for item in tds.samples:
#     print(str(torch.tensor(float(item[1][0]))))

t_src_tens = [torch.tensor(vocab(item[0])) for item in tds.samples]
testval = t_src_tens[0].size()
t_tgt_tens = [torch.tensor(float(item[1][0])) for item in tds.samples]

print("")


class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class MyModel(nn.Module):

    def __init__(self, ntoken: int, d_model: int, nhead: int, d_hid: int, nlayers: int, dropout: float = 0.5):
            super().__init__()
            self.model_type = 'Transformer'
            self.pos_encoder = PositionalEncoding(d_model, dropout)
            encoder_layers = TransformerEncoderLayer(d_model, nhead, d_hid, dropout)
            self.transformer_encoder = TransformerEncoder(encoder_layers, nlayers)
            self.encoder = nn.Embedding(ntoken, d_model)
            self.d_model = d_model
            self.decoder = nn.Linear(d_model, ntoken)

            self.init_weights()

    def init_weights(self) -> None:
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src: Tensor) -> Tensor:
        """
        Args:
            src: Tensor, shape [seq_len, batch_size]
            src_mask: Tensor, shape [seq_len, seq_len]

        Returns:
            output Tensor of shape [seq_len, batch_size, nprice_points] where d_model is nprice_points
        """
        src = self.encoder(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src)
        output = self.decoder(output)
        return output


