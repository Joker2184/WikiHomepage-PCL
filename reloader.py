import requests
import re
import datetime
from bs4 import BeautifulSoup

response = requests.get("https://zh.minecraft.wiki").text
obj = BeautifulSoup(response, 'html.parser')


def while_delete(del_txt, txt):
    while del_txt in txt:
        txt.remove(del_txt)


def get_news_card():
    resp = requests.get("https://news.bugjump.net/apis/versions/latest-card").text
    return resp


def gr():
    origin = obj.find('div', class_="weekly-content").text
    result = origin.strip().split("。")
    result = [i.strip("\n") for i in result]
    result = [f"<ListItem><Paragraph>{i}。</Paragraph></ListItem>" for i in result]
    links = get_link_txt(str(obj.find('div', class_="weekly-content")))
    for k, v in links.items():
        result = [i.replace(k, link_to_xaml((k, v))) if k in i else i for i in result]
    result.pop()
    return result


def get_link_txt(txt):
    raw_links = re.findall(r'<a href=".*?" title=".*?"', txt, re.S)
    links = {}
    for link in raw_links:
        key = re.findall(r'title="(.*?)"', link, re.M)[0]
        ref = re.findall(r'href="(.*?)"', link, re.M)[0]
        links[key] = "https://zh.minecraft.wiki" + ref
    return links


def link_to_xaml(lk):
    xaml = f'''<Underline><local:MyTextButton EventType="打开网页" \
    EventData="{lk[1]}" Margin="0,0,0,-8">{lk[0]}</local:MyTextButton></Underline>'''
    return xaml


def gs():
    img_src = 'https://zh.minecraft.wiki' + obj.find('div', class_='weekly-image').find('img')['src']
    img_src = re.sub(r'&', '&amp;', img_src)
    return img_src


def update():
    now = datetime.datetime.now()
    with open("Custom.xaml", "r", encoding='UTF-8') as f:
        content_text = f.read()
    with open("Custom.xaml", "w", encoding='UTF-8') as f:
        txt = re.sub(re.findall('''<Border.Background>\n<ImageBrush ImageSource="(.*?)" />\n</Border.Background><Image Source="(.*?)"/>\n</Border>''', content_text)[0],
                     f'''<Border Style="{{StaticResource HeadImageBorder}}">
<Border.Background>
<ImageBrush ImageSource="{gs()}" Stretch="UniformToFill"/>
</Border.Background>
<Image Source="{gs()}" Opacity="0" Stretch="Fill"/>
</Border>''', content_text, re.S)
        txt = re.sub(r'<sys:String x:Key="datetime">.*?</sys:String>',
                     f'<sys:String x:Key="datetime">最后更新：{now.strftime("%Y-%m-%d")}</sys:String>', txt)
        txt = re.sub(r'<sys:String x:Key="WikiPage">.*?</sys:String>', '<sys:String x:Key="WikiPage">' +
                     list(get_link_txt(f'''{obj.find('div', class_="weekly-content")}''').values())[0] +
                     "</sys:String>", txt)
        txt = re.sub(re.findall(r'<!-- NewsCard -->.*?<!-- end_NewsCard -->', txt, re.S)[0],
                     f'<!-- NewsCard -->{get_news_card()}<!-- end_NewsCard -->', txt, re.S)
        txt = re.sub(r'^<!-- introduction -->(.*?)<!-- end_introduction -->',
                     f'<!-- introduction -->{gr()[0]}<!-- end_introduction -->', txt, re.S)
        txt = re.sub(r'^<!-- intro_2 -->(.*?)<!-- end_intro_2 -->',
                     f'<!-- intro_2 -->{gr()[1]}<!-- end_intro_2 -->', txt, re.S)
        txt = re.sub(r'^<!-- body -->(.*?)<!-- end_body -->',
                     f'<!-- body -->{"".join(gr()[2:])}<!-- end_body -->', txt, re.S)
        if txt:
            f.write(txt)
        elif not txt:
            print(txt)


update()
