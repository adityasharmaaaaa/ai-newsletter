import torch
import torch.nn as nn

class ArticleClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(ArticleClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size,embedding_dim,padding_idx=0)
        self.fc = nn.Linear(embedding_dim,1)

    def forward(self, x):
        embedded = self.embedding(x)
        pooled = embedded.mean(dim=1)
        output = self.fc(pooled)
        return torch.squeeze(output, dim=1)
    
if __name__ == "__main__":
    dummy_input = torch.tensor([
        [4, 5, 6, 0, 0, 0],
        [7, 8, 5, 9, 10, 11]
    ], dtype=torch.long)
    
    model = ArticleClassifier(vocab_size=20, embedding_dim=16)
    
    predictions = model(dummy_input)
    
    print("Dummy Input Shape:", dummy_input.shape)
    print("Predictions Shape:", predictions.shape)
    print("Raw Predictions (Logits):", predictions)