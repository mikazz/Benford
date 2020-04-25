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

## What to do next?
* Implement better json DBMS (MongoDB)

## References
* [Redis](https://redis.io/)
* [RQ (Redis Queue): Simple job queues for Python](https://python-rq.org/)
* [PickleDB](https://pythonhosted.org/pickleDB/)

