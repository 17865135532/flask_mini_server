import os
import glob

import ujson
from flask_restx import fields, Model

from app.utils.security import rsa_decrypt


base_resp = Model('Body', {
    'return_code': fields.Integer(title='返回码', description='200为成功', example=200, required=True),
    'return_msg': fields.String(title='返回信息', description='成功时可为空字符串', example='Success', required=True)
})
resource_model = Model('ResourceModel', {
    'created_by': fields.Integer(title='创建者ID', example=1, required=True),
    'created_at': fields.String(title='创建时间', example='2020-01-01 08:00:00', required=True),
    'updated_by': fields.Integer(title='更新者ID', example=1),
    'updated_at': fields.String(title='更新时间', example='2020-01-01 08:00:01')
})
user_model = resource_model.clone('user', {
    "user_id": fields.Integer(title="用户ID"),
    'user_name': fields.String(title="用户名"),
    'contact_person': fields.String(title="联系人"),
    'address': fields.String(title="联系地址"),
    'email': fields.String(title="联系人邮箱"),
    'telephone': fields.String(title="联系电话"),
    'api_key': fields.String(title="接口id"),
    'secret_key': fields.String(
        title="接口密钥",
        attribute=lambda x: x.sk if x and x.sk else None)
})
company_model = resource_model.clone('company', {
    "company_id": fields.Integer(title="企业id"),
    'company_name': fields.String(title="企业名称"),
    'tax_number': fields.String(title="企业税号"),
    'taxpayer_identification': fields.String(
        title="纳税人资格认定类型",
        attribute=lambda x: x.taxpayer_identification.taxpayer_identification_name if x and x.taxpayer_identification else None),
    "head_office": fields.String(
        title='总机构所在地',
        attribute=lambda x: x.head_office_province.province_name if x and x.head_office_province else None),
    'province': fields.String(
        title="省份",
        attribute=lambda x: x.province.province_name if x and x.province else None),
    'login_way': fields.String(title="登录方式"),
    'login_account': fields.String(title="登录账号"),
    'login_password': fields.String(
        title="登录密码",
        attribute=lambda x: rsa_decrypt(x.login_password).decode() if x and x.login_password else None),
    'natural_person_name': fields.String(title="自然人姓名"),
    'natural_person_ID': fields.String(title="自然人身份证号"),
    'natural_person_password': fields.String(
        title="自然人登录密码",
        attribute=lambda x: rsa_decrypt(x.natural_person_password).decode() if x and x.natural_person_password else None),
    'taxpayer_name': fields.String(title="报税人名称"),
    'taxpayer_ID': fields.String(title="报税人身份证号"),
    'taxpayer_telephone': fields.String(title="报税人手机号"),
    'valid_start_date': fields.String(title="有效期开始日期"),
    'valid_end_date': fields.String(title="有效期结束日期"),
    'company_state': fields.String(title="企业状态")
})