from fastapi import APIRouter, HTTPException, Query, Body
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
from sqlalchemy.orm import sessionmaker, Session
from typing import Any, Dict
from urllib.parse import quote_plus

class APIBridge:

    def __init__(self, db_configs: Dict[str, Dict[str, Any]], base_endpoint: str = "/api"):
        self.db_configs = db_configs
        self.base_endpoint = base_endpoint
        self.engines = {}
        self.sessions = {}
        self.router = APIRouter()
        self._setup_routes()
        self._setup_connections()

    def _setup_connections(self):
        """Initialize database connections synchronously after object creation."""
        self.engines = {
            name: self._get_db_connection(**config)
            for name, config in self.db_configs.items()
        }

        self.sessions = {
            name: sessionmaker(bind=self.engines[name], expire_on_commit=False, class_=Session)
            for name in self.engines
        }

    def _get_db_connection(self, type, host, port, database, user, password):
        try:
            SERVERS = {
                "postgresql": "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                "mysql": "mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            }

            if type not in SERVERS:
                raise ValueError(f"{type} is an invalid or missing server type for '{database}'.")

            encoded_password = quote_plus(password)

            db_url = SERVERS[type].format(
                user=user,
                password=encoded_password,
                host=host,
                port=port,
                database=database
            )

            engine = create_engine(db_url)

            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return engine
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def _get_table_columns(self, db_name: str, table_name: str):
        inspector = inspect(self.engines[db_name])
        columns = inspector.get_columns(table_name)
        return {column['name']: column['type'] for column in columns}

    def _setup_routes(self):
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/test", self.test_db_connection, methods=["GET"])
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/{{table_name}}", self.get_all_records, methods=["GET"])
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/{{table_name}}", self.create_record, methods=["POST"])
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/{{table_name}}/{{record_id}}", self.update_record, methods=["PUT"])
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/{{table_name}}/{{record_id}}", self.soft_delete_record, methods=["DELETE"])
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/{{table_name}}/{{record_id}}/hard", self.delete_record, methods=["DELETE"])
        self.router.add_api_route(f"{self.base_endpoint}/{{db_name}}/{{table_name}}/{{record_id}}", self.patch_record, methods=["PATCH"])

    def test_db_connection(self, db_name: str):
        try:
            engine = self.engines.get(db_name)
            if not engine:
                raise HTTPException(status_code=404, detail=f"Database {db_name} not found")
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return {"message": f"Database {db_name} connection successful"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_all_records(self, db_name: str, table_name: str, page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
        offset = (page - 1) * limit
        try:
            with self.sessions[db_name]() as session:
                query = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
                result = session.execute(query, {"limit": limit, "offset": offset})
                rows = result.mappings().all()

                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                total_records = (session.execute(count_query)).scalar()

                with self.engines[db_name].connect() as conn:
                    columns = [col["name"] for col in inspect(conn).get_columns(table_name)]


                result_dict = [dict(zip(columns, row.values())) for row in rows]

                pagination = {
                    "total_records": total_records,
                    "limit": limit,
                    "skip": offset,
                    "total_pages": (total_records // limit) + (1 if total_records % limit else 0),
                    "current_page": page,
                }

                return {"data": result_dict, "pagination": pagination}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading table: {str(e)}")

    def create_record(self, db_name: str, table_name: str, record: Dict[str, Any] = Body(...)):
        session = self.sessions.get(db_name)()
        try:
            columns = ", ".join(record.keys())
            placeholders = ", ".join([f":{key}" for key in record.keys()])
            query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
            session.execute(query, record)
            session.commit()

            return {"message": f"Record added to {table_name} in {db_name}"}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error inserting record: {str(e)}")
        finally:
            session.close()

    def update_record(self, db_name: str, table_name: str, record_id: int, record: Dict[str, Any] = Body(...)):
        session = self.sessions.get(db_name)()
        try:
            set_clause = ", ".join([f"{key}=:{key}" for key in record.keys()])
            query = text(f"UPDATE {table_name} SET {set_clause} WHERE id = :record_id")
            params = {**record, "record_id": record_id}
            session.execute(query, params)
            session.commit()
            return {"message": f"Record {record_id} updated in {table_name} in {db_name}"}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")
        finally:
            session.close()

    def soft_delete_record(self, db_name: str, table_name: str, record_id: int, deleted_by_guid: int):
        session = self.sessions.get(db_name)()
        try:
            current_time = datetime.now()

            query = text(f"""
                UPDATE {table_name}
                SET active = 0,
                    deleted = 1,
                    deleted_by_guid = :deleted_by_guid,
                    deleted_at = :deleted_at
                WHERE id = :record_id
            """)

            params = {
                "record_id": record_id,
                "deleted_by_guid": deleted_by_guid,
                "deleted_at": current_time
            }

            result = session.execute(query, params)
            session.commit()

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Record {record_id} not found in {table_name}"
                )

            return {
                "message": f"Record {record_id} soft deleted from {table_name}",
                "deleted_at": current_time,
                "deleted_by": deleted_by_guid
            }

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error soft deleting record: {str(e)}")
        finally:
            session.close()
    
    def delete_record(self, db_name: str, table_name: str, record_id: int):
        session = self.sessions.get(db_name)()
        try:
            query = text(f"DELETE FROM {table_name} WHERE id = :record_id")
            session.execute(query, {"record_id": record_id})
            session.commit()
            return {"message": f"Record {record_id} deleted from {table_name} in {db_name}"}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")
        finally:
            session.close()

    def patch_record(self, db_name: str, table_name: str, record_id: int, record: Dict[str, Any] = Body(...)):
        session = self.sessions.get(db_name)()
        try:
            set_clause = ", ".join([f"{key}=:{key}" for key in record.keys()])
            query = text(f"UPDATE {table_name} SET {set_clause} WHERE id = :record_id")
            params = {**record, "record_id": record_id}
            result = session.execute(query, params)
            session.commit()

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Record {record_id} not found in {table_name}"
                )

            return {"message": f"Record {record_id} patched in {table_name}"}

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error patching record: {str(e)}")
        finally:
            session.close()
