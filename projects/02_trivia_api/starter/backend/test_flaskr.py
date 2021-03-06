import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', True])
        self.assertEqual(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', True])
        self.assertEqual(data['questions'])
        self.assertEqual(len(data['questions']))
        self.assertEqual(data['total_questions'])
        self.assertEqual(len(data['categories']))
        self.assertEqual(data['current_category'])

    def test_get_question(self):
        res = self.client().get('/question/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', True])
        self.assertEqual(data['questions',1])

    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        Question = Question.guery.filter_by(Question.id == 4).one_or_none()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['categories'])
        self.assertEqual(data['total_categories'])

    def test_search(self):
        res = self.client().post('/questions/search', json={'searchTerm':'something'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quiz(self):
        res = self.app.post('/quizzes')
        data = dict(pre_question=[1,2,3], quiz_category=[1])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()