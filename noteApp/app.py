from flask import Flask, request,g, render_template,url_for, make_response , flash, redirect , session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.secret_key = 'asdfasfsdf'
#Mongo Connectison
client=MongoClient('localhost:27017')
mydb=client.noteApp
mycollection=mydb.user

@app.route("/")
def index():
    return render_template('homePage.html')

@app.route("/login" , methods=['GET' , 'POST'])
def login():
    #taking data from login form
    if request.method == 'POST':

        #popping any existing session
        session.pop('user', None)

        name=request.form['username']
        password=request.form['password']

       #retrieving password of username from db
        result=mycollection.find({"Username": name},{'_id':0,'password':1})
        database_pwd=None
        state=False
        for r in result :
            database_pwd=r['password']
        if database_pwd == None:
            pass
        else:
            state=check_password_hash(database_pwd,password)
        if state == True:

            #setting session and cookie after validation:
            session['user']=name
            resp = make_response(redirect (url_for('notes')))
            resp.set_cookie('username', name)
            return resp
        else:
            flash('Invalid user')
            return redirect('/login')

    return render_template('loginPage.html')

@app.route("/signup" , methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        #Taking data from signup form
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']
        password1=request.form['password1']

        if password == password1:
            hash_pwd=generate_password_hash(password)
            myrecord = {"Email": email ,"Username" : username , "password" : hash_pwd}
            record_id = mycollection.insert(myrecord)
        else:
            flash("Password missmatch")
            return redirect('/signup')
            #If we use angular JS the flashing of error message will be user friendly and wont have to load page again(redirect).
        return redirect(url_for('login'))
    return render_template('signupPage.html')


@app.route("/notes")
def notes():
    #getting cookie to check if in session
    name= request.cookies.get('username')
    if name != session['user']:
        return redirect(url_for('login'))

    #Getting all the notes that belong to the current user and displaying it
    collection=mydb.notedb
    notes=collection.find({"Username":name})
    allnotes=[]
    for n in notes:
        allnotes.append(n)
    return render_template('notes.html',notes=allnotes)

@app.route("/create_note" , methods=['GET', 'POST'])
def create_note():
    if request.method == 'POST':
        name= request.cookies.get('username')
        if name != session['user']:
            return redirect(url_for('login'))

        #using counter collection to get counter for note ID
        collectionCounter=mydb.counter
        counterValue=collectionCounter.find({})
        for c in counterValue:
            counter=c['id']

        #getting data for new note
        title=request.form['title']
        text=request.form['note']

        #inserting into notedb all the notes being created
        collection=mydb.notedb
        record = { "noteID": counter , "Username" : name , "title" : title , "text" : text}
        collection.insert(record)

        #updating value of counter- using $inc
        collectionCounter.update({'id': int(counter)},{'$inc':{ 'id': 1} },upsert=False)
        return redirect (url_for('notes'))
    return render_template('createNote.html')

@app.route("/notes/edit" , methods=['GET' , 'POST'])
def edit():
    id=request.args.get('nid')
    if request.method == 'POST':

        collection=mydb.notedb
        #getting edited note details
        title=request.form['title']
        text=request.form['note']

        #Updating the note db: - using $set
        collection.update_one({'noteID': int(id)},{'$set':{ 'title': title , 'text': text} },upsert=False)
        return redirect(url_for("notes"))
    #getting note id for the note to be edited

    print(id)
    #getting the note to be edited from db
    collection=mydb.notedb
    note=collection.find({"noteID":int(id)})
    no={}
    for n in note:
        no=n
    print no


    return render_template('edit.html',note=no)
if __name__=="__main__":
    app.run(debug=True)
