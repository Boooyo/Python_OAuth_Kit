import requests
from flask import request, redirect, jsonify, make_response
from flask_restx import Namespace, Resource

from config import CLIENT_ID, REDIRECT_URI

oauth_api = Namespace(
    name='Kakaologin',
    description='API for Using Kakao login',
    path='/oauth/kakao'
)

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_PROFILE_URL = "https://kapi.kakao.com/v2/user/me"
KAKAO_LOGOUT_URL = "https://kauth.kakao.com/oauth/logout"

def get_kakao_token_url(code):
    return f"{KAKAO_TOKEN_URL}?grant_type=authorization_code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&code={code}"

def request_kakao_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.get(KAKAO_PROFILE_URL, headers=headers)

@oauth_api.route("/")
class KakaoSignIn(Resource):
    def get(self):
        kakao_oauth_url = f"{KAKAO_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
        return redirect(kakao_oauth_url)

@oauth_api.route("/callback")
class KakaoSignInCallback(Resource):
    def get(self):
        try:
            code = request.args.get("code")
            if not code:
                return make_response({"message": "MISSING_CODE"}, 400)

            token_request = requests.get(get_kakao_token_url(code))
            token_json = token_request.json()
            
            if 'error' in token_json:
                return make_response({"message": "INVALID_CODE"}, 400)

            access_token = token_json.get("access_token")
            if not access_token:
                return make_response({"message": "INVALID_TOKEN"}, 400)

            profile_request = request_kakao_profile(access_token)
            profile_json = profile_request.json()

        except requests.exceptions.RequestException:
            return make_response({"message": "KAKAO_API_ERROR"}, 500)

        from apis.oauthdb import social_signin
        return social_signin(profile_json)

@oauth_api.route('/signout')
class KakaoSignOut(Resource):
    def get(self):
        logout_url = f"{KAKAO_LOGOUT_URL}?client_id={CLIENT_ID}&logout_redirect_uri={REDIRECT_URI}"
        return redirect(logout_url)
