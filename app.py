import os
import requests
from flask import Flask, jsonify, request, make_response
from firebase_admin import credentials, firestore, initialize_app
from flask_cors import CORS
from datamodel.origamimodule import Origami

app = Flask(__name__)
CORS(app)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
ori_ref = db.collection('Origami')

@app.route('/', methods = ['GET'])
def get_articles():
    return jsonify({"Hello" : "world"})

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
            model = Origami(creator=formData['creator_field'], model_name=formData['model_name_field'], 
                            level_of_difficulty=formData['level_of_difficulty_field'],number_of_steps=formData['steps_field'],
                            source_pattern=formData['source_pattern_link_field'],paper_ratio=formData['paper_ratio_field'],
                            video_tutorial=formData['video_tutorial_field'],img=formData['img_field'])

        db.collection(formData['collection']).document().set(model.to_dict())
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents    """
    try:
        # details of the request
        print('sanity check')
        dir_id = request.args.get('collection')  
          
        print('in collection ' + dir_id)
        curr_dir = db.collection(dir_id)
        filter_applied = request.args.get('filter_applied')
        if filter_applied == "false":
            print("initial list")
            all_dirs = [doc.to_dict() for doc in curr_dir.stream()]
            return jsonify(all_dirs), 200

        if dir_id == "Origami":
            
            difficulty = request.args.get('difficulty')
            step_lb = request.args.get('low_steps')
            step_up = request.args.get('high_steps')
            order_by = request.args.get('order_by')
            print('filtering with difficulty: ' + difficulty + ', steps from: ' + step_lb + ' and up to ' + step_up + ' ; order by ' + order_by)
        
            if difficulty != "":
                print("in diff")
                curr_dir = curr_dir.where("level_of_difficulty", "==", difficulty)
            if step_lb != "0" or step_up != "1000":
                print("in steps")                
                curr_dir = curr_dir.where("number_of_steps", ">=", int(step_lb))
                print("check passed to see if steps filtering is working")
            if step_up != "1000":
                curr_dir = curr_dir.where("number_of_steps", "<=", int(step_up))
                print("check passed to see if steps up filtering is working")
            if order_by != "":
                print("in orderBy")
                if order_by == "asc":
                    curr_dir = curr_dir.order_by("number_of_steps")
                else:
                    curr_dir = curr_dir.order_by("number_of_steps", direction=firestore.Query.DESCENDING)

            # now all the filter params are applied to the query collection, get the query
            docs = curr_dir.get()
            # check query returns documents
            # exists = False
            for doc in docs:
                # exists = True
                print("the query returns results")
                return jsonify([doc.to_dict() for doc in curr_dir.stream()]), 200
            return jsonify({'result':"No Document Found"}), 90
            #     break
            # if exists:
            #     print("final stage")
            # else:
            #     return jsonify({'result':"No Document Found"}), 90
            
        # filters = request.json Not allowed in GET method
        # Check if ID was passed to URL query
        # dir_id = request.args.get('page')    
        # if dir_id:
        #     dir = db.collection(dir_id).get()
        #     # where("page","==",dir_id).get()
        #     # Querying use operators
        #     docs = db.collection('HomeDirectory').where("comment", "==", True).get()
        #     ## ==, <=, >=, >, <, array_contains, 
        #     for doc in docs:
        #         print(doc.to_dict())

        #     return jsonify([doc.to_dict() for doc in dir]), 200
        # else:
        
    except Exception as e:
        print("error encountered: " + e)
        return f"An Error Occured: {e}"


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

        # id = request.json['id']
        # ori_ref.document(id).update(request.json)
        # return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

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

@app.route('/test', methods=['GET'])
def testing():
    try:
        tvshow = request.args.get('show', type=str)
        if tvshow:
            response = requests.get("https://api.tvmaze.com/singlesearch/shows?", params={"q": tvshow, "embed": "episodes"})
            print(response.url)
            return jsonify(response.json()['_embedded']['episodes']), 200
        else:
            response = requests.get("https://api.tvmaze.com/singlesearch/shows?q=rick-&-morty&embed=episodes")
            print(response.status_code)
            return jsonify(response.json()['_embedded']['episodes']), 200
    except Exception as e:
        return f"An Error Occured: {e}"
        

# @app.route('/subredditapi', methods=['GET'])
# def subreddit():
#     try:
#         # Check if ID was passed to URL query
#         subreddit = request.args.get('topic', type=str)
#         if subreddit:
#             response = requests.get("https://www.reddit.com/r/"+str(subreddit)+".json")
#             print(response.status_code)
#             print(response.url)
#             return jsonify(response.json()['data']['children']), 200
#         else:
#             response = requests.get("https://www.reddit.com/r/java.json")
#             print(response.status_code)
#             return jsonify(response.json()['data']['children']), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)

