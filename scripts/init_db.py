from alembic import op

op.execute(
    'insert into sys_user (user_name, password, contact_person, address, email, telephone, ip, user_state, api_state, role_id, created_by, api_key, secret_key) '
    'values ("developer", "pbkdf2:sha256:150000$LTftI2ji$d779c6395537a45e5ae696ec1c28ef8c50ec0a0b2ffc38019b39b6b9d9f15cee", "developer", "北京",'
    ' "developer@tzcpa.com", "1234567", "127.0.0.1", "active", "active", 1, 0, "10162afcc69f36ec94bebb560fe2bd5f", '
    '"6f0c26f1200cefb2797030dc03b6063f57dc6499c5504b76105ed65ff11bbaf4c1a275c6309b7b19594b584dc29a91617d8cae9868a4e93adf11f68d3822bba12f9e811d5abd2fe9d1db6f829929e0c6e7b8225ed3b59c29c47efefec81ff51bbfb34f33d08fd4127bcfc386423d73de5d8f1384e8619d89b2271379635fbe52");')
op.execute(
    'insert into dat_company (company_name, company_state, tax_number, taxpayer_identification_id, province_id,head_office, login_way,valid_start_date,valid_end_date,user_id,ip,created_by) values '
    '("测试专用公司勿删", "active", ""XXXXXXXXXXXXXXXXX", 1,1,1,"real_name","2020-01-01","2999-01-01",1,"127.0.0.1",1)')
