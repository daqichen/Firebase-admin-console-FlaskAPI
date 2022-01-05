# Firebase-admin-console-FlaskAPI

Back-end code. <a href="https://firebase-admin-console-api.herokuapp.com/list?collection=Origami&filter_applied=false&difficulty=&low_steps=0&high_steps=1000&order_by=">Deployed</a> on Heroku.

## Overview

Firebase Admin Console is a centralized platform for easy viewing and maintenance of Firestore database, the application's front-end is built in ReactJS, and the back-end API is a Python Flask app. This application serves as a starting template for developers to customize, build, and even deploy the desired admin console for their DB. 


## Python Flask App and Firestore DB Set Up

Assuming that you already have a Firestore NoSQL database up and running, you can built a CRUD (Create, Read, Update, and Delete) API using Flask in Python. To set up your Firestore DB, here is a <a href="https://medium.com/google-cloud/building-a-flask-python-crud-api-with-cloud-firestore-firebase-and-deploying-on-cloud-run-29a10c502877">Medium article</a> to help you get started. The objective is to allow your front-end application to access data, or documents in a NoSQL context, stored in your Firestore database on Firebase. Below is the set up for <strong>/app.py</strong>.


```python
import os
import requests
from flask import Flask, jsonify, request, make_response
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
```

All the necessary libraries required are listed in <strong>/requirement.txt</strong>.

```plaintext
CacheControl==0.12.10
cachetools==4.2.4
certifi==2021.10.8
charset-normalizer==2.0.10
click==8.0.3
dataclasses-json==0.5.6
firebase-admin==5.2.0
Flask==2.0.2
Flask-Cors==3.0.10
google-api-core==2.3.2
google-api-python-client==2.34.0
google-auth==2.3.3
google-auth-httplib2==0.1.0
google-cloud-core==2.2.1
google-cloud-firestore==2.3.4
google-cloud-storage==1.43.0
google-crc32c==1.3.0
google-resumable-media==2.1.0
googleapis-common-protos==1.54.0
grpcio==1.43.0
grpcio-status==1.43.0
gunicorn==20.0.4
...
```

## CRUD Requests

Create, Read, Update, and Delete (CRUD) are the basic four back-end operations you should be able to execute upon the DB. And one of the most basic operations you might want to perform is to <strong>READ</strong> and view all the documents in your DB (in NoSQL DB, datapoints are referred to as "documents"). This can also act as a sanity check for the configuration in your Flask app to connect with your Firestore DB.

```python
@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents    """
    try:
        # details of the request
        dir_id = request.args.get('collection')  

        print('in collection ' + dir_id)
        curr_dir = db.collection(dir_id)
        all_dirs = [doc.to_dict() for doc in curr_dir.stream()]
        return jsonify(all_dirs), 200
```

Once you run your flask app, you can navigate to the port it is running on and navigate to PORT_URL/list, the documents should be displayed in JSON format. Now that you can access the existing documents, it's time to implement <strong>CREATE</strong>.

```python
from datamodel.origamimodule import Origami

@app.route('/add', methods=['POST'])
def create():
    try:
        # details of the request
        formData = request.json
        if (formData['collection'] == "Origami"):
            model = Origami(creator=formData['creator_field'], model_name=formData['model_name_field'], 
                            level_of_difficulty=formData['level_of_difficulty_field'],number_of_steps=formData['steps_field'],
                            source_pattern=formData['source_pattern_link_field'],paper_ratio=formData['paper_ratio_field'],
                            video_tutorial=formData['video_tutorial_field'],img=formData['img_field'])
            print(model.to_dict())
        elif (formData['collection'] == "Placeholder for some other collection"):
            #some other custom datamodel
        db.collection(formData['collection']).document().set(model.to_dict())
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
```

You probably noticed the import statement for a module named "Origami". I have dedicated a <a href="https://locrian-colt-32b.notion.site/Better-alternative-Fireclass-acde50619f074c358f0f99461b6f1f8b">page</a> on Notion with more details on utilizing dataclasses in Python and its compatibility with JSON to simplify creating new documents and standardizing the set of fields each document has. Meanwhile, below is the implementation code for <strong>/origamimodule.py</strong>.

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json 

@dataclass_json
@dataclass
class Origami:
    model_name:str
    level_of_difficulty:str
    number_of_steps:int
    source_pattern:str
    creator:str
    paper_ratio:str
    video_tutorial:str
    img:str
```

Next is <strong>UPDATE</strong>, which is very similar to CREATE. The main distinction is that UPDATE requires you to know the corresponding document ID of which you are attempting to update. In Firestore DB, you can either auto-generate IDs or assign them yourself; here in this template, they are auto-generated.

```python
@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        # details of the request
        details = request.json
        collection_dir = details['collection']
        name = details['identifier_name']
        value = details['identifier_value']
        # get doc id
        docs = db.collection(collection_dir).where(name, "==", value).get()
        for doc in docs:
            doc_id = doc.id
            print("doc id: " + doc_id)
            break

        # details of the UPDATE request
        formData = request.json
        if (formData['collection'] == "Origami"):
            model = Origami(creator=formData['creator_field'], model_name=formData['model_name_field'], 
                            level_of_difficulty=formData['level_of_difficulty_field'],number_of_steps=formData['steps_field'],
                            source_pattern=formData['source_pattern_link_field'],paper_ratio=formData['paper_ratio_field'],
                            video_tutorial=formData['video_tutorial_field'],img=formData['img_field'])
            print(model.to_dict())
        
        db.collection(formData['collection']).document(doc_id).update(model.to_dict())
        return jsonify({"success": True}), 200

    except Exception as e:
        return f"An Error Occured: {e}"
```
Last but not least, is <strong>DELETE</strong>. 

```python
@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    try:
        # details of the request
        details = request.json
        collection_dir = details['collection']
        name = details['identifier_name']
        value = details['identifier_value']
        print(collection_dir, name, value)
        # check if the document exists
        docs = db.collection(collection_dir).where(name, "==", value).get()
        exists = False
        for doc in docs:
            doc_id = doc.id
            exists = True
            print("this doc exists")
            break
        if exists:
            db.collection(collection_dir).document(doc_id).delete()
            print('deleted successfully for '+value)
            return jsonify({"success": True}), 200
        else:
            print("no doc found")
            return jsonify({"fail": "Document you are trying to delete does not exist"})
    except Exception as e:
        print(e)
        return f"An Error Occured: {e}"
```

