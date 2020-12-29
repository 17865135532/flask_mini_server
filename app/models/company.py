from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin
from app.constants import ResourceState, LoginWayCode
from app.utils.security import rsa_encrypt, rsa_decrypt


class Company(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "dat_company"
    __table_args__ = {'comment': '企业基本信息表'}

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='企业id')
    company_name = db.Column(db.String(150), nullable=False, unique=True, index=True, comment="企业名称")
    tax_number = db.Column(db.String(18), nullable=False, unique=True, comment="企业税号")
    taxpayer_identification_id = db.Column(db.Integer, nullable=False, comment="纳税人资格认定类型id")
    head_office = db.Column(db.Integer, nullable=False, comment="总机构所在地")
    province_id = db.Column(db.Integer, nullable=False, comment="省份id")
    login_way = db.Column(db.String(30), nullable=False, default=LoginWayCode.real_name.value, comment="登录方式")
    login_account = db.Column(db.String(20), comment="登录账号")
    login_password = db.Column(db.String(256), comment="登录密码(加密)")
    natural_person_name = db.Column(db.String(20), comment="自然人姓名")
    natural_person_ID = db.Column(db.String(18), comment="自然人身份证号")
    natural_person_password = db.Column(db.String(256), comment="自然人登录密码(加密)")
    taxpayer_name = db.Column(db.String(20), comment="报税人名称")
    taxpayer_ID = db.Column(db.String(18), comment="报税人身份证号")
    taxpayer_telephone = db.Column(db.String(20), comment="报税人手机号")
    valid_start_date = db.Column(db.DateTime(timezone=True), nullable=False, comment='有效期开始日期')
    valid_end_date = db.Column(db.DateTime(timezone=True), nullable=False, comment='有效期结束日期')
    user_id = db.Column(db.Integer, nullable=False, comment="用户id")
    ip = db.Column(db.String(20), nullable=False, comment='ip')
    company_state = db.Column(db.String(10), nullable=False, default=ResourceState.active.value, comment='企业状态')

    company_taxes = db.relationship(
        'ComanyTax', backref='company',
        primaryjoin='foreign(ComanyTax.company_id)==Company.company_id')
    declarations = db.relationship(
        'Declaration', backref='company',
        primaryjoin='foreign(Declaration.company_id)==Company.company_id')
    company_robots = db.relationship(
        'RobotCompany', backref='company',
        primaryjoin='foreign(RobotCompany.company_id)==Company.company_id')
    company_interfaces = db.relationship(
        'CompanyInterface', backref='company',
        primaryjoin='foreign(CompanyInterface.company_id)==Company.company_id')
    tax_clearance_certificates = db.relationship(
        'TaxClearanceCertificate', backref='company',
        primaryjoin='foreign(TaxClearanceCertificate.company_id)==Company.company_id')

    def __str__(self):
        return self.company_name

    @property
    def login_pwd(self):
        return rsa_decrypt(self.login_password).decode()

    @login_pwd.setter
    def login_pwd(self, value):
        self.login_password = rsa_encrypt(value)

    @property
    def natural_person_pwd(self):
        return rsa_decrypt(self.natural_person_password).decode()

    @natural_person_pwd.setter
    def natural_person_pwd(self, value):
        self.natural_person_password = rsa_encrypt(value)
