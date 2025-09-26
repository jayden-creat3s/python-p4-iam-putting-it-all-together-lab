from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.Text)

    recipes = db.relationship('Recipe', backref='user')

    serialize_rules = ('-recipes', '-_password_hash')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        if not self._password_hash:
            return False
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    serialize_rules = ('-user',)

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError('Instructions must be at least 50 characters long.')
        return instructions