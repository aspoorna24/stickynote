from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///signup.db'

app.config['SQLALCHEMY_BINDS'] = {
    'note' : 'sqlite:///note.db' 
}
app.config['SECRET_KEY'] = 'mysecret'
db = SQLAlchemy(app)
admin = Admin(app)

class Sign(db.Model):
    sid = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(200), nullable=False)
    passw = db.Column(db.String(200), nullable=False)
    notes = db.relationship('Note', backref='owner')


class Note(db.Model):
    __bind_key__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    titl = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_create = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('sign.sid'))

  

admin.add_view(ModelView(Note, db.session))
admin.add_view(ModelView(Sign, db.session))

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        email = request.form['email']
        user = request.form['user']
        passw = request.form['passw']
        task = Sign(email=email,user=user,passw=passw)
        try:
            db.session.add(task)
            db.session.commit()
            return render_template('login.html')
        except:
            return "Account is not signed up"

    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
     if request.method=='POST':
        user = request.form['user']
        passw = request.form['passw']
        user = Sign.query.filter_by(user=user).first()
        if user:
            if(user.passw==passw):
                global x
                x =  user.sid
                return render_template('index.html' )
            else:
                return 'wrong password'
        else:
            return 'wrong user info'  
        

     return render_template('login.html')

@app.route('/note', methods=['GET','POST'])
def take():
    owner_id = x
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        tas = Note(titl=title,desc=desc,owner_id=owner_id)
        try:
            db.session.add(tas)
            db.session.commit()
            return redirect('/note')
            
        except:
            return 'There was an issue in Data'
    else:
        tasks = Note.query.filter_by(owner_id=x).all()
        return render_template('index.html',tasks=tasks)
        
        

@app.route('/view/<int:id>')
def view(id):
    task = Note.query.get_or_404(id)
    return render_template('view.html',task=task)

@app.route('/delete/<int:id>')
def delete(id):
    task = Note.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/note')
    except:
        return "Something is wrong with database"

@app.route('/update/<int:id>', methods = ['GET','POST'])
def update(id):
    task = Note.query.get_or_404(id)
    if request.method == 'POST':
        task.titl = request.form['title']
        task.desc = request.form['desc']
        try:
            db.session.commit()
            return redirect('/note')
        except:
            return "There is an error in this"
    else:
        return render_template('update.html',task=task)


if __name__ == '__main__':
    app.run(debug=True)