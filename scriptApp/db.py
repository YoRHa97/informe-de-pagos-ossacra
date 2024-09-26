from sqlalchemy import create_engine, Column, ForeignKey, String, Integer, BigInteger, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///:memory:')

session = sessionmaker(bind=engine)()

Base = declarative_base()

class Provider(Base):
    __tablename__ = "provider"
    id = Column("id", Integer, primary_key=True)
    code = Column("code", Integer, nullable=False)
    name = Column("name", String(100), nullable=False)
    cuit = Column("cuit", BigInteger, nullable=False)
    email = Column("email", String(50), nullable=False)
    cc = Column("cc", String(50), nullable=False)
    payment_orders = relationship("PayOrder", backref="provider")
    def __repr__(self):
        return f"{self.code}"


class PayOrder(Base):
    __tablename__ = "pay_order"
    id = Column("id", Integer, primary_key=True)
    number = Column("number", Integer, unique=True, nullable=False)
    invoice = Column("invoice", String(30), nullable=False)
    provider_code = Column(Integer, ForeignKey('provider.code'))
    transfer = relationship("Transfer", uselist=False, backref="pay_order")
    def __repr__(self):
        return f"{self.number}"


class Transfer(Base):
    __tablename__ = "transfer"
    id = Column("id", Integer, primary_key=True)
    number = Column("number", BigInteger, unique=True, nullable=False)
    amount = Column("amount", Float, nullable=False)
    state = Column("state", String(50), nullable=False)
    date = Column("date", String(10), nullable=False)
    pay_order_number = Column(Integer, ForeignKey('pay_order.number'), unique=True)
    def __repr__(self):
        return f"{self.number}"

Base.metadata.create_all(bind=engine)
