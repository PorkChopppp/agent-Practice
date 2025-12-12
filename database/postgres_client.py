"""
PostgreSQL数据库客户端模块

PostgreSQL是一个功能强大的开源关系型数据库管理系统。
在本应用中，它用于存储结构化的研究结果和相关元数据，
如研究报告的主题、内容和创建时间等信息。

本模块实现了PostgreSQL数据库的基本操作接口，
包括连接、创建表、保存和查询研究报告等功能。
如果无法连接到数据库，系统会自动切换到内存存储模式。
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

class PostgresClient:
    """
    PostgreSQL数据库客户端类
    
    负责与PostgreSQL数据库交互，包括连接、创建表、保存和查询数据等功能。
    如果无法连接到数据库，系统会自动切换到内存存储模式以保证基本功能可用。
    """
    
    def __init__(self):
        """
        初始化PostgreSQL客户端
        
        在初始化时尝试连接到数据库，并创建所需的表结构。
        """
        self.connection = None  # 数据库连接对象
        self._connect()         # 尝试建立数据库连接

    def _connect(self):
        """
        连接到PostgreSQL数据库
        
        使用配置文件中的参数建立数据库连接。
        连接成功后会自动创建所需的表结构。
        如果连接失败，则打印错误信息并切换到内存存储模式。
        """
        try:
            # 构造数据库连接参数
            connection_params = {
                'host': POSTGRES_HOST,        # 数据库主机地址
                'port': POSTGRES_PORT,        # 数据库端口
                'dbname': POSTGRES_DB,        # 数据库名称
                'user': POSTGRES_USER,        # 用户名
                'sslmode': 'prefer',          # SSL连接模式
                'connect_timeout': 10         # 连接超时时间（秒）
            }
            
            # 如果设置了密码，则添加到连接参数中
            if POSTGRES_PASSWORD:
                connection_params['password'] = POSTGRES_PASSWORD
                
            print(f"尝试连接到PostgreSQL数据库: {connection_params}")
            # 尝试建立数据库连接
            self.connection = psycopg2.connect(**connection_params)
            
            # 创建所需的表结构
            self._create_tables()
            print("成功连接到PostgreSQL数据库")
        except Exception as e:
            # 连接失败时的错误处理
            print(f"连接PostgreSQL数据库失败: {e}")
            print("将使用内存存储替代数据库存储")
            self.connection = None

    def _create_tables(self):
        """
        创建数据库表结构
        
        在数据库中创建存储研究报告所需的表。
        使用IF NOT EXISTS子句确保表不存在时才创建，避免重复创建错误。
        """
        if not self.connection:
            return
            
        try:
            # 创建游标对象用于执行SQL语句
            cursor = self.connection.cursor()
            
            # 创建研究报告表的SQL语句
            # 包含自增主键、主题、内容和创建时间字段
            create_reports_table = """
            CREATE TABLE IF NOT EXISTS research_reports (
                id SERIAL PRIMARY KEY,                    -- 自增主键
                topic VARCHAR(255) NOT NULL,             -- 报告主题，最大长度255字符
                content TEXT NOT NULL,                   -- 报告内容，TEXT类型可存储大量文本
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 创建时间，默认为当前时间
            );
            """
            
            # 执行创建表的SQL语句
            cursor.execute(create_reports_table)
            # 提交事务以确保表被创建
            self.connection.commit()
            # 关闭游标
            cursor.close()
        except Exception as e:
            print(f"创建表时出错: {e}")

    def save_report(self, topic, content):
        """
        保存研究报告到数据库
        
        将研究报告的主题和内容保存到数据库中。
        如果数据库连接不可用，则只在内存中保存并返回虚拟ID。
        
        Args:
            topic (str): 研究报告的主题
            content (str): 研究报告的内容
            
        Returns:
            int: 保存的报告ID，如果使用内存存储则返回虚拟ID 1
        """
        if not self.connection:
            print("数据库未连接，报告将仅在内存中保存")
            return 1  # 返回虚拟ID
            
        try:
            # 创建游标对象
            cursor = self.connection.cursor()
            
            # 插入数据的SQL语句，使用参数化查询防止SQL注入攻击
            insert_query = """
            INSERT INTO research_reports (topic, content)
            VALUES (%s, %s)
            RETURNING id;  -- 返回新插入记录的ID
            """
            
            # 执行插入操作
            cursor.execute(insert_query, (topic, content))
            # 获取返回的报告ID
            report_id = cursor.fetchone()[0]
            # 提交事务以确保数据被保存
            self.connection.commit()
            # 关闭游标
            cursor.close()
            
            return report_id
        except Exception as e:
            print(f"保存报告时出错: {e}")
            return 1  # 返回虚拟ID

    def get_report(self, report_id):
        """
        根据ID获取研究报告
        
        从数据库中查询指定ID的研究报告。
        如果数据库连接不可用，则返回None。
        
        Args:
            report_id (int): 要查询的报告ID
            
        Returns:
            dict or None: 包含报告信息的字典，如果未找到或数据库不可用则返回None
        """
        if not self.connection:
            return None
            
        try:
            # 创建带字典游标的游标对象
            # RealDictCursor使得查询结果可以直接以字典形式访问
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # 查询指定ID报告的SQL语句
            select_query = """
            SELECT * FROM research_reports WHERE id = %s;
            """
            
            # 执行查询操作
            cursor.execute(select_query, (report_id,))
            # 获取查询结果
            report = cursor.fetchone()
            # 关闭游标
            cursor.close()
            
            return report
        except Exception as e:
            print(f"获取报告时出错: {e}")
            return None

    def get_all_reports(self):
        """
        获取所有研究报告
        
        查询数据库中的所有研究报告，并按创建时间倒序排列。
        如果数据库连接不可用，则返回空列表。
        
        Returns:
            list: 包含所有报告信息的列表，如果数据库不可用则返回空列表
        """
        if not self.connection:
            return []
            
        try:
            # 创建带字典游标的游标对象
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # 查询所有报告的SQL语句，按创建时间倒序排列
            select_query = """
            SELECT * FROM research_reports ORDER BY created_at DESC;
            """
            
            # 执行查询操作
            cursor.execute(select_query)
            # 获取所有查询结果
            reports = cursor.fetchall()
            # 关闭游标
            cursor.close()
            
            return reports
        except Exception as e:
            print(f"获取所有报告时出错: {e}")
            return []

    def close(self):
        """
        关闭数据库连接
        
        清理数据库连接资源，释放占用的网络连接。
        """
        if self.connection:
            try:
                self.connection.close()
            except:
                pass

    def get_connection(self):
        """
        获取数据库连接
        
        返回当前的数据库连接对象
        
        Returns:
            connection: 数据库连接对象
        """
        return self.connection
