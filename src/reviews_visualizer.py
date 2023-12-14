from typing import List

from aqt import gui_hooks, mw
from aqt.webview import WebContent, AnkiWebView
from anki.utils import ids2str
from os.path import basename

import time

from itertools import groupby
from dataclasses import dataclass
from datetime import datetime, date, timedelta

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
    max_date: date
    due_date: date
    question: str
    logs: List[Revlog]


def create_revlog(a):
    # todo: day starting hour compensate
    return Revlog(datetime.fromtimestamp(a[0]/1000), date.fromtimestamp(a[0]/1000), a[1], a[2])


def create_plot(cards: List[Card], max_date: date):
    config = mw.addonManager.getConfig(__name__)

    box_width = config['box_width']
    box_height = config['box_height']
    image_height = config['image_height']
    due_days = config['due_days']
    show_line = config['show_line']

    content = ''
    y = 0
    max_x = 0

    if due_days > 0:
        max_date += timedelta(days=due_days)

    for card in cards:
        onclick = f"javascript:pycmd('revhm_browse:cid:{card.card_id}')"

        if card.due_date is not None and card.due_date < max_date:
            x = (max_date - card.due_date).days * (box_width + 1)
            content += f'<rect class="due" x="{x}" y="{y}" width="{box_width}" height="{box_height}" onclick=\"{onclick}\"><title>{card.due_date}</title></rect>'

        for log in card.logs:
            x = (max_date - log.date).days * (box_width + 1)
            max_x = x if x > max_x else max_x
            content += f'<rect class="a{log.ease}" x="{x}" y="{y}" width="{box_width}" height="{box_height}" onclick=\"{onclick}\"><title>{log.date}</title></rect>'

        y += box_height + 1

    max_x += box_width + 1

    html = ''
    html += f'<div style="overflow: scroll; width: 100%; height: {image_height}; border: 1px solid black">'
    html += f'<svg id="{ELEMENT_ID}" width="{max_x}" height="{y}" shape-rendering="crispEdges">'
    html += '<style>.a1 { fill: red; } .a2 { fill: blue; } .a3 { fill: green; } .a4 { fill: yellow; } .due { fill: gray; } .max_date { stroke: gray; }</style>'

    if show_line:
        x = due_days * (box_width + 1)
        html += f'<line x1={x} y1={0} x2={x} y2={y} class="max_date" />'

    html += content
    html += '</svg>'
    html += '</div>'

    return html


def webview_will_set_content(web_content: WebContent, context):
    try:
        context_name = type(context).__name__

        if context_name == 'Overview':
            html = process()
            web_content.body += html
    except:
        pass


def webview_did_inject_style_into_page(webview: AnkiWebView):
    try:
        page = basename(webview.page().url().path())

        if page == "congrats.html":
            html = process()
            js = f'if (document.getElementById("{ELEMENT_ID}") == null) document.body.innerHTML += `{html}`'
            webview.eval(js)
    except:
        pass

def attr_sort(attrs: List[str]):
    return lambda x: [getattr(x, attr) for attr in attrs]


def process():
    config = mw.addonManager.getConfig(__name__)
    card_limit = config['card_limit']

    deck_anki = mw.col.decks.current()
    #deck_name = deck_anki['name']
    deck_id = deck_anki['id']

    cards = []
    global_max_date = None

    dids = [id for (_, id) in mw.col.decks.deck_and_child_name_ids(deck_id)]

    for card_raw in mw.col.db.all(f"select c.id, c.due, c.queue from cards c where c.queue != 0 and c.did in {ids2str(dids)}"): #not new
        card_id = card_raw[0]
        due = card_raw[1]
        queue = card_raw[2]

        #card_anki = mw.col.get_card(card_id)
        #question = card_anki.question()

        question = ''

        raw = mw.col.db.all(f"select r.id, r.ease, r.type from revlog r where r.cid={card_id} and r.type != 4") #not manual

        revlogs = [create_revlog(a) for a in raw]

        items = [min(group, key=lambda x: x.datetime) for _, group in groupby(revlogs, lambda x: x.date)]

        if len(items) > 0:
            min_date = min(items, key=lambda x: x.date).date
            max_date = max(items, key=lambda x: x.date).date

            if global_max_date is None or max_date > global_max_date:
                global_max_date = max_date

            try:
                due_date = (datetime.now() + timedelta(days=due - mw.col.sched.today)).date() if queue != -1 else None
            except:
                due_date = None

            cards.append(Card(card_id, min_date, max_date, due_date, question, items))

    if len(cards) > 0:
        config = mw.addonManager.getConfig(__name__)
        order_by = config['order_by']
        order_reverse = config['order_reverse']

        order_by_list = [a.strip() for a in order_by.split(',')]
        order_by_list.append('card_id')

        cards.sort(key=attr_sort(order_by_list), reverse=order_reverse)

        if card_limit != -1:
            cards = cards[:card_limit]

        return create_plot(cards, global_max_date)

    return ''


gui_hooks.webview_will_set_content.append(webview_will_set_content)
gui_hooks.webview_did_inject_style_into_page.append(webview_did_inject_style_into_page)
