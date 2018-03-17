from flask import Flask, render_template, request, session
from pymongo import MongoClient
import uuid
import base64
import datetime
import os
import time

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'PNG', 'jpg', 'jpeg', 'gif','csv'])
beforetime=time.time()

UPLOAD_FOLDER ='C:\\Users\\vivek1\\PycharmProjects\\prakash\\static'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "prakash secret key"
global aftertime


@app.route('/')
def index():
    if session.get('logged_in') == True:
        aftertime=time.time()
        print(aftertime - beforetime)
        return render_template('upload.html')
    else:

        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    client = MongoClient('mongodb://localhost:27017/')
    u = request.form['user'];
    p = request.form['pass'];
    users = client.users.users.find_one({"username": u})
    pass1 = users['password']

    if str(pass1) == str(p):
        session['logged_in'] = True
        session['user'] = str(u)
        client.close()
        return render_template('upload.html')
    else:
        session['logged_in'] = False
        session['user'] = ""
        client.close()
        return render_template('login.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def insert_img(username, post_id, image_data, filename, cmnt):
    client = MongoClient('mongodb://localhost:27017/')
    img_coll = client.users.images
    post_dict = {}
    post_dict['filename'] = filename
    post_dict['username'] = username
    post_dict['post_id'] = post_id
    encoded_string = base64.b64encode(image_data)
    post_dict['image_data'] = encoded_string
    post_dict['post_time'] = str(datetime.datetime.now())
    post_dict['comments'] = str(cmnt)
   # post_dict['size'] = str(size_in_kb)
    output = img_coll.save(post_dict)
    images1 = client.users.comments.insert({"username": username, "filename": filename, "comment": cmnt})
    client.close()
    return str(output) + "" + str(cmnt)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    client = MongoClient('mongodb://localhost:27017/')
    # comments_from_user = []
    print 'in upload'

    file = request.files['myfile']

    # size1 = os.stat(file.filename).st_size
    username = session.get('user')
    print username
    # size_in_kb = size1 / 1024;
    # allowed_size = 1000;
    # allowed_count = 20;
    allowed_total_size = 10000
    comments_from_user = request.form['comments']
    print comments_from_user
    total_size = 0



    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # if size_in_kb<allowed_size and count1<allowed_count and (allowed_total_size-total_size)>size_in_kb:
        fname = str(file)
        image_data = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb').read()
        post_id = str(uuid.uuid1())
        insert_img(username, post_id, image_data, str(file.filename), comments_from_user)
        # else:
        # client.close()
        # return "file size exceeded or count exceeded or less limit"
    client.close()
    return 'successfully uploaded.' + '''<br>'''


@app.route('/show', methods=['GET', 'POST'])
def show():
    client = MongoClient('mongodb://localhost:27017/')
    username = session.get('user')
    l = ""
    a = []
    b = []
    images1 = client.users.images.find({"username": username})
    for images2 in images1:
        imagename = images2['filename']
        imagecontent = images2['image_data']

        print "imagesname: " + str(imagename)
        a.append(imagecontent)
        b.append(imagename)
    client.close()
    return render_template('list.html', result=a, name1=b)


@app.route('/del1/<fol>', methods=['GET', 'POST'])
def del1(fol):
    client = MongoClient('mongodb://localhost:27017/')
    username = session.get('user')
    print "in del"
    images1 = client.users.images.remove({"username": username, "filename": fol})
    client.close()
    return "Deleted successfully"


@app.route('/delete/<folder_name>', methods=['GET', 'POST'])
def delete(folder_name):
    client = MongoClient('mongodb://localhost:27017/')
    images1 = client.users.images.find({"filename": folder_name})
    imgs = []
    com1 = []
    username = session.get('user')
    for images2 in images1:
        imgs.append(images2)
    for i1 in imgs:
        img1 = i1['image_data']
        comments = i1['comments']
        decode = img1.decode()
    images1 = client.users.comments.find({"filename": folder_name, "username": username})
    for images2 in images1:
        com1.append(images2['comment'])
    client.close()
    return render_template('comment.html', result=decode, comm=com1, file=folder_name)


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    client = MongoClient('mongodb://localhost:27017/')
    username = session.get('user')
    print "in comments"
    cc1 = request.form['comment1']
    cc2 = request.form['filename1']
    images1 = client.users.comments.insert({"username": username, "filename": cc2, "comment": cc1})
    client.close()
    return "success comments"


@app.route('/retrieve_image', methods=['GET', 'POST'])
def retrieve_image():
    client = MongoClient('mongodb://localhost:27017/')
    l = ""
    a = []
    imgs = []
    c = []
    username = session.get('user')
    # images1=client.users.images.find({"username":u})
    images1 = client.users.images.find()
    for images2 in images1:
        imagename = images2['filename']
        imagecomments = images2['comments']
        imagecontent = images2['image_data']
        imageuser = images2['username']
        imgs.append({'image': images2['image_data'], 'comments': images2['comments'], 'date': images2['post_time'],
                     'uname': images2['username']})

    client.close()
    return render_template('retrieve_image.html', result=imgs)


@app.route('/getSomething', methods=['GET', 'POST'])
def getSomething():
    client = MongoClient('mongodb://localhost:27017/')
    num = request.form['num1']
    username = session.get('user')
    imgs = []
    a = request.form["num1"]
    comment1 = client.users.comments.find({"comment": a},{"filename":1, "_id":0})
    for x in comment1:
        var1=x['filename']
        images1 = client.users.images.find({"filename": var1})
        for images2 in images1:
            imagename = images2['filename']
            imagecomments = images2['comments']
            imagecontent = images2['image_data']
            imageuser = images2['username']
            imgs.append({'image': images2['image_data'], 'comments': images2['comments'], 'date': images2['post_time'],
                     'uname': images2['filename']})

    client.close()
    return render_template('getSomething.html', result=imgs)

@app.route('/getDetails/<folder_name>', methods=['GET', 'POST'])
def getDetails(folder_name):
    client = MongoClient('mongodb://localhost:27017/')
    print("In getDetials")
    username = session.get('user')
    print("filename= ", str(folder_name))
    images1 = client.users.images.find_one({"filename": str(folder_name)})
    imgs = []
    com1 = []
    for images2 in images1:
        imgs.append(images2)
    for i1 in imgs:
        img1 = i1['image_data']
        comments = i1['comments']
        decode = img1.decode()
    images1 = client.users.comments.find({"filename": folder_name, "username": username})
    for images2 in images1:
        com1.append(images2['comment'])

    return render_template('comment.html', result=decode, comm=com1, file=folder_name)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('login.html')








if __name__ == "__main__":
    app.run()


