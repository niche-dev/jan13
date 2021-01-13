from bs4 import BeautifulSoup
import requests
import pymysql

class Stock:
    #建構式
    def __init__(self, *stock_numbers):
        self.stock_numbers = stock_numbers
    
    #爬取
    def scrape(self):
	
        result = list()  #最終結果
    
        for stock_number in self.stock_numbers:
            
            response = requests.get(
                "https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
                
            stock_date = soup.find(
                "font", {"class": "tt"}).getText().strip()[-9:]  #資料日期
                
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:11]  #取得表格中1到10格
            
            result.append((stock_date,) +
                tuple(td.getText().strip() for td in tds))
                
        return result


    def save(self, stocks):
         
        db_settings = {
            "host": "us-cdbr-east-03.cleardb.com",
            "port": 3306,
            "user": "xxx",
            "password": "xxx",
            "db": "xxx",
            "charset": "utf8"
        }

        try:
            conn = pymysql.connect(**db_settings)
            
            with conn.cursor() as cursor:
                sql = """INSERT INTO market(
                            market_date,
                            stock_name,
                            market_time,
                            final_price,
                            buy_price,
                            sell_price,
                            ups_and_downs,
                            lot,
                            yesterday_price,
                            opening_price,
                            highest_price,
                            lowest_price)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
                for stock in stocks:
                    cursor.execute(sql, stock)
                conn.commit()
 
        except Exception as ex:
            print("Exception:", ex)

if __name__ == "__main__":
    stock = Stock('0051', '0052')  #建立Stock物件
    print(stock.scrape())
    stock.save(stock.scrape())  # 將爬取的結果存入MySQL資料庫中
