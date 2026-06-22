import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import json
import mlflow  

from tokenizer import SimpleTokenizer
from data_pipeline import ArticleDataset
from model import ArticleClassifier

# --- 1. Mock Data ---
dummy_texts = [
    "Transformers revolutionized AI!",
    "PyTorch is great for Deep Learning.",
    "Data engineering is the foundation of machine learning systems.",
    "I love cooking pasta for dinner.",
    "The weather is beautiful today.",
    "Generative AI and LLMs are changing software."
]
dummy_labels = [1, 1, 1, 0, 0, 1]

# --- 2. Pipeline Setup ---
tokenizer = SimpleTokenizer()
tokenizer.fit(dummy_texts)
dataset = ArticleDataset(dummy_texts, dummy_labels, tokenizer, max_length=8)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

vocab_size = len(tokenizer.word2idx)
embedding_dim = 16
model = ArticleClassifier(vocab_size=vocab_size, embedding_dim=embedding_dim)

# --- 3. Loss & Optimizer Setup ---
criterion = nn.BCEWithLogitsLoss()
learning_rate = 0.01  # Extracted as a variable for tracking
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
epochs = 15

# --- 4. MLflow Experiment Tracking ---
# This creates a folder called 'mlruns' in your directory to store the database
mlflow.set_experiment("Content_Curator_Classifier")

with mlflow.start_run():
    # 1. LOG PARAMETERS (What goes IN)
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("learning_rate", learning_rate)
    mlflow.log_param("vocab_size", vocab_size)
    mlflow.log_param("embedding_dim", embedding_dim)
    
    print("Starting Training...")
    for epoch in range(epochs):
        epoch_loss = 0.0
        
        for texts, labels in dataloader:
            optimizer.zero_grad()
            predictions = model(texts)
            loss = criterion(predictions, labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            
        avg_loss = epoch_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")
        
        # 2. LOG METRICS (What comes OUT)
        # We pass 'step=epoch' so MLflow can draw a line graph over time
        mlflow.log_metric("train_loss", avg_loss, step=epoch)

    print("Training complete. Saving model and vocabulary...")
    
    # Save files locally as before
    torch.save(model.state_dict(), "model_weights.pth")
    with open("vocab.json", "w") as f:
        json.dump(tokenizer.word2idx, f)
        
    # 3. LOG ARTIFACTS (The physical files)
    mlflow.log_artifact("model_weights.pth")
    mlflow.log_artifact("vocab.json")
    
    print("Successfully logged run to MLflow!")