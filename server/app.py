#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        if not username or not password:
            return {'message': 'Username and password required'}, 422

        user = User(
            username=username,
            bio=bio,
            image_url=image_url
        )
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Username already exists'}, 422

        session['user_id'] = user.id
        return user.to_dict(), 201


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Unauthorized'}, 401

        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'Unauthorized'}, 401

        return user.to_dict()


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not user.authenticate(password):
            return {'message': 'Invalid username or password'}, 401

        session['user_id'] = user.id
        return user.to_dict()


class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Unauthorized'}, 401

        session['user_id'] = None
        return {}, 204


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Unauthorized'}, 401

        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'Unauthorized'}, 401

        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Unauthorized'}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'Unauthorized'}, 401

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user=user
            )
            db.session.add(recipe)
            db.session.commit()
        except (IntegrityError, ValueError):
            db.session.rollback()
            return {'message': 'Invalid recipe data'}, 422

        return recipe.to_dict(), 201


# Register resources
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
