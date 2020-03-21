import json
import os
import wikipediaapi

from aws_xray_sdk.core import xray_recorder
from flask import Flask, redirect, render_template, request, url_for, jsonify

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
# https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-middleware.html

# Create and configure the Flask application
application = Flask(__name__, instance_relative_config=True)
xray_recorder.configure(service='api_on_ec2', sampling=False)
XRayMiddleware(application, xray_recorder)


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = ''
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    DEBUG_MODE = False
    RENDER_HTML = False


@application.route('/')
def index():
    return redirect('/api/Python_(programming_language)')


@application.route('/api/<needle>')
def api(needle='Python_(programming_language)'):

    pg_info = {'status': False, }

    try:
        _wiki = wikipediaapi.Wikipedia('en')
        _wiki_page = _wiki.page(str(needle))

        if not _wiki_page.exists():
            print('Hell N0!')
            pg_info['ERROR'] = f'No information available for \'{needle}\''

        pg_info['title'] = _wiki_page.title
        pg_info['summary'] = _wiki_page.summary[0:100]
        pg_info['url'] = _wiki_page.fullurl
        pg_info['status'] = True

    except Exception as e:
        print(str(e))
        pg_info['ERROR'] = str(e)

    if global_args.RENDER_HTML:
        return render_template("wiki_page.html",
                               _wiki_needle=str(needle),
                               _wiki_page_info=pg_info
                               )
    else:
        return jsonify(pg_info)
        # return pg_info


if __name__ == '__main__':
    application.run(host=os.getenv('IP', '0.0.0.0'),
                    debug=global_args.DEBUG_MODE)