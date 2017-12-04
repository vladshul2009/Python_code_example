# if field "social_to_user" is empty at first entry(signup user scenario)
# we will not save social user info into database table "users"

def _is_correct_val(val):
    if val is not None and type(val) is str:
        return True
    return False

def filter_google_plus_image(val):
    if _is_correct_val(val):
        val = val.split('?')[0]
    return val

def filter_twitter_first_name(val):
    if _is_correct_val(val):
        splited = val.split(' ')
        if len(splited) == 2:
            val = splited[0]
    return val

def filter_twitter_last_name(val):
    if _is_correct_val(val):
        splited = val.split(' ')
        if len(splited) == 1:
            val = None
        if len(splited) == 2:
            val = splited[1]
    return val

def filter_twitter_image(val):
    if _is_correct_val(val):
        val = val.replace('_normal.', '.')
    return val

config = {
    "socials": {
        # get test facebook oauth token: https://developers.facebook.com/tools/explorer/
        "facebook": {
            # fields: (our_db_field_name, fb_api_response_field_name)
            # if one param db and api fields are same
            "fields": [
                ('social_ident', 'id'),
                ('email',),
                ('first_name',),
                ('last_name',),
            ],
            "api_url": "https://graph.facebook.com/me?access_token=",
            # what we will write to users table when we signup using facebook?
            # social_table_field: user_table_field
            "social_to_user": {
                "first_name": "first_name",
                "last_name": "last_name"
            }
        },
        #lib used for twitter: https://github.com/bear/python-twitter
        "twitter": {
            "consumer_key": "eNDgqQzf8HhlDTvhPwgFg1GRz",
            "consumer_secret": "c5oF0QumW3j9xi5wbMDkAeVFBfhZOfcdSTi7YD05Ts1dmAvE91",
            "access_token": "807255816013287424-m3uTntgcPNz2sTVFrZ6kKmZomMWsINg",
            "access_token_secret": "EF0i65rEU4P1Mcya0LNDh3uHaLNKrxys2MqFoNDVjoNg6",
            "fields": [
                ('social_ident', 'id'),
                ('first_name', 'name', filter_twitter_first_name),
                ('last_name', 'name', filter_twitter_last_name),
                ('avatar', 'profile_image_url', filter_twitter_image),
                ('nickname',),
            ],
            "social_to_user": {
                "first_name": "first_name",
                "last_name": "last_name",
                "avatar": "photo",
                "nickname": "nickname"
            }
        },
        # get test google plus access token: https://developers.google.com/oauthplayground/
        "google_plus": {
            "api_url": "https://www.googleapis.com/plus/v1/people/me?access_token=",
            "fields": [
                ('social_ident', 'id'),
                ("first_name", "name.givenName"),
                ("last_name", "name.familyName"),
                ("avatar", "image.url", filter_google_plus_image),
            ],
            "social_to_user": {
                "first_name": "first_name",
                "last_name": "last_name",
                "avatar": "photo"
            }
        },
    },
}
