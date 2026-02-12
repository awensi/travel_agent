import sqlite3
import pymysql
import psutil  #用于获取系统信息
from mcp.server.fastmcp import FastMCP
from contextlib import contextmanager
import logging
import sys
import io

# 强制设置 UTF-8 编码并禁用缓冲区
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    filename="D:\\project\\travel_agent\\mcp_server_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
#初始化mcp服务，名字可以自定义
mcp = FastMCP("MyAssistant")

#数据库功能部分
DB_CONFIG = {
    "host":"localhost",
    "port":3306,
    "user":"root",
    "password":"Liusir@2026",
    "database":"my_assistant_db",
    # "chartset":"utf8mb4",
    "cursorclass":pymysql.cursors.DictCursor
}

@contextmanager
def get_db_cursor():
    #上下文管理器，自动处理连接开启与关闭
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()


@mcp.tool()  #mcp.tool 用于接收参数并执行 INSERT 或 UPDATE SQL 语句
def query_user(name_filter: str = None) -> str:
    #从user表中查询用户，可选参数name_filter用于模糊搜索
    sql = "select id,username,email from users"
    params = []
    if name_filter:
        sql += "where username like %s"
        params.append(f"%{name_filter}%")
    
    with get_db_cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return str(rows) if rows else "未找到匹配的数据"
    
#新增
@mcp.tool()
def add_user(username: str, email: str) -> str:
    #向数据库添加新用户，需要提供用户名和邮箱名
    try:
        with get_db_cursor() as cursor:
            sql = "insert into users (username, email, status) values (%s, %s, 'active')"
            cursor.execute(sql, (username, email))
        return f"success create user {username}"
    except Exception as e:
        return f"fail to add user {str(e)}"
    

#修改
@mcp.tool()
def update_user_info(user_id: int, new_email: str) -> str:
    #根据用户id更新电子邮箱
    try:
        with get_db_cursor() as cursor:
            sql = "update user set email = %s where id = %s"
            affected_rows = cursor.execute(sql, (new_email, user_id))
        
        if affected_rows > 0:
            return f"user's email had update to {new_email}"
        return "no find this id ,update fail"
    except Exception as e:
        return f"updata fail {str(e)}"
    
#删除
@mcp.tool()
def delete_user(user_id: int) -> str:
    #根据用户id彻底删除用户记录
    try:
        with get_db_cursor() as cursor:
            sql = "delete from user where uer_id = $s"
            affected_rows = cursor.execute(sql, (user_id,))
        if affected_rows > 0:
            return "user's email had deleted"
        return "no find this id ,delete fail"
    except Exception as e:
        return f"delete fail {str(e)}"
    
if __name__ == "__main__":
    try:
        logging.info("MySQL MCP Server 尝试启动...")
        mcp.run()
        # response = query_user()
        # print(response)
    except Exception as e:
        logging.error(f"Server 崩溃: {e}", exc_info=True)

