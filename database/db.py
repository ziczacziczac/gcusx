from flask_mongoengine import MongoEngine

config = {
    'host': 'mongodb://localhost/clustering'
}
db = MongoEngine(config=config)


def initialize_db(app):
    db.init_app(app)