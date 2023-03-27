from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
from flask_app.models.user import User
from flask_app.models.tree import Tree
import copy

@app.route('/dashboard', methods = ['GET'])
def index():
    if 'user' not in session:
        return redirect('/')
    user = User.get_user_by_id(session['user']['id'])
    trees = Tree.tree_get_all()
    return render_template('dashboard.html', trees=trees, user=session['user'])

@app.route('/new/tree', methods= ['GET', 'POST'])
def tree_create():
    if 'user' not in session:
        return redirect ('/')
    if request.method == "POST":
        if not Tree.validate_tree(request.form):
            return redirect(url_for("tree_create"))
        data = request.form | {'users_id': session['user']['id']}
        Tree.tree_create(data)
    else:
        return render_template("create_edit_tree.html")
    return redirect('/dashboard')

@app.route('/edit/<int:id>', methods = ['GET', 'POST'])
def tree_update(id):
    if 'user' not in session:
        return redirect ('/')
    if request.method == "POST":
        if not Tree.validate_tree(request.form):
            return redirect(url_for("tree_create"))
        Tree.tree_update(request.form | {})
    else:
        tree = Tree.tree_get(id)
        if not tree:
            flash ("tree does not exist!")
            return redirect('/dashboard')
        if tree.users_id != session['user']['id']:
            flash("this isn't your tree!")
            return redirect('/dashboard')
        return render_template("create_edit_tree.html", tree=tree)
    return redirect('/dashboard')

@app.route('/delete/tree', methods = ['POST'])
def tree_delete():
    if 'user' not in session:
        return redirect ('/')
    tree = Tree.tree_get(int(request.form['id']))
    if tree.users_id != session['user']['id']:
        flash("that isn't your tree!")
        return redirect('/dashboard')
    Tree.tree_delete(tree.id)
    return redirect(request.form['redirect_url'])


@app.route('/show/<int:tree_id>', methods=['GET'])
def tree_get(tree_id):
    if 'user' not in session:
        return redirect('/')
    tree = Tree.tree_get(tree_id)
    visitors = Tree.get_visitors_by_tree(tree_id)
    user_id = session['user']['id']
    is_visitor = any(s.id == user_id for s in visitors)
    return render_template('show_tree.html', is_visitor=is_visitor, tree=tree, visitors=visitors)

@app.route('/user/account', methods=['GET'])
def my_trees():
    if 'user' not in session:
        return redirect('/')
    user = session['user']
    my_trees = Tree.tree_get_by_user(int(user['id']))
    return render_template('my_trees.html', user=user, trees=my_trees)

@app.route('/add_visitor', methods=['POST'])
def add_visitor():
    if 'user' not in session:
        return redirect('/')
    user_id = int(session['user']['id'])
    tree_id = int(request.form['tree_id'])
    Tree.tree_add_visitor(tree_id, user_id)
    return redirect(f'/show/{tree_id}')







