"""
详细测试数据库连接的脚本
"""

import psycopg2

def test_database_connection():
    print("详细测试PostgreSQL数据库连接...")
    
    # 测试不同的连接参数组合
    connection_configs = [
        {
            'host': '127.0.0.1',
            'port': '5432',
            'dbname': 'research_assistant',
            'user': 'admin',
            'password': 'admin'
        },
        {
            'host': 'localhost',
            'port': '5432',
            'dbname': 'research_assistant',
            'user': 'admin',
            'password': 'admin'
        },
        {
            'host': '127.0.0.1',
            'port': '5432',
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres'
        }
    ]
    
    for i, config in enumerate(connection_configs, 1):
        print(f"\n测试配置 {i}: {config}")
        try:
            connection = psycopg2.connect(**config)
            print(f"✓ 成功连接到数据库: {config['dbname']} (用户: {config['user']})")
            
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"  数据库版本: {version[0]}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"✗ 连接失败: {e}")

if __name__ == "__main__":
    test_database_connection()