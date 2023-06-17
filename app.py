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


class Animal(db.Model):
    __tablename__ = 'animal'
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(100))
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(100))
    filename = db.Column(db.String)

    def to_dict(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'breed': self.breed,
            'age': self.age,
            'gender': self.gender,
            'filename': self.filename
        }



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

@app.route('/update/animals/<int:id>', methods=['POST', 'GET'])
def update_animal(id):
    form = AnimalForm()
    animal = Animal.query.get(id)
    if form.validate_on_submit():
        animal.kind = form.kind.data.lower()
        animal.breed = form.breed.data
        animal.age = form.age.data
        animal.gender = form.gender.data
        db.session.commit()
        return redirect('/')
    return render_template('update_animal.html', form=form, animal=animal)


@app.route('/delete/animals/<int:id>')
def delete_animal(id):
    animal = Animal.query.get(id)
    db.session.delete(animal)
    db.session.commit()
    return redirect('/')

@app.route('/new/arrivals')
def new_arrivals():
    animals = [animal.to_dict() for animal in Animal.query.order_by(Animal.id.desc())]
    return render_template('new.html', animals=animals)

@app.route('/animals/<string:kind>')
def same_kind_animals(kind):
    animal = [animal.to_dict() for animal in Animal.query.filter(Animal.kind == kind)]
    return render_template('info_animal.html', animal=animal)


@app.route('/about')
def about():
    return render_template('about.html')

with app.app_context():
    db.create_all()
    app.run()
