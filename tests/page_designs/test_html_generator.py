from env_settings import BASE_DIR
from scripts.page_designs.html_generator import HTMLGenerator


def test_mobile_html_generation():
    tmp_path = BASE_DIR / "page_designs" / "tmp"
    # 範例 product_data
    product_data = {
        "images": "fumeow/tra-fumeow",
        "description": "お茶は自然農法で栽培され…\n低温乾燥と熟成の製法で…",
        "features": "アソート烏龍茶ティーバッグ四角ボックス…",
        "highlights": "お茶は自然農法…\nティーバッグ素材は天然…",
        "product_info": "規格名稱\tペット烏龍茶ティーバッグ20個入りボックス\n內容量\tティーバッグ20個入り、1個3グラム"
    }

    # 先建立一個暫時 template
    template_file = tmp_path / "mobile_template.html"
    template_file.write_text(
        "{{IMAGES}}\n{{DESCRIPTION}}\n{{FEATURES}}\n{{HIGHLIGHTS}}\n{{PRODUCT_INFO}}", encoding="utf-8"
    )

    # 建立 generator
    generator = HTMLGenerator(str(template_file), image_base_url="https://image.rakuten.co.jp/giftoftw/cabinet")

    # 生成 HTML
    output_file = tmp_path / "output.html"
    generator.generate_html(product_data, str(output_file))

    # 驗證輸出存在
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "<img src=" in content
    assert "<p>" in content
    assert "<tr>" in content

    print("MobileHTMLGenerator 測試通過！")
