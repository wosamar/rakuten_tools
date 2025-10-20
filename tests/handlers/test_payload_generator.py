import re
from handlers.payload_generator import CampaignPayloadGenerator

def test_generate_and_trim_title_with_brackets():
    generator = CampaignPayloadGenerator(title_format="Campaign Title: {original_title}")
    original_title = "マグカップ ガラス グラス 350ml 耐熱 コップ ティーカップ ラウンドマグ 取っ手 透明 軽量 デザイン おしゃれ シンプル プレゼント ギフト お茶 カフェ 高品質 食器【TG】【台湾直送】【送料無料】【台湾エクセレンス】"

    # Calculate widths of bracketed parts
    bracketed_texts = re.findall(r'【.*?】', original_title)
    bracketed_width = sum(generator._get_display_width(text) for text in bracketed_texts)

    # Calculate frame width
    frame_text_example = "Campaign Title: "
    frame_width = generator._get_display_width(frame_text_example)

    # Non-bracketed part of the original title
    non_bracketed_part = "マグカップ ガラス グラス 350ml 耐熱 コップ ティーカップ ラウンドマグ 取っ手 透明 軽量 デザイン おしゃれ シンプル プレゼント ギフト お茶 カフェ 高品質 食器"
    
    # Let's aim to trim the non-bracketed part to "マグカップ ガラス グラス 350ml 耐熱 コップ ティーカップ ラウンドマグ 取っ手 透明 軽量 デザイン おしゃれ シンプル プレゼント ギフト"
    target_non_bracketed_part = "マグカップ ガラス グラス 350ml 耐熱 コップ ティーカップ ラウンドマグ 取っ手 透明 軽量 デザイン おしゃれ シンプル プレゼント ギフト"
    target_non_bracketed_width = generator._get_display_width(target_non_bracketed_part)

    # Desired total width = frame_width + target_non_bracketed_width + bracketed_width
    max_width_for_test = frame_width + target_non_bracketed_width + bracketed_width

    # Calculate allowed_title_width for debugging
    allowed_title_width = max_width_for_test - frame_width - bracketed_width

    expected_result = "Campaign Title: " + target_non_bracketed_part + "【TG】【台湾直送】【送料無料】【台湾エクセレンス】"

    trimmed_title = generator._generate_and_trim_title(
        original_title=original_title,
        max_width=max_width_for_test
    )
    assert trimmed_title == expected_result

    # Test case 2: No trimming needed
    no_trim_original_title = "Short title 【BRACKET】"
    no_trim_max_width = 100
    no_trim_expected_result = "Campaign Title: Short title 【BRACKET】"
    trimmed_no_trim_title = generator._generate_and_trim_title(
        original_title=no_trim_original_title,
        max_width=no_trim_max_width
    )
    assert trimmed_no_trim_title == no_trim_expected_result

    # Test case 3: Empty original title
    empty_original_title = ""
    empty_max_width = 50
    empty_expected_result = "Campaign Title: "
    trimmed_empty_title = generator._generate_and_trim_title(
        original_title=empty_original_title,
        max_width=empty_max_width
    )
    assert trimmed_empty_title == empty_expected_result

    # Test case 4: Original title with only brackets
    only_brackets_title = "【ONLY BRACKETS】"
    only_brackets_max_width = 50
    only_brackets_expected_result = "Campaign Title: 【ONLY BRACKETS】"
    trimmed_only_brackets_title = generator._generate_and_trim_title(
        original_title=only_brackets_title,
        max_width=only_brackets_max_width
    )
    assert trimmed_only_brackets_title == only_brackets_expected_result

    # Test case 5: Original title with brackets and no other words to trim
    no_other_words_to_trim_title = "A B C 【BRACKET】"
    no_other_words_to_trim_max_width = 127 # Sufficiently large
    no_other_words_to_trim_expected_result = "Campaign Title: A B C 【BRACKET】"
    trimmed_no_other_words_to_trim_title = generator._generate_and_trim_title(
        original_title=no_other_words_to_trim_title,
        max_width=no_other_words_to_trim_max_width
    )
    assert trimmed_no_other_words_to_trim_title == no_other_words_to_trim_expected_result

def test_generate_and_trim_title_with_kwargs():
    generator = CampaignPayloadGenerator(title_format="{prefix} {original_title}")
    original_title = "This is a very long title that needs to be trimmed for the campaign."
    prefix_text = "Special Offer"
    max_width = 50

    # Manually trim original_title to fit allowed_title_width
    # "This is a very long title that needs" (width 36)
    trimmed_original_title_part = "This is a very long title that needs"

    expected_result = f"{prefix_text} {trimmed_original_title_part}"

    trimmed_title = generator._generate_and_trim_title(
        original_title=original_title,
        max_width=max_width,
        prefix=prefix_text
    )
    assert trimmed_title == expected_result
