from app.resources.Common.UsersCommon import UsersCommon
from flask import request, session
from flask_jwt_extended import create_access_token


class SignIn(UsersCommon):

    def post(self):
        try:
            login = request.json['login']
            password_request = self.to_hash(request.json['password'])
            result = self.__check_login_password_status(login, password_request)
            if result != "ok":
                return {'message': result}
            result_obj = self.create_token()
            return result_obj
        except Exception as e:
            print(e)
            return e

    def __check_login_password_status(self, login, password_request):
        sql = '''SELECT user_id, password, status, fake FROM users
                         WHERE login = %s
                        ;'''
        record = (login,)
        user_data = self.base_get_one(sql, record)
        if not user_data:
            return "Login does not exist"
        if not user_data['status']:
            return "You are not confirmed email address"
        if password_request != user_data['password']:
            return "Invalid Passport"
        if user_data['fake']:
            return "Your account is blocked"
        session['login'] = login
        session['user_id'] = user_data['user_id']
        print('user_id sign in: ', session['user_id'])
        return "ok"

    def create_token(self):
        access_token = create_access_token(identity=session['user_id'], expires_delta=False)
        result_obj = {
            'message': "ok",
            'access_token': access_token,
            'user_id': session['user_id']
        }
        return result_obj


    # forgot password
    def put(self):
        email = request.json['email']
        if not self.__check_email(email):
            return "Invalid Email"
        new_pass = self.__create_new_password()
        res = self.__add_new_password_to_db(new_pass, email)
        if res == 'error':
            return res
        from app.resources.loginPage.Email import Email
        res = Email.send_new_password(email, new_pass)
        return res

    def __check_email(self, email):
        sql = '''SELECT email FROM users
                 WHERE email = %s
                  ;'''
        record = (email,)
        user_email = self.base_get_one(sql, record)
        if user_email['email'] == email:
            return True
        return False

    def __create_new_password(self):
        import random
        password_string = "jkhTVY147"
        new_pass = ''.join(random.choice(password_string) for _ in range(12))
        return new_pass

    def __add_new_password_to_db(self, new_pass, email):
        password_hashed = self.to_hash(new_pass)
        sql = "UPDATE users SET password = %s WHERE email =%s;"
        record = (password_hashed, email)
        res = self.base_write(sql, record)
        return res

