import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer

# Required downloads
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Input text
text = "tell me about rasa and rasa"

# Tokenize
tokens = word_tokenize(text)

# POS Tagging
pos_tags = nltk.pos_tag(tokens)

# Lemmatization
lemmatizer = WordNetLemmatizer()
lemmatized = [lemmatizer.lemmatize(word.lower()) for word in tokens]  # lowercase for vectorizer

# Vectorization using CountVectorizer
vectorizer = CountVectorizer()
vector = vectorizer.fit_transform([' '.join(lemmatized)])

# Output
print("Tokens:", tokens)
print("POS Tags:", pos_tags)
print("Lemmatized:", lemmatized)
print("Vocabulary:", vectorizer.vocabulary_)
print("TF IDF")
print("Vector (Array):\n", vector.toarray())
