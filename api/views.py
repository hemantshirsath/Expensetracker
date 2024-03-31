# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import json
from rest_framework.permissions import IsAuthenticated 
from .serializers import YourDataSerializer  


nltk.download('punkt')
nltk.download('stopwords')


class PredictCategory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_input = request.data.get('description')
        data = pd.read_csv(
            'dataset.csv')
        tfidf_vectorizer = TfidfVectorizer()
        X = tfidf_vectorizer.fit_transform(data['clean_description'])
        model = RandomForestClassifier()
        model.fit(X, data['category'])
        user_input = preprocess_text(user_input)
        user_input_vector = tfidf_vectorizer.transform([user_input])
        similarities = cosine_similarity(user_input_vector, X)
        closest_match_index = similarities.argmax()
        predicted_category = model.predict(X[closest_match_index])

        return Response({'predicted_category': predicted_category[0]}, status=status.HTTP_200_OK)




class UpdateDataset(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
       new_data = request.data.get('new_data')

       if 'description' in new_data and 'category' in new_data:
            # Load your existing dataset
            data = pd.read_csv('dataset.csv')  # Load the existing dataset
            new_category = new_data['category']
            new_description = new_data['description']

            # Append the new data to the dataset
            new_row = {'description': new_description, 'category': new_category, 'clean_description': preprocess_text(new_description)}
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            # Save the updated dataset
            data.to_csv('dataset.csv', index=False)
            
            tfidf_vectorizer = TfidfVectorizer()

            # Retrain the model with the updated dataset
            X = tfidf_vectorizer.transform(data['clean_description'])
            model.fit(X, data['category'])



def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    return ' '.join(tokens)
