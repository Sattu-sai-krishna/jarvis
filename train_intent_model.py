import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

print("Loading intents.json...")

with open("intents.json", "r") as f:
    data = json.load(f)

sentences = []
labels = []

for intent, info in data.items():
    for pattern in info["patterns"]:
        sentences.append(pattern)
        labels.append(intent)
print("Training model...")

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sentences)

model = LogisticRegression(max_iter=2000)
model.fit(X, labels)

print("Saving model file...")

with open("intent_model.pkl", "wb") as f:
    pickle.dump((model, vectorizer), f)

print("SUCCESS! intent_model.pkl CREATED.")
