import sys
import json
import fileinput
import re

def clean_infobox(val):
    """
    Clean up infobox values, saving the raw value. :en
    Infobox の値を洗い出し、処理前の値も返す。:ja
    
    Infobox values are often links or include parentheticals. :en
    This removes the wiki markup from a single value. :en

    Infobox にリンクや括弧内のコメントがよくあるので、 :ja
    この関数でそのような markup を除外する。 :ja
    
    A raw Infobox looks a bit like this, including newlines: :en

    処理前の Infobox は以下のようになっている。:ja
    
      {{Infobox animanga/Game
      |ゲームジャンル=[[サウンドノベル]]
      |対応機種=[[Microsoft Windows|Windows]] ... 
    """
    raw = val
    # first remove everything before the = :en
    # まずは = までの情報を取り除く :ja
    val = val.split("=", 1)[1].strip()
    # there can be multiple values :en
    # 複数の値がある場合に対応する :ja
    vals = re.split("<br[ /]*>", val)
    # remove any parentheticals :en
    # 括弧内のコメントを除外する :ja
    vals = [re.sub("[(（][^)）]*[)）]", "", val) for val in vals]
    # remove brackets :en
    # その他の括弧を除外する :ja
    vals = [val.strip("[]") for val in vals]
    # if there are pipes, take the value after the pipe :en
    # パイプがある場合、パイプ後の文字列を使う :ja
    vals = [val.split("|", 1)[-1] for val in vals]
    # remove empty values :en
    # 空の値を除く :ja
    vals = [val for val in vals if val]
    return vals, raw


def get_infobox_value(keys, lines):
    """
    Extract a value from a value from an infobox.  :en
    Infobox から値を抽出する。 :ja
    
    keys are multiple keys, any of which are acceptable. :en
    lines are the raw lines from the page source. :en

    keys は複数のキーであり、どちらも同等に扱う。:ja
    lines はページのソースの行。:ja
    """
    alt = "|".join(keys)
    regex = f"^\| *({alt}) *="
    for line in lines:
        # for simplicity, return only the first :en
        # とりあえず最初の値のみを返す:ja
        if re.search(regex, line):
            return clean_infobox(line)
    return None, None

def prep_data(fname):
    """Given a filename, read in the Cirrus Dump data and prepare it for analysis. :en"""
    """引数のファイル名から Cirrus Dump データを読み込み、解析準備をする。:ja"""
    cleaned = []
    for line in open(fname):
        entry = json.loads(line)

        # find infobox entries :en
        # infobox のある記事を特定 :ja
        st = entry["source_text"].split("\n")
        dev, raw_dev = get_infobox_value(["開発元", "Dev"], st)
        pub, raw_pub = get_infobox_value(["発売元", "Pub"], st)
        # "opening_text" is roughly the first content paragraph. :en
        # "opening_text" は最初の段落相当 :ja
        text = entry.get("opening_text")

        # We'll only keep articles that have both a dev and publisher listed :en
        # 開発元と発売元両方の情報のある記事以外は除外する :ja
        if not (dev and pub):
            continue

        # Some articles don't have "opening_text", which is set manually :en
        # separately from the main article text. Articles with opening text :en
        # are typically higher quality. :en
        # "opening_text" は手動で登録されるので、設定されていない記事もある。 :ja
        # 一般的に、ある記事の方は質が高い。 :ja
        if not text:
            continue

        # make sure the dev is listed in the main text so it's possible to extract it :en
        # 抽出できるように、記事内に開発元の文字列が含まていることを確認 :ja
        if dev[0] not in text:
            continue

        # Now we'll save the extracted values to use in the next step. :en
        # Note that we save the raw values as well - this is important :en
        # for troubleshooting. :en
        # 抽出した値をオブジェクトに整理する。デバッグのために、処理前の値も :ja
        # 取っておこう。:ja
        out = {
            "dev": dev,
            "raw_dev": raw_dev,
            "pub": pub,
            "raw_pub": raw_pub,
            "text": entry["opening_text"],
            "title": entry["title"],
        }
        cleaned.append(out)
    return cleaned

if __name__ == "__main__":
    for item in prep_data(sys.argv[1]):
        print(json.dumps(item))
