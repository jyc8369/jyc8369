from pathlib import Path

OUT = Path('assets/profile')
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {
    'dark': {
        'outer': '#070B12', 'bg': '#0D1117', 'bar': '#080E19', 'border': '#26344D',
        'card': '#101723', 'card2': '#0B1320', 'title': '#F2F6FF', 'body': '#D8E1F0',
        'muted': '#8290A8', 'a0': '#C4B5FD', 'a1': '#67E8F9',
        'a2': '#4ADE80', 'a4': '#FBBF24',
    },
    'light': {
        'outer': '#F6F8FA', 'bg': '#FFFFFF', 'bar': '#F0F3F7', 'border': '#D0D7E2',
        'card': '#F6F8FA', 'card2': '#FFFFFF', 'title': '#1F2328', 'body': '#24292F',
        'muted': '#6E7781', 'a0': '#8250DF', 'a1': '#0969DA',
        'a2': '#1A7F37', 'a4': '#9A6700',
    },
}

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def generate(theme: str) -> str:
    c = THEMES[theme]
    height = 740
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="About jyc8369">
  <defs>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{c['a0']}"><animate attributeName="stop-color" values="{c['a0']};{c['a1']};{c['a2']};{c['a0']}" dur="12s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="{c['a1']}"><animate attributeName="stop-color" values="{c['a1']};{c['a2']};{c['a0']};{c['a1']}" dur="12s" repeatCount="indefinite"/></stop>
    </linearGradient>
  </defs>
  <rect width="1200" height="{height}" rx="34" fill="{c['outer']}"/>
  <rect x="20" y="20" width="1160" height="700" rx="28" fill="{c['bg']}" stroke="{c['border']}" stroke-width="2"/>
  <path d="M48 20H1152Q1180 20 1180 48V72H20V48Q20 20 48 20Z" fill="{c['bar']}"/>
  <circle cx="48" cy="46" r="6" fill="#FF5F56"/>
  <circle cx="70" cy="46" r="6" fill="#FFBD2E"/>
  <circle cx="92" cy="46" r="6" fill="#27C93F"/>
  <text x="600" y="51" text-anchor="middle" fill="{c['muted']}" font-size="14" font-family="{FONT}">jyc8369@github: ~/profile $ cat about.txt</text>
  <rect x="20" y="71" width="1160" height="2" fill="url(#accent)"/>

  <g font-family="{FONT}">
    <text x="70" y="142" fill="{c['title']}" font-size="34" font-weight="700">I build software around friction I can actually see.</text>
    <text x="70" y="184" fill="{c['body']}" font-size="17">
      <tspan x="70" dy="0">I start from repetitive, inconvenient, or unnecessarily complicated workflows.</tspan>
      <tspan x="70" dy="29">Then I turn that friction into focused tools and small services I can actually use.</tspan>
    </text>

    <g transform="translate(70 255)">
      <rect width="515" height="165" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
      <rect x="20" y="20" width="8" height="125" rx="4" fill="{c['a0']}"/>
      <text x="52" y="43" fill="{c['a0']}" font-size="17" font-weight="700">01 · Notice real friction</text>
      <text x="52" y="78" fill="{c['body']}" font-size="14">
        <tspan x="52" dy="0">Start from a concrete inconvenience, not a feature list.</tspan>
        <tspan x="52" dy="24">Look for repetition, confusing steps, and wasted time.</tspan>
      </text>
      <text x="52" y="141" fill="{c['body']}" font-size="13">Problem first · features second</text>
    </g>

    <g transform="translate(615 255)">
      <rect width="515" height="165" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
      <rect x="20" y="20" width="8" height="125" rx="4" fill="{c['a1']}"/>
      <text x="52" y="43" fill="{c['a1']}" font-size="17" font-weight="700">02 · Build a usable fix</text>
      <text x="52" y="78" fill="{c['body']}" font-size="14">
        <tspan x="52" dy="0">Keep the scope small enough to understand,</tspan>
        <tspan x="52" dy="24">but complete enough to be useful in practice.</tspan>
      </text>
      <text x="52" y="141" fill="{c['body']}" font-size="13">Utilities · developer tools · automation</text>
    </g>

    <g transform="translate(70 450)">
      <rect width="1060" height="180" rx="20" fill="{c['card']}" stroke="{c['border']}"/>
      <rect x="20" y="20" width="8" height="140" rx="4" fill="{c['a2']}"/>
      <text x="52" y="43" fill="{c['a2']}" font-size="17" font-weight="700">03 · Learn from operation</text>
      <text x="52" y="80" fill="{c['body']}" font-size="14">
        <tspan x="52" dy="0">Deploy what I build and learn what becomes difficult</tspan>
        <tspan x="52" dy="24">once software leaves localhost.</tspan>
        <tspan x="52" dy="31">Failures become feedback for the next design, deployment,</tspan>
        <tspan x="52" dy="24">and operational decision.</tspan>
      </text>

      <path d="M700 24V156" stroke="{c['border']}" stroke-width="1.5"/>
      <text x="735" y="38" fill="{c['muted']}" font-size="12" font-weight="700" letter-spacing="1.5">CURRENT DIRECTION</text>
      <g transform="translate(735 52)">
        <rect width="265" height="32" rx="16" fill="{c['card2']}" stroke="{c['a2']}" stroke-width="1.5"/>
        <text x="132.5" y="21" text-anchor="middle" fill="{c['a2']}" font-size="13" font-weight="700">DEVOPS</text>
      </g>
      <g transform="translate(735 94)">
        <rect width="265" height="32" rx="16" fill="{c['card2']}" stroke="{c['a1']}" stroke-width="1.5"/>
        <text x="132.5" y="21" text-anchor="middle" fill="{c['a1']}" font-size="13" font-weight="700">SYSTEMS ENGINEERING</text>
      </g>
      <g transform="translate(735 136)">
        <rect width="265" height="32" rx="16" fill="{c['card2']}" stroke="{c['a4']}" stroke-width="1.5"/>
        <text x="132.5" y="21" text-anchor="middle" fill="{c['a4']}" font-size="13" font-weight="700">RELIABILITY</text>
      </g>
    </g>

    <g transform="translate(70 650)">
      <rect width="1060" height="55" rx="17" fill="{c['card2']}" stroke="{c['border']}"/>
      <text x="22" y="22" fill="{c['a1']}" font-size="12" font-weight="700" letter-spacing="1.3">LONG-TERM GOAL</text>
      <text x="22" y="42" fill="{c['body']}" font-size="14">Connect development decisions with reliable system operation and real user needs.</text>
    </g>
  </g>
</svg>
'''


for theme in THEMES:
    path = OUT / f'about-{theme}.svg'
    path.write_text(generate(theme), encoding='utf-8')
    print(path)
