class Socket:
    __clients = {}
    __users = {}

    @staticmethod
    def add_client(client):
        user_id = getattr(client, 'user_id')
        if user_id:
            if client not in Socket.__clients:
                Socket.__clients[user_id] = client

    @staticmethod
    def del_client(client_or_user_id):
        if type(client_or_user_id) is int:
            try:
                del Socket.__clients[client_or_user_id]
                return True
            except:
                pass
        else:
            try:
                del Socket.__clients[client_or_user_id.user_id]
                return True
            except:
                pass
        return False

    @staticmethod
    def clients(user_id=None):
        if user_id is None:
            return Socket.__clients
        else:
            try:
                return Socket.__clients[user_id]
            except:
                return None
                # return getattr(Socket.__clients, user_id)

    @staticmethod
    def authorize(ws, data):
        if not getattr(ws, 'user_id', False):
            from app.models.User import User
            api_token = data.get('api_token')
            if api_token is not None and api_token:
                user = User.where('api_token', '=', api_token).first()
                if user is not None:
                    ws.user_id = user.id
                    Socket.__clients[user.id] = ws

    @staticmethod
    def is_logged_in(ws):
        if ws is not None and getattr(ws, 'user_id', False):
            return True
        return False

    @staticmethod
    async def update_last_connection(ws):
        from app.models.User import User
        if Socket.is_logged_in(ws):
            user = User.where('id', ws.user_id).first()
            if user is not None:
                user.update_last_connection()

# socket possible useful methods/properties
[
    'can_prepare',
    'can_start',
    'charset',
    'chunked',
    'close',
    'close_code',
    'closed',
    'compression',
    'content_length',
    'content_type',
    'cookies',
    'del_cookie',
    'drain',
    'enable_chunked_encoding',
    'enable_compression',
    'exception',
    'force_close',
    'headers',
    'keep_alive',
    'last_modified',
    'ping',
    'pong',
    'prepare',
    'prepared',
    'protocol',
    'reason',
    'receive',
    'receive_bytes',
    'receive_json',
    'receive_msg',
    'receive_str',
    'send_bytes',
    'send_json',
    'send_str',
    'set_cookie',
    'set_status',
    'set_tcp_cork',
    'set_tcp_nodelay',
    'start',
    'started',
    'status',
    'tcp_cork',
    'tcp_nodelay',
    'write',
    'write_eof'
]
