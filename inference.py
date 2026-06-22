import torch
import json
from model import ArticleClassifier
from tokenizer import SimpleTokenizer

with open("vocab.json", "r") as f:
    word2idx = json.load(f)

tokenizer = SimpleTokenizer()
tokenizer.word2idx = word2idx

vocab_size = len(tokenizer.word2idx)
model = ArticleClassifier(vocab_size=vocab_size, embedding_dim=16)

model.load_state_dict(torch.load("model_weights.pth", weights_only=True))

model.eval()

def predict(text, max_length=8):
    text=tokenizer.encode(text)
    if len(text)>max_length:
        text=text[:max_length]
    else:
        required_padding=max_length-len(text)
        text=text+[0]*required_padding
    text_tensor=torch.tensor([text],dtype=torch.long)
    with torch.no_grad():
        predictions=model(text_tensor)
    prob=torch.sigmoid(predictions)
    return prob.item()


if __name__ == "__main__":
    test_1 = "I am building a Deep Learning pipeline with PyTorch."
    test_2 = "I want to cook dinner and watch a movie."
    
    prob_1 = predict(test_1)
    prob_2 = predict(test_2)
    
    print(f"Text: '{test_1}' | AI Probability: {prob_1:.4f}")
    print(f"Text: '{test_2}' | AI Probability: {prob_2:.4f}")