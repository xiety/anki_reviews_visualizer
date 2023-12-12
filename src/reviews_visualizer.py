from typing import List

from aqt import gui_hooks, mw
from aqt.webview import WebContent, AnkiWebView
from os.path import basename

from itertools import groupby
from dataclasses import dataclass
from datetime import datetime, date

ELEMENT_ID = 'REVIEWS_VISUALIZER'


@dataclass
class Revlog:
    datetime: datetime
    date: date
    ease: int
    type: int #0=learn, 1=review, 2=relearn, 3=filtered, 4=manual


@dataclass
class Card:
    card_id: int #long?
    min_date: date
    question: str
    logs: List[Revlog]


def create_revlog(a):
    # todo: day starting hour compensate
    return Revlog(datetime.fromtimestamp(a[0]/1000), date.fromtimestamp(a[0]/1000), a[1], a[2])


def create_plot(cards: List[Card]):
    box_width = 4
    box_height = 4

    max_date = cards[0].min_date

    content = ''
    y = 0
    max_x = 0

    for card in cards:
        onclick = f"javascript:pycmd('revhm_browse:cid:{card.card_id}')"

        for log in card.logs:
            x = (max_date - log.date).days * (box_width + 1)
            max_x = x if x > max_x else max_x
            content += f'<rect class="a{log.ease}" x="{x}" y="{y}" width="{box_width}" height="{box_height}" onclick=\"{onclick}\"><title>{log.date}</title></rect>'

        y += box_height + 1

    max_x += box_width + 1

    html = ''
    html += '<div style="overflow: scroll; width: 100%; height: 450px; border: 1px solid black">'
    html += f'<svg id="{ELEMENT_ID}" width="{max_x}" height="{y}">'
    html += '<style>.a1 { fill: red; } .a2 { fill: blue; } .a3 { fill: green; } .a4 { fill: yellow; }</style>'
    html += content
    html += '</svg>'
    html += '</div>'

    return html


def webview_will_set_content(web_content: WebContent, context):
    context_name = type(context).__name__

    if context_name == 'DeckBrowser':
        html = process()
        web_content.body += html


def webview_did_inject_style_into_page(webview: AnkiWebView):
    page = basename(webview.page().url().path())

    if page == "congrats.html":
        html = process()
        js = f'if (document.getElementById("{ELEMENT_ID}") == null) document.body.innerHTML += `{html}`'
        webview.eval(js)


def process():
    deck_anki = mw.col.decks.current()
    #deck_name = deck_anki['name']
    deck_id = deck_anki['id']

    cards = []

    for card_raw in mw.col.db.all(f"select c.id from cards c where c.queue != 0 and c.did = {deck_id}"): #not new
        card_id = card_raw[0]

        #card_anki = mw.col.get_card(card_id)
        #question = card_anki.question()

        question = ''

        raw = mw.col.db.all(f"select r.id, r.ease, r.type from revlog r where r.cid={card_id} and r.type != 4") #not manual

        revlogs = [create_revlog(a) for a in raw]

        items = [min(group, key=lambda x: x.datetime) for _, group in groupby(revlogs, lambda x: x.date)]

        if len(items) > 0:
            min_date = min(items, key=lambda x: x.date).date

            cards.append(Card(card_id, min_date, question, items))

    if len(cards) > 0:
        cards.sort(key=lambda x: x.min_date, reverse=True)

        return create_plot(cards)

    return ''


#gui_hooks.webview_will_set_content.append(webview_will_set_content)
gui_hooks.webview_did_inject_style_into_page.append(webview_did_inject_style_into_page)
