from flask_app.config.mysqlconnection import ConnectToMySQL
from flask import flash
from flask_app.models import user
from datetime import datetime

class Tree:
    def __init__(self, data):
        self.id = data['id']
        self.users_id = data['users_id']
        self.species = data['species']
        self.location = data['location']
        self.reason = data['reason']
        self.date_planted = data['date_planted']
        self.num_visitors = data['num_visitors'] if ('num_visitors' in data) else 0
    
    @classmethod
    def tree_create(cls, data):
        if 'species' not in data: raise Exception("species ID is required to create tree")
        if 'location' not in data: raise Exception("location is required to create tree")
        if 'reason' not in data: raise Exception("reason is required to create tree")
        if 'date_planted' not in data: raise Exception("date_planted is required to create tree")
        if 'users_id' not in data: raise Exception("users_id is required to create tree")

        query = "INSERT INTO trees (species, location, reason, date_planted, users_id) VALUES ( %(species)s, %(location)s, %(reason)s, %(date_planted)s, %(users_id)s)"
        return ConnectToMySQL('trees_schema').query_db(query, data)

    @classmethod
    def tree_update(cls, data):
        if 'id' not in data: raise Exception("id is required to create tree")
        if 'species' not in data: raise Exception("species ID is required to create tree")
        if 'location' not in data: raise Exception("location is required to create tree")
        if 'reason' not in data: raise Exception("reason is required to create tree")
        if 'date_planted' not in data: raise Exception("date_planted is required to create tree")

        query = """
        UPDATE trees SET id=%(id)s, species=%(species)s, location=%(location)s, reason=%(reason)s, date_planted=%(date_planted)s WHERE id=%(id)s
        """
        return ConnectToMySQL('trees_schema').query_db(query, data)
    
    @classmethod
    def tree_get_by_user(cls, user_id):
        if user_id is None or not isinstance(user_id, int): raise Exception("user_id must be an integer")
        query = """
           SELECT * FROM trees WHERE users_id = %(id)s;
        """
        results = ConnectToMySQL('trees_schema').query_db(query, {"id": user_id})
        trees = []
        for row in results:
            tree = Tree(row)
            trees.append(tree)
        return trees


    @classmethod
    def tree_get(cls, id):
        if id is None or not isinstance(id, int): raise Exception("id must be an integer")
        query = """
           SELECT
            t.id AS tree_id,
            t.species,
            t.location,
            t.reason,
            t.date_planted,
            u.id AS planter_id,
            u.first_name AS planter_first_name,
            u.last_name AS planter_last_name,
            u.email AS planter_email,
            u.password_hash AS planter_password_hash,
            COUNT(v.users_id) AS num_visitors
            FROM trees t
            JOIN users u ON t.users_id = u.id
            LEFT JOIN visitors v ON t.id = v.trees_id
            WHERE t.id = %(id)s
            GROUP BY t.id;
        """
        result = ConnectToMySQL('trees_schema').query_db(query, {"id": id})[0]
        planted_by = user.User({
            'id': result['planter_id'],
            'first_name': result['planter_first_name'],
            'last_name': result['planter_last_name'],
            'email': result['planter_email'],
            'password_hash': result['planter_password_hash']
        })
        tree = Tree({
            'id': result['tree_id'],
            'users_id': result['planter_id'],
            'species': result['species'],
            'location': result['location'],
            'reason': result['reason'],
            'date_planted': result['date_planted'],
            'num_visitors': result['num_visitors']
        })
        tree.planted_by = planted_by
        return tree


    @classmethod
    def tree_get_all(cls):
        query = """
           SELECT
            t.id AS tree_id,
            t.species,
            t.location,
            t.reason,
            t.date_planted,
            u.id AS planter_id,
            u.first_name AS planter_first_name,
            u.last_name AS planter_last_name,
            u.email AS planter_email,
            u.password_hash AS planter_password_hash,
            COUNT(v.users_id) AS num_visitors
            FROM trees t
            JOIN users u ON t.users_id = u.id
            LEFT JOIN visitors v ON t.id = v.trees_id
            GROUP BY t.id;
        """
        results = ConnectToMySQL('trees_schema').query_db(query, {"id": id})
        trees = []
        for row in results:  
            planted_by = user.User({
                'id': row['planter_id'],
                'first_name': row['planter_first_name'],
                'last_name': row['planter_last_name'],
                'email': row['planter_email'],
                'password_hash': row['planter_password_hash']
            })
            tree = Tree({
                'id': row['tree_id'],
                'users_id': row['planter_id'],
                'species': row['species'],
                'location': row['location'],
                'reason': row['reason'],
                'date_planted': row['date_planted'],
                'num_visitors': row['num_visitors']
            })
            tree.planted_by = planted_by
            trees.append(tree)
        return trees


    @classmethod
    def tree_delete(cls, id):
        if id is None or not isinstance(id, int): raise Exception("tree_id must be an integer")
        query = "DELETE FROM trees WHERE id = %(id)s"
        return ConnectToMySQL('trees_schema').query_db(query, {"id": id})

    @classmethod
    def tree_add_visitor(cls, tree_id, user_id):
        if tree_id is None or not isinstance(tree_id, int): raise Exception("tree_id must be an integer")
        if user_id is None or not isinstance(user_id, int): raise Exception("user_id must be an integer")

        if Tree.has_been_visited_by(tree_id, user_id):
            return

        query = "INSERT INTO visitors (users_id, trees_id) VALUES (%(users_id)s, %(trees_id)s)"
        data = {
            "users_id": user_id,
            "trees_id": tree_id
        }

        return ConnectToMySQL('trees_schema').query_db(query, data)
    
    @classmethod
    def has_been_visited_by(cls, tree_id, user_id):
        query = "SELECT * from visitors WHERE trees_id = %(trees_id)s AND users_id = %(users_id)s"
        data = {
            "trees_id": tree_id,
            "users_id": user_id,
        }
        results = ConnectToMySQL('trees_schema').query_db(query, data)
        if len(results) > 0:
            return True;
        else:
            return False;
    @classmethod
    def tree_remove_visitor(cls, tree_id, user_id):
        if tree_id is None or not isinstance(tree_id, int): raise Exception("tree_id must be an integer")
        if user_id is None or not isinstance(user_id, int): raise Exception("user_id must be an integer")

        if Tree.has_been_visited_by(tree_id, user_id):
            return

        query = "DELETE FROM visitors WHERE users_id=%(users_id)s AND trees_id=%(trees_id)s"
        data = {
            "users_id": user_id,
            "trees_id": tree_id
        }

        return ConnectToMySQL('trees_schema').query_db(query, data)
    
    @classmethod
    def get_visitors_by_tree(cls, tree_id):
        query = "SELECT * from visitors LEFT JOIN users on users.id = users_id WHERE trees_id = %(tree_id)s"
        data = {
            "tree_id": tree_id
        }
        results = ConnectToMySQL('trees_schema').query_db(query, data)
        visitors = []
        for row in results:
            visitors.append(user.User(row))
        return visitors
    
    @staticmethod
    def validate_tree(form_data):
        is_valid = True
        if 'location' not in form_data or len(form_data['location']) < 1:
            flash("please enter a location")
            is_valid = False
        if 'species' not in form_data or len(form_data['species']) < 1:
            flash("please enter a species!")
            is_valid = False
        if 'reason' not in form_data or len(form_data ['reason']) < 1:
            flash("please give a description of why you planted a tree!")
            is_valid = False
        try:
            date_planted = datetime.strptime(form_data ['date_planted'], '%Y-%m-%d').date()
        except ValueError:
            flash("please enter a valid date")
            is_valid = False
        return is_valid
    



        
