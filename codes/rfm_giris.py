"""
Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
pazarlama stratejileri belirlemek istiyor.

 Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.
# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara.
C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke."""

#İŞ PROBLEMİ
import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', None) #Tüm sutunları yazdırma
# pd.set_option('display.max_rows', None) #Tüm satırları yazdırma

#sayısal değişkenlerin virgülden sonra kaç basamağını göstermeliyim?
pd.set_option('display.float_format', lambda x: '%.3f' % x)
#2010-2011 yap
df_= pd.read_excel("/Users/sevvalhaticeoter/PycharmProjects/CRM_Analytıc/datasets/online_retail_II.xlsx",sheet_name= "Year 2009-2010")
df=df_.copy() #verinin büyüklüğünden dolayı daha sonra kolay okunması için kopyalama yaptık
#Veriyi tanıyalım.


df.head()
#Invoicelar çoklama durumunda çünkü fatura bilgisinde birden fazla ürün olabilir.

df.shape()
df.isnull.sum()
#eksik değerleri ölçülebilirlik değeri taşımadığından dolayı sileceğiz.

df["Description"].nunique() #eşsiz ürün sayısı nedir?

df["Description"].value_counts().head()

df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity",ascending=False).head()

df["Invoice"].nunique() #eşsiz fatura sayısı

df["TotalPrice"]=df["Quantity"] * df["Price"] #ürünlerin priceı

df.groupby("Invoice").agg({"TotalPrice": "sum"}).head() #invoice başına toplam ne kadar ödendi?


#Veri Hazırlama
df.dropna(inplace=True) #kalıcı olarak na değerlerini uçurma
df.desribe().T

df=df[df["Invoice"].str.contains("C",na=False)]
#iade olan değişkenleri gözlemleme quantityleri - li


df=df[~df["Invoice"].str.contains("C",na=False)]
#başında c olanları ifadeleri df den attık

#RFM Metriklerinin Hesaplanması
"""
Her bir müşteri özelinde rfm değerlerini hesaplamak istiyoruz.
Recency:Analizin yapıldığı tarih-ilgili müşterinin son satın alma yaptığı tarih,müşterinin yeni ve sıcaklığı
Frequency:Müşterinin yaptığı toplam satın alma.
Monetary: Müşterinin  toplam satın almalar neticesinde bıraktığı toplam
"""
df.head()

df["InvoiceDate"].max() #müşterinin son satın alma tarihi

today_date = dt.datetime(2010, 12, 11)
type(today_date)
#InvoiceDate.max() kullanıcının son alışveriş yaptığı tarih
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()

#Değişkenlerin isimlerini değiştirme
rfm.columns = ['recency', 'frequency', 'monetary']

rfm.describe().T
#min değeri sıfır gelsin istemiyorum.
rfm = rfm[rfm["Monetary"] > 0] #Bu metrikleri skorlara çevirmeliyiz
rfm.shape

###############################################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
###############################################################

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
#bana bir değişken ver bu değişkeni kaça böleceğimi söyle böldükten sonra etiketlere
#hangi değeri vereceğimi söyle.
# 0-100, 0-20, 20-40, 40-60, 60-80, 80-100
rfm["frequency_score"] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5])
#hata çok fazla tekrar eden değişken olduğundan daha fazla aralığa hep aynı değerler geldiğinden rank kullandık.
#ilk gördüğünü ilk sınıfa ata.

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
#ilk gördüğünü ilk sınıfa ata.

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

#2 BOYUTLU DF DE RFM Skorunu hesaplamak içi RF DEĞERLERİ YETERLİ
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"] #şampiyon sınıf

rfm[rfm["RFM_SCORE"] == "11"] #loser sınıfı

###############################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
###############################################################
# regex araştır.

# RFM isimlendirmesi,segment map
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True) #birleştirilen skorlar seg_map
#regex true segmentleri birleştirir.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "cant_loose"].head()
rfm[rfm["segment"] == "cant_loose"].index

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index

new_df["new_customer_id"] = new_df["new_customer_id"].astype(int) #ondalıklılardan kurtulma

new_df.to_csv("new_customers.csv") #departmanımızda diğer kişilerin anlaması için çeviri
#dizinde yeni bir csv oluşur.

rfm.to_csv("rfm.csv")  #tüm segment bilgileri csv olarak çıkar.

###############################################################
# 7. Tüm Sürecin Fonksiyonlaştırılması(SCRİPTE ÇEVİRMESİ)
###############################################################

def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))

    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv") #çıktının csv sini oluşturma ama bir özellik olarak eklenir.

    return rfm

df = df_.copy()

rfm_new = create_rfm(df, csv=True)
