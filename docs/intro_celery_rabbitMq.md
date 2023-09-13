
# Introduction to Celery

- Celery is an open-source distributed task queue system that is widely used for building asynchronous and distributed applications.
- It allows you to execute tasks (functions or methods) asynchronously, making it particularly useful for tasks that are time-consuming, computationally intensive, or need to be scheduled for future execution.

### Key features of Celery
- Task scheduling and execution.
- Distributed task processing with multiple worker nodes.
- Support for task prioritization and retries.
- Scalability for handling large workloads.
- Monitoring and management tools.

### Example
- Consider a Django package, it has many tasks running simultaneously.
- If we wait for one task to complete before picking the next one, it will significantly increase the page loading time.
- To avoid this, we can run the tasks in parallel. This can be achieved by using Celery.

![Celery Example](./celery_png.png)

### What we need to use Celery
- To use Celery we need a message transport, as Celery can only create messages and keep them ready to be transported.
- These transporters are called as Brokers, The RabbitMQ is the well known broker transports.


# Introduction to RabbitMQ
- RabbitMQ is an open-source message broker software that facilitates communication between different parts of a distributed system.
- It is a key component of many modern software architectures, particularly in systems where different parts need to exchange data and messages in a scalable and asynchronous manner.
- RabbitMQ is feature-complete, stable, durable, and easy to install. It’s an excellent choice for a production environment.

### Key features of RabbitMQ
- Reliability
- Flexible Routing
- Clustering
- Highly Available Queues
- Management UI

## Basic Concepts
![RabbitMQ Example](./rabbitMqCeleryExample.png)

- **Broker**: The Broker (RabbitMQ) is responsible for the creation of task queues, dispatching tasks to task queues according to some routing rules, and then delivering tasks from task queues to workers.
- **Consumer (Celery Workers)**: The Consumer is the one or multiple Celery workers executing the tasks. You could start many workers depending on your use case.
- **Result Backend**: The Result Backend is used for storing the results of your tasks. However, it is not a required element, so if you do not include it in your settings, you cannot access the results of your tasks.

## A simple Demo Project

Now let’s create a simple project to demonstrate the use of Celery.

**Step 1**: Install RabbitMQ by using the following commands
```
sudo apt-get install rabbitmq-server
```
**Note**: 
- Check the proper installation of RabbitMQ using the below command in terminal
```
rabbitmq-server
```
- If the above command didn't work, you can try script provide .[here](https://www.rabbitmq.com/install-debian.html#apt-quick-start-cloudsmith) to install RabbitMQ.

**Step 2**: Configure RabbitMQ for Celery, use the following commands.
```
rabbitmqctl add_user jimmy jimmy123
rabbitmqctl add_vhost jimmy_vhost
rabbitmqctl set_user_tags jimmy jimmy_tag
rabbitmqctl set_permissions -p jimmy_vhost jimmy ".*" ".*" ".*"
```
- The ".*" ".*" ".*" string at the end of the above command means that the user “jimmy” will have all configure, write and read permissions.
- To find more information about permission control in RabbitMQ, you can refer to http://www.rabbitmq.com/access-control.html.

**Step 3**:  Open new terminal and install Celery using pip
```
pip install celery
```
**Step 4**: Follow the below structure of our demo project
```
test_celery
    __init__.py
    celery.py
    tasks.py
    run_tasks.py
```
**Step 5**: Add the following code in celery.py
```
from __future__ import absolute_import
from celery import Celery

app = Celery('test_celery',
             broker='amqp://jimmy:jimmy123@localhost/jimmy_vhost',
             backend='rpc://',
             include=['test_celery.tasks'])
```
**Step 6**: In this file, we define our task longtime_add
```
from __future__ import absolute_import
from test_celery.celery import app
import time

@app.task
def longtime_add(x, y):
    print 'long time task begins'
    # sleep 5 seconds
    time.sleep(5)
    print 'long time task finished'
    return x + y
```
**Step 7**: After setting up Celery, we need to run our task, which is included in the runs_tasks.py
```
from .tasks import longtime_add
import time

if __name__ == '__main__':
    result = longtime_add.delay(1,2)
    # at this time, our task is not finished, so it will return False
    print 'Task finished? ', result.ready()
    print 'Task result: ', result.result
    # sleep 10 seconds to ensure the task has been finished
    time.sleep(10)
    # now the task should be finished and ready method will return True
    print 'Task finished? ', result.ready()
    print 'Task result: ', result.result
```
**Step 8**: Now, we can start Celery worker using the command below (run in the parent folder of our project folder test_celery)
```
celery -A test_celery worker --loglevel=info
```
**Step 9**: In another console, input the following (run in the parent folder of our project folder test_celery)
```
python -m test_celery.run_tasks
```

**Note**: We can use the follwing commands to know more about the arguments which can be used with celery

```
celery worker --help
celery help
```
### Monitor Celery in Real Time
- Flower is a real-time web-based monitor for Celery. Using Flower, you could easily monitor your task progress and history.
- We can use pip to install Flower
```
pip install flower
```
- To start the Flower web console, we need to run the following command (run in the parent folder of our project folder test_celery)
```
celery -A test_celery flower
```
- Flower will run a server with default port 5555, and you can access the web console at http://localhost:5555.
