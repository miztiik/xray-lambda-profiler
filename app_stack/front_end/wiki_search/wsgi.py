# from wiki_search import flask_http_endpoint
from flask_http_endpoint import application

# Run the application
# gunicorn --bind 0.0.0.0:5000 wsgi:application

if __name__ == "__main__":
    application.run()
