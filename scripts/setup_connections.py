from airflow import settings
from airflow.models import Connection
from sqlalchemy.orm import sessionmaker

def setup():
    Session = sessionmaker(bind=settings.engine)
    session = Session()

    connections = [
        {
            'conn_id': 'postgres_default',
            'conn_type': 'postgres',
            'host': 'postgres',
            'schema': 'airflow',
            'login': 'airflow',
            'password': 'airflow',
            'port': 5432
        },
        {
            'conn_id': 'postgres_gold',
            'conn_type': 'postgres',
            'host': 'postgres',
            'schema': 'gold_predictions',
            'login': 'airflow',
            'password': 'airflow',
            'port': 5432,
            'extra': '{"schema": "gold"}'
        }
    ]

    for conn_data in connections:
        existing = session.query(Connection).filter(Connection.conn_id == conn_data['conn_id']).first()
        if existing:
            session.delete(existing)
            session.commit()
        
        conn = Connection(**conn_data)
        session.add(conn)
        session.commit()
        print(f"Connection '{conn_data['conn_id']}' OK!")
        
    session.close()

if __name__ == "__main__":
    setup()
    