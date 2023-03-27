from flask_app.config.mysqlconnection import ConnectToMySQL
from flask_app.models.tree import Tree
from flask import flash
import re
import bcrypt

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password_hash = data['password_hash']

    @classmethod
    def get_user_by_email(cls, email):
        if email is None or not isinstance(email, str): raise Exception("email must be a string")
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = ConnectToMySQL('trees_schema').query_db(query, { 'email': email })
        print(results)
        if len(results) == 0:
            return None
        user = User(results[0])
        return user
    
    
    @classmethod
    def get_user_by_id(cls, user_id):
        if user_id is None or not isinstance(user_id, int): raise Exception("user_id must be a string")

        query = "SELECT * FROM users WHERE id = %(id)s"
        results = ConnectToMySQL('trees_schema').query_db(query, { 'id': user_id })
        if len(results) == 0:
            return None
        user = User(results[0])
        return user


    @classmethod
    def create_user(cls, form_data):
        if 'first_name' not in form_data: raise Exception("first_name ID is required to create user")
        if 'last_name' not in form_data: raise Exception("last_name is required to create user")
        if 'email' not in form_data: raise Exception("email is required to create user")
        if 'password' not in form_data: raise Exception("password is required to create user")

        query = "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s)"

        password = form_data['password']
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)

        data = {
            'first_name': form_data['first_name'],
            'last_name': form_data['last_name'],
            'email': form_data['email'],
            'password_hash': password_hash
        }
        result = ConnectToMySQL('trees_schema').query_db(query, data)
        return result




    @staticmethod
    def validate_registration(form_data):
        is_valid = True
        if len(form_data['email']) < 6:
            flash("please enter an email address")
            is_valid = False
        if not EMAIL_REGEX.match(form_data['email']):
            flash("invalid email address")
            is_valid = False
        if User.get_user_by_email(form_data['email']):
            flash("An account with this email already exists")
            is_valid = False
        if len(form_data ['password']) < 8:
            flash ("please choose a password that is at least 8 characters in length")
            is_valid = False
        if form_data['password'] != form_data['password2']:
            flash ("Passwords do not match")
            is_valid = False
        if len(form_data['first_name']) < 2:
            flash ("first name must be at least 2 characters")
            is_valid = False
        if len(form_data['last_name']) < 2:
            flash ("last name must be at least 2 characters")
            is_valid = False

        return is_valid
    

    @staticmethod
    def login_user(form_data):
        if 'email' not in form_data: raise Exception("email is required to log in user")
        if 'password' not in form_data: raise Exception("password is required to log in user")

        if not EMAIL_REGEX.match(form_data['email']):
            flash("invalid email")
            return None
        
        user = User.get_user_by_email(form_data['email'])
        if not user:
            flash("invalid user")
            return None
        
        password = form_data['password']

        
        password_bytes = password.encode('utf-8')


        if not bcrypt.checkpw(password_bytes, user.password_hash.encode('utf-8')):
            flash("invalid password")
            return None
        
        return user