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
    product_id = Column(String(50), nullable=False)  # 商品流水號
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
        UniqueConstraint('product_id', 'shop_id', name='uq_product_shop'),
    )

    @property
    def manage_number(self):
        """生成管理編號，格式為 '專案名-商店名-商品代號'"""
        try:
            # 確保 shop 和 project 關聯物件都已載入
            if self.shop and self.shop.project:
                project_name = self.shop.project.name
                shop_name = self.shop.name
                product_id = self.product_id
                return f"{project_name}-{shop_name}-{product_id}"
            return None
        except Exception:
            return None


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(100), nullable=False)

    created_time = Column(DateTime, server_default=func.now())

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product = relationship("Product", back_populates="images")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    path = Column(String(100), nullable=False)
    description = Column(String(100), nullable=False)

    created_time = Column(DateTime, server_default=func.now())
    updated_time = Column(DateTime, server_default=func.now())


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(50), nullable=False)
    path = Column(String(100), nullable=False)
    status_code = Column(Integer, nullable=False)
    message = Column(String(100), nullable=False)

    created_time = Column(DateTime, server_default=func.now())
