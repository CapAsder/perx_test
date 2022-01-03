import logging
import os

from flask import Flask, json, Blueprint
from flask_restful import Api

app = Flask(__name__)
handler = logging.FileHandler("app.log")
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
defaultFormatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(defaultFormatter)

errors = Blueprint('errors', __name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'very-secret-key')
USERNAME = os.environ.get('USERNAME', 'user')
app.config['USERNAME'] = USERNAME
PASSWORD = os.environ.get('PASSWORD', '*f62p2B"ES+*asA5')
app.config['PASSWORD'] = PASSWORD
TOKEN = os.environ.get('TOKEN', 'G9YNXXs6Y3fQJzPPmDwsRr7HzYDrTxnzLnmFEf98rFzch4MAKRpHmWPdSwVNzframD9ES9t')
app.config['TOKEN'] = TOKEN

app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', './uploads')
app.config['ALLOWED_EXTENSIONS'] = json.loads(os.environ.get('ALLOWED_EXTENSIONS', '["xls", "xlsx"]'))

app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', 'redis')
app.config['REDIS_PORT'] = os.environ.get('REDIS_PORT', '5001')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16Mb

api = Api(app, prefix='/api')

