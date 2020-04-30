# Imports
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView
# app initialization

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.debug = False
CORS(app, resources={r"*": {"origins": "*"}})

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Modules
db = SQLAlchemy(app)
# Models
class Version(db.Model):
    __tablename__  = 'versions'
    uuid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    number = db.Column(db.String(256), index=True, unique=True)
    note = db.Column(db.Text)

    def __repr__(self):
        return '<Version %r>' % self.name


# Schema Objects
class VersionObject(SQLAlchemyObjectType):
    class Meta:
        model = Version
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_versions = SQLAlchemyConnectionField(VersionObject)


class CreateVersion(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        number = graphene.String(required=True)
        note = graphene.String(required=False)

    version = graphene.Field(lambda: VersionObject)

    def mutate(self, info, name, number, note):
        version = Version(name=name, number=number, note=note)
        db.session.add(version)
        db.session.commit()
        return CreateVersion(version=version)


class Mutation(graphene.ObjectType):
    create_version = CreateVersion.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

# Routes
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)

@app.route("/")
def index():
    return '<p> Hello World</p>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
