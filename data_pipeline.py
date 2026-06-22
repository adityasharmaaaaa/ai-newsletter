import torch
from torch.utils.data import Dataset, DataLoader
from tokenizer import SimpleTokenizer

class ArticleDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
    
        text=self.texts[idx]
        label=self.labels[idx]
        encoded=self.tokenizer.encode(text)
        if len(encoded)>self.max_length:
            encoded=encoded[:self.max_length]
        else:
            padding_needed=self.max_length-len(encoded)
            encoded=encoded+[0]*padding_needed
        text_tensor = torch.tensor(encoded, dtype=torch.long)
        label_tensor=torch.tensor(label,dtype=torch.float32)

        return text_tensor,label_tensor


dummy_texts = [
    "Transformers revolutionized AI!",
    "PyTorch is great.",
    "Data engineering is the foundation of machine learning systems."
]
dummy_labels = [1, 1, 0] 

tokenizer = SimpleTokenizer()
tokenizer.fit(dummy_texts)

dataset = ArticleDataset(dummy_texts, dummy_labels, tokenizer, max_length=6)

dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

for text_batch, label_batch in dataloader:
    print("Text Batch Shape:", text_batch.shape)
    print("Text Batch Tensors:\n", text_batch)
    print("Label Batch Tensors:", label_batch)
    break # We only want to see the first batch