import jwt
from config import CLIENT_SECRET
from app import kakao_collection

def generate_token(kakao_id):
    """카카오 ID를 사용하여 JWT 토큰 생성."""
    token = jwt.encode({'id': kakao_id}, CLIENT_SECRET, algorithm="HS256")
    return token.encode("utf-8").decode("utf-8")

def create_response_object(status, message, token):
    """상태와 메시지를 포함한 응답 객체 생성."""
    return {
        'status': status,
        'message': message,
        'Authorization': token
    }, 200 if status == 'success' else 201

def social_signin(profile_json):
    """소셜 로그인 처리 및 사용자 데이터베이스 작업."""
    kakao_account = profile_json.get("kakao_account", {})
    email = kakao_account.get("email")
    nickname = kakao_account.get("profile", {}).get("nickname")
    kakao_id = str(profile_json.get("id"))

    user_data = {
        'email': email,
        'nickname': nickname,
        'kakao_id': kakao_id
    }

    document = kakao_collection.find_one({'kakao_id': kakao_id})
    token = generate_token(kakao_id)

    if document is None:
        kakao_collection.insert_one(user_data)
        return create_response_object(
            'success',
            'Welcome! You have successfully registered.',
            token
        )
    else:
        return create_response_object(
            'already signed in',
            'You are already a member. Login successful.',
            token
        )
