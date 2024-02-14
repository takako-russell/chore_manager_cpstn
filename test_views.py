import os
from unittest import TestCase
from flask import url_for
from models import db, Child,Parent,Chore,Assigned


os.environ['DATABASE_URL'] = "postgresql:///chore_manager_test"

from app import app

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.create_all()
        # db.session.rollback()
        
        # with app.app_context():
        #     db.create_all()
        
        Child.query.delete()
        Chore.query.delete()
        Parent.query.delete()
        Assigned.query.delete()
        
        self.client = app.test_client()

        self.testchild1 = Child(id=1,childname='child1', child_color='Red')
        db.session.add(self.testchild1)
        db.session.commit()
    
        self.testparent1 = Parent(id=1,parentname='parent1', relation='Dad')
        db.session.add(self.testparent1)
        db.session.commit()
        
        self.testchore1 = Chore(title='Dishes',description='Do the dishes',payrate=2)
        db.session.add(self.testchore1)
        db.session.commit()
        
        self.app = app
        
        

    def test_assign_chore(self):
        with self.client:
            
            cell_id = 'testchild1_0'
            
            res = self.client.post(f"/calendar/1/{self.testchild1.id}/assign",data={'chore_to_assign':self.testchore1.id,'assigned_by':self.testparent1.id})

            assigned_tasks = Assigned.query.filter_by(assigned_child=self.testchild1.id).all()
            
            self.assertEqual(res.status_code, 302)
            self.assertEqual(len(assigned_tasks), 1)
            self.assertEqual(assigned_tasks[0].assigned_chore, self.testchore1.id)
            
                
                
    def test_delete_assigned_chore(self):
        with self.client:
            
            res = self.client.post(f"/calendar/1/{self.testchild1.id}/delete")
            
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, url_for('homepage', _external=True))
            
            
            
    def test_mark_as_done(self):
        with self.client:
            
            res = self.client.post(f"/calendar/1/{self.testchild1.id}/mark_as_done",data={'checked_chore_ids':[self.testchore1.id]})
            
            child = Child.query.get(self.testchild1.id)
            tasks = child.assigned_tasks
            
            self.assertEqual(res.status_code, 302)
            for task in tasks:
                self.assertTrue(task.done)
                
                
    def test_achievement(self):     
        with self.client:
            self.testchore2 = Chore(title='Mopping',description='Mop the first floor',payrate=1)
            db.session.add(self.testchore2)
            db.session.commit()
            
            assigned_tasks = [
            Assigned(assigned_child=self.testchild1.id, assigned_chore=self.testchore1.id, parent_assigned=self.testparent1.id, assigned_day=1, done=True),
            Assigned(assigned_child=self.testchild1.id, assigned_chore=self.testchore2.id, parent_assigned=self.testparent1.id, assigned_day=1, done=True),
            ]
            
            for task in assigned_tasks:
                db.session.add(task)
                db.session.commit()
            
            
            res = self.client.get(f"/calendar/achievement")
            
            total_payrate = sum(Chore.query.get(task.assigned_chore).payrate for task in assigned_tasks)
            
            self.assertEqual(res.status_code, 200)
            self.assertEqual(total_payrate, 3)
            self.assertIn(b'<span style="font-size: 30px">$3',res.data)
            
            
            
            
    def tearDown(self):
            """Clean up any fouled transaction."""
            db.session.rollback()
            db.drop_all()