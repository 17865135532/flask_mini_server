#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

from sqlalchemy.inspection import inspect
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.exc
from flask import g, request
from flask_login import current_user

from app.dao.mysql import db
from app import constants
from app.utils import errors, helpers


logger = logging.getLogger(__name__)


class BaseModel(db.Model):
    __table_args__ = {}
    __abstract__ = True
    logger = logger.getChild('BaseModel')
    # TODO: 解决插入失败依然自增

    @classmethod
    def pk_field(cls):
        return inspect(cls).primary_key[0].name

    @property
    def pk_id(self):
        return getattr(self, self.pk_field())

    def save(self, user=None, robot=None, *args, **kwargs):
        user = user or getattr(g, 'user', None)
        robot = robot or getattr(g, 'robot', None)
        if user is None and robot is None:
            raise Exception('user/robot is required')
        try:
            with db.auto_commit_db():
                if 'created_by' in [c.name for c in self.__table__.columns] and user:
                    self.created_by = user.user_id
                elif 'create_robot' in [c.name for c in self.__table__.columns] and robot:
                    self.create_robot = robot.robot_id
                db.session.add(self)
        except sqlalchemy.exc.IntegrityError as e:
            if e.orig.args[0] == 1062:
                raise errors.DBParamValueDuplicate(errmsg=e)
            raise errors.DBStatementError(errmsg=e)
        except sqlalchemy.exc.StatementError as e:
            raise errors.DBStatementError(errmsg=e)

    def delete(self, *args, **kwargs):
        # 删
        with db.auto_commit_db():
            db.session.delete(self)

    def update(self, data, user=None, robot=None, *args, **kwargs):
        # 改
        user = user or getattr(g, 'user', None)
        robot = robot or getattr(g, 'robot', None)
        if user is None and robot is None:
            raise Exception('user/robot is required')
        if 'updated_by' in [c.name for c in self.__table__.columns] and user:
            self.updated_by = user.user_id
        elif 'update_robot' in [c.name for c in self.__table__.columns] and robot:
            self.update_robot = robot.robot_id
        try:
            with db.auto_commit_db():
                for key, val in data.items():
                    if val is not None and hasattr(self, key):
                        setattr(self, key, val)
        except sqlalchemy.exc.IntegrityError as e:
            if e.orig.args[0] == 1062:
                raise errors.DBParamValueDuplicate(errmsg=e)
            raise errors.DBStatementError(errmsg=e)
        except sqlalchemy.exc.StatementError as e:
            raise errors.DBStatementError(errmsg=e)
    
    def to_dict(self):
        return {
            c.name: getattr(self, c.name, None)
            for c in self.__table__.columns
        }

    def __str__(self):
        return f'<{self.__class__.__name__} {self.pk_id}>'

    def __repr__(self):
        return self.__str__()


class CreationMixin:
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), index=True, comment='创建日期')

    @declared_attr
    def created_by(cls):
        return db.Column(db.Integer, index=True, comment='创建人')

    @declared_attr
    def create_robot(cls):
        return db.Column(db.Integer, index=True, comment='负责创建的机器人')


class UpdationMixin:
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now(), index=True, comment='更新日期')

    @declared_attr
    def updated_by(cls):
        return db.Column(db.Integer, index=True, comment='更新人')

    @declared_attr
    def update_robot(cls):
        return db.Column(db.Integer, index=True, comment='负责更新的机器人')


class OperationLogMixin(CreationMixin):
    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True, comment='日志流水号')

    @declared_attr
    def user_name(cls):
        return db.Column(db.String(20), comment='用户名称')

    @declared_attr
    def operation(cls):
        return db.Column(db.String(10), nullable=False, default=constants.Operation.create.value, comment='操作')

    @declared_attr
    def object_type(cls):
        return db.Column(db.String(20), comment='操作对象类型')

    @declared_attr
    def object_id(cls):
        return db.Column(db.String(20), comment='操作对象id')

    @declared_attr
    def info(cls):
        return db.Column(db.String(50), comment='信息')

    @declared_attr
    def user_ip(cls):
        return db.Column(db.String(20), comment='用户ip')

    def __str__(self):
        s = f'{self.user_name} {self.operation} {self.object_type}({self.object_id})'
        if self.info:
            s += f':{self.info}'
        return s


class UserOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'u_operation_log'
    __table_args__ = ({'comment': '用户操作日志表'},)


class ApiOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'u_api_operation_log'
    __table_args__ = ({'comment': 'api操作日志表'},)


class AdminOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'admin_operation_log'
    __table_args__ = ({'comment': '后台用户操作日志表'},)


class AdminApiOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'admin_api_operation_log'
    __table_args__ = ({'comment': '后台api操作日志表'},)


class RobotApiOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'robot_api_operation_log'
    __table_args__ = ({'comment': '机器人api操作日志表'},)


def audit_log(op, mapper, connect, self):
    _logger = logger.getChild('audit_log')

    try:
        role_and_situation = helpers.get_role_and_situation()
        role = role_and_situation.get('role')
        situation = role_and_situation.get('situation')
        user = getattr(g, 'user', None)
        if role == 'user' and situation == 'web':
            sql = f'insert into {UserOperationLog.__tablename__} ' \
                  f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                  f'values ("{user.user_name}","{op.value}",' \
                  f'"{self.__table_args__.get("comment") or self.__tablename__}",' \
                  f'{self.pk_id},"{request.remote_addr}",{g.user.user_id});'
        elif role == 'user' and situation == 'api':
            sql = f'insert into {ApiOperationLog.__tablename__} ' \
                  f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                  f'values ("{user.user_name}","{op.value}",' \
                  f'"{self.__table_args__.get("comment") or self.__tablename__}",' \
                  f'{self.pk_id},"{request.remote_addr}",{g.user.user_id});'
        elif role == 'admin' and situation == 'api':
            sql = f'insert into {AdminApiOperationLog.__tablename__} ' \
                  f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                  f'values ("{user.user_name}","{op.value}",' \
                  f'"{self.__table_args__.get("comment") or self.__tablename__}",' \
                  f'{self.pk_id},"{request.remote_addr}",{g.user.user_id});'
        elif role == 'admin' and situation == 'web':
            if not user:
                user = current_user
            if user:
                user_name = user.user_name
                user_id = user.user_id
                ip = request.remote_addr
            else:
                user_name = None
                user_id = getattr(self, 'created_by')
                ip = ''
            sql = f'insert into {AdminOperationLog.__tablename__} ' \
                  f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                  f'values ("{user_name}","{op.value}",' \
                  f'"{self.__table_args__.get("comment") or self.__tablename__}",' \
                  f'{self.pk_id},"{ip}",{user_id});'
        elif role == 'robot':
            robot = g.robot
            sql = f'insert into {RobotApiOperationLog.__tablename__} ' \
                  f'(user_name, operation, object_type, object_id, user_ip, create_robot)' \
                  f'values ("{robot.robot_name}","{op.value}",' \
                  f'"{self.__table_args__.get("comment") or self.__tablename__}",' \
                  f'{self.pk_id},"{request.remote_addr}",{g.robot.robot_id});'
        else:
            raise Exception(f'user is {user}, robot is {getattr(g, "robot", None)}, '
                            f'auth_method is {getattr(g, "auth_method", None)}')
        connect.execute(sql)
    except Exception as e:
        _logger.critical(f'object is {self}, operation is {op.value}', exc_info=e)
