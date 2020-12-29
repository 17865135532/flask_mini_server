from flask import g


def get_role_and_situation():
    user = getattr(g, 'user', None)
    robot = getattr(g, 'robot', None)
    auth_method = getattr(g, 'auth_method', None)
    if auth_method == 'token':
        if user:
            return {'role': 'user', 'situation': 'web'}
        else:
            raise Exception('User is required')
    elif auth_method == 'ak':
        if user:
            role = user.role
            if not role:
                raise Exception(f'user {user} has not role: {user.role}')
            if role.role_name == 'administrator':
                return {'role': 'admin', 'situation': 'api'}
            elif role.role_name == 'customer':
                return {'role': 'user', 'situation': 'api'}
            else:
                raise Exception(f'Unknown role:{role}')
        else:
            raise Exception('user is required')
    elif auth_method == 'robot_id':
        if robot:
            return {'role': 'robot', 'situation': 'api'}
        else:
            raise Exception('robot is required')
    else:
        return {'role': 'admin', 'situation': 'web'}
