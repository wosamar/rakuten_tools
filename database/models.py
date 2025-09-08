import json

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # 專案名稱 (tra / twe)
    created_time = Column(DateTime, server_default=func.now())

    shops = relationship("Shop", back_populates="project")


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # 英文代號
    display_name = Column(String(100), nullable=False)  # 中文名稱
    created_time = Column(DateTime, server_default=func.now())

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    project = relationship("Project", back_populates="shops")
    products = relationship("Product", back_populates="shop")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sequence = Column(String(50), nullable=False)  # 商品流水號
    description = Column(Text, nullable=False)
    feature = Column(Text, nullable=False)
    highlight = Column(Text, nullable=False)
    info = Column(Text, nullable=False)

    updated_time = Column(DateTime, server_default=func.now())
    created_time = Column(DateTime, server_default=func.now())

    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)

    shop = relationship("Shop", back_populates="products")
    images = relationship("Image", back_populates="product")

    __table_args__ = (
        UniqueConstraint('sequence', 'shop_id', name='uq_product_shop'),
    )

    @property
    def manage_number(self):
        """生成管理編號，格式為 '專案名-商店名-商品代號'"""
        try:
            # 確保 shop 和 project 關聯物件都已載入
            if self.shop and self.shop.project:
                project_name = self.shop.project.name
                shop_name = self.shop.name
                sequence = self.sequence
                return f"{project_name}-{shop_name}-{sequence}"
            return None
        except Exception:
            return None

    @property
    def info_dict(self):
        try:
            return json.loads(self.info) if self.info else {}
        except json.JSONDecodeError:
            return {}

    @info_dict.setter
    def info_dict(self, value: dict):
        self.info = json.dumps(value, ensure_ascii=False)


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(100), nullable=False)

    created_time = Column(DateTime, server_default=func.now())

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product = relationship("Product", back_populates="images")

    __table_args__ = (
        UniqueConstraint('file_name', 'product_id',  name='uq_image_product'),
    )

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    path = Column(String(100), nullable=False)
    description = Column(String(100), nullable=True)
    template_type_id = Column(Integer, ForeignKey("template_types.id"), nullable=False)  # 1=main 2=sub 3=mobile

    created_time = Column(DateTime, server_default=func.now())
    updated_time = Column(DateTime, server_default=func.now())
    template_type = relationship("TemplateType", back_populates="templates")


class TemplateType(Base):
    __tablename__ = "template_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(100), nullable=True)

    created_time = Column(DateTime, server_default=func.now())
    templates = relationship("Template", back_populates="template_type")


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(50), nullable=False)
    path = Column(String(100), nullable=False)
    status_code = Column(Integer, nullable=False)
    message = Column(String(100), nullable=False)

    created_time = Column(DateTime, server_default=func.now())
