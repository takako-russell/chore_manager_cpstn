import os

from flask import Flask, render_template,request, flash, redirect, session
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import not_
from forms import ChildAddForm,ChoreAddForm, AddParentForm,ChooseChoreToAssignForm
from models import db, connect_db, Parent, Child, Chore, Assigned

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///chore_manager'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


connect_db(app)
app.app_context().push()
db.create_all()


def get_children_and_parents():
    parents = Parent.query.all()
    children = Child.query.all()
    chores = Chore.query.all()
    return parents, children,chores


def get_child_id_and_cellnum(cell_id):
    
    list_name = str(cell_id).split("_")
    
    child_name = list_name[0]
    cell_num = list_name[1]
    
    child = Child.query.filter(Child.childname == child_name).first()
    childid = child.id
    
    return childid,cell_num


@app.context_processor
def inject_children_and_parents():
    parents, children, chores = get_children_and_parents()
    return dict(parents=parents, children=children, chores = chores)



@app.route("/")
def homepage():
    # parents, children, and chores are all sent in the context processor.
    # assigned_chores lookup table is also retrieved and visible within
    # child.assigned_tasks
    parents, children, chores = get_children_and_parents()
    view_children = []

    for child in children:
        assigned_task_ids = [t.assigned_chore for t in child.assigned_tasks]
        assigned_chores = Chore.query.filter(Chore.id.in_(assigned_task_ids)).all()
        
        view_assigned_tasks = []
        for chore in assigned_chores:
            done = [t for t in child.assigned_tasks if t.assigned_chore == chore.id][0].done
            parent_assigned = [t for t in child.assigned_tasks if t.assigned_chore == chore.id][0].parent_assigned
            parent = Parent.query.get(parent_assigned)
            view_assigned_tasks.append({
                'title': chore.title,
                'description': chore.description,
                'id': chore.id,
                'assigned_day': [t for t in child.assigned_tasks if t.assigned_chore == chore.id][0].assigned_day,
                "payrate": chore.payrate,
                'done': done,
                'parent_assigned':parent,
                'bg_color': 'gray' if done else child.child_color
            })

        view_children.append({
            'assigned_tasks': view_assigned_tasks,
            'id': child.id,
            'child_color': child.child_color,
            "childname": child.childname,
        })
    
    return render_template('home.html',view_children = view_children )



@app.route("/parents")
def show_all_parents():
    
    return render_template("show_parents.html")
    

@app.route('/parents/addparent', methods=["GET", "POST"])
def add_parent():
    
    form = AddParentForm()
    
    if form.validate_on_submit():
        
            parent = Parent(parentname = form.parentname.data, relation = form.relation.data)
            
            db.session.add(parent)
            db.session.commit()
            
            return redirect('/')
            
    return render_template('parents/addParent.html', form = form)



@app.route('/parents/<int:parent_id>')
def parent_details(parent_id):
    
    parent = Parent.query.get(parent_id)
    
    return render_template('parents/parentDetails.html', parent = parent)

@app.route('/parents/<int:parent_id>/update', methods = ['GET','POST'])
def update_parent(parent_id):
    parent = Parent.query.get(parent_id)
    form = AddParentForm(obj=parent)

    if form.validate_on_submit():
        form.populate_obj(parent)
        db.session.commit()
        
        flash('Parent updated successfully!', 'success')
        return redirect(f"/parents/{parent_id}")
    
    return render_template(f'parents/update_parent.html', form = form, parent = parent)


@app.route('/parents/<int:parent_id>/delete',methods=["POST"])
def parent_delete(parent_id):
    
    parent = Parent.query.get(parent_id)
    if parent.assignment:
        for assignment in parent.assignment:
            db.session.delete(assignment)
    
    db.session.delete(parent)
    db.session.commit()
    
    return redirect("/")


@app.route("/children")
def show_all_children():
    
    children = Child.query.all()
    
    return render_template("show_children.html",children = children)


@app.route('/children/addchild', methods=["GET", "POST"])
def add_child():
    
    form = ChildAddForm()
    
    if form.validate_on_submit():
        
            child = Child(childname = form.childname.data, child_color = form.color.data)
            
            db.session.add(child)
            db.session.commit()
            
            return redirect('/')
            
    return render_template('children/addChild.html', form = form)



@app.route('/children/<int:child_id>')
def child_details(child_id):
    
    child = Child.query.get(child_id)
    # assigned_chores = Assigned.query.filter_by(assigned_child=child.id, done=True).all()
    
    # 
    
    assigned_chores = db.session.query(Assigned, Chore).\
                      join(Chore, Assigned.assigned_chore == Chore.id).\
                      filter(Assigned.assigned_child == child_id, Assigned.done == True).\
                      all()
    
    total_payrate = sum(chore.payrate for assigned, chore in assigned_chores)
    number_done = len(assigned_chores)
        
        
    child.total_earnings = total_payrate
    
    
    return render_template('children/childDetails.html', child = child, number_done = number_done)


@app.route('/children/<int:child_id>/update', methods = ['GET','POST'])
def update_child(child_id):
    child = Child.query.get(child_id)
    form = ChildAddForm(obj=child)

    if form.validate_on_submit():
        form.populate_obj(child)
        db.session.commit()
        
        flash('Child updated successfully!', 'success')
        return redirect(f"/children/{child_id}")
    
    return render_template(f'children/update_child.html', form = form, child = child)

    


@app.route('/children/<int:child_id>/delete',methods=["POST"])
def child_delete(child_id):
    
    child = Child.query.get(child_id)
    if child.assigned_tasks:
        for assignment in child.assigned_tasks:
            db.session.delete(assignment)
    
    db.session.delete(child)
    db.session.commit()
    
    return redirect("/")


@app.route("/chores")
def show_all_chores():
    
    chores = Chore.query.all()
    
    return render_template("/chores/show_chores.html",chores = chores)


@app.route('/chores/addchore', methods=["GET", "POST"])
def add_chore():
    
    form = ChoreAddForm()
    
    if form.validate_on_submit():
        
            chore = Chore(title = form.title.data, description = form.description.data, payrate = form.payrate.data)
            
            db.session.add(chore)
            db.session.commit()
            
            return redirect("/")
            
    return render_template('chores/addChore.html', form = form)



@app.route('/chores/<int:chore_id>')
def chore_details(chore_id):
    
    chore = Chore.query.get(chore_id)
    
    return render_template('chores/chore_details.html', chore = chore)


@app.route('/chores/<int:chore_id>/update', methods=["GET", "POST"])
def update_chore(chore_id):
    
    chore = Chore.query.get(chore_id)
    form = ChoreAddForm(obj=chore)

    if form.validate_on_submit():
        form.populate_obj(chore)
        db.session.commit()
        
        flash('Chore updated successfully!', 'success')
        return redirect(f"/chores/{chore_id}")
    
    return render_template(f'chores/update_chore.html', form = form, chore = chore)





@app.route('/chores/<int:chore_id>/delete',methods=["POST"])
def chore_delete(chore_id):
    
    chore = Chore.query.get(chore_id)
    
    if chore.assignment:
        for assignment in chore.assignment:
            db.session.delete(assignment)
    
    db.session.delete(chore)
    db.session.commit()
    
    return redirect("/")


@app.route('/calendar/<cell_id>',methods=["GET"])
def show_daily_chores(cell_id):
        
    childid, cell_Idx = get_child_id_and_cellnum(cell_id)
    
    child = Child.query.get(childid)
    assigned_task_ids = [t.assigned_chore for t in child.assigned_tasks]
    
    assigned_chores = Chore.query.filter(Chore.id.in_(assigned_task_ids)).filter(Assigned.assigned_day == cell_Idx).all()
    
   
    view_chores = []
    parent_assigned_chore = None
    for chore in assigned_chores:
       
        child_tasks = [t for t in child.assigned_tasks if t.assigned_chore == chore.id]
        
        
        done_task = next((t for t in child_tasks if t.done), None)
        
       
        parent = [t.parent_assigned for t in child.assigned_tasks if t.assigned_chore == chore.id][0]
        parent_assigned_chore = Parent.query.get(parent)
        
        view_chores.append({
            'title': chore.title,
            'description': chore.description,
            'id': chore.id,
            "payrate": chore.payrate,
            'done': done_task is not None,
            'parent_assigned': parent_assigned_chore,
            'bg_color': 'gray' if done_task else child.child_color
        })
    
    
    return render_template('calendar/show_daily_chores.html', assigned_chores = view_chores, cell_id = cell_Idx,child=child,parent_assigned=parent_assigned_chore)
    
    
    
@app.route('/calendar/<int:cell_id>/<int:child_id>/assign',methods=["GET","POST"]) 
def assign_a_chore(cell_id,child_id):
    parents = Parent.query.all()
    
    form = ChooseChoreToAssignForm()
    
    assigned_chores_ids = [assigned.assigned_chore for assigned in Assigned.query.filter_by(assigned_child=child_id, assigned_day=cell_id).all()]
    allChores = Chore.query.filter(not_(Chore.id.in_(assigned_chores_ids))).all()
    
    form.chore_to_assign.choices = [(str(chore.id), chore.title) for chore in allChores]
    form.assigned_by.choices = [(str(parent.id), parent.parentname) for parent in parents]
    
    if form.validate_on_submit():
        
        chosen_chore_id = form.chore_to_assign.data
        assigned_parent_id = form.assigned_by.data
        
        assigned_chore = Assigned(
        assigned_child=child_id,
        assigned_chore=chosen_chore_id,
        parent_assigned = assigned_parent_id,
        assigned_day=cell_id,
        done=False)
    

        db.session.add(assigned_chore)
        db.session.commit()
        
        
        
        return redirect("/")
    
    return render_template('calendar/assign_chore.html',form =form,allChores = allChores)
    
    
@app.route("/calendar/<int:cell_id>/<int:child_id>/mark_as_done", methods=["POST"])
def mark_checked_chores_as_done(cell_id,child_id):
    
    checked_chore_ids = request.form.getlist("checked_chores")
    
    chores_done = Assigned.query.filter(Assigned.assigned_chore.in_(checked_chore_ids)).filter(Assigned.assigned_day == cell_id).filter(Assigned.assigned_child == child_id).all()
    
    for chore_done in chores_done:
        
       chore_done.done = True
       
    db.session.commit()
    
    return redirect("/")



@app.route("/calendar/<int:cell_id>/<int:child_id>/show_delete", methods=["POST"])
def show_delete_assigned_chores(cell_id,child_id):
    child = Child.query.get(child_id)
    assigned_task_ids = [t.assigned_chore for t in child.assigned_tasks]
    
    assigned_chores = Chore.query.filter(Chore.id.in_(assigned_task_ids)).filter(Assigned.assigned_day == cell_id).all()
    
    # jinja doesn't seem to like fanciness whatsoever
    # build a viewmodel that has some data from both Chore and Assignment
    view_chores = []
    for chore in assigned_chores:
       
        child_tasks = [t for t in child.assigned_tasks if t.assigned_chore == chore.id]
        
        # Find the task that is marked as done, if any
        done_task = next((t for t in child_tasks if t.done), None)
        
        # If a done task is found, retrieve its parent_assigned
        parent_assigned = None
        if done_task:
            parent_assigned = done_task.parent_assigned
            # Retrieve parent information
            parent = Parent.query.get(parent_assigned)
        else:
            parent = None 
            
        view_chores.append({
            'title': chore.title,
            'description': chore.description,
            'id': chore.id,
            "payrate": chore.payrate,
            'done': done_task is not None,
            'parent_assigned': parent_assigned,
            'parent':parent,
            'bg_color': 'gray' if done_task else child.child_color
        })
    
    
    
    return render_template("/calendar/delete_assigned_chore.html",assigned_chores = view_chores, cell_id = cell_id,child=child)



@app.route("/calendar/<int:cell_id>/<int:child_id>/delete", methods=["POST"])
def delete_assigned_chores(cell_id,child_id):
    
    checked_chore_ids = request.form.getlist("checked_chores")
    
    chores_to_delete = Assigned.query.filter(Assigned.assigned_chore.in_(checked_chore_ids)).filter(Assigned.assigned_day == cell_id).filter(Assigned.assigned_child == child_id).all()
    
    for chore in chores_to_delete:
        db.session.delete(chore)
       
    db.session.commit()
    
    return redirect("/")


@app.route("/calendar/achievement")
def show_achievement_so_far():
    children = Child.query.all()
    for child in children:
        assigned_chores = Assigned.query.filter_by(assigned_child=child.id, done=True)
        total_payrate = sum(Chore.query.get(chore.assigned_chore).payrate for chore in assigned_chores)
        
        
        child.total_earnings = total_payrate
    
        
    
    return render_template("calendar/show_achievement.html",children = children)