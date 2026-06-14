import sqlite3


def nonempty():
    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    cursor.execute(
        f"SELECT question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 FROM main WHERE user_id = {user_id}")
    results = cursor.fetchone()
    columns = ['question1', 'question2', 'question3', 'question4', 'question5',
               'question6', 'question7', 'question8', 'question9', 'question10']
    non_empty_columns = {columns[i]: value for i, value in enumerate(results) if value and value != ''}
    non_empty_columns_list = list(non_empty_columns.values())
    non_empty_columns_list_keys = list(non_empty_columns.keys())