import psycopg2
from config.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def test_connection():
    print("测试PostgreSQL连接...")
    print(f"连接参数: host={POSTGRES_HOST}, port={POSTGRES_PORT}, db={POSTGRES_DB}, user={POSTGRES_USER}")
    
    try:
        # 构造数据库连接参数
        connection_params = {
            'host': POSTGRES_HOST,
            'port': POSTGRES_PORT,
            'dbname': POSTGRES_DB,
            'user': POSTGRES_USER,
            'password': POSTGRES_PASSWORD,
            'sslmode': 'prefer',
            'connect_timeout': 10
        }
        
        print(f"尝试连接到PostgreSQL数据库: {connection_params}")
        connection = psycopg2.connect(**connection_params)
        print("成功连接到PostgreSQL数据库")
        
        # 创建游标对象用于执行SQL语句
        cursor = connection.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"数据库版本: {version[0]}")
        
        # 关闭游标和连接
        cursor.close()
        connection.close()
        print("连接测试完成")
        
    except Exception as e:
        print(f"连接PostgreSQL数据库失败: {e}")

if __name__ == "__main__":
    test_connection()