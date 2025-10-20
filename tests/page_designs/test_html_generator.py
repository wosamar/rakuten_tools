from env_settings import BASE_DIR
from handlers.html_generator import HTMLGenerator
from models.product_descript import ProductDescriptionData


def test_html_generator():
    # 範例 product_data
    product_data = {
        "shop_code":"tra-demo",
        "image_infos": [{"image_url":"","description":"","link":""}],
        "description": "お茶は自然農法で栽培され…\n低温乾燥と熟成の製法で…",
        "feature": "アソート烏龍茶ティーバッグ四角ボックス…",
        "highlight": "お茶は自然農法…\nティーバッグ素材は天然…",
        "product_info": {"規格名稱":"ペット烏龍茶ティーバッグ20個入りボックス","內容量":"ティーバッグ20個入り、1個3グラム"}
    }

    # 先建立一個暫時 template
    template_file = BASE_DIR / "tests" / "tmp" / "mobile_template.html"
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text(
        "{{IMAGES}}\n{{DESCRIPTION}}\n{{FEATURES}}\n{{HIGHLIGHTS}}\n{{PRODUCT_INFO}}", encoding="utf-8"
    )

    # 建立 generator
    generator = HTMLGenerator(str(template_file))

    # 生成 HTML
    content = generator.generate_html(ProductDescriptionData(**product_data))

    assert "<img src=" in content
    assert "<p>" in content
    assert "<tr>" in content

    print("MobileHTMLGenerator 測試通過！")
