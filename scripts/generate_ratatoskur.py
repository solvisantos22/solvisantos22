#!/usr/bin/env python3
"""An inline, scripted Ratatoskur lesson for the GitHub profile.

Content follows ratatoskur-website/src/components/simulator/demo-content.ts
and ratatoskur_ios/api_contract_examples/query_confirm_reading.json.
It is an illustration of a fixed example, not a recording or a live AI response.
"""
from pathlib import Path

PALETTES = {
    'light': dict(bg='#fffcf6', border='#d9d1c5', ink='#3c1d11', muted='#785e47', guide='#e7dccb', accent='#9b521f', highlight='#f2d6aa', good='#285944'),
    'dark': dict(bg='#191c20', border='#3d434a', ink='#f1e8da', muted='#c3b6a3', guide='#383734', accent='#f0b779', highlight='#66401d', good='#91c4a6'),
}


def color_rules(theme):
    p=PALETTES[theme]
    return '\n'.join((
        f'.paper {{ fill: {p["bg"]}; stroke: {p["border"]}; }}',
        f'text {{ fill: {p["ink"]}; }}',
        f'.muted {{ fill: {p["muted"]}; }}',
        f'.accent {{ fill: {p["accent"]}; }}',
        f'.highlight {{ fill: {p["highlight"]}; }}',
        f'.guide {{ stroke: {p["guide"]}; }}',
        f'.good {{ fill: {p["good"]}; }}',
    ))


def text(x,y,content,size=26,css='',anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" class="{css}">{content}</text>'


def stage_content(stage):
    result=[]
    if stage==0:
        result += [text(320,153,'2x + 3 = 11',58,'math'), text(320,216,'Find x.',28,'muted')]
    elif stage==1:
        result += [text(320,130,'2x + 3 = 11',53,'math'), text(320,196,'−3',36,'math accent'), text(320,245,'Subtract 3 from both sides.',26,'muted')]
    elif stage==2:
        result += [text(320,118,'2x = 8',47,'math'), text(320,189,'x = 4',56,'math'), text(320,245,'Divide both sides by 2.',26,'muted')]
    elif stage==3:
        result += [text(320,128,'2x + <tspan class="accent">?</tspan> = 11',53,'math'), text(320,199,'Is the unclear symbol a 3?',27,'accent'), text(320,244,'Confirm the reading before checking.',23,'muted')]
    else:
        result += [text(320,106,'2x + 3 = 11',38,'math muted'), text(320,155,'2x = 8',38,'math muted'), text(320,211,'x = 4',56,'math'), text(320,255,'2 × 4 + 3 = 11',28,'math good')]
    labels=['Write the problem','Ask for a hint','Continue the working','Confirm the reading','Check the solution']
    result += [text(28,307,f'0{stage+1} / {labels[stage]}',23,'muted','start')]
    for i in range(5):
        result.append(f'<rect x="{494+i*22}" y="293" width="14" height="5" rx="2" class="'+('accent' if i<=stage else 'highlight')+'"/>')
    return '\n'.join(result)


def render(theme='light',animated=True):
    styles=color_rules(theme)+'\n.math { font-family: Georgia, Times New Roman, serif; }\n.accent { stroke: none; }\n'
    # Discrete changes keep different equations from overlapping. Each stage
    # remains readable for 3.6 seconds before the next one appears.
    if animated:
        styles+='\n.lesson-stage { opacity: 0; animation: 18s step-end infinite both; }\n.final-stage { opacity: 1; }\n'
        intervals=[('0%, 19.999%, 100% { opacity: 1; } 20%, 99.999% { opacity: 0; }'),
                   ('0%, 19.999%, 40%, 100% { opacity: 0; } 20%, 39.999% { opacity: 1; }'),
                   ('0%, 39.999%, 60%, 100% { opacity: 0; } 40%, 59.999% { opacity: 1; }'),
                   ('0%, 59.999%, 80%, 100% { opacity: 0; } 60%, 79.999% { opacity: 1; }'),
                   ('0%, 79.999%, 100% { opacity: 0; } 80%, 99.999% { opacity: 1; }')]
        for i,frames in enumerate(intervals):
            styles+=f'.stage-{i} {{ animation-name: lesson-{i}; }}\n@keyframes lesson-{i} {{ {frames} }}\n'
        styles+='@media (prefers-reduced-motion: reduce) { .lesson-stage { animation: none; opacity: 0; } .lesson-stage.final-stage { opacity: 1; } }\n'
    else:
        styles+='@media (prefers-color-scheme: dark) { '+color_rules('dark')+' }\n'
    parts=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="334" viewBox="0 0 640 334" role="img" aria-labelledby="title desc">',
        '<title id="title">A scripted Ratatoskur maths lesson</title>',
        '<desc id="desc">Solve 2x + 3 = 11. A hint suggests subtracting 3 from both sides. The student writes 2x = 8, then x = 4. An uncertain symbol is confirmed as 3 before the solution is checked: 2 times 4 plus 3 equals 11. This is a fixed illustration based on the prototype, not an app recording. '+('The 18-second loop repeats; collapse the surrounding section to hide it.' if animated else 'Static view of the completed solution.')+'</desc>',
        f'<style>{styles}</style>',
        '<rect class="paper" x=".5" y=".5" width="639" height="333" rx="10"/>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        text(28,40,'Ratatoskur',23,'','start'),
        text(612,40,'Guided example',21,'muted','end'),
        '<path class="guide" d="M 28 59 H 612 M 28 275 H 612" fill="none"/>',
    ]
    for i in range(5) if animated else (4,):
        parts.extend([f'<g class="lesson-stage stage-{i}'+(' final-stage' if i==4 else '')+f'" data-step="{i+1}">',stage_content(i),'</g>'])
    parts.extend(['</g>','</svg>',''])
    return '\n'.join(parts)


def main():
    root=Path(__file__).resolve().parents[1]/'assets'
    for filename,theme,animated in [('ratatoskur.svg','light',True),('ratatoskur-dark.svg','dark',True),('ratatoskur-static.svg','light',False)]:
        (root/filename).write_text(render(theme,animated),encoding='utf-8')

if __name__=='__main__':main()
