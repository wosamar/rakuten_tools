from database import Session as DBSession, Product, Image
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

    def commit(self):
        self._session.commit()

    def close(self):
        """關閉 Session"""
        self._session.close()


class ProductHandler:
    def __init__(self, db_handler):
        self.db = db_handler

    def create_product_with_images(self, data: dict):
        """新增一個新商品及其關聯的所有圖片。"""
        # 建立商品實例
        new_product = Product(sequence=data['sequence'])

        # 將圖片實例添加到商品的 images 列表
        for img_data in data['images']:
            new_product.images.append(Image(file_name=img_data['file_name']))

        # 使用 add 方法將商品及其所有關聯的圖片一併新增到資料庫
        return self.db.add(new_product)

    def update_product_with_images(self, data: dict):
        """更新一個既有商品及其關聯的圖片。
        data 應包含商品所有需要更新的屬性，以及圖片列表。
        """
        # 1. 取得現有的商品實例
        existing_product = self.db.get(Product, **{"id": data.get('id')})
        if not existing_product:
            raise ValueError(f"商品 ID {data.get('id')} 不存在。")

        # 2. 更新商品屬性 (your existing logic)
        allowed_fields = ['sequence', 'description', 'feature', 'highlight', 'info']
        update_fields = {key: data.get(key) for key in allowed_fields if key in data}
        if update_fields:
            self.db.update(existing_product, **update_fields)

        # 3. 處理圖片：取得傳入資料中所有圖片的 ID
        incoming_images_data = data.get('images', [])
        incoming_image_ids = {img_data.get('id') for img_data in incoming_images_data if img_data.get('id')}

        # 4. 處理刪除：建立一個副本進行迭代，避免在迴圈中修改列表
        for existing_img in list(existing_product.images):
            if existing_img.id not in incoming_image_ids:
                # Instead of letting SQLAlchemy handle the delete,
                # you explicitly set the product_id to NULL.
                # In your case, you must DELETE it directly instead.
                self.db.delete(existing_img)

        # 5. 處理新增與更新：建立一個現有圖片的字典以加速查找
        existing_images_map = {img.id: img for img in existing_product.images}

        for img_data in incoming_images_data:
            img_id = img_data.get('id')
            if img_id:
                # 更新現有圖片
                if img_id in existing_images_map:
                    img_to_update = existing_images_map[img_id]
                    self.db.update(img_to_update, file_name=img_data['file_name'])
            else:
                # 新增圖片
                new_image = Image(file_name=img_data['file_name'])
                # Manually set the product_id to ensure it's not NULL
                new_image.product_id = existing_product.id
                self.db.add(new_image)  # Add new image to the session

        self.db.commit()
        return existing_product
