# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()
PASSWORD = os.getenv('PASSWORD')

class ProjectScrapyPipeline:

    def clean_currency(self,item,currency_col):
        adapter = ItemAdapter(item)
        currency_str = adapter.get(currency_col)
        adapter[currency_col] = float(currency_str.replace('£',''))
        return item
    
    def clean_price(self,item):
        return self.clean_currency(item,"price")
    
    def clean_price_tax(self,item):
        return self.clean_currency(item,"price_tax")
    
    def clean_tax(self,item):
        return self.clean_currency(item,"tax")


    def clean_availability(self,item):
        adapter = ItemAdapter(item)
        availability = adapter.get('availability')
        adapter['availability'] = int(re.search(r'(\d+)',availability).group(0))
        return item
    
    def clean_number_of_reviews(self,item):
        adapter = ItemAdapter(item)
        adapter["number_of_reviews"] = int(adapter.get("number_of_reviews"))
        return item


    def process_item(self, item, spider):
        item = self.clean_price(item)
        item = self.clean_price_tax(item)
        item = self.clean_tax(item)
        item = self.clean_availability(item)
        item = self.clean_number_of_reviews(item)
        return item
    

class DataBasePipeline:
    
    def open_spider(self, spider):
        try:
            self.connection = pymysql.connect(
                host="localhost",
                user="root",
                password=PASSWORD,
                database="BooksScrapy" 
            )
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1049:
                raise Exception("Erreur : La base de données 'BooksScrapy' n'existe pas.")
            elif e.args[0] == 1045:
                raise Exception("Erreur : Accès refusé pour l'utilisateur 'root'@'localhost' (mot de passe incorrect).")
            else:
                raise Exception(f"Erreur de connexion : {e}")

        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    image TEXT,
                    description TEXT,
                    UPC TEXT,
                    product_type TEXT,
                    price FLOAT,
                    price_tax FLOAT,
                    tax FLOAT,
                    availability INTEGER,
                    number_of_reviews INTEGER
                );
            """)
            self.connection.commit()
        except Exception as e:
            self.connection.close()
            raise Exception(f"Erreur lors de la création de la table : {e}")



    def process_item(self, item, spider):
        self.cursor.execute("""
            INSERT INTO books (title, image, description, UPC, product_type, price, price_tax, tax, availability, number_of_reviews)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            item['title'],
            item['image'],
            item['description'],
            item['UPC'],
            item['product_type'],
            item['price'],
            item['price_tax'],
            item['tax'],
            item['availability'],
            item['number_of_reviews']
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
