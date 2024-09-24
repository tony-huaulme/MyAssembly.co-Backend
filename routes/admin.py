from sqlalchemy import inspect, text
from models.models import db
from flask import render_template, session, jsonify

def get_all_tables_data(limit=100):
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    table_data = {}
    print(f"Tables: {tables}")  # Debugging line
    for table in tables:
        query = text(f"SELECT * FROM {table} LIMIT {limit}")
        print(f"Executing query: {query} with limit {limit}")  # Debugging line
        result = db.session.execute(query, {"limit": limit}).fetchall()
        print(f"Result: {result}")  # Debugging line

        columns = [col['name'] for col in inspector.get_columns(table)]

        table_data[table] = (columns, result)

    return table_data

def rendertables():

    if session.get('user_id') != 50:
        return jsonify({"error": "Not authorized"})

    tables_data = get_all_tables_data(limit=100)
    return render_template('index.html', tables_data=tables_data)
