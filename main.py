# Modules which we want import during creating websites
import math 
from flask import Flask , render_template , request , session , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json 
import os
from werkzeug.utils import secure_filename
from flask import abort

# Import json file from local disk 

with open('config.json','r') as c : 
    params = json.load(c)["params"]
local_server = True

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']

# For sending mail by user from contact me link 

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['mail_username'],
    MAIL_PASSWORD = params['mail_passw']
)
mail = Mail(app)

# For creating login in php my admin using Flask SQLALACHEMY

if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
db= SQLAlchemy(app)


# Database entry for Post 
class Posts(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable = False)
    Sub_heading = db.Column(db.String(500), nullable = False)
    Slug = db.Column(db.String(20), nullable = False)
    Content = db.Column(db.String(120), nullable = False)
    img_file = db.Column(db.String(12), nullable = True)
    Date = db.Column(db.String (20),nullable = True)


# Databse entry for Contact

class Contact(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable = False)
    Email_adress = db.Column(db.String(20), nullable = False)
    Phone_number = db.Column(db.String(12), nullable = False)
    Message = db.Column(db.String(120) , nullable = False)  
    Date = db.Column(db.String (20),nullable = True)


# Link for home , suraj coder , post , contact and about 
@app.route("/")
def home():
    posts = Posts.query.filter_by().all() 
    last = math.ceil(len(posts)/int(params["no_of_post"]))
    #[0:params['no_of_post']]
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts= posts[ (page - 1 )* int (params['no_of_post']) : (page -1 ) * int (params['no_of_post']) + int(params['no_of_post'])  ]
#Pagination Logic 
        #First
    if (page==1):
        prev = "#"
        next = "/?page="+ str(page+1)
    
    elif (page==last):
        prev = "/?page="+ str(page-1)
        next = "#"

    else : 
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    return render_template('index.html',params=params,posts=posts , prev=prev , next = next )

@app.route("/index")
def home1():
    return render_template('index.html',params=params)

@app.route("/about")
def about():
    return render_template('about.html',params=params )

@app.route("/contact" ,methods = ['GET','POST']  )
def contact():
    if (request.method=='POST') :
        '''ADD DATA TO DATABASE'''
        name = request.form.get('name')
        email = request.form.get('email')  
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(Name=name,Email_adress=email,Phone_number=phone,Message=message , Date = datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name , 
                          sender = email , 
                          recipients = [params['mail_username']],
                          body = message + '\n' + phone )
    return render_template('contact.html',params=params)

@app.route("/sample_post",methods=['GET'])
def sample_post():
    post = Posts.query.first()
    return render_template('sample_post.html' ,params=params,post=post)
    # return render_template('sample_post.html',params=params)

@app.route("/post/<string:Posts_Slug>",methods=['GET'])
def post_route(Posts_Slug):
    post = Posts.query.filter_by(Slug=Posts_Slug).first()
    return render_template('post.html' ,params=params,post=post)

@app.route("/login" , methods= ['GET' , 'POST'])
def login():
    posts = None  # Initialize posts variable here
    if ('user' in session and session['user'] == params['usr_name']):
        posts = Posts.query.all() 
        return render_template ('admin.html', params=params , posts = posts)

    if request.method == 'POST':
         username = request.form.get('uname')
         userpass = request.form.get('pass')
         if (username == params['usr_name'] and userpass == params['usr_pass'] ) :
             session ['user'] = username 
             posts = Posts.query.all() 
             return render_template ('admin.html',params=params , posts = posts)          
    return render_template ('login.html',params=params,posts=posts)
    
@app.route("/edit/<string:Sno>" ,methods= ['GET' , 'POST'])
def edit (Sno): 
    if request.method == 'POST':
        print(request.form)
    if ('user' in session and session['user'] == params['usr_name']):
        if request.method == 'POST':
            box_title = request.form.get('Title') 
            tline = request.form.get('Sub_heading') 
            slug = request.form.get('Slug') 
            content = request.form.get('Content')  
            img_file = request.form.get('img_file')
            date = datetime.now()  
            
            if Sno=='0' :
                post = Posts(Title=box_title,Slug=slug,Sub_heading=tline,Content=content,Date=date,img_file=img_file)
                db.session.add(post)
                db.session.commit() 

            else : 
                post = Posts.query.filter_by(Sno=Sno).first()
                post.Title = box_title
                post.Sub_heading = tline
                post.Slug = slug 
                post.Content = content 
                post.img_file = img_file
                post.Date = date 
                db.session.commit()
                # return redirect(+Sno)
        post = Posts.query.filter_by(Sno=Sno).first()
        return render_template("edit.html",params=params,Sno=Sno,post=post) 
       
@app.route("/uploader", methods = ['GET','POST'])
def uploader () : 
     if ('user' in session and session['user'] == params['usr_name']):
         if (request.method == "POST"):
             f = request.files['file1']
             f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
             return "Uploaded sucessfully "
         

@app.route("/logout")
def logout (): 
    session.pop('user')
    return redirect('/login')

@app.route("/delete/<string:Sno>" ,methods= ['GET' , 'POST'])
def delete(Sno):
    if ('user' in session and session['user'] == params['usr_name']):
        post=Posts.query.filter_by(Sno=Sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/login')



app.run(debug=True)