from flask_restx import Api, Resource, fields
from flask import Blueprint

api_bp = Blueprint('api', __name__)
api = Api(api_bp,
    title='Flask Server Manager API',
    version='1.0',
    description='API documentation for Flask Server Manager'
)

# API namespaces
ns_server = api.namespace('server', description='Server operations')
ns_user = api.namespace('user', description='User operations')
ns_monitoring = api.namespace('monitoring', description='Monitoring operations')

# Models
server_model = api.model('Server', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'host': fields.String(required=True),
    'port': fields.Integer(required=True),
    'status': fields.String(readonly=True),
    'last_active': fields.DateTime(readonly=True)
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'role': fields.String()
})

stats_model = api.model('SystemStats', {
    'cpu_percent': fields.Float(),
    'memory_percent': fields.Float(),
    'disk_usage': fields.Float()
})

# Server endpoints
@ns_server.route('/')
class ServerList(Resource):
    @api.doc('list_servers')
    @api.marshal_list_with(server_model)
    def get(self):
        """List all servers"""
        pass

    @api.doc('create_server')
    @api.expect(server_model)
    @api.marshal_with(server_model, code=201)
    def post(self):
        """Create a new server"""
        pass

@ns_server.route('/<int:id>')
class Server(Resource):
    @api.doc('get_server')
    @api.marshal_with(server_model)
    def get(self, id):
        """Get a server by ID"""
        pass

    @api.doc('update_server')
    @api.expect(server_model)
    @api.marshal_with(server_model)
    def put(self, id):
        """Update a server"""
        pass

    @api.doc('delete_server')
    def delete(self, id):
        """Delete a server"""
        pass

# User endpoints
@ns_user.route('/')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        pass

# Monitoring endpoints
@ns_monitoring.route('/stats')
class SystemStats(Resource):
    @api.doc('get_system_stats')
    @api.marshal_with(stats_model)
    def get(self):
        """Get system statistics"""
        pass