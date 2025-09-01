cabinet_prefix = "https://image.rakuten.co.jp/giftoftw/cabinet"


class ProductDescriptionData:
    def __init__(self, shop_code, product_id, image_amount,
                 description, features, highlights, product_info):
        self.shop_code = shop_code
        self.product_id = product_id

        self.images = self._build_image_urls(shop_code, product_id, image_amount)
        self.description = [p.strip() for p in description if p.strip()]
        self.features = [{"title": "", "content": f.strip()} for f in features if f.strip()]
        self.highlights = [h.strip() for h in highlights if h.strip()]
        self.product_info = [{"name": k, "value": v} for k, v in product_info.items()]

    @staticmethod
    def _build_image_urls(shop_code: str, product_id: str, image_amount):
        urls = []
        shop_en = shop_code.split("-")[-1]
        for i in range(image_amount):
            img_path = f"{shop_code}-{product_id}_{i + 1:02}.jpg"
            full_url = f"{cabinet_prefix}/{shop_en}/{img_path}"
            # 可以加入檢查檔案是否存在，這裡假設都存在
            urls.append(full_url)
        return urls

    def to_dict(self):
        return {
            "images": self.images,
            "description": self.description,
            "features": self.features,
            "highlights": self.highlights,
            "product_info": self.product_info
        }

# if __name__ == '__main__':
# product_data = ProductToJSON(
#     shop_code="tra-immoto",
#     prduct_id="03",
#     image_amount=8,
#     description="""
# "✓スピーディーな染毛で、ヘアケアとスカルプケアが同時に完了
# ✓独自の植物由来染毛剤
# ✓においがなく無毒、頭皮や肌への刺激なし
#
# 泡カラー ヘアカラー
# 白髪専用泡カラー
# 白髪専用ヘアカラー
# 泡状ヘアカラー
# ヘアケアカラークリーム
# 植物由来泡カラー
# ヘアケアカラー
# シャンプーカラー
# 台湾圭宝ヘアカラー
#
# 【製品の特徴】
#
# ✓15分ですばやく染毛、ヘアケア、スカルプケアの3つの効果が同時に完了
# ✓均一に色づき、白髪をすばやくカバー
# ✓独自の植物由来染毛剤（ヘナ、何首烏、甘草）
# ✓無臭で無毒、髪を傷めず、頭皮や肌への刺激なし
# ✓成分にラノリン（羊油）を配合。トリートメント（ヘアケア）効果も
# ✓山芙蓉を特別に配合。リグナンが髪を黒くし抜け毛を防止
# ✓1箱10パック入り
# ✓独立した小分け包装。量を正確に調節できてムダがなく、お財布にも環境にもやさしい
#
# 【製品仕様】
#
# 圭宝山芙蓉泡カラー - 染毛、ヘアケア、スカルプケアが同時に完了
# カラー：ナチュラルブラック / ダークブラウン / マロンレッド
# 内容量：10ml*10パック / 1箱
#
# 【使い方】
# 髪を水で濡らし、8割ほど乾かします。泡カラーを直接髪に付けて、シャンプーするように泡立ててもみ込み、15分間待ちます。その後水で洗い流し、シャンプーで一度洗髪すれば、染毛プロセスが完了します。"
# """,
#     features="""
# 独自の植物由来染毛剤で、15分ですばやく染毛、ヘアケア、スカルプケアの3つの効果が同時に完了します。独立した小分け包装で、量を正確に調節できムダがなく、お財布にも環境にもやさしく、均一に色づき、白髪をすばやくカバーします
# """,
#     highlights="""
# 15分ですばやく染毛、ヘアケア、スカルプケアの3つの効果が同時に完了
# 独自の植物由来染毛剤（ヘナ、何首烏、甘草）
# 白髪をすばやくカバー。無臭で無毒、髪を傷めず、頭皮や肌への刺激なし
# 成分にラノリン（羊油）を配合。トリートメント（ヘアケア）効果も。山芙蓉に含まれるリグナンが髪を黒くし、抜け毛を防止
# 独立した小分け包装。1箱10包入り。量を正確に調節できてムダがなく、お財布にも環境にもやさしい
# """,
#     product_info="""
# 規格名稱	カラー：ダークブラウン、ナチュラルブラック、マロンレッド
# "    詳細成分"
# 第1剤/主成分
# Resorcinol.
# 2.4-Diamincphenoxyethanol HCT
# 第1剤/その他の成分
# Water, Sodium Laureth Sulfate, Propylene Cilycol, Moncethanolamine, Lancilin, Fragrance, Sodium Sulfulfte
# L-Ascortic Acid, Dipotassum Glycymbizinate, Desdium EDTA, Vranamin E Acctate, Hiscus Tarwarsis Extract
# Rosemary Extract, Henna, Polygoni Mution Radiri Radix.
# 第2剤/主成分
# Hyctrogen peroxide
# 第2剤/その他の成分
# Water, Ceteary! Alcobol"
# 内容量	10ml*10 /パック
# 用途	すばやく染毛、ヘアケア、スカルプケアの3つの効果
# 建議用量	1回1パック
# 製造地	台湾
# """)
