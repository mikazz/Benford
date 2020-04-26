__author__ = "mikazz"
__version__ = "1.0"

from pymongo import MongoClient

from rq import Queue, Connection
import rq_dashboard
from redis import Redis

from flask import Flask, request, jsonify, abort, send_from_directory
from flask import flash, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from jobs import run_benford_job
from file_utils import create_directory_name, is_allowed_file

import os
import shutil

app = Flask(__name__)
app.secret_key = "install-gentoo"

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# RQ Dashboard configuration
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

#HOST = "0.0.0.0"
#PORT = 5000
#DEBUG = False

# MONGO DATABASE CONFIGURATION (Jobs and Results databases)

# Connecting to MongoDB
client = MongoClient('mongodb', 27017)
# Getting a Database
db = client['app']

# Create Collections
if not db['result_collection']:
    db.create_collection("result_collection")
else:
    result_collection = db['result_collection']

if not db['jobs_collection']:
    db.create_collection("jobs_collection")
else:
    jobs_collection = db['jobs_collection']


def allowed_file_ext(filename):
    """Return True if file extension of a file name is in ALLOWED_EXTENSIONS"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file_ext(file.filename):
            filename = secure_filename(file.filename)

            directory_name = create_directory_name()
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], directory_name))

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], directory_name, filename)
            file.save(file_path)
            flash('File successfully uploaded')

            file_ok, log_message = is_allowed_file(file_path)

            if file_ok:
                flash('File Accepted')

                # Lets start a Redis Job
                response = run_job(directory_name)
                job_id = response.json["data"]["job_id"]
                # And Let's wait for the results in 'waiting room' page
                return redirect(url_for('get_job', job_id=job_id))

            else:
                flash("Incorrect file structure.")
                flash(log_message)
                shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'], directory_name))
                return redirect(request.url)
        else:
            flash(f"Allowed file types are: {', '.join(ALLOWED_EXTENSIONS)}")
            return redirect(request.url)


@app.route('/job/<directory_name>', methods=['POST'])
def run_job(directory_name):
    job_function_name = run_benford_job

    with Connection(connection=Redis(host="redis")):
        q = Queue()
        job = q.enqueue(job_function_name, directory_name=directory_name, job_timeout=60)

    # We need to Save Redis Job details to DB (they disappear after 500 seconds)
    post = {"key": job.get_id(), "data": directory_name}
    jobs_collection.insert_one(post)

    response_object = {
        'status': 'success',
        'data': {
            'job_id': job.get_id(),
            'job_func_name': job.func_name,
            'job_args': job.args,
            'job_kwargs': job.kwargs,
            'job_is_queued': job.is_queued,
            'job_enqueued_at': job.enqueued_at,
        }
    }
    return jsonify(response_object)


@app.route('/job/<job_id>')
def get_job(job_id):

    with Connection(connection=Redis(host="redis")):
        q = Queue()
        job = q.fetch_job(job_id)
    if job:
        response_object = {
            'data': {
                'job_id': job.get_id(),
                'job_status': job.get_status(),
                'job_result': job.result,
                'job_is_started': job.is_started,
                'job_started_at': job.started_at,
                'job_is_queued': job.is_queued,
                'job_timeout': job.timeout,
                'job_enqueued_at': job.enqueued_at,
                'job_ended_at': job.ended_at,
                'job_func_name': job.func_name,
                'job_args': job.args,
                'job_kwargs': job.kwargs,
            }
        }

        if job.is_failed:
            response_object = {
                'status': 'failed',
                'data': {
                    'job_id': job.get_id(),
                    'job_status': job.get_status(),
                    'job_result': job.result,
                    'message': job.exc_info.strip().split('\n')[-1]
                }
             }
    else:
        response_object = {
            'status': 'ERROR: Unable to fetch the job from RQ'
        }

    # Retrieve directory id by providing known job id
    directory_name = jobs_collection.find_one({"key": job_id})

    # If there is no such directory yet
    if not directory_name:
        abort(404)
    directory_name = directory_name['data']

    image_filename = f"{directory_name}.png"

    json_result = result_collection.find_one({"key": directory_name})

    if json_result:
        observed_counts = json_result["data"]["observed_counts"]
        expected_counts = json_result["data"]["expected_counts"]
        first_digit_probabilities = json_result["data"]["first_digit_probabilities"]
        chi_squared_test_statistic = json_result["data"]["chi-squared_test_statistic"]
        result = json_result["data"]["result"]
    else:
        observed_counts = None
        expected_counts = None
        first_digit_probabilities = None
        chi_squared_test_statistic = None
        result = None

    return render_template('job.html', job=response_object, image_name=image_filename,
                           observed_counts=observed_counts,
                           expected_counts=expected_counts, first_digit_probabilities=first_digit_probabilities,
                           chi_squared_test_statistic=chi_squared_test_statistic, result=result)


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs_list = jobs_collection.find()

    jobs = []
    for job in jobs_list:
        jobs.append(job)

    jobs_list = [job["key"] for job in jobs if "key" in job]  # that's nice
    return render_template('jobs.html', jobs=list(jobs_list))


if __name__ == '__main__':
    app.run()
