#!/usr/bin/env python3
"""A compact, source-backed Réttarvísir retrieval illustration for GitHub.

Uses saved evaluation question 5, rrf-bge-m3-bm25-rerank, from the public
maltaekni_lokaverkefni repository. It depicts the method and final sources;
intermediate rankings, scores and real elapsed times are not asserted.
"""
from html import escape
from pathlib import Path
import re
import textwrap

PALETTES = {
    'light': dict(bg='#fbfcf9', panel='#f0f4ee', border='#ccd7cd', ink='#1c332d', muted='#51665b', teal='#087f72', tealsoft='#dff2e9', gold='#8b6823', goldsoft='#f1ead5'),
    'dark': dict(bg='#080a09', panel='#111614', border='#2d342f', ink='#f0f2ed', muted='#a5b4aa', teal='#28c6b2', tealsoft='#132f2a', gold='#d7b56d', goldsoft='#332b18'),
}
QUESTION=('Getur neytandi krafist úrbóta', 'eða nýrrar afhendingar vegna galla?')
SOURCES=[(1,'29. gr.','Úrbætur og ný afhending'),(2,'30. gr.','Framkvæmd úrbóta'),(3,'26. gr.','Úrræði vegna galla')]


def text(x,y,value,size=25,css='',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" class="{css}">{escape(value)}</text>'


def box(x,y,w,h,css='panel',rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{css}"/>'


def color_rules(theme):
    p=PALETTES[theme]
    return f'''text {{ fill: {p['ink']}; }}
.paper {{ fill: {p['bg']}; stroke: {p['border']}; }}
.panel {{ fill: {p['panel']}; stroke: {p['border']}; }}
.muted {{ fill: {p['muted']}; }}
.teal {{ fill: {p['teal']}; }}
.gold {{ fill: {p['gold']}; }}
.mark {{ fill: {p['goldsoft']}; stroke: {p['gold']}; }}
.selected {{ fill: {p['tealsoft']}; stroke: {p['teal']}; }}
.guide {{ fill: none; stroke: {p['border']}; }}
.flow {{ fill: none; stroke: {p['teal']}; }}
.travel {{ fill: {p['teal']}; }}
'''


def question(y=118, size=29):
    return '\n'.join(text(320,y+i*41,line,size,'serif','middle') for i,line in enumerate(QUESTION))


def source_row(number,article,title,y,selected=False):
    return '\n'.join([box(28,y,584,52,'selected' if selected else 'panel'),
        text(44,y+34,f'[{number}]',24,'gold'),
        text(90,y+34,article,25,'serif'),text(185,y+34,title,24)])


def stage_content(stage):
    out=[]
    if stage==0:
        out += [text(28,97,'SPURNING',19,'muted'),question(157,31),text(320,264,'A question from the evaluation set.',24,'muted','middle')]
    elif stage==1:
        out += [question(102,26),'<path class="flow" stroke-width="1.5" d="M320 158 V178 H170 V197 M320 178 H470 V197"/>',
                box(55,197,230,53),box(355,197,230,53),text(170,232,'BM25',27,'','middle'),text(470,232,'BGE-M3',27,'','middle'),
                '<path class="flow" stroke-width="1.5" d="M170 250 V270 H320 V290 M470 250 V270 H320"/>',
                text(320,318,'RRF → rerank',27,'teal','middle'),
                '<circle class="travel travel-left" r="4"/><circle class="travel travel-right" r="4"/>']
    elif stage==2:
        out += [text(28,103,'Lög um neytendakaup',28,'serif'),text(612,103,'48/2003',21,'muted','end')]
        for number,article,title in SOURCES:
            out.append(source_row(number,article,title,126+(number-1)*62,number==1))
        out += [text(28,329,'Top three sources from the saved run.',22,'muted')]
    else:
        out += answer_content()
    labels=['Ask in Icelandic','Retrieve and rerank','Read the sources','Answer with citations']
    out += [text(28,383,f'0{stage+1} / {labels[stage]}',23,'muted')]
    for i in range(4):
        out.append(box(516+i*23,369,15,5,'teal' if i<=stage else 'panel',2))
    return '\n'.join(out)


ANSWER_EXCERPT = 'Já, neytandi getur valið á milli þess að krefja seljanda um úrbætur á galla á eigin reikning seljanda eða krefjast nýrrar afhendingar [1][3]. Þessi réttur á þó ekki við ef fyrir hendi er hindrun sem seljandi ræður ekki við eða ef krafan veldur seljanda ósanngjörnum kostnaði [1].'


def answer_content():
    out=[text(28,102,'SVAR (ÚTDRÁTTUR)',19,'muted')]
    for i,line in enumerate(textwrap.wrap(ANSWER_EXCERPT,width=50)):
        # Citations retain the saved answer's exact IDs, with the app's gold colour.
        markup=re.sub(r'(\[\d\])',r'<tspan class="gold">\1</tspan>',escape(line))
        out.append(f'<text x="28" y="{136+i*29}" font-size="23">{markup}</text>')
    out += [box(28,313,170,28,'mark',4),text(113,334,'[1] 29. gr.',20,'gold','middle'),
            box(212,313,170,28,'mark',4),text(297,334,'[3] 26. gr.',20,'gold','middle')]
    return out


def render(theme='light',animated=True):
    styles=color_rules(theme)+'.serif { font-family: Georgia, Times New Roman, serif; }\n'
    if animated:
        styles+='''
.scene { opacity: 0; animation: 24s step-end infinite both; }
.final-scene { opacity: 1; }
.scene-0 { animation-name: stage-0; }
.scene-1 { animation-name: stage-1; }
.scene-2 { animation-name: stage-2; }
.scene-3 { animation-name: stage-3; }
@keyframes stage-0 { 0%, 16.666%, 100% { opacity: 1; } 16.667%, 99.999% { opacity: 0; } }
@keyframes stage-1 { 0%, 16.666%, 37.5%, 100% { opacity: 0; } 16.667%, 37.499% { opacity: 1; } }
@keyframes stage-2 { 0%, 37.499%, 58.334%, 100% { opacity: 0; } 37.5%, 58.333% { opacity: 1; } }
@keyframes stage-3 { 0%, 58.333%, 100% { opacity: 0; } 58.334%, 99.999% { opacity: 1; } }
.travel { offset-rotate: 0deg; animation: trace 2.4s linear infinite; }
.travel-left { offset-path: path('M320 158 L320 178 L170 178 L170 197'); }
.travel-right { offset-path: path('M320 158 L320 178 L470 178 L470 197'); }
@keyframes trace { 0% { offset-distance: 0%; opacity: 0; } 12% { opacity: 1; } 85% { opacity: 1; } 100% { offset-distance: 100%; opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .scene { animation: none; opacity: 0; }
  .scene.final-scene { opacity: 1; }
  .travel { animation: none; display: none; }
}
'''
    else:
        styles+='@media (prefers-color-scheme: dark) { '+color_rules('dark')+' }\n'
    out=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">',
        '<title id="title">Réttarvísir: from an Icelandic question to cited sources</title>',
        '<desc id="desc">A reconstruction of saved evaluation question 5: can a consumer request repair or replacement for a defect? The selected method combines BM25 and BGE-M3 through reciprocal rank fusion and reranking. Its top sources are articles 29, 30 and 26 of the Consumer Purchases Act. The final panel quotes the first two sentences of the recorded answer, retaining the stated exception and source citations. The diagram is illustrative, not a live search, a recording, intermediate ranking data or elapsed time.</desc>',
        f'<style>{styles}</style>',box(.5,.5,639,409,'paper',10),
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        box(28,20,31,30,'mark',3),text(43.5,43,'§',25,'gold serif','middle'),text(71,44,'Réttarvísir',28,'serif'),text(612,43,'Saved example',21,'muted','end'),
        '<path class="guide" d="M28 65 H612 M28 350 H612"/>',
    ]
    for i in range(4) if animated else (3,):
        out += [f'<g class="scene scene-{i}'+(' final-scene' if i==3 else '')+f'" data-stage="{i+1}">',stage_content(i),'</g>']
    out += ['</g>','</svg>','']
    return '\n'.join(out)


def main():
    root=Path(__file__).resolve().parents[1]/'assets'
    for filename,theme,animated in [('rettarvisir.svg','light',True),('rettarvisir-dark.svg','dark',True),('rettarvisir-static.svg','light',False)]:
        (root/filename).write_text(render(theme,animated),encoding='utf-8')

if __name__=='__main__':main()
