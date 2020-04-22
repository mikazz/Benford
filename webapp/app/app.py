__author__ = "mikazz"
__version__ = "1.0"

from rq import Queue, Connection
from flask import Flask, request, jsonify, abort, send_file


import os
from flask import flash, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from redis import Redis
from webapp.app.jobs import run_benford_job


import zipfile
import io
import pathlib
import rq_dashboard
import csv

app = Flask(__name__)
app.secret_key = "secret key"

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# RQ Dashboard configuration
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

HOST = "127.0.0.1"
PORT = 5000
DEBUG = True


def allowed_file_ext(filename):
    """Return True if file extension of a file name is in ALLOWED_EXTENSIONS"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(uploaded_file):
    return True
    # try:
    #     with uploaded_file as csvfile:
    #         start = csvfile.read(4096)
    #
    #         # isprintable does not allow newlines, printable does not allow umlauts...
    #         if not all([c in string.printable or c.isprintable() for c in start]):
    #             return False
    #         dialect = csv.Sniffer().sniff(start)
    #         return True
    # except csv.Error:
    #     # Could not get a csv dialect -> probably not a csv.
    #     return False


# File appears not to be in CSV format; move along

@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file_ext(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')

            if allowed_file(file):
                flash('File Accepted')
                run_job()
                return redirect('/')
            else:
                flash(f"Incorrect file structure. Make sure it's valid delimited")
                return redirect(request.url)
        else:
            flash(f'Allowed file types are: {ALLOWED_EXTENSIONS}')
            return redirect(request.url)


#@app.route('/job', methods=['POST'])
def run_job():
    job_func_name = run_benford_job

    with Connection(connection=Redis()):
        q = Queue()
        job = q.enqueue(job_func_name, page_url=page_url, job_timeout=60)

    response_object = {
        'status': 'success',
        'data': {
            'job_id': job.get_id(),
            'job_func_name': job.func_name,
            'job_args': job.args,
            'job_kwargs': job.kwargs,
            'job_status_url': f"http://{HOST}:{PORT}/jobs/{job.get_id()}",
            'job_download_url': f"http://{HOST}:{PORT}/jobs/{job.get_id()}/download",
            'job_is_queued': job.is_queued,
            'job_enqueued_at': job.enqueued_at,
        }
    }
    return jsonify(response_object), 202  # ACCEPTED


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """
        Get single job status
        curl -X GET http://localhost:5000/jobs/7758ecb7-59db-40b0-8336-8a38e087e5b6
    """
    with Connection(connection=Redis()):
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
                'job_exc_info': job.exc_info,
                'job_dependent_ids': job.dependent_ids,
                'job_meta': job.meta,
                'job_status_url': f"http://{HOST}:{PORT}/jobs/{job.get_id()}",
                'job_download_url': f"http://{HOST}:{PORT}/jobs/{job.get_id()}/download",
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
    return jsonify(response_object)


@app.route('/jobs/<job_id>/download', methods=['GET'])
def get_job_download(job_id):

    with Connection(connection=Redis()):
        q = Queue()
        job = q.fetch_job(job_id)

    if not job.get_status() == "finished":
        abort(404)

    directory_name = job.kwargs.get("page_url")
    directory_name = url_to_page_name(directory_name)

    # if dir there is none so what?

    base_path = pathlib.Path(directory_name)
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=f'{directory_name}.zip'
    )


@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
        curl -X GET http://localhost:5000/jobs
    """
    with Connection(connection=Redis()):
        q = Queue()
        jobs = q.get_jobs()

    if jobs:
        response_object = {
            'status': 'success',
            'in_queue_jobs_number': str(len(q)),
            'jobs': str(jobs)
        }

    else:
        response_object = {
            'status': 'success',
            'queue_size': f'{len(q)}'
        }
    return jsonify(response_object)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
