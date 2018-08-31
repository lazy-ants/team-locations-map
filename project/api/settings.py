import json
import jwt
from bson.son import SON
from flask import current_app as app
from run import TokenAuth

with open('db.config.json') as config:
    config = json.load(config)

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_URI = 'mongodb://' + config['MONGO_USERNAME'] + ':' + config['MONGO_PASSWORD'] + '@' + config['MONGO_HOST'] + ':' + config['MONGO_PORT']

MONGO_DBNAME = config['MONGO_DBNAME']

X_DOMAINS = '*'
IF_MATCH = False
X_HEADERS = ['Authorization', 'Content-Type', 'If-Match']

# Enable reads (GET), inserts (POST) for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST']

# Enable reads (GET), edits (PATCH) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

markers = {
    'authentication': TokenAuth,
    'public_methods': ['GET'],
    'public_item_methods': ['GET'],
    
    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    'schema': {
        # Schema definition, based on Cerberus grammar. Check the Cerberus project
        # (https://github.com/pyeve/cerberus) for details.
        'username': {
            'type': 'string',
            'required': True,
        },
        'workPosition': {
            'type': 'string',
        },
        'email': {
            'type': 'string',
        },
        'skype': {
            'type': 'string',
        },
        'bio': {
            'type': 'string',
        },
        'avatar': {
            'type': 'string',
            'required': True,
        },
        'location': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string'
                },
                'lat': {
                    'type': 'number'
                },
                'lng': {
                    'type': 'number'
                },
            },
            'required': True,
        },
    },
}

accounts = {
    'schema': {
        'email': {
            'type': 'string',
            'required': True,
            'regex': '^\S+@\S+$',
            'unique': True,
        },
        'password': {
            'type': 'string',
            'required': True,
        },
        'confirmed': {
            'type': 'boolean',
            'default': False,
            'required': True,
        }
    }
}

schemas = {
    'markers': markers
}

for attr, value in schemas.items():
    print(attr, value)
    schemas[attr]['schema'].update({
        'account': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'accounts',
                'embeddable': True
            }
        }
    })
    schemas[attr].update({
        'mongo_indexes': {
            'account': [('account', 1)]
        }
    })

DOMAIN = schemas
