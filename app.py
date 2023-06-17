import os
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FileField, validators
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'static/files'
db = SQLAlchemy(app)





class AnimalForm(FlaskForm):
    kind = StringField('kind', validators=[validators.DataRequired()])
    breed = StringField('breed', validators=[validators.DataRequired()])
    age = IntegerField('age', validators=[validators.DataRequired()])
    gender = StringField('gender', validators=[validators.DataRequired()])
    image = FileField('image')
    create = SubmitField('Create')


@app.route('/')
def get_animals():
    animals = [animal.to_dict() for animal in Animal.query.all()]
    lst = []
    lst1 = []
    dickt = {}
    image = {}
    for animal in animals:
        lst.append(animal['kind'].lower())
    for i in lst:
        if i not in lst1:
            lst1.append(i)
    print(animals)
    print(lst1)
    print(image)
    for animal in lst1:
        image[animal] = Animal.query.filter(Animal.kind == animal).first().filename
    for animal in lst1:
        dickt[str(animal)] = {'count':lst.count(str(animal)), 'image': image[animal]}
    return render_template('main.html', dickt=dickt, animals=animals)


@app.route('/add/animals', methods=['POST', 'GET'])
def create_animal():
    form = AnimalForm()
    if form.validate_on_submit():
        kind = form.kind.data.lower()
        breed = form.breed.data
        age = form.age.data
        gender = form.gender.data
        file = form.image.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))
        animal = Animal(kind=kind, breed=breed, age=age, gender=gender, filename=filename)
        db.session.add(animal)
        db.session.commit()
        return redirect('/add/animals')
    return render_template('add_animal.html', form=form)


with app.app_context():
    db.create_all()
    app.run()
