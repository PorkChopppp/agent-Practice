import psycopg2
from config.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def test_connection():
    print("测试PostgreSQL连接...")
    print(f"连接参数: host={POSTGRES_HOST}, port={POSTGRES_PORT}, db={POSTGRES_DB}, user={POSTGRES_USER}")
    
    # 测试不同的主机地址
    hosts_to_try = ['127.0.0.1', 'localhost']
    
    for host in hosts_to_try:
        try:
            # 构造数据库连接参数
            connection_params = {
                'host': host,
                'port': POSTGRES_PORT,
                'dbname': POSTGRES_DB,
                'user': POSTGRES_USER,
                'password': POSTGRES_PASSWORD,
                'sslmode': 'prefer',
                'connect_timeout': 10
            }
            
            print(f"尝试连接到PostgreSQL数据库: {connection_params}")
            connection = psycopg2.connect(**connection_params)
            print(f"成功连接到PostgreSQL数据库 (使用主机: {host})")
            
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
            return  # 成功连接后退出
            
        except Exception as e:
            print(f"使用主机 {host} 连接PostgreSQL数据库失败: {e}")
    
    print("所有连接尝试都失败了")

if __name__ == "__main__":
    test_connection()