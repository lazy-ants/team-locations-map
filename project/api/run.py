import json
import smtplib
import jwt
import time
from eve import Eve
from eve.auth import TokenAuth
from os.path import dirname, abspath
from flask import Config, request, current_app, url_for, abort
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson.objectid import ObjectId
from cerberus import Validator
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Create a Flask Config object
config = Config(dirname(abspath(__file__)))

# Load your settings.py config file
config.from_pyfile('settings.py')

class TokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        try:
            user_info = confirm_token(token)
        except:
            return False
        dt = int(round(time.time() * 1000))
        if user_info and dt > user_info['iat'] and dt < user_info['exp']:
            if 'from_app' in user_info and user_info['from_app']:
                return True;
            accounts = current_app.data.driver.db['accounts']
            user = accounts.find({'email': user_info['email']})
            if user.count() > 0 and user[0] and user[0]['confirmed']:
                return True
            else:
                return False
        else:
            return False

def insert_hook(resource_name, items):
    auth = request.headers.get('Authorization');
    if (auth != None):
        token = auth.replace('Bearer ', '')
        try:
            user_info = confirm_token(token)
            account = user_info['id']
            for item in items:
                item['account'] = account
                strip_dictionary(item)
        except:
            return abort(401, 'Please provide proper credentials')

    return items

def update_hook(resource_name, item, original):
    auth = request.headers.get('Authorization');
    if (auth != None):
        token = auth.replace('Bearer ', '')
        try:
            user_info = confirm_token(token)
            account = user_info['id']
            if (original['account'] != account):
                return abort(401, 'You don\'t have an access to complete this action')
            
            strip_dictionary(item)
        except:
            return abort(401, 'Please provide proper credentials')

    return item

def replace_hook(resource_name, item):
    auth = request.headers.get('Authorization');
    if (auth != None):
        token = auth.replace('Bearer ', '')
        try:
            user_info = confirm_token(token)
            account = user_info['id']
            if (item['account'] != account):
                return abort(401, 'You don\'t have an access to complete this action')
            
            strip_dictionary(item)
        except:
            return abort(401, 'Please provide proper credentials')

    return item

def fetched_resource_hook(resource_name, response):
    auth = request.headers.get('Authorization');
    if (auth != None):
        token = auth.replace('Bearer ', '')
        try:
            user_info = confirm_token(token)
            account = user_info['id']
            for item in response['_items']:
                if (item['account'] != account):
                    return abort(401, 'You don\'t have an access to complete this action')
        except:
            return abort(401, 'Please provide proper credentials')

    for item in response['_items']:
        if 'account' in item:
            item.pop('account')

    return response

def fetched_item_hook(resource_name, response):
    auth = request.headers.get('Authorization');
    if (auth != None):
        token = auth.replace('Bearer ', '')
        try:
            user_info = confirm_token(token)
            account = user_info['id']
            if (response['account'] != account):
                return abort(401, 'You don\'t have an access to complete this action')
        except:
            return abort(401, 'Please provide proper credentials')

    if 'account' in response:
        response.pop('account')

    return response

def delete_item_hook(resource_name, item):
    auth = request.headers.get('Authorization');
    if (auth != None):
        token = auth.replace('Bearer ', '')
        try:
            user_info = confirm_token(token)
            account = user_info['id']
            if (item['account'] != account):
                return abort(401, 'You don\'t have an access to complete this action')
        except:
            return abort(401, 'Please provide proper credentials')

    return item

app = Eve(settings=config, auth=TokenAuth)
bcrypt = Bcrypt(app)
app.on_insert += insert_hook
app.on_update += update_hook
app.on_replace += replace_hook
app.on_fetched_resource += fetched_resource_hook
app.on_fetched_item += fetched_item_hook
app.on_delete_item += delete_item_hook

cors = CORS(app, resources={r"/register": {"origins": "*"}})
cors = CORS(app, resources={r"/confirm/*": {"origins": "*"}})
cors = CORS(app, resources={r"/login": {"origins": "*"}})
cors = CORS(app, resources={r"/refresh-token/*": {"origins": "*"}})
cors = CORS(app, resources={r"/forgot-password": {"origins": "*"}})
cors = CORS(app, resources={r"/reset-password": {"origins": "*"}})

def generate_confirmation_token(data):
    with open('app.config.json') as config_file:
        config_file = json.load(config_file)
    
    return jwt.encode(data, config_file['secret_word'], algorithm='HS256').decode('utf-8')

def confirm_register_token(token):
    with open('app.config.json') as config_file:
        config_file = json.load(config_file)
    try:
        user_info = jwt.decode(token, config_file['secret_word'], algorithms=['HS256'])
        if (user_info['type'] != 'register'):
            return abort(400, 'Invalid token')    
    except:
        return abort(400, 'Invalid token')
    return user_info

def confirm_forgot_password_token(token):
    with open('app.config.json') as config_file:
        config_file = json.load(config_file)
    try:
        user_info = jwt.decode(token, config_file['secret_word'], algorithms=['HS256'])
        if (user_info['type'] != 'forgot-password'):
            return abort(400, 'Invalid token')    
    except:
        return abort(400, 'Invalid token')
    return user_info

def confirm_token(token):
    with open('app.config.json') as config_file:
        config_file = json.load(config_file)
    try:
        user_info = jwt.decode(token, config_file['secret_word'], algorithms=['HS256'])
        if (user_info['type'] != 'login'):
            return abort(400, 'Invalid token')    
    except:
        return abort(400, 'Invalid token')

    return user_info

def send_email(To, From, Subj, Msg):
    with open('app.config.json') as config_file:
        config_file = json.load(config_file)

    msg = MIMEMultipart()
    msg['From'] = From
    msg['To'] = To
    msg['Subject'] = Subj
    msg.attach(MIMEText(Msg, 'plain'))

    server = smtplib.SMTP(
        config_file['email_config']['mailer_host'], config_file['email_config']['mailer_port'])
    server.starttls()
    server.login(
        From, config_file['email_config']['mailer_password'])
    text = msg.as_string()
    server.sendmail(From, To, text)
    server.quit()

def validateRegister(req):
    validator = Validator(
        {
            'email': {'type': 'string', 'minlength': 4, 'required': True},
            'password': {'type': 'string', 'minlength': 5, 'required': True}
        },
    )
    validator.allow_unknown = False
    valid = validator.validate(req.json)
    if (valid != True):
        return abort(400, 'Bad request')

@app.route('/register', methods=['GET', 'POST', 'OPTIONS'])
def register():
    if (request.method == 'OPTIONS'):
        return 'Good'
    if request.method == 'POST':
        validateRegister(request)
        accounts = app.data.driver.db['accounts']
        count = accounts.find({'email': request.json['email']}).count()
        
        if count == 0:
            account = accounts.insert_one({
                'email': request.json['email'],
                'confirmed': False,
                'password': bcrypt.generate_password_hash(request.json['password'])
            })

            iat = int(round(time.time() * 1000))
            exp = int(round(time.time() * 1000)) + 15 * 60 * 1000
            token = generate_confirmation_token({'type': 'register', 'email': request.json['email'], 'id': str(account), 'iat': iat, 'exp': exp})

            with open('app.config.json') as config_file:
                config_file = json.load(config_file)

            send_email(
                request.json['email'],
                config_file['email_config']['mailer_user'],
                'Lazy Ants - Team locations map. Please confirm your email',
                config_file['admin_url'] + '/#/confirm/' + token
            )
            return 'A confirmation link has been sent to your email address'
        else:
            return 'Account already exists'
        return abort(401, 'Invalid method')


@app.route('/confirm/<token>', methods=['GET', 'OPTIONS'])
def confirm_email(token):
    if (request.method == 'OPTIONS'):
        return 'Good'
    user_info = confirm_register_token(token)
    dt = int(round(time.time() * 1000))
    if user_info and dt > user_info['iat'] and dt < user_info['exp']:
        accounts = app.data.driver.db['accounts']
        user = accounts.find({'email': user_info['email']})[0]
        if user['confirmed']:
            return abort(401, 'Invalid token')
        else:
            accounts.update_one({'_id': user['_id']}, {'$set': {'confirmed': True}})
            return 'Account successfully confirmed'
    else:
        return abort(401, 'Invalid token')

def validateLogin(req):
    loginValidator = Validator(
        {
            'email': {'type': 'string', 'minlength': 4, 'required': True},
            'password': {'type': 'string', 'minlength': 5, 'required': True}
        },
    )
    loginValidator.allow_unknown = False
    valid = loginValidator.validate(req.json)
    if (valid != True):
        return abort(400, 'Bad request')

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if (request.method == 'OPTIONS'): 
        return 'Good'
    validateLogin(request)
    accounts = app.data.driver.db['accounts']
    user = accounts.find({'email': request.json['email']})
    if user.count() > 0:
        user = user[0]
        if user['confirmed']:
            if bcrypt.check_password_hash(user['password'], request.json['password']):  
                iat = int(round(time.time() * 1000))
                exp = int(round(time.time() * 1000)) + 60 * 60 * 1000
                token = generate_confirmation_token({'type': 'login', 'email': request.json['email'], 'id': str(user['_id']), 'iat': iat, 'exp': exp});
                return json.dumps({
                    'token': token
                })
            else:
                return abort(401, 'Password is not correct')
        else:
            return abort(401, 'Please confirm your account')
    else:
        return abort(401, 'Account was not found')


@app.route('/refresh-token/<token>',  methods=['GET', 'OPTIONS'])
def refreshToken(token):
    if (request.method == 'OPTIONS'):
        return 'Good'
    try:
        user_info = confirm_token(token)
    except:
        return abort(401, 'Bad credentials')
    dt = int(round(time.time() * 1000))
    if user_info and dt > user_info['iat'] and dt < user_info['exp']:
        user_info['iat'] = dt
        user_info['exp'] = dt + 60 * 60 * 1000
        newToken = generate_confirmation_token({'type': 'login', 'email': user_info['email'], 'id': user_info['id'], 'iat': user_info['iat'], 'exp': user_info['exp']})
        return json.dumps({'token': newToken})
    else:
        return abort(401, 'Bad credentials')

def strip_dictionary(d):
    """
    Recursively remove whitespace from values in dictionary 'd'
    """
    for key, value in d.items():
        if ' ' in key:
            d[key] = value
            del d[key]
        if isinstance(value, dict):
            strip_dictionary(value)
        elif isinstance(value, list):
            d[key] = [x.strip() for x in value]
        elif isinstance(value, str):
            d[key] = value.strip()

def validateForgotPassword(req):
    validator = Validator({'email': {'type': 'string', 'minlength': 4, 'required': True}})
    validator.allow_unknown = False
    valid = validator.validate(req.json)
    if (valid != True):
        return abort(400, 'Bad request')

@app.route('/forgot-password', methods=['OPTIONS', 'POST'])
def forgot_password():
    if (request.method == 'OPTIONS'):
        return 'Good'
    validateForgotPassword(request);
    accounts = app.data.driver.db['accounts']
    user = accounts.find_one({'email': request.json['email']})
    if (user == None):
        return abort(401, 'User not found')

    iat = int(round(time.time() * 1000))
    exp = int(round(time.time() * 1000)) + 15 * 60 * 1000
    token = generate_confirmation_token(
        {
            'type': 'forgot-password',
            'email': request.json['email'],
            'id': str(user['_id']),
            'iat': iat,
            'exp': exp
        }
    )

    with open('app.config.json') as config_file:
        config_file = json.load(config_file)

    Msg = "Here's your reset password link: " + \
        config_file['admin_url'] + \
        '/#/reset-password/' + token

    send_email(
        request.json['email'],
        config_file['email_config']['mailer_user'],
        'Lazy Ants - Team locations map - Reset Password',
        Msg
    )
    return 'A reset password link has been sent to your email address'

def validateResetPassword(req):
    validator = Validator(
        {
            'password': {'type': 'string', 'minlength': 5, 'required': True},
            'token': {'type': 'string', 'minlength': 4, 'required': True}
        },
    )
    validator.allow_unknown = False
    valid = validator.validate(req.json)
    if (valid != True):
        return abort(400, 'Bad request')

@app.route('/reset-password', methods=['OPTIONS', 'POST'])
def reset_password():
    if (request.method == 'OPTIONS'):
        return 'Good'
    validateResetPassword(request)
    try:
        user_info = confirm_forgot_password_token(request.json['token'])
    except:
        return abort(401, 'Bad credentials')

    accounts = app.data.driver.db['accounts']
    user = accounts.find_one({'_id': ObjectId(user_info['id'])})
    if (user == None):
        return abort(401, 'User not found')

    accounts.update_one(
        {
            '_id': user['_id']
        },
        { 
            '$set': {
                'password': bcrypt.generate_password_hash(request.json['password']) 
            }
        }
    )
    iat = int(round(time.time() * 1000))
    exp = int(round(time.time() * 1000)) + 60 * 60 * 1000
    return json.dumps({'token': generate_confirmation_token({'type': 'login', 'email': user['email'], 'id': str(user['_id']), 'iat': iat, 'exp': exp})})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
