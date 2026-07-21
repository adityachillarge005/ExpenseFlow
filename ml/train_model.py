import pandas as pd
import pickle
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
data = pd.read_csv("data.csv")
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data["title"])# X is a sparse matrix 
y = data["category"]
# print(y)
# print(X)
# print(vectorizer.get_feature_names_out())
# print(X.toarray())
model = MultinomialNB()
# print(type(model))
model.fit(X,y) #Learn the relationship between X and y.
with open("model.pkl","wb") as file:
    pickle.dump(model,file)
with open("vectorizer.pkl","wb") as file:
    pickle.dump(vectorizer,file)
print("Model and vectorizer saved successfully!")
print("Model trained succesfully")
prediction = model.predict(vectorizer.transform(["uber"])) #here we transform again for new data added by user is converted to numbers given to model to predict
print(prediction)