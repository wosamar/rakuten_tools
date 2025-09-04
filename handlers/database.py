from sqlalchemy.orm import Session


class DBHandler:
    def __init__(self):
        self._session: Session = Session()

    def add(self, instance):
        """新增一個實例到資料庫"""
        try:
            self._session.add(instance)
            self._session.commit()
            return instance
        except Exception as e:
            self._session.rollback()
            print(f"Error adding instance: {e}")
            return None

    def get(self, model, **kwargs):
        """根據條件查詢單個實例"""
        try:
            return self._session.query(model).filter_by(**kwargs).first()
        except Exception as e:
            print(f"Error retrieving instance: {e}")
            return None

    def get_all(self, model, **kwargs):
        """根據條件查詢多個實例"""
        try:
            return self._session.query(model).filter_by(**kwargs).all()
        except Exception as e:
            print(f"Error retrieving instances: {e}")
            return []

    def update(self, instance, **kwargs):
        """更新一個實例的屬性"""
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self._session.commit()
            return instance
        except Exception as e:
            self._session.rollback()
            print(f"Error updating instance: {e}")
            return None

    def delete(self, instance):
        """刪除一個實例"""
        try:
            self._session.delete(instance)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            print(f"Error deleting instance: {e}")

    def close(self):
        """關閉 Session"""
        self._session.close()