"""
测试数据库连接的脚本
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from database.postgres_client import PostgresClient
from config.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def test_postgres_direct_connection():
    print("测试PostgreSQL数据库直连...")
    
    try:
        # 直接连接测试
        connection_params = {
            'host': POSTGRES_HOST,
            'port': POSTGRES_PORT,
            'dbname': POSTGRES_DB,
            'user': POSTGRES_USER,
            'sslmode': 'prefer',
            'connect_timeout': 10
        }
        
        # 如果设置了密码，则添加到连接参数中
        if POSTGRES_PASSWORD:
            connection_params['password'] = POSTGRES_PASSWORD
            
        print(f"尝试连接到PostgreSQL数据库: {connection_params}")
        connection = psycopg2.connect(**connection_params)
        print("✓ 成功连接到PostgreSQL数据库")
        connection.close()
    except Exception as e:
        print(f"✗ 连接PostgreSQL数据库失败: {e}")

def test_database_connection():
    print("测试PostgreSQL数据库连接...")
    
    try:
        # 创建PostgreSQL客户端实例
        db_client = PostgresClient()
        
        # 检查连接状态
        if db_client.connection:
            print("✓ 成功连接到PostgreSQL数据库")
            
            # 测试插入数据
            print("测试插入数据...")
            report_id = db_client.save_report(
                "测试主题", 
                "这是一个测试报告内容，用于验证数据库连接和基本操作。"
            )
            print(f"✓ 成功保存报告，ID: {report_id}")
            
            # 测试查询数据
            print("测试查询数据...")
            report = db_client.get_report(report_id)
            if report:
                print(f"✓ 成功查询报告: {report['topic']}")
            else:
                print("✗ 未能查询到刚插入的报告")
                
            # 测试查询所有报告
            print("测试查询所有报告...")
            all_reports = db_client.get_all_reports()
            print(f"✓ 数据库中共有 {len(all_reports)} 个报告")
            
            # 关闭连接
            db_client.close()
            print("✓ 数据库连接测试完成")
        else:
            print("✗ 无法连接到PostgreSQL数据库")
            print("系统正在使用内存存储替代数据库存储")
            
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_postgres_direct_connection()
    test_database_connection()