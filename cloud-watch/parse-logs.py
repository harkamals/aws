'''
MIT License
Copyright (c) 2017 @harkamals

AWS Cloud Watch is an immensely powerful tool but comes with complexity, with filters and metrics, 
and especially when reading logs from other services.

For the current use-case, I was trying to watch for patterns in cloud watch log stream and subscribed to AWS Lambda 
function to take an action. It turned out to be hour long ordeal as I figured out the various 
layers of data encapsulation.

('Debug: Event received:', '{ "awslogs": {
"data": "H4sIAAAAAAAAAKWQ3WqDQBCFX0WWgi1YnP1fvRNqc5Ne6V0MYV03idQ/1CSUkHfv1qRPkMs5czjnm7mi1k6TPtj8Z7AoRh9Jnuy+0ixL
VikKUH/p7OhkQSXDWALnDDu56Q+rsT8NbhPqyxQ2ui0rHZ6GptfV+32627J5tLp1PgJYhoBDIOHmZZ3kaZZvjSFQckV1ZBSTWpXUVHvC93tjSiEIc
RHTqZzMWA9z3XefdTPbcULxBq2Xinv4ztXsLno2R4e6XVrTs+3mP+MV1ZUrpxRkJCLFQXJMCSOcCsGEwFRGyo2UEeCCUCIxBSK4AsWASXAAc+0eNO
vW3YqZopSxSFEAHvw/zsW/+kuhN1pj67OtYj/w/GtRdJ5XIGcpUOwRCLyH0ul2kQp01OO3bnVTILe6+W9Fh27Bc8z0KeYHw/b2C5sH1vcYAgAA"
}}')

Python has the native libraries to decode data format:
Base64 encoding > gzip compression > JSON > List > Dictionary > Key:Value pair
'''

import json
import gzip
from StringIO import StringIO

def lambda_handler(event, context):
    print('Hello: lambda log watcher')

    print('Debug: Event received:', json.dumps(event, indent=2))
    print('Debug: Context vars:  ', vars(context))

    event_data = str(event['awslogs']['data'])
    event_data = gzip.GzipFile(fileobj=StringIO(event_data.decode('base64', 'strict'))).read()
    event_data = json.loads(event_data)

    for e in event_data['logEvents']:
        print (json.dumps(e, indent=2))

    return 'Finished: lambda log watcher'
