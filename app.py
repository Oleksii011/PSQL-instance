import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'host': 'junction.proxy.rlwy.net',
    'port': '19910',
    'database': 'RailwayDB',
    'user': 'postgres',
    'password': 'ybFsTxMPmeikkNgpBcAGDwjbLfMGJbDG'
}


def connect_to_db():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def create_table_if_not_exists(cursor):
    table_check_query = "SELECT to_regclass('public.users');"
    cursor.execute(table_check_query)
    if cursor.fetchone()[0]:
        print("Таблица 'users' уже существует.")
    else:
        print("Таблица 'users' не найдена. Создаю таблицу...")
        cursor.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            name VARCHAR(100),
            age INT,
            email VARCHAR(100),
            phone VARCHAR(15),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        print("Таблица успешно создана.")


def add_user(cursor, username, name, age, email, phone, address):
    try:
        cursor.execute('''
        INSERT INTO users (username, name, age, email, phone, address)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
        ''', (username, name, age, email, phone, address))
        print(f"Пользователь {username} добавлен.")
    except Exception as e:
        print(f"Ошибка добавления пользователя {username}: {e}")


def update_user(cursor, username, **kwargs):
    if not kwargs:
        print("Нет данных для обновления.")
        return
    update_clauses = [f"{key} = %s" for key in kwargs.keys()]
    params = list(kwargs.values()) + [username]
    try:
        cursor.execute(f'''
        UPDATE users SET {', '.join(update_clauses)}
        WHERE username = %s;
        ''', params)
        print(f"Пользователь {username} обновлен.")
    except Exception as e:
        print(f"Ошибка обновления пользователя {username}: {e}")


def delete_user(cursor, username):
    try:
        cursor.execute("DELETE FROM users WHERE username = %s;", (username,))
        print(f"Пользователь {username} удален.")
    except Exception as e:
        print(f"Ошибка удаления пользователя {username}: {e}")


def fetch_all_users(cursor):
    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()
    print("Данные из таблицы 'users':")
    for row in rows:
        print(row)


def main():
    connection = connect_to_db()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            create_table_if_not_exists(cursor)
            connection.commit()

            users_to_add = [
                ('jane_smith', 'Jane Smith', 30, 'jane.smith@example.com', '123-456-7890', '123 Elm Street'),
                ('john_doe', 'John Doe', 25, 'john.doe@example.com', '987-654-3210', '456 Oak Avenue'),
                ('alice_brown', 'Alice Brown', 28, 'alice.brown@example.com', '555-789-1234', '789 Pine Road')
            ]

            for user in users_to_add:
                add_user(cursor, *user)

            update_user(cursor, 'jane_smith', age=31, phone='123-456-0000')
            delete_user(cursor, 'alice_brown')

            fetch_all_users(cursor)
            connection.commit()
    except Exception as error:
        print(f"Ошибка: {error}")
    finally:
        connection.close()


if name == 'main':
    main()
