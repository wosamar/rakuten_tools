from sqlalchemy import inspect

from database import Session as DBSession
from sqlalchemy.orm import Session


class DBHandler:
    def __init__(self):
        self._session: Session = DBSession()

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

    def create_or_update(self, instance, unique_keys: list):
        """
        根據指定的唯一鍵判斷資料是否存在，若存在則更新，否則新增。

        參數:
        - instance: 要新增或更新的模型實例。
        - unique_keys: 用於判斷唯一性的欄位名稱列表，例如 ['shop_id', 'product_id']。
        """
        try:
            # 建立查詢條件字典
            filter_kwargs = {key: getattr(instance, key) for key in unique_keys}

            # 查詢現有實例
            existing_instance = self.get(type(instance), **filter_kwargs)

            if existing_instance:
                # 如果存在，就更新其屬性
                return self.update(existing_instance, **filter_kwargs)
            else:
                # 如果不存在，就新增
                return self.add(instance)
        except Exception as e:
            print(f"Error in create_or_update: {e}")
            self._session.rollback()
            return None

    def close(self):
        """關閉 Session"""
        self._session.close()
