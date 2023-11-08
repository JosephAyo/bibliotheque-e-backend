from sqlalchemy import DateTime


def convert_db_timestamp_to_datetime(db_timestamp):
    timestamp_from_db = db_timestamp.scalar()

    # Convert the timestamp from the database to a Python datetime object
    return timestamp_from_db.replace(tzinfo=None)


def convert_datetime_to_db_timestamp(py_datetime):
    # Ensure the Python datetime object has no timezone information (tzinfo=None)
    py_datetime = py_datetime.replace(tzinfo=None)

    # Create a SQLAlchemy DateTime object
    db_timestamp = DateTime()
    db_timestamp = db_timestamp.process_bind_param(py_datetime, None)

    return db_timestamp
