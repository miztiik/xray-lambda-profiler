# from wiki_search import flask_http_endpoint
from get_wiki_url import application

# Run the application
# gunicorn --bind 0.0.0.0:80 wsgi:application --access-logfile - --error-logfile - --capture-output --enable-stdio-inheritance

if __name__ == "__main__":
    application.run()
