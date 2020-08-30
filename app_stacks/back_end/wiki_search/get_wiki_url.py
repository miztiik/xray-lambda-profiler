import json
import os
import wikipediaapi

from aws_xray_sdk.core import xray_recorder
from flask import Flask, redirect, render_template, request, url_for

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
# https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-middleware.html

# Create and configure the Flask application
application = Flask(__name__, instance_relative_config=True)
xray_recorder.configure(service='legacy_app_on_ec2', sampling=False)
XRayMiddleware(application, xray_recorder)


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    DEBUG_MODE = False
    # RENDER_HTML = False


@application.route('/')
def index():
    # return redirect('/api/Python_(programming_language)')
    return redirect('/home')


@application.route('/home/')
@application.route('/home/<needle>')
def home(needle='Mystique', RENDER_HTML=True):
    resp = get_wiki_data(needle=needle, RENDER_HTML=RENDER_HTML)
    return resp


@application.route('/api/<needle>')
def api(needle='Python_(programming_language)', RENDER_HTML=False):
    resp = get_wiki_data(needle=needle, RENDER_HTML=RENDER_HTML)
    return resp


def get_wiki_data(needle='Python_(programming_language)', RENDER_HTML=False):
    # resp = {'statusCode': 404, }
    pg_info = {'status': False}

    try:
        # AWS XRay Annotation
        xray_recorder.put_annotation("LEGACY_APP_ON_EC2", "BEGIN_PROCESSING")
        _wiki = wikipediaapi.Wikipedia('en')
        _wiki_page = _wiki.page(str(needle))

        if not _wiki_page.exists():
            print('Hell N0!')
            pg_info['ERROR'] = f'No information available for \'{needle}\'. Be the first person to create a wiki page for this topic.'
        else:
            pg_info['title'] = _wiki_page.title
            pg_info['summary'] = _wiki_page.summary[0:100]
            pg_info['url'] = _wiki_page.fullurl
            pg_info['status'] = True
            # AWS XRay Metadata
            xray_recorder.put_metadata('WIKI_QUERY_INFO', pg_info)
    except Exception as e:
        print(str(e))
        pg_info['ERROR'] = str(e)

    # Deliver as web page using HTML/CSS if NEEDED, set using global variable.
    if RENDER_HTML:
        return render_template("wiki_page.html",
                               _wiki_needle=str(needle),
                               _wiki_page_info=pg_info
                               )
    else:
        # return jsonify(pg_info)
        # return pg_info

        # Prep for API Gateway
        return {
            'statusCode': 200,
            'body': {'message': pg_info}
        }


if __name__ == '__main__':
    application.run(host=os.getenv('IP', '0.0.0.0'),
                    debug=global_args.DEBUG_MODE)
