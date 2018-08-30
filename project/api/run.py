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
    for item in items:
        strip_dictionary(item)
    return items

def update_hook(resource_name, item, original):
    strip_dictionary(item)
    return item

def replace_hook(resource_name, item, original):
    strip_dictionary(item)
    return item


app = Eve(settings=config, auth=TokenAuth)
bcrypt = Bcrypt(app)
app.on_insert += insert_hook
app.on_update += update_hook
app.on_replace += replace_hook

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

def confirm_token(token):
    with open('app.config.json') as config_file:
        config_file = json.load(config_file)
    try:
        user_info = jwt.decode(token, config_file['secret_word'], algorithms=['HS256'])
    except:
        return abort(200, 'Invalid token')
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
            account = accounts.insert({
                'email': request.json['email'],
                'confirmed': False,
                'password': bcrypt.generate_password_hash(request.json['password'])
            })
            iat = int(round(time.time() * 1000))
            exp = int(round(time.time() * 1000)) + 3600 * 1000
            token = generate_confirmation_token({'email': request.json['email'], 'iat': iat, 'exp': exp})

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
    user_info = confirm_token(token)
    dt = int(round(time.time() * 1000))
    if user_info and dt > user_info['iat'] and dt < user_info['exp']:
        accounts = app.data.driver.db['accounts']
        user = accounts.find({'email': user_info['email']})[0]
        if user['confirmed']:
            return json.dumps({
                'token': token,
                'accountId': str(user['_id'])
            })
        else:
            updated_account = accounts.update_one({'_id': user['_id']}, {'$set': {'confirmed': True}})
            if updated_account['updatedExisting']:
                return json.dumps({'token': token, 'accountId': user['_id']})
            else:
                return 'Error'
    else:
        return abort(401, '<Invalid token>')

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
                exp = int(round(time.time() * 1000)) + 3600 * 1000
                token = generate_confirmation_token({'email': request.json['email'], 'iat': iat, 'exp': exp});
                return json.dumps({
                    'token': token,
                    'accountId': str(user['_id'])
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
        user_info['exp'] = dt + 3600 * 1000
        newToken = generate_confirmation_token({'email': user_info['email'], 'iat': user_info['iat'], 'exp': user_info['exp']})
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
    exp = int(round(time.time() * 1000)) + 3600 * 1000
    token = generate_confirmation_token(
        {
            'email': request.json['email'],
            'iat': iat,
            'exp': exp
        }
    )

    with open('app.config.json') as config_file:
        config_file = json.load(config_file)

    Msg = "Here's your reset password link: " + \
        config_file['admin_url'] + \
        '/#/reset-password/' + str(user['_id']) + '/' + token

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
            'newPassword': {'type': 'string', 'minlength': 5, 'required': True},
            'newPasswordConfirm': {'type': 'string', 'minlength': 5, 'required': True},
            'token': {'type': 'string', 'minlength': 4, 'required': True},
            'userId': {'type': 'string', 'minlength': 4, 'required': True}
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
        user_info = confirm_token(request.json['token'])
    except:
        return abort(401, 'Bad credentials')

    if (request.json['newPassword'] != request.json['newPasswordConfirm']):
        return abort(400, 'Password does not match')

    accounts = app.data.driver.db['accounts']
    objectId = ObjectId(request.json['userId']);
    user = accounts.find_one({'_id': objectId})
    if (user == None):
        return abort(401, 'User not found')

    accounts.update_one(
        {
            '_id': objectId
        },
        { 
            '$set': {
                'password': bcrypt.generate_password_hash(request.json['newPassword']) 
            }
        }
    )
    iat = int(round(time.time() * 1000))
    exp = int(round(time.time() * 1000)) + 3600 * 1000
    return json.dumps(generate_confirmation_token({'email': user['email'], 'iat': iat, 'exp': exp}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
