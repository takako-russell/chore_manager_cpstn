import os
from unittest import TestCase
from models import db, connect_db, Parent,Child,Chore,Assigned


os.environ['DATABASE_URL'] = "postgresql:///chore_manager_test"


from app import app

# db.create_all()


app.config['WTF_CSRF_ENABLED'] = False



class ModelTests(TestCase):
    """Test models"""
    
    def setUp(self):
        """Create test client, add sample data."""

        db.create_all()
        # with app.app_context():
        #     db.create_all()
            
        # User.query.delete()
        # Message.query.delete()

        self.client = app.test_client()

        # self.testparent = User.signup(username="testuser",
        #                             email="test@test.com",
        #                             password="testuser",
        #                             image_url=None)

        # db.session.commit()
            
    def test_add_parent(self):
        """Tests if a parent can be added"""
        with self.client:
            
            parent = Parent(id=1,parentname='parent1', relation='Dad')
            db.session.add(parent)
            db.session.commit()

            retrieved_parent = Parent.query.get(1)

            self.assertEqual(retrieved_parent.parentname, 'parent1')
            self.assertEqual(retrieved_parent.id, 1)
            self.assertEqual(retrieved_parent.relation, 'Dad')
            
    
    
    def test_add_child(self):
        """Tests if a parent can be added"""
        with self.client:
            
            child = Child(id=1,childname='child1', child_color='Red')
            db.session.add(child)
            db.session.commit()

            retrieved_child = Child.query.get(1)

            self.assertEqual(retrieved_child.childname, 'child1')
            self.assertEqual(retrieved_child.id, 1)
            self.assertEqual(retrieved_child.child_color, 'Red')
            
    
    def test_update_chore(self):
        """Test if a chore can be updated"""
        with self.client:
            chore = Chore(title='Mopping', description='Mop the first floor', payrate=1)
            db.session.add(chore)
            db.session.commit()

            res = self.client.post(f"/chores/{chore.id}/update", data={'title': 'Mopping', 'description': 'Mop the first floor', 'payrate':'2'})
            
            updated_chore = Chore.query.get(chore.id)
            
            self.assertEqual(res.status_code, 302)
            self.assertEqual(updated_chore.title, 'Mopping')
            self.assertEqual(updated_chore.payrate, 2)


    def test_assign_chore(self):
        with self.client:
            parent = Parent(parentname = "parent", relation="father")
            db.session.add(parent)
            
            child = Child(childname = "testchild1",child_color="Red")
            db.session.add(child)
            
            chore = Chore(title="Test Chore", description="test", payrate=1)
            db.session.add(chore)
            db.session.commit()            
            
            res = self.client.post(
                f"/calendar/1/{child.id}/assign",data={"chore_to_assign": chore.id,
                "assigned_by": parent.id })
    
            updated_child = Child.query.get(child.id)
            # task on the child from form
            child_task = updated_child.assigned_tasks[0]
            
            # task in the db
            assigned_task = Assigned.query.get(
                (child_task.assigned_child,
                 child_task.assigned_chore,
                 child_task.parent_assigned,
                 child_task.assigned_day
                 )
            )
            # assertions
            self.assertEqual(res.status_code, 302)
            self.assertEqual(child_task, assigned_task)
    
    
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()
        db.drop_all()