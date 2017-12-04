config = {
    'get_one': {
        'user': {
            'field': 'id',
            'model': 'User:format_admin'
        }
    },
    'update_one': {
        'user': {
            'field': 'id',
            'model': 'User',
            'not_update': [
                'id', 'api_token', 'created_at', 'textsearchable_index_col', 'reset_pass_token'
            ],
            'key_filters': {
                # 'birthday': lambda x: x*2
            }
        }
    }
}
