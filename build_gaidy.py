# -*- coding: utf-8 -*-
"""Сборка дома гайдов на сайте: /gaidy/ (оглавление) + /kodovoe-slovo/ (первый гайд).
Опус, 08.07.2026. Стиль сайта iraai.ru (Inter/Outfit, красный #E50914).
Текст гайда НЕ меняется, только мета-подпись (устаревшее «лежит в телеге» → «открыт для всех»).
Запуск: python3 build_gaidy.py
"""
import re, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent
GUIDE_SRC = pathlib.Path.home() / "Desktop/ФАБЛ/ДЕНЬ-9/CHATPLACE-СВЯЗКА/03-гайд-кодовое-слово-без-конструктора.html"

# --- каталог гайдов (из ПЛАН-ГАЙДОВ.md). live=True только у готовых ---
GUIDES = [
    {"slug": "kodovoe-slovo", "live": True,
     "title": "Кодовое слово в директе без конструктора",
     "teaser": "Человек пишет вам слово в директ, робот сразу отдаёт ссылку или файл. Настраивается разговором с Клодом, без блоков и стрелочек."},
    {"slug": "kto-vryot", "live": True, "self_designed": True,
     "title": "Кто вам врёт: проверка любой «сенсации» за 10 минут",
     "teaser": "Пять промптов, чтобы закинуть статью, исследование или вирусную новость в ИИ и увидеть, что доказано, а что притянуто."},
    {"slug": "chetyre-yaschika", "live": False,
     "title": "Куда девать всё, что вы насохраняли: четыре ящика вместо ста вкладок",
     "teaser": "Структура из четырёх ящиков и правило «кинула и отпустила»."},
    {"slug": "prompt-razborschik", "live": False,
     "title": "Промпт-разборщик: разберите свой хаос заметок за один вечер",
     "teaser": "Новичковая версия разборщика, копипаст в чат. Победа в тот же вечер."},
    {"slug": "ii-dlya-vzroslyh", "live": False,
     "title": "ИИ для взрослых: с чего начать, если вы дай бог открыли чат",
     "teaser": "Карта, что бывает и что из этого нужно вам. Столп категории."},
    {"slug": "kartochka-konteksta", "live": False,
     "title": "Карточка личного контекста: почему нейросеть отвечает вам как всем",
     "teaser": "Шаблон, который один раз заполняешь и кормишь им все задачи."},
    {"slug": "erunda-ili-net", "live": False,
     "title": "Ерунда или нет: 7 проверок, чтобы нейросеть не подставила вас перед клиентом",
     "teaser": "Чек-лист, чтобы не понести чушь в свой канал или клиенту."},
    {"slug": "pyat-zadach", "live": False,
     "title": "Пять задач, которые взрослый человек отдаёт нейросети за неделю",
     "teaser": "Облегчённые скелеты: письмо, разбор документа, структура выступления."},
    {"slug": "kak-vybrat-neyroset", "live": False,
     "title": "Как выбрать свою нейросеть и не платить за три",
     "teaser": "Сравнение по-человечески, чтобы не платить за три подписки сразу."},
]

CSS = """
:root{--ink:#0d0d0d;--red:#E50914;--paper:#fff;--grey:#f2f0ec;--dim:#777;--line:#e5e2dc}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Outfit',sans-serif;color:var(--ink);background:var(--paper);line-height:1.62}
.wrap{max-width:720px;margin:0 auto;padding:0 24px}
.topbar{border-bottom:2px solid var(--ink)}
.topbar .wrap{display:flex;justify-content:space-between;align-items:center;padding:16px 24px}
.topbar a{color:var(--ink);text-decoration:none;font-family:'Inter';font-weight:800;font-size:15px}
.topbar .back{font-weight:600;color:var(--dim);font-size:13px;text-transform:uppercase;letter-spacing:.12em}
main{padding:44px 0 20px}
h1{font-family:'Inter';font-weight:800;font-size:clamp(30px,6vw,46px);line-height:1.08;text-wrap:balance;margin-bottom:6px}
h1 br{display:inline}
.kicker{font-family:'Inter';font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--red);font-weight:700;margin-bottom:16px}
.stamp{color:var(--dim);font-size:14px;margin-bottom:28px}
main h2{font-family:'Inter';font-weight:700;font-size:clamp(20px,3.4vw,26px);margin:34px 0 10px;line-height:1.2}
main p{font-size:17px;margin-bottom:14px;text-wrap:pretty}
main ul,main ol{margin:0 0 16px 22px}
main li{margin-bottom:7px;font-size:17px}
main img{max-width:100%;height:auto;border:2px solid var(--ink);margin:14px 0;display:block}
main b,main strong{font-weight:700}
main a{color:var(--red)}
code{background:var(--grey);padding:1px 6px;font-size:.92em}
.bridge{background:var(--ink);color:#fff;padding:30px 26px;margin:44px 0 0}
.bridge p{color:#fff;font-size:17px;margin:0 0 10px}
.bridge a{color:#fff;font-weight:700}
.bridge .row{display:flex;flex-direction:column;gap:14px;margin-top:6px}
.bridge .line b{color:var(--red);background:#fff;padding:0 4px}
footer{padding:30px 0 60px}
footer p{color:var(--dim);font-size:13px}
/* оглавление */
.lead{font-size:19px;margin:8px 0 30px;text-wrap:pretty}
.card{display:block;border:2px solid var(--ink);padding:22px 24px;margin-bottom:14px;text-decoration:none;color:var(--ink);transition:background .15s,color .15s}
.card:hover{background:var(--ink);color:#fff}
.card.soon{border-color:var(--line);color:var(--dim);pointer-events:none}
.card .ct{font-family:'Inter';font-weight:700;font-size:19px;line-height:1.22;margin-bottom:6px}
.card .cd{font-size:15px}
.card .tag{font-family:'Inter';font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--red);display:block;margin-bottom:8px}
.card.soon .tag{color:var(--dim)}
"""

TOPBAR = ('<div class="topbar"><div class="wrap">'
          '<a href="https://iraai.ru/">IRA<span style="color:var(--red)">&AI</span></a>'
          '<a class="back" href="/gaidy/">Все гайды</a></div></div>')

BRIDGE = ('<div class="bridge"><div class="row">'
          '<p class="line">Живое и по делу каждый день в телеге: <a href="https://telegram.me/ira_and_ai">telegram.me/ira_and_ai</a></p>'
          '<p class="line">Система целиком, а не один навык: программа «Понедельник» '
          '<a href="https://iraai.ru/ponedelnik/">iraai.ru/ponedelnik</a></p>'
          '</div></div>')

def page(title, desc, body, extra_head=""):
    return f"""<!doctype html><html lang="ru"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>{extra_head}
</head><body>
{TOPBAR}
{body}
<footer><div class="wrap">
<p style="margin-bottom:10px;"><a href="https://iraai.ru/" style="color:var(--ink);text-decoration:none;font-weight:700;">На главную</a> &nbsp;·&nbsp; <a href="/gaidy/" style="color:var(--ink);text-decoration:none;">Все гайды</a> &nbsp;·&nbsp; <a href="/rassylka/" style="color:var(--ink);text-decoration:none;">Рассылка</a> &nbsp;·&nbsp; <a href="https://telegram.me/ira_and_ai" style="color:var(--ink);text-decoration:none;">Телега</a></p>
<p>iraai.ru · Ира Буян · «ИИ для взрослых» · открыто всем, без подписок</p></div></footer>
</body></html>"""

def extract_guide_body(src):
    txt = src.read_text(encoding="utf-8")
    # содержимое внутри внешнего контейнерного div
    m = re.search(r'<div[^>]*max-width:680px[^>]*>(.*)</div>\s*$', txt, re.S)
    inner = m.group(1) if m else txt
    # выкинуть h1 и подпись-строку (сверстаем свои), вернуть остальное тело
    # убрать первый h1
    inner = re.sub(r'<h1[^>]*>.*?</h1>', '', inner, count=1, flags=re.S)
    # убрать устаревшую мета-строку про «лежит в телеге»
    inner = re.sub(r'<p[^>]*>\s*Гайд Иры Буян.*?</p>', '', inner, count=1, flags=re.S)
    return inner.strip()

# --- страница гайда: kodovoe-slovo ---
body_inner = extract_guide_body(GUIDE_SRC)
guide_body = f"""<main><div class="wrap">
<div class="kicker">Гайд · ИИ для взрослых</div>
<h1>Кодовое слово в директе<br>без конструктора</h1>
<p class="stamp">Гайд Иры Буян · «ИИ для взрослых» · июль 2026. Открыт для всех, без подписок и условий.</p>
{body_inner}
{BRIDGE}
</div></main>"""

guide_html = page(
    "Как настроить кодовое слово в директе без конструктора",
    "Пошаговый гайд Иры Буян: как настроить кодовое слово в директе Instagram через Клода, без конструктора с блоками. Живое демо, три правила, разбор ошибок.",
    guide_body)
(ROOT / "kodovoe-slovo").mkdir(exist_ok=True)
(ROOT / "kodovoe-slovo" / "index.html").write_text(guide_html, encoding="utf-8")

# --- оглавление /gaidy/ ---
cards = ""
for g in GUIDES:
    if g["live"]:
        cards += (f'<a class="card" href="/{g["slug"]}/">'
                  f'<span class="tag">Открыт</span>'
                  f'<div class="ct">{html.escape(g["title"])}</div>'
                  f'<div class="cd">{html.escape(g["teaser"])}</div></a>')
    else:
        cards += (f'<div class="card soon">'
                  f'<span class="tag">Скоро</span>'
                  f'<div class="ct">{html.escape(g["title"])}</div>'
                  f'<div class="cd">{html.escape(g["teaser"])}</div></div>')

gaidy_body = f"""<main><div class="wrap">
<div class="kicker">Библиотека · ИИ для взрослых</div>
<h1>Гайды</h1>
<p class="lead">Рабочие куски системы, каждый доводит вас до одной победы. Пишу голосом, без воды и без подписок. Новые появляются раз в неделю-полторы.</p>
{cards}
{BRIDGE}
</div></main>"""

gaidy_html = page(
    "Гайды по ИИ для взрослых · Ира Буян",
    "Библиотека практических гайдов Иры Буян по нейросетям для нетехнических экспертов. Каждый гайд доводит до одной рабочей победы. Без воды и подписок.",
    gaidy_body)
(ROOT / "gaidy").mkdir(exist_ok=True)
(ROOT / "gaidy" / "index.html").write_text(gaidy_html, encoding="utf-8")

print("собрано: /kodovoe-slovo/index.html + /gaidy/index.html")
