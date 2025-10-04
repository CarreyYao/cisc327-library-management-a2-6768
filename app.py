"""
Main Flask application entry point for the Library Management System.

This module provides the application factory pattern for creating Flask app instances.
Routes are organized in separate blueprint modules in the routes package.
"""

from flask import Flask
from database import init_database, add_sample_data
from routes import register_blueprints
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

def create_app():
    """
    Application factory function to create and configure Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    #@app.route('/')
    #def index():
    #    return "Welcome to the Library Management System"
        
    app.secret_key = "super secret key"
    
    # Initialize the database
    init_database()
    
    # Add sample data for testing and demonstration
    add_sample_data()
    
    # Register all route blueprints
    register_blueprints(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    Timer(1, open_browser).start()
    app.run(debug=False, host='127.0.0.1', port=5000)
