from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.inspection import inspect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, URLField
from wtforms.validators import DataRequired, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Bootstrap(app)


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = URLField('Cafe location on GoogleMaps URL', validators=[DataRequired(), URL()])
    img_url = URLField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Location of Cafe', validators=[DataRequired()])
    has_sockets = BooleanField('Does the cafe have sockets?')
    has_toilet = BooleanField('Does the cafe have toilet?')
    has_wifi = BooleanField('Does the cafe have wifi?')
    can_take_calls = BooleanField('Does the cafe allopw to take calls?')
    seats = SelectField('How many seats?', validators=[DataRequired()],
                        choices=[('Less than 3'), ('3 to 5'), ('5 to 10'), ('More than 10')])
    coffee_price = StringField('Coffee price', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cafes")
def cafes():
    table = inspect(Cafe)
    column_names = [column.name for column in table.c][1:]
    length = len(column_names)
    cafes_data = db.session.execute(db.select(Cafe)).scalars()
    cafes = [cafe.to_dict() for cafe in cafes_data]
    return render_template('cafes.html', column_names=column_names, all_cafes=cafes, n=length)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
