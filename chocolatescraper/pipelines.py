# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import mysql.connector


class ChocolatescraperPipeline:
    def process_item(self, item, spider):
        return item


class PriceToUSDPipeline:
    gdpToUsdRate = 1.3

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('price'):
            floatPrice = float(adapter['price'])

            adapter['price'] = floatPrice * self.gdpToUsdRate

            return item

        else:

            raise DropItem(f"Missing price in {item}")


class DuplicatePipeline:

    def __init__(self):
        self.name_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter['name'] in self.name_seen:
            raise DropItem(f"Duplicate item found : {item}")

        else:
            self.name_seen.add(adapter['name'])
            return item


class SavingToMysqlPipeline(object):
    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.connection=mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='chocolate_scraping',
            port='3306'
        )

        self.curr=self.connection.cursor()

    def process_item(self, item, spider):

        self.store_db(item)
        return item

    def store_db(self,item):
        self.curr.execute("""insert into products (name,price,url) values(%s,%s,%s)""",(
            item['name'],
            item['price'],
            item['url'],
        ))
        self.connection.commit()
