-- 创建admin用户
CREATE USER admin WITH PASSWORD 'admin';

-- 创建research_assistant数据库并指定admin为拥有者
CREATE DATABASE research_assistant OWNER admin;

-- 授予admin用户创建数据库的权限
ALTER USER admin CREATEDB;