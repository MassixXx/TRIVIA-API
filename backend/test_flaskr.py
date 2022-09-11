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
        if os.getenv('DATABASE_NAME') is None:
            os.environ['DATABASE_NAME'] = "trivia_test"
        if os.getenv('USER_NAME') is None:
            os.environ['USER_NAME'] = 'postgres'
        if os.getenv('USER_PASSWORD') is None:
            os.environ['USER_PASSWORD'] = 'postgres'
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(os.getenv('USER_NAME'),os.getenv('USER_PASSWORD'),'localhost', os.getenv('DATABASE_NAME'))
        
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
    def test_fail_get_categories(self):
        res = self.client().get("/categories?page=5")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(data['success'], False)
        
        

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
    
    def test_404_get_categories(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"],"resource not found")
    

    def test_get_questions_from_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["category"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])


  
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

    def test_404_delete(self):
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    

    def test_create_question(self):
        quest_count = Question.query.count()
        res = self.client().post('/questions',json={"question":"WHat is the capital of Algeria?","answer":"Algiers","category":4,"difficulty":2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(quest_count + 1 ,Question.query.count() )

    def test_fail_creation(self):
        res = self.client().post('/questions',json={"question":"WHat is the capital of Tunisia?","answer":"Tunis"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    
    def test_search_question(self):
        res = self.client().post('/questions',json={"search":"Taj Mahal"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data["questions"]),1)
        self.assertEqual(data['questions'][0]['question'],'The Taj Mahal is located in which Indian city?')

    def test_fail_search(self):
        res = self.client().post('/questions',json={"searchTerm":'Algeria'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    

    def test_get_question_quizz(self):
        res = self.client().post('/quizzes',json={'quiz_category':1,'previous_questions':[20,21]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(data["question"]['id'],22)

    def test_404_quizzes(self):
        res = self.client().post('/quizzes',json={'quiz_category':30,'previous_questions':[20,21]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()