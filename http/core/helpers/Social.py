import urllib.request
import json
#from core.config.social import config as social_config
import twitter
from core.helpers.Config import Config

social_config = Config.get('socials', 'social')

class Social:

    @staticmethod
    def get_user(social_alias, token, params=None):
        social_keys = Social.get_socials()
        if social_alias in social_keys:
            if social_alias == 'twitter':
                # here get:
                # 1. Access Token
                # 2. Access Token Secret
                access_token = social_config['twitter']['access_token']
                access_token_secret = social_config['twitter']['access_token_secret']
                if params is not None and params.get('secret'):
                    return Social.__get_twitter_data(token, params.get('secret'), params)
                else:
                    raise Exception('Parameter secret is requried for twitter.')

            else:
                return Social.__get_user_data(social_alias, token)
        else:
            raise Exception('Unknown social network "' + social_alias + '". Supported networks: ' + str(social_keys))

    @staticmethod
    def __get_user_data(social_alias, access_token):
        api_url = social_config[social_alias]['api_url']
        try:
            return Social.__get_url_data(api_url + access_token)
        except Exception:
            return None

    @staticmethod
    def __get_twitter_data(access_token_key, access_token_secret, params=None):
        consumer_key = social_config['twitter']['consumer_key']
        consumer_secret = social_config['twitter']['consumer_secret']
        api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token_key,
                          access_token_secret=access_token_secret)
        try:
            # result = api.GetUser()
            result = api.VerifyCredentials()
            return json.JSONDecoder().decode(str(result))
        except twitter.error.TwitterError:
            # error invalid_oauth2_token (if None)
            return None

        # if params is not None and type(params) is dict:
        #     username = params.get('username')
        #     if username is not None:
        #         try:
        #             # creates object User
        #             # if user not found throws exception
        #             # https://github.com/bear/python-twitter/blob/master/twitter/models.py
        #             result = api.GetUser(screen_name=username)
        #             return json.JSONDecoder().decode(str(result))
        #         except twitter.error.TwitterError:
        #             # error invalid_oauth2_token (if None)
        #             return None
        #     else:
        #         raise Exception('Parameter username is required.')
        # else:
        #     raise Exception('Parameter username is required.')

    @staticmethod
    def __get_url_data(url, headers={'Accept': 'application/json'}):
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            response = json.loads(response.read().decode('utf-8'))
            return response

    @staticmethod
    def get_socials():
        return social_config.keys()

    @staticmethod
    def get_social_fields(name):
        return social_config[name]['fields']

    @staticmethod
    def get_config():
        return social_config
