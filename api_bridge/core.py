from fastapi import APIRouter, HTTPException, Query, Body
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Any, Dict, List
from urllib.parse import quote_plus

class APIBridge:
    def __init__(self, db_config: Dict[str, Any], base_endpoint: str = "/api"):
        self.db_config = db_config
        self.base_endpoint = base_endpoint
        self.engine = self._get_db_connection(**self.db_config)
        self.Session = sessionmaker(bind=self.engine)
        self.router = APIRouter()
        self._setup_routes()

    def _get_db_connection(self, host, port, database, user, password):
        try:
            encoded_password = quote_plus(password)
            engine = create_engine(
                f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
            )
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return engine
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def _validate_table(self, table_name: str) -> None:
        """
        Validate if the given table exists in the database.
        Raises a ValueError if the table does not exist.
        """
        inspector = inspect(self.engine)
        existing_tables = set(inspector.get_table_names())

        if table_name not in existing_tables:
            raise ValueError(f"Invalid table name specified: {table_name}")
    
    def _validate_columns(
        self, table_name: str, columns: List[str]
    ) -> None:
        """
        Validate if the given columns exist in the model class.
        Raises a ValueError if any invalid columns are found.
        """
        model_columns = [column.get("name") for column in inspect(self.engine).get_columns(table_name)]
        invalid_columns = set(columns) - set(model_columns)
        if invalid_columns:
            raise ValueError(
                f"Invalid column(s) specified: {', '.join(invalid_columns)}"
            )

    def _get_table_columns(self, table_name: str):
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        return {column['name']: column['type'] for column in columns}

    def _generate_dynamic_model(self, table_name: str):
        columns = self._get_table_columns(table_name)
        dynamic_model = type(
            f"{table_name.capitalize()}Model",
            (BaseModel,),
            {col: (str, ...) for col in columns}
        )
        return dynamic_model

    def _setup_routes(self):
        self.router.add_api_route(f"{self.base_endpoint}/test", self.test_db_connection, methods=["GET"])
        self.router.add_api_route(f"{self.base_endpoint}/{{table_name}}", self.get_all_records, methods=["GET"])
        self.router.add_api_route(f"{self.base_endpoint}/{{table_name}}", self.create_record, methods=["POST"])
        self.router.add_api_route(f"{self.base_endpoint}/{{table_name}}/{{record_id}}", self.update_record, methods=["PUT"])
        self.router.add_api_route(f"{self.base_endpoint}/{{table_name}}/{{record_id}}", self.soft_delete_record, methods=["DELETE"])
        self.router.add_api_route(f"{self.base_endpoint}/{{table_name}}/{{record_id}}/hard", self.delete_record, methods=["DELETE"])
        self.router.add_api_route(f"{self.base_endpoint}/{{table_name}}/{{record_id}}", self.patch_record, methods=["PATCH"])

    def test_db_connection(self):
        try:
            engine = self._get_db_connection(**self.db_config)
            return {"message": "Database connection successful"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_all_records(self, table_name: str, page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
        session = self.Session()
        offset = (page - 1) * limit

        try:
            self._validate_table(table_name)
            query = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
            result = session.execute(query, {"limit": limit, "offset": offset}).fetchall()
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            total_records = session.execute(count_query).scalar()

            columns = [column['name'] for column in inspect(self.engine).get_columns(table_name)]
            result_dict = [dict(zip(columns, row)) for row in result]

            pagination = {
                "total_records": total_records,
                "limit": limit,
                "skip": offset,
                "total_pages": (total_records // limit) + (1 if total_records % limit else 0),
                "current_page": page,
            }

            return {
                "data": result_dict,
                "pagination": pagination
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading table: {str(e)}")
        finally:
            session.close()

    def create_record(self, table_name: str, record: Dict[str, Any] = Body(...)):
        session = self.Session()
        try:
            self._validate_table(table_name)
            self._validate_columns(table_name, record.keys())
            columns = ", ".join(record.keys())
            placeholders = ", ".join([f":{key}" for key in record.keys()])
            query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
            session.execute(query, record)
            session.commit()

            return {"message": f"Record added to {table_name}"}

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error inserting record: {str(e)}")
        finally:
            session.close()

    def update_record(self, table_name: str, record_id: int, record: Dict[str, Any] = Body(...)):
        session = self.Session()
        try:
            self._validate_table(table_name)
            self._validate_columns(table_name, record.keys())
            set_clause = ", ".join([f"{key}=:{key}" for key in record.keys()])
            query = text(f"UPDATE {table_name} SET {set_clause} WHERE id = :record_id")
            params = {**record, "record_id": record_id}
            session.execute(query, params)
            session.commit()

            return {"message": f"Record {record_id} updated in {table_name}"}

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")
        finally:
            session.close()

    def soft_delete_record(self, table_name: str, record_id: int, payload: Dict[str, Any] = Body(...)):
        session = self.Session()
        try:
            self._validate_table(table_name)
            self._validate_columns(table_name, payload.keys())
            current_time = int(datetime.now().timestamp())

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
                "deleted_by_guid": payload["deleted_by_guid"],
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
                "deleted_by": payload["deleted_by_guid"]
            }

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error soft deleting record: {str(e)}")
        finally:
            session.close()

    def delete_record(self, table_name: str, record_id: int):
        session = self.Session()
        try:
            self._validate_table(table_name)
            query = text(f"DELETE FROM {table_name} WHERE id = :record_id")
            session.execute(query, {"record_id": record_id})
            session.commit()

            return {"message": f"Record {record_id} deleted from {table_name}"}

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")
        finally:
            session.close()

    def patch_record(self, table_name: str, record_id: int, record: Dict[str, Any] = Body(...)):
        session = self.Session()
        try:
            self._validate_table(table_name)
            self._validate_columns(table_name, record.keys())
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
