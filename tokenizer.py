import re
class SimpleTokenizer:
    def __init__(self):
        self.word2idx = {
            "<PAD>": 0,
            "<UNK>": 1
        }

    def clean_text(self, text):
        text=text.lower()
        cleaned = re.sub(r'[^\w\s]', '', text)
        return cleaned

    def fit(self, text_list):
        for text in text_list:
            cleaned=self.clean_text(text)
            words=cleaned.split()
            for word in words:
                if word not in self.word2idx:
                    self.word2idx[word]=len(self.word2idx)

    def encode(self, text):
        cleaned=self.clean_text(text)
        words=cleaned.split()
        encoded=[]
        for word in words:
            encoded.append(
                self.word2idx.get(word, self.word2idx["<UNK>"])
            )

        return encoded
    

if __name__=="__main__":

    training_texts = [
        "Transformers revolutionized AI!",
        "PyTorch is great for Deep Learning."
    ]

    tokenizer = SimpleTokenizer()
    tokenizer.fit(training_texts)

    print("Vocabulary Map:", tokenizer.word2idx)

    test_sentence = "PyTorch is awesome for AI"
    print("Encoded:", tokenizer.encode(test_sentence))