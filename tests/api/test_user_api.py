from app.dao.mysql import db
from app.models.user import User
from tests import helpers
from app.utils import errors
from tests import constants


class TestUser:

    def setup_method(self):
        user = db.session.query(User).filter(User.email == 'zhangsan@tzcpa.com')
        user.delete()

    def teardown_method(self):
        if getattr(self, 'user_id', None) is not None:
            user = db.session.query(User).filter(User.user_id == self.user_id).first()
            db.session.delete(user)
            db.session.commit()

    def check_user(self, data, action='create'):
        assert data.get("user_id") == self.user_id
        assert data.get("email") == "zhangsan@tzcpa.com"
        if action == 'create':
            assert data.get("telephone") == "+8612345678901"
            assert data.get("user_name") == "customer1"
            assert data.get("contact_person") == "张三"
            assert data.get("address") == "北京市海淀区"
        elif action == 'update':
            assert data.get("telephone") == "01123456789"
            assert data.get("address") == "北京市海淀区修改一"
            assert data.get("user_name") == "customer修改1"
            assert data.get("contact_person") == "张三修改1"

    def test_workflow(self, client):
        email = 'zhangsan@tzcpa.com'
        password1 = 'PWDzhangsan1#'
        password2 = 'PWDzhangsan1~'
        # 创建用户
        raw_body = {
            'user_name': 'customer1',
            'password': password1,
            'contact_person': '张三',
            'address': '北京市海淀区',
            'email': email,
            'telephone': '+8612345678901'
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        path = '/api/v1/ad/users'
        rv = client.post(path, json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='get')
        data = res.get('data')
        assert data, res
        user_id = data.get("user_id")
        assert isinstance(user_id, int), data
        self.user_id = user_id
        self.check_user(data)

        # 登录
        for raw_body in [{'telephone': '+8612345678901', 'password': password1},
                         {'email': email, 'password': password1}, {'user_id': user_id, 'password': password1}]:
            headers, body = helpers.format_headers_and_body(raw_body)
            path = '/api/v1/users/login'
            rv = client.post(path, json=body, headers=headers)
            res = helpers.validate_resp(rv, path=path, method='get')
            data = res.get('data')
            assert data, res
            token = data.get('token')

        # 修改1
        raw_body = {
            'email': email,
            'password': password2,
            'address': '北京市海淀区修改一',
            'user_name': 'customer修改1',
            'contact_person': '张三修改1',
            'telephone': '01123456789'
        }
        headers, body = helpers.format_headers_and_body(raw_body, token=token, auth_method='token')
        path = f'/api/v1/users/{user_id}'
        rv = client.post(path, json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='post')
        data = res.get('data')
        assert isinstance(data, dict), rv.json
        self.check_user(data, action='update')

        # 修改2
        raw_body = {
            'email': email,
            'password': password2,
            'address': '北京市海淀区修改一',
            'user_name': 'customer修改1',
            'contact_person': '张三修改1',
            'telephone': '01123456789'
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post(f'/api/v1/ad/users/{user_id}', json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='post')
        data = res.get('data')
        assert isinstance(data, dict), rv.json
        self.check_user(data, action='update')

        # list
        params = {
            'create_date_start': constants.YESTERDAY.strftime('%Y-%m-%d'),
            'create_date_end': constants.TOMORROW.strftime('%Y-%m-%d'),
            'page': 1,
            'per_page': 100000000,
            'user_state': 'active',
        }
        headers1, _ = helpers.format_headers_and_body()
        headers2, _ = helpers.format_headers_and_body(params=params)
        path1 = f'/api/v1/ad/users'
        path2 = f'/api/v1/ad/users' + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        for path, _headers in [(path1, headers1), (path2, headers2)]:
            rv = client.get(path, headers=_headers)
            res = helpers.validate_resp(rv, path=path, method='get')
            data = res.get('data')
            assert data, res
            users = data.get('users')
            assert isinstance(users, list), data
            for user in users:
                if user.get('user_id') == user_id:
                    self.check_user(user, action='update')
                    break
            else:
                assert 0, data

        # 查询用户信息
        headers, _ = helpers.format_headers_and_body()
        path = f'/api/v1/ad/users/{user_id}'
        rv = client.get(path, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='get')
        data = res.get('data')
        assert data, res
        self.check_user(user, action='update')

        api_key = data.get("api_key")
        secret_key = data.get("secret_key")
        # api/v1
        headers, _ = helpers.format_headers_and_body(auth_method='ak', ak=api_key, sk=secret_key)
        path = f'/api/v1/users/{user_id}'
        rv = client.get(path, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='get')
        data = res.get('data')
        assert data, res
        self.check_user(user, action='update')

    def test_creation_400(self, client):
        raw_body = {
            'user_name': 'customer1',
            'contact_person': '张三',
            'address': '北京市海淀区',
            'email': 'zhangsan@tzcpa.com',
            'telephone': '+8612345678901'
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post('/api/v1/ad/users', json=body, headers=headers)
        assert rv.status_code == 200, (rv.status_code, rv.data)
        assert rv.is_json, str(rv.data)
        assert isinstance(rv.json, dict), rv.json
        assert rv.json.get('return_code') == errors.ErrorCode.DataParamError.value, rv.json
        assert rv.json.get('return_msg') == "'password' is a required property: data", rv.json

        raw_body = {
            'user_name': 'customer1',
            'contact_person': '张三',
            'address': '北京市海淀区',
            'email': 'zhangsan@tzcpa.com',
            'password': 'abc',
            'f': 'a'
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post('/api/v1/ad/users', json=body, headers=headers)
        assert rv.status_code == 200, (rv.status_code, rv.data)
        assert rv.is_json, str(rv.data)
        assert isinstance(rv.json, dict), rv.json
        assert rv.json.get('return_code') == errors.ErrorCode.DataParamError.value, rv.json
        assert rv.json.get('return_msg') == "'telephone' is a required property: data", rv.json
