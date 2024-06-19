from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sock import Sock, ConnectionClosed

import os
from dotenv import load_dotenv
from config.db import Base





load_dotenv()

# App Config
app = Flask(__name__, )
app.config.from_object('config')
app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.getenv('DATABASE_URI'))
db = SQLAlchemy(app)
ma = Marshmallow(app)

sock = Sock(app)
CORS(app)


CL = '\x1b[0K'
BS = '\x08'

# print('checking metadata ...')
# print('Base Metadata: ', Base.metadata)
# print('db metadata: ', db.metadata)
# print('equality: ', db.metadata == Base.metadata)

# Database
from config import secret
app.secret_key = secret
migrate = Migrate(app, db)


# Controllers
from app.call.controller import bp as call_bp
app.register_blueprint(call_bp)

# Error handlers
from .error_handlers import *