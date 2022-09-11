from cgi import print_exception
import os
from traceback import print_stack
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    QUESTIONS_PER_SHELF = 10
    
    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_SHELF
        end = start + QUESTIONS_PER_SHELF
        questions = [question.format() for question in selection]
        current_quest = questions[start:end]

        return current_quest

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        return jsonify(
            {
                "success": True,
                "categories": {categorie.format()['id'] : categorie.format()['type'] for categorie in categories} ,
                "total_categories": len(categories),
            }
        )

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """ 

    @app.route('/questions')
    def get_questions():
        
        page = request.args.get("page", 1, type=int)
        questions = Question.query.order_by(Question.id).all()
        current_quest = paginate_questions(request,questions)
        category = Category.query.first()


        return jsonify(
            {
                "success" : True,
                "questions":current_quest,
                "total_questions" : len(questions),
                "current_category" : category.format()['type'],
                "categories" : {categorie.format()['id'] : categorie.format()['type'] for categorie in Category.query.order_by(Category.id).all()}
            }
        ) 
    

    """
    Create an endpoint to DELETE question using a question ID.
    """
    @app.route('/questions/<int:question_id>',methods = ['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify(
            {
                "success" : True
            }
        )

    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """

    @app.route('/questions',methods = ['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)        
        
        search = body.get("search", None)

        if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                ).all()
                current_quest = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_quest,
                        "total_questions": len(selection),
                    }
                )
        else:
            try:
                
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty= new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_quest = paginate_questions(request, selection)
                
            
                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "total_questions": len(Question.query.all()),
                    }
                )

            except:
                abort(422)

    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """



    """
    Create a GET endpoint to get questions based on category.
    """

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_from_category(category_id):
        page = request.args.get("page", 1, type=int)
        questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
        questions = paginate_questions(request,questions)
        category = Category.query.filter(Category.id == category_id).one_or_none()

        if len(questions) == 0 :
            abort(404)
        else:
            return jsonify(
                {
                    "success" : True,
                    "questions":questions,
                    "total_questions" : len(questions),
                    "category" : category.format()['type'],
                }
            ) 
  

    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """

    @app.route('/quizzes',methods=['POST'])
    def play_get_question():
        data = request.get_json()
        if data['quiz_category'] == 0:
            question = Question.query.filter(~Question.id.in_(data["previous_questions"])).order_by(func.random()).limit(1)
        else:
            question = Question.query.filter(Question.category == data['quiz_category']).filter(~Question.id.in_(data["previous_questions"])).order_by(func.random()).limit(1)
    
        current_quest = question.one_or_none()
        return jsonify(
            {
                "success" : True,
                "question" : current_quest.format() if question.one_or_none() else None,
            }
        )
        

   

    """
    Create error handlers for all expected errors including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app

