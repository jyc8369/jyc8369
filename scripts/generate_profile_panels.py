from pathlib import Path
from html import escape

OUT = Path('assets/profile')
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {
    'dark': {
        'outer':'#070B12','bg':'#0D1117','bar':'#080E19','border':'#26344D','card':'#101723','card2':'#0B1320',
        'title':'#F2F6FF','body':'#D8E1F0','muted':'#8290A8','faint':'#5D6B82',
        'a0':'#C4B5FD','a1':'#67E8F9','a2':'#4ADE80','a3':'#F9A8D4','a4':'#FBBF24',
        'grid':'#26344D'
    },
    'light': {
        'outer':'#F6F8FA','bg':'#FFFFFF','bar':'#F0F3F7','border':'#D0D7E2','card':'#F6F8FA','card2':'#FFFFFF',
        'title':'#1F2328','body':'#24292F','muted':'#6E7781','faint':'#8A949F',
        'a0':'#8250DF','a1':'#0969DA','a2':'#1A7F37','a3':'#BF3989','a4':'#9A6700',
        'grid':'#D8DEE8'
    },
}

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

def start_svg(width, height, aria, c, command):
    return f'''<svg
  xmlns="http://www.w3.org/2000/svg"
  width="{width}"
  height="{height}"
  viewBox="0 0 {width} {height}"
  role="img"
  aria-label="{escape(aria)}"
>
  <defs>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{c['a0']}">
        <animate attributeName="stop-color" values="{c['a0']};{c['a1']};{c['a2']};{c['a0']}" dur="12s" repeatCount="indefinite"/>
      </stop>
      <stop offset="1" stop-color="{c['a1']}">
        <animate attributeName="stop-color" values="{c['a1']};{c['a2']};{c['a0']};{c['a1']}" dur="12s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" rx="34" fill="{c['outer']}"/>
  <rect x="20" y="20" width="1160" height="{height-40}" rx="28" fill="{c['bg']}" stroke="{c['border']}" stroke-width="2"/>
  <path d="M48 20H1152Q1180 20 1180 48V72H20V48Q20 20 48 20Z" fill="{c['bar']}"/>
  <circle cx="48" cy="46" r="6" fill="#FF5F56"/>
  <circle cx="70" cy="46" r="6" fill="#FFBD2E"/>
  <circle cx="92" cy="46" r="6" fill="#27C93F"/>
  <text x="600" y="51" text-anchor="middle" fill="{c['muted']}" font-size="14" font-family="{FONT}">{escape(command)}</text>
  <rect x="20" y="71" width="1160" height="2" fill="url(#accent)"/>
  <g font-family="{FONT}">
'''

def end_svg():
    return '  </g>\n</svg>\n'

def multiline_text(x, y, lines, fill, size, dy=27, weight=None, anchor=None):
    attrs = f'x="{x}" y="{y}" fill="{fill}" font-size="{size}"'
    if weight: attrs += f' font-weight="{weight}"'
    if anchor: attrs += f' text-anchor="{anchor}"'
    spans=''.join(f'<tspan x="{x}" dy="{0 if i==0 else dy}">{escape(line)}</tspan>' for i,line in enumerate(lines))
    return f'    <text {attrs}>{spans}</text>\n'

def card(x,y,w,h,c,accent,title,body_lines, title_size=17, body_size=14, stripe=True, footer=None):
    s=f'''    <g transform="translate({x} {y})">
      <rect width="{w}" height="{h}" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
'''
    tx=28
    if stripe:
        s+=f'      <rect x="20" y="20" width="8" height="{h-40}" rx="4" fill="{accent}"/>\n'
        tx=52
    s+=f'      <text x="{tx}" y="43" fill="{accent}" font-size="{title_size}" font-weight="700">{escape(title)}</text>\n'
    if body_lines:
        spans=''.join(f'<tspan x="{tx}" dy="{0 if i==0 else 24}">{escape(line)}</tspan>' for i,line in enumerate(body_lines))
        s+=f'      <text x="{tx}" y="78" fill="{c["body"]}" font-size="{body_size}">{spans}</text>\n'
    if footer:
        s+=f'      <text x="{tx}" y="{h-24}" fill="{c["muted"]}" font-size="13">{escape(footer)}</text>\n'
    s+='    </g>\n'
    return s


def about(theme):
    c=THEMES[theme]; h=700
    s=start_svg(1200,h,'About jyc8369',c,'jyc8369@github: ~/profile $ cat about.txt')
    s+='    <text x="70" y="142" fill="%s" font-size="36" font-weight="700">I build software around friction I can actually see.</text>\n' % c['title']
    s+=multiline_text(70,184,[
        'I start from repetitive, inconvenient, or unnecessarily complicated workflows.',
        'Then I turn that friction into focused tools and small services I can actually use.'
    ],c['body'],16,27)
    s+=card(70,265,515,165,c,c['a0'],'01 · Notice real friction',[
        'Start from a concrete inconvenience, not a feature list.',
        'Look for repetition, confusing steps, and wasted time.'
    ], footer='Problem first · features second')
    s+=card(615,265,515,165,c,c['a1'],'02 · Build a usable fix',[
        'Keep the scope small enough to understand,',
        'but complete enough to be useful in practice.'
    ], footer='Utilities · developer tools · automation')
    s+=f'''    <g transform="translate(70 460)">
      <rect width="1060" height="150" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
      <rect x="20" y="20" width="8" height="110" rx="4" fill="{c['a2']}"/>
      <text x="52" y="43" fill="{c['a2']}" font-size="17" font-weight="700">03 · Learn from operation</text>
      <text x="52" y="78" fill="{c['body']}" font-size="14"><tspan x="52" dy="0">Deploy what I build and learn what becomes difficult once software leaves localhost.</tspan><tspan x="52" dy="24">Failures become feedback for the next design, deployment, and operational decision.</tspan></text>
      <g transform="translate(720 34)">
        <rect width="280" height="32" rx="16" fill="{c['card2']}" stroke="{c['a2']}"/>
        <text x="140" y="21" text-anchor="middle" fill="{c['a2']}" font-size="13" font-weight="700">DEVOPS</text>
        <rect y="42" width="280" height="32" rx="16" fill="{c['card2']}" stroke="{c['a1']}"/>
        <text x="140" y="63" text-anchor="middle" fill="{c['a1']}" font-size="13" font-weight="700">SYSTEMS ENGINEERING</text>
        <rect y="84" width="280" height="32" rx="16" fill="{c['card2']}" stroke="{c['a4']}"/>
        <text x="140" y="105" text-anchor="middle" fill="{c['a4']}" font-size="13" font-weight="700">RELIABILITY</text>
      </g>
    </g>
'''
    s+=multiline_text(70,650,[
        'Long-term goal: connect development decisions with reliable system operation and real user needs.'
    ],c['muted'],14,24)
    return s+end_svg()


def values(theme):
    c=THEMES[theme]; h=670
    s=start_svg(1200,h,'What I value',c,'jyc8369@github: ~/profile $ cat values.txt')
    s+='    <text x="70" y="142" fill="%s" font-size="36" font-weight="700">Convenience and efficiency are the starting point.</text>\n' % c['title']
    s+=multiline_text(70,184,[
        'Useful software should remove unnecessary work instead of moving complexity onto the user.',
        'I prefer clear workflows, practical results, and improvements that can be felt immediately.'
    ],c['body'],16,27)
    items=[
        (70,270,c['a0'],'01','Convenience',['Reduce unnecessary effort so the user can focus','on the task they actually care about.']),
        (620,270,c['a1'],'02','Efficiency',['Prefer fewer steps, less repetition, and a faster','path to the same reliable result.']),
        (70,440,c['a2'],'03','Practicality',['A small project is valuable when it solves a clear','problem and fits into a real workflow.']),
        (620,440,c['a3'],'04','Iteration',['Ship a usable version, observe the next friction,','then improve the workflow step by step.']),
    ]
    for x,y,a,num,title,lines in items:
        s+=f'''    <g transform="translate({x} {y})">
      <rect width="510" height="145" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
      <text x="28" y="40" fill="{a}" font-size="13" font-weight="700">{num}</text>
      <text x="72" y="41" fill="{a}" font-size="18" font-weight="700">{title}</text>
      <path d="M28 58H482" stroke="{c['border']}"/>
      <text x="28" y="88" fill="{c['body']}" font-size="14"><tspan x="28" dy="0">{escape(lines[0])}</tspan><tspan x="28" dy="24">{escape(lines[1])}</tspan></text>
    </g>
'''
    return s+end_svg()


def lifecycle(theme):
    c=THEMES[theme]; h=720
    s=start_svg(1200,h,'Learning through small services',c,'jyc8369@github: ~/profile $ ./operate')
    s+='    <text x="70" y="142" fill="%s" font-size="36" font-weight="700">Build. Deploy. Observe. Debug. Improve.</text>\n' % c['title']
    s+=multiline_text(70,184,[
        'I build and deploy small services to experience the software lifecycle beyond development.',
        'When something fails, I use the incident as feedback for the next run.'
    ],c['body'],16,27)
    s+=f'''    <path id="flow" d="M110 330H1090" fill="none" stroke="{c['border']}" stroke-width="4" stroke-linecap="round"/>
    <circle r="8" fill="{c['a1']}"><animateMotion dur="8s" repeatCount="indefinite"><mpath href="#flow"/></animateMotion></circle>
'''
    stages=[(110,c['a0'],'01','BUILD'),(355,c['a1'],'02','DEPLOY'),(600,c['a2'],'03','OBSERVE'),(845,c['a3'],'04','DEBUG'),(1090,c['a4'],'05','IMPROVE')]
    for x,a,num,label in stages:
        s+=f'''    <g transform="translate({x} 330)">
      <circle r="34" fill="{c['card2']}" stroke="{a}" stroke-width="2.5"/>
      <text y="6" text-anchor="middle" fill="{a}" font-size="14" font-weight="700">{num}</text>
      <text y="75" text-anchor="middle" fill="{c['title']}" font-size="17" font-weight="700">{label}</text>
    </g>
'''
    learn=[
        (70,c['a0'],'Deployment reality',['What changes outside localhost,','and what environments developers need.']),
        (435,c['a2'],'Useful signals',['Which logs, metrics, and state','actually help during incidents.']),
        (800,c['a4'],'Operational leverage',['Where automation and prevention','remove repetitive operational work.']),
    ]
    for x,a,title,lines in learn:
        s+=card(x,465,330,145,c,a,title,lines,title_size=16,body_size=13,stripe=False)
    s+='    <text x="70" y="665" fill="%s" font-size="14">CI/CD · Linux · Containers · Networking · Observability · Reliability</text>\n' % c['muted']
    return s+end_svg()


def projects(theme):
    c=THEMES[theme]; h=820
    s=start_svg(1200,h,'Featured projects',c,'jyc8369@github: ~/profile $ ls featured-projects')
    s+=multiline_text(70,138,['Projects built around problems','I actually wanted to solve'],c['title'],34,42,'700')
    s+=multiline_text(70,238,[
        'Each project starts from a concrete inconvenience, then becomes a tool, extension,',
        'or experiment that can be used in practice rather than remaining only an idea.'
    ],c['body'],16,27)
    items=[
        (70,330,c['a0'],'Minecraft Mod Translator Gemini',[
            'Translates Minecraft mod language files with Gemini,',
            'then rebuilds a translated copy of the mod package.'
        ],'Python · Gemini API · automation'),
        (620,330,c['a1'],'Codex Multi Login',[
            'A VS Code extension for managing multiple Codex',
            'accounts and switching between them more easily.'
        ],'TypeScript · VS Code · developer tooling'),
        (70,555,c['a2'],'Icon Bundler',[
            'Converts source images into Windows ICO and macOS',
            'ICNS files for application packaging.'
        ],'Python · desktop utility · packaging'),
        (620,555,c['a3'],'Cost Aware Agent Router',[
            'Routes reasoning-heavy work to stronger available',
            'agents while keeping deterministic execution local.'
        ],'Codex plugin · agent routing · local execution'),
    ]
    for x,y,a,title,lines,footer in items:
        s+=card(x,y,510,185,c,a,title,lines,title_size=16,body_size=14,footer=footer)
    return s+end_svg()


def stack(theme):
    c=THEMES[theme]; h=780
    s=start_svg(1200,h,'Programming languages and current direction',c,'jyc8369@github: ~/profile $ cat stack.txt')
    s+='    <text x="70" y="142" fill="%s" font-size="36" font-weight="700">Tools I use. Systems I want to understand.</text>\n' % c['title']
    s+=multiline_text(70,184,[
        'Programming languages are tools for building the things I need today.',
        'DevOps and Systems Engineering are the direction I want to grow toward over time.'
    ],c['body'],16,27)
    s+='    <text x="70" y="272" fill="%s" font-size="14" font-weight="700">LANGUAGES</text>\n' % c['muted']
    langs=[
        (70,295,c['a0'],'Python','Automation · desktop utilities · API integrations'),
        (70,390,c['a1'],'TypeScript','VS Code extensions · developer tooling'),
        (70,485,c['a2'],'JavaScript · Shell','Web utilities · system and workflow automation'),
        (70,580,c['a3'],'HTML / CSS','Simple web interfaces · supporting UIs'),
    ]
    for x,y,a,name,desc in langs:
        s+=f'''    <g transform="translate({x} {y})">
      <rect width="500" height="78" rx="18" fill="{c['card']}" stroke="{c['border']}"/>
      <rect x="20" y="18" width="8" height="42" rx="4" fill="{a}"/>
      <text x="52" y="34" fill="{a}" font-size="17" font-weight="700">{escape(name)}</text>
      <text x="52" y="58" fill="{c['body']}" font-size="13">{escape(desc)}</text>
    </g>
'''
    s+='    <text x="630" y="272" fill="%s" font-size="14" font-weight="700">DIRECTION · DEVOPS / SYSTEMS ENGINEERING</text>\n' % c['muted']
    s+='    <text x="630" y="305" fill="%s" font-size="13">Focus areas — not a hierarchy</text>\n' % c['faint']
    chips=[
        (630,335,c['a0'],'Linux'),(885,335,c['a1'],'CI/CD'),
        (630,425,c['a2'],'Containers'),(885,425,c['a3'],'Networking'),
        (630,515,c['a1'],'Observability'),(885,515,c['a4'],'Reliability'),
    ]
    for x,y,a,label in chips:
        s+=f'''    <g transform="translate({x} {y})">
      <rect width="225" height="68" rx="18" fill="{c['card2']}" stroke="{a}" stroke-width="2"/>
      <circle cx="28" cy="34" r="7" fill="{a}"/>
      <text x="50" y="40" fill="{c['title']}" font-size="16" font-weight="700">{label}</text>
    </g>
'''
    s+=f'''    <g transform="translate(630 620)">
      <rect width="480" height="100" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
      <text x="24" y="32" fill="{c['a2']}" font-size="13" font-weight="700">GOAL</text>
      <text x="24" y="60" fill="{c['body']}" font-size="13"><tspan x="24" dy="0">Understand how software is built, deployed, operated, observed,</tspan><tspan x="24" dy="22">and recovered when something goes wrong.</tspan></text>
    </g>
'''
    return s+end_svg()

GENERATORS={'about':about,'values':values,'lifecycle':lifecycle,'projects':projects,'stack':stack}
for name,fn in GENERATORS.items():
    for theme in THEMES:
        path=OUT/f'{name}-{theme}.svg'
        path.write_text(fn(theme),encoding='utf-8')
        print(path)
