from operator import index
from django.contrib import messages
import documents
import pymongo
from .models import person_collection
from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.contrib.auth.models import User , auth
from django.contrib.auth import logout , authenticate,login
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

llm = pipeline("text-generation", model="gpt2")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
documents = ["Document 1 text...", "Document 2 text...", "Document 3 text..."]
document_embeddings = embedding_model.encode(documents)
dimension = document_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(document_embeddings))
# Create your views here.
# def index(request):
#     return HttpResponse("Hello and welcome to my first")
def chatbot(request):
    l=str(input())
    generated_response = llm(request, max_length=100, num_return_sequences=1)[0]['generated_text']
    return generated_response

# Retrieve documents
def retrieve_documents(query, top_k=2):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [documents[i] for i in indices[0]]

# Generate chatbot response
def chatbot_response(query):
    retrieved_docs = retrieve_documents(query)
    augmented_query = query + "\n\n".join(retrieved_docs)
    response = llm(augmented_query, max_length=200)
    return response[0]['generated_text']

# Example interaction
user_query = "Give the Answer of the following description in a single value form the list :[Landscape architect, Interior architect, Urban planning and design architect, Commercial architect,  Residential architect, Historic architect] : "
response = chatbot_response(user_query)
s1=(response)
if "Landscape" in s1[224::] or "landscape" in s1[224::]:
    print("Landscape")
elif "Interior" in s1[224::] or "interior" in s1[224::]:
    print("Interior")
elif "urban" in s1[224::] or "Urban" in s1[224::]:
    print("Urban planning and design")
elif "Commercial" in s1[224::] or "commercial" in s1[224::]:
    print("Commercial")
elif "Residential" in s1[224::] or "residential" in s1[224::]:
    print("Residential")
elif "Historic" in s1[224::] or "historic" in s1[224::]:
    print("Historic")

def add_person(request):
    record = {
        "first_name": "john"
    }
    person_collection.insert_one(record)
    return HttpResponse("Person added")
def get_all_persons(request):
    person = person_collection.find()
    return HttpResponse(person) 
    
def style(request):
    return render(request, "style.html")
def home(request):
    return render(request, "index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! .")
        return redirect('signin')
    return render(request, "signup.html")
    

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            # messages.success(request, "Logged In Sucessfully!!")
            return render(request, "index.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "signin.html")
def chat_bot(request):
    return render(request, "chat_bot.html")
    # response = chatbot(request)
    # return render(request, "chat_bot.html",{"response":response})
    # return render(request, "chat_bot.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')
