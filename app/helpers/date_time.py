def convert_db_timestamp_to_datetime(db_timestamp):
    timestamp_from_db = db_timestamp.scalar()

    # Convert the timestamp from the database to a Python datetime object
    return timestamp_from_db.replace(tzinfo=None)
