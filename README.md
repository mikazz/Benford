# Benford
 
 ## Main

* User input validation and protection
* The preferred form of asynchronous execution - a separate worker that could potentially work on another machine 
and some kind of communication system between them (e.g. through RabbitMQ or Redis).
* The solution should include automatic tests.
* Tests should be written in some test framework, e.g. built-in unittest or pytest, and should be run independently.
* Starting the microservice should be maximally automated (Docker).

## Goal

* Goal is to create a python-based web application, that can ingest flat file with a viable target column, and do some
computations over it.
* Because files can be any length, the computations can also be very long.
* Because of such reason we need some sort of asynchronous execution of our code, so that our users would be allowed to 
see what's happening with their order (stopped?, running?, done?).
* I'm using Redis to meet this requirement. It's a message broker. Our application will send him a basic task 
information. And job (computations) will be executed by separate worker(s). Each worker will process a single job
at a time. Within a worker, there is no concurrent processing going on, so if we want to perform more jobs concurrently,
we simply have to start more workers (scalability).

## Running
Check docker-compose.yml

Windows (without docker):
* Manually run app: webapp/app/app.py
* Manually run worker: webapp/app/worker.py
* Run Redis Server: _Redis-x64-3.2.100/redis-server.exe
* Run MongoDB server.exe

## References
* [Redis](https://redis.io/)
* [RQ (Redis Queue): Simple Redis job queues management for Python](https://python-rq.org/)
* [MongoDB](https://www.mongodb.com/)
* [PyMongo: MongoDB Connector](https://pymongo.readthedocs.io/en/stable/)
* [rq_dashboard: Dashboard for RQ Stats](https://github.com/Parallels/rq-dashboard)
* [flask_testing: Easy testing for flask](https://pythonhosted.org/Flask-Testing/)

## Log
* v1.00 Release 26-04-2020