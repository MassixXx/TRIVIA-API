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
        self.database_path = "postgres://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
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
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))

    def test_get_questions_from_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    """    
    # need more data in the db to test
    def test_get_questions_from_category_bad_page(self):
        res = self.client().get("/categories/1/questions?page=2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
    """

    def test_get_questions_unavailable_category(self):
        res = self.client().get("/categories/500/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    def test_get_questions_from_category_wrong_page(self):
        res = self.client().get("/categories/1/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    

    def test_delete_question(self):
        
        res = self.client().delete('/questions/24')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)

    def test_create_question(self):
        quest_count = Question.query.count()
        res = self.client().post('/questions',json={"question":"WHat is the capital of Algeria?","answer":"Algiers","category":4,"difficulty":2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data['questions'])
        self.assertEqual(quest_count + 1 ,Question.query.count() )

    def test_search_question(self):
        res = self.client().post('/questions',json={"search":"Taj Mahal"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data["questions"]),1)
        self.assertEqual(data['questions'][0]['question'],'The Taj Mahal is located in which Indian city?')

    def test_get_question_quizz(self):
        res = self.client().post('/quizzes',json={'quiz_category':1,'previous_questions':[20,21]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(data["question"]['id'],22)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()