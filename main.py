import psycopg2

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import configparser

Base = declarative_base()

class Publisher(Base):
    __tablename__ = "publisher"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), unique=True)

    book = relationship("Book", back_populates="publisher")
    #homeworks = relationship("Homework", backref ="course")

    def __str__(self):
        return f'Publisher {self.id}: {self.name}'

class Book(Base):
    __tablename__ = "book"

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=40), unique=True)

    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"), nullable=False)


    publisher = relationship(Publisher, back_populates="book")
    stock = relationship("Stock", back_populates="book")

    def __str__(self):
        return f'Book {self.id}: {self.title}'

class Shop(Base):
    __tablename__ = "shop"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), unique=True)

    stock = relationship("Stock", back_populates="shop")

    def __str__(self):
        return f'Shop {self.id}: {self.name}'



class Stock(Base):
    __tablename__ = "stock"

    id = sq.Column(sq.Integer, primary_key=True)

    id_book = sq.Column(sq.Integer, sq.ForeignKey("book.id"), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey("shop.id"), nullable=False)

    count = sq.Column(sq.Integer)



    book = relationship(Book, back_populates="stock")
    shop = relationship(Shop, back_populates="stock")
    sale = relationship("Sale", back_populates="stock")

    def __str__(self):
        return f'Stock {self.id}: {self.id_book}: {self.id_shop}'

class Sale(Base):
    __tablename__ = "sale"

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Integer)
    date_sale = sq.Column(sq.Date)

    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)
    count = sq.Column(sq.Integer)


    stock = relationship(Stock, back_populates="sale")

    def __str__(self):
        return f'sale {self.id}: {self.date_sale}: {self.price}'

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг

password_my = config["Passwords"]["Password"]
user_my = config["Passwords"]["User"]

DSN = "postgresql://"+user_my+":"+password_my+"@localhost:5432/postgres"
engine = sq.create_engine(DSN)

#create_tables(engine)


Session = sessionmaker(bind=engine)
session = Session()

connection = engine.connect()

# with open('tests_data.json', 'r') as fd:
#     data = json.load(fd)
#
# for record in data:
#     model = {
#         'publisher': Publisher,
#         'shop': Shop,
#         'book': Book,
#         'stock': Stock,
#         'sale': Sale,
#     }[record.get('model')]
#     session.add(model(id=record.get('pk'), **record.get('fields')))
# session.commit()

name = input()
# q = session.query(Sale, Shop, Book).join(Stock.sale).join(Shop).join(Book).join(Publisher).filter(Publisher.name == name)
#
#  for c in q:
#      print(c.date_sale)


with psycopg2.connect(database="postgres", user=user_my, password=password_my) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT book.title, shop.name, sale.price, sale.date_sale FROM sale  join stock on stock.id = sale.id_stock JOIN book ON book.id = stock.id_book JOIN publisher t ON t.id = book.id_publisher JOIN shop ON shop.id = stock.id_shop WHERE t.name =%s",
                    (name,));

        python_id = cur.fetchall()
        for c in python_id:
            print('Продажи', *c, sep='|')

session.close()
