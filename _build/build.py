#!/usr/bin/env python3
"""Genera il sito statico di giovannitedesco.it.

Uso: python3 _build/build.py   (scrive il sito nella cartella principale del repository; le immagini stanno in img/)
Produce: / (inglese), /it/ (italiano), /works/<slug>/ e /it/opere/<slug>/, sitemap.xml, robots.txt.
"""
import html, json, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from works import WORKS, DEEP_GEAR, Y
from i18n_en import PAIRS

SITE = 'https://giovannitedesco.it'
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, '..'))
WBASE = {'en': '/works/', 'it': '/it/opere/'}
HOME = {'en': '/', 'it': '/it/'}
LANGS = ('en', 'it')

def work_url(w, lang): return WBASE[lang] + w['slug'][lang] + '/'
def gear(w, lang):
    g = w.get('gear')
    if not g: return []
    rows = DEEP_GEAR[lang]
    if w['id'] == 'andromeda':  # Giovanni non cita correttore e N.I.N.A. per Andromeda
        rows = [r for r in rows if r[0] not in ('Correttore', 'Corrector', 'Software')]
    if w['id'] == 'velo':  # descrizione interrotta: solo i dati certi
        rows = rows[:2]
    return rows

def data_js(lang):
    W, E = [], []
    for w in WORKS:
        t = w[lang]
        o = dict(id=w['id'], img=w['img'], w=w['w'], h=w['h'], t=t['t'], k=t['k'], d=t['d'], look=t['look'], then=t['then'],
                 tab=t['tab'] + gear(w, lang), p=t['body'], cat=w['cat'], iso=w['iso'])
        if 'dl' in t: o['dl'] = t['dl']
        if w.get('badge'): o['badge'] = 'NASA APOD'
        if w.get('journey'):
            o['secs'] = w['secs']; W.append(o)
        else:
            E.append(o)
    rd = {w['id']: list(w['ra']) for w in WORKS if w.get('ra')}
    if lang == 'en':
        rd['luna'] = ['Moon', '384,400 km']; rd['saturno'] = ['Saturn', '']
        rd = {k: [x.replace('AR ', 'RA ') for x in v] for k, v in rd.items()}
    slugs = {w['id']: w['slug'][lang] for w in WORKS}
    j = lambda x: json.dumps(x, ensure_ascii=False)
    return (f"const Y={Y};\nconst W={j(W)};\nconst E={j(E)};\nconst RD={j(rd)};\n", j(slugs)[1:-1])

def build_main(lang):
    s = open(os.path.join(SRC, 'src/main.html'), encoding='utf-8').read()
    if lang == 'en':
        for a, b in PAIRS:
            if a not in s: raise SystemExit('Coppia non trovata: ' + a[:100])
            s = s.replace(a, b)
    data, slugs = data_js(lang)
    s = s.replace('/*DATA*/\n', data)
    s = s.replace("/*CFG*/const LANG='it',WBASE='/it/opere/',SLUG={/*SLUGS*/};", f"const LANG='{lang}',WBASE='{WBASE[lang]}',SLUG={{{slugs}}};")
    s = s.replace('{{CANON}}', SITE + HOME[lang]).replace('{{LANG}}', lang)
    s = s.replace("ALL.forEach(x=>{x.cat=META[x.id][0];x.iso=META[x.id][1]});", '')
    return s

# ---------- pagine delle opere ----------
L = {
 'it': dict(home='Home', portfolio='Portfolio', journey='Viaggio nel tempo', editions='Edizioni', contact='Contatti', lang='Lingua', moon='Luna',
            light='la luce che vedi è partita', ago='fa', details='Scheda tecnica', zoom='Ingrandisci', prev='Opera precedente', next='Opera successiva',
            edition='Disponibile in edizione limitata', from_='da', ed_cta='Scopri le edizioni', ig='Scrivi a Giovanni', back='Tutte le opere',
            by='foto di Giovanni Esteban Tedesco', contact_h='Contatti', contact_p='Per collaborazioni, mostre e stampe, Giovanni risponde su Instagram.',
            ig_btn='@g.tedesco_ su Instagram', copy="© 2026 Giovanni Esteban Tedesco · Brindisi, Puglia · Tutte le immagini sono dell'autore.",
            close='Chiudi', hint='Rotella o pizzico per ingrandire · trascina per muoverti', apod='Ripubblicata da NASA APOD', creator_job='Astrofotografo',
            phases=("piena", "nuova", "crescente", "calante"), moon_t='Luna', moon_aria='Luna oggi: {p}% illuminata, {ph}', eur=lambda n: f'{n} €', loc='Brindisi, Italia',
            title_suffix='Giovanni Esteban Tedesco, astrofotografo'),
 'en': dict(home='Home', portfolio='Portfolio', journey='Journey in time', editions='Editions', contact='Contact', lang='Language', moon='Moon',
            light='the light you see set off', ago='ago', details='Technical details', zoom='Zoom', prev='Previous work', next='Next work',
            edition='Available as a limited edition', from_='from', ed_cta='Discover the editions', ig='Write to Giovanni', back='All works',
            by='photo by Giovanni Esteban Tedesco', contact_h='Contact', contact_p='For collaborations, exhibitions and prints, Giovanni replies on Instagram.',
            ig_btn='@g.tedesco_ on Instagram', copy='© 2026 Giovanni Esteban Tedesco · Brindisi, Apulia, Italy · All images by the author.',
            close='Close', hint='Scroll or pinch to zoom · drag to move', apod='Reposted by NASA APOD', creator_job='Astrophotographer',
            phases=("full", "new", "waxing", "waning"), moon_t='Moon', moon_aria='Moon today: {p}% illuminated, {ph}', eur=lambda n: f'€{n}', loc='Brindisi, Italy',
            title_suffix='Giovanni Esteban Tedesco, astrophotographer'),
}

def main_css():
    s = open(os.path.join(SRC, 'src/main.html'), encoding='utf-8').read()
    return re.search(r'<style>(.*?)</style>', s, re.S).group(1)

WORK_CSS = """
.wk-page header.solid{background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(8px)}
.wk-hero{position:relative;height:min(86svh,980px);min-height:420px;overflow:hidden;display:grid;place-items:center;padding:80px 4vw 20px}
.wk-hero button{padding:0;cursor:zoom-in;display:flex;align-items:center;justify-content:center;max-width:100%;max-height:100%}
.wk-hero img{width:auto;height:auto;max-width:92vw;max-height:calc(min(86svh,980px) - 110px);mix-blend-mode:screen;-webkit-mask-image:radial-gradient(ellipse closest-side,#000 62%,transparent);mask-image:radial-gradient(ellipse closest-side,#000 62%,transparent);opacity:0;transform:scale(.94);transition:opacity 1.2s ease,transform 1.6s cubic-bezier(.22,.8,.2,1)}
.wk-hero img.small{max-height:52svh;-webkit-mask-image:radial-gradient(ellipse closest-side,#000 30%,transparent 62%);mask-image:radial-gradient(ellipse closest-side,#000 30%,transparent 62%)}
.wk-hero.in img{opacity:1;transform:none}
.wk-hero .ret{width:min(72svh,84vw);left:50%;top:calc(50% + 30px);transform:translate(-50%,-50%) rotate(var(--h,0deg));opacity:0;transition:opacity 1.4s ease .3s}
.wk-hero.in .ret{opacity:.55}
.wk-hero .zh{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);font-size:12px;color:var(--mute)}
.wk{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:clamp(28px,5vw,80px);align-items:start}
.crumb{font-size:13px;color:var(--mute);margin-bottom:14px}.crumb a{color:var(--mute)}
.wk h1{font-size:calc(clamp(38px,5vw,64px)*var(--ds));margin:12px 0 26px}
.wk .lede{font-size:19px;line-height:1.55;color:var(--ink)}
.wk p{color:#cfcfd5}
.wk blockquote{margin:30px 0;padding:0;font-family:var(--fd);font-style:italic;font-size:calc(26px*var(--ds));line-height:1.3;color:var(--oiii)}
.wk blockquote::after{content:"";display:block;width:76px;height:40px;margin-top:10px;background:url(/img/firma.png) left center/contain no-repeat;opacity:.8}
.side{position:sticky;top:90px;display:grid;gap:22px}
.side h2{font:600 13px var(--fb);color:var(--mute);margin:0 0 4px}
.edbox{padding:22px 22px 18px}.edbox b{display:block;font-family:var(--fd);font-weight:var(--dw);font-size:calc(28px*var(--ds));margin:4px 0 12px}
.edbox span{font-size:13px;color:var(--mute)}
.wnav{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}
.wnav a{display:flex;align-items:center;gap:16px;padding:16px;text-decoration:none;color:inherit;--c:var(--line)}
.wnav a:hover{--c:var(--ha)}
.wnav a.nx{flex-direction:row-reverse;text-align:right}
.wnav img{width:72px;height:72px;object-fit:cover;border-radius:50%;flex:none}
.wnav small{display:block;font-size:12px;color:var(--mute)}.wnav b{font-family:var(--fd);font-weight:var(--dw);font-size:calc(20px*var(--ds))}
#zoom{position:fixed;inset:0;z-index:60;background:var(--bg);display:none;touch-action:none;cursor:grab}
#zoom.open{display:block}#zoom img{position:absolute;left:0;top:0;transform-origin:0 0;max-width:none;user-select:none;-webkit-user-drag:none}
#zoom .vb{position:absolute;top:12px;right:12px;z-index:2}
#zoom .zh{position:absolute;bottom:16px;left:50%;transform:translateX(-50%);font-size:13px;color:var(--mute);white-space:nowrap}
@media(max-width:900px){.wk{grid-template-columns:minmax(0,1fr)}.side{position:static}}
@media(max-width:600px){.wnav{grid-template-columns:1fr}.wnav a.nx{flex-direction:row;text-align:left}.wk-hero{height:72svh;padding-top:70px}.wk-hero img{max-height:calc(72svh - 100px)}}
"""

def esc(x): return html.escape(x, quote=True)
def strip(x): return re.sub(r'<[^>]+>', '', x)

def header(lang, alt_href):
    l = L[lang]; h = HOME[lang]
    other = 'it' if lang == 'en' else 'en'
    links = {lang: '', other: alt_href}
    return f'''<header id="top" class="solid">
  <a class="sig" href="{h}" aria-label="{l['home']}"></a>
  <div class="langs" role="navigation" aria-label="{l['lang']}"><a class="fr{' on' if lang=='en' else ''}" hreflang="en" lang="en" href="{alt_href if lang=='it' else '#'}" data-lang="en"{' aria-current="true"' if lang=='en' else ''}>EN</a><a class="fr{' on' if lang=='it' else ''}" hreflang="it" lang="it" href="{alt_href if lang=='en' else '#'}" data-lang="it"{' aria-current="true"' if lang=='it' else ''}>IT</a></div>
  <div class="moon" id="moon" role="img" aria-label="{l['moon']}"><span class="md"><svg viewBox="-1 -1 2 2" aria-hidden="true"><path id="moonP" d=""/></svg></span><span class="mt" id="moonT"></span></div>
  <button class="menu fr" id="menu" aria-expanded="false" aria-controls="mnav">Menu</button>
  <nav id="mnav"><a href="{h}" class="fr">{l['home']}</a><a href="{h}#portfolio" class="fr keep on">{l['portfolio']}</a><a href="{h}#viaggio" class="fr">{l['journey']}</a><a href="{h}#edizioni" class="fr">{l['editions']}</a><a href="#contatti" class="fr">{l['contact']}</a></nav>
</header>'''

ICON = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="5.5" fill="none" stroke="currentColor"/><path d="M8 0v4M8 12v4M0 8h4M12 8h4" stroke="currentColor"/></svg>'

def ring_svg(a, b):
    import math
    ticks = ''.join(f'<line x1="{100+99*math.sin(i*5*math.pi/180):.2f}" y1="{100-99*math.cos(i*5*math.pi/180):.2f}" x2="{100+(99-(8 if i%18==0 else 4 if i%6==0 else 2))*math.sin(i*5*math.pi/180):.2f}" y2="{100-(99-(8 if i%18==0 else 4 if i%6==0 else 2))*math.cos(i*5*math.pi/180):.2f}" opacity=".5"/>' for i in range(72))
    return (f'<svg viewBox="0 0 200 200"><circle cx="100" cy="100" r="99" opacity=".35"/><circle cx="100" cy="100" r="93" opacity=".12"/>{ticks}'
            '<line x1="100" y1="-6" x2="100" y2="10" class="ha"/><line x1="100" y1="190" x2="100" y2="206" class="ha"/><line x1="-6" y1="100" x2="10" y2="100" class="ha"/><line x1="190" y1="100" x2="206" y2="100" class="ha"/>'
            f'<text x="106" y="-7" style="font-size:4.6px">{esc(a)}</text><text x="106" y="211" style="font-size:4.6px">{esc(b)}</text></svg>')

FMT = [(45, 'A4'), (85, 'A3'), (160, 'A2')]

def work_page(w, lang, prev, nxt):
    l = L[lang]; t = w[lang]; h = HOME[lang]
    url = SITE + work_url(w, lang)
    other = 'it' if lang == 'en' else 'en'
    alt_href = work_url(w, other)
    body = t['body']
    first = strip(body[0]) if body else t['t']
    desc = (first[:152].rsplit(' ', 1)[0] + '…') if len(first) > 155 else first
    title = f"{strip(t['t'])} · {l['title_suffix']}"
    paras = ''
    lede = True
    for p in body:
        if p.startswith(('«', '“')):
            paras += f'<blockquote>{p}</blockquote>'
        else:
            paras += f'<p class="{"lede" if lede else ""}">{p}</p>'; lede = False
    meta_line = ' · '.join(x for x in (t['k'], t['d']) if x)
    light = ''
    if t.get('look'):
        then_html = f'<em>{t["then"]}</em>' if t['then'] else ''
        light = f'<div class="vlight"><span>{l["light"]}</span><b>{t["look"]} {l["ago"]}</b>{then_html}</div>'
    coord = ''
    if w.get('ra') and w['ra'][0].startswith('AR'):
        ra = w['ra'] if lang == 'it' else [x.replace('AR ', 'RA ') for x in w['ra']]
        coord = f'<div class="vcoord">{ICON}{ra[0]} · {ra[1]}</div>'
    stats = ''
    if t.get('dl'):
        stats = '<div class="vstats">' + ''.join(f'<div class="fr"><b>{esc(b)}</b><span>{esc(a)}</span></div>' for a, b in t['dl']) + '</div>'
    apod = f'<p class="apodl"><b style="color:var(--ha)">★ {l["apod"]}</b></p>' if w.get('badge') else ''
    spec_rows = t['tab'] + gear(w, lang)
    spec = ''
    if spec_rows:
        spec = f'<div><h2>{l["details"]}</h2><dl class="spec">' + ''.join(f'<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in spec_rows) + '</dl></div>'
    edbox = ''
    if w.get('ed'):
        sizes = ' · '.join(f for _, f in FMT[:w['ed']])
        edbox = f'<div class="edbox fr"><span>{l["edition"]}</span><b>{sizes}</b><div style="margin-top:6px"><a class="btn fr" href="{h}#edizioni">{ICON} {l["ed_cta"]}</a></div></div>'
    ig = f'<div><a class="btn fr quiet" href="https://www.instagram.com/g.tedesco_/" target="_blank" rel="noopener">{l["ig"]}</a></div>'
    small = ' class="small"' if w['w'] < 600 else ''
    ra = w.get('ra') or (t['t'], '')
    if lang == 'en' and w['id'] == 'luna': ra = ('Moon', '384,400 km')
    if lang == 'en' and w['id'] == 'saturno': ra = ('Saturn', '')
    if lang == 'en': ra = tuple(x.replace('AR ', 'RA ') for x in ra)
    navl = lambda x, cls, lab: f'<a class="fr {cls}" href="{work_url(x, lang)}"><img src="/img/t/{x["img"]}" alt="" loading="lazy"><span><small>{lab}</small><b>{esc(strip(x[lang]["t"]))}</b></span></a>'
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Photograph", "@id": url + "#photo", "name": strip(t['t']), "url": url, "image": SITE + '/img/' + w['img'],
         "description": first, "inLanguage": lang, "creator": {"@id": SITE + "/#giovanni"},
         **({"dateCreated": w['iso']} if w.get('iso') else {}), "copyrightHolder": {"@id": SITE + "/#giovanni"}},
        {"@type": "Person", "@id": SITE + "/#giovanni", "name": "Giovanni Esteban Tedesco", "jobTitle": l['creator_job'], "url": SITE + "/", "sameAs": ["https://www.instagram.com/g.tedesco_/"]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Giovanni Esteban Tedesco", "item": SITE + h},
            {"@type": "ListItem", "position": 2, "name": l['portfolio'], "item": SITE + h + "#portfolio"},
            {"@type": "ListItem", "position": 3, "name": strip(t['t']), "item": url}]}]}
    phases = l['phases']
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#08080a">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="{lang}" href="{url}">
<link rel="alternate" hreflang="{other}" href="{SITE + alt_href}">
<link rel="alternate" hreflang="x-default" href="{SITE + work_url(w, 'en')}">
<link rel="icon" type="image/png" sizes="32x32" href="/img/icon-32.png">
<link rel="apple-touch-icon" href="/img/icon-180.png">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/img/{w['img']}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;1,6..96,400&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}{WORK_CSS}</style>
</head>
<body class="wk-page">
<canvas id="sky" aria-hidden="true"></canvas>
{header(lang, alt_href)}
<main>
 <section class="wk-hero" id="hero">
  <button id="zbtn" aria-label="{l['zoom']}: {esc(strip(t['t']))}"><img src="/img/{w['img']}" width="{w['w']}" height="{w['h']}" alt="{esc(strip(t['t']))}, {l['by']}"{small}></button>
  <div class="ret" aria-hidden="true">{ring_svg(*ra)}</div>
 </section>
 <section class="band" style="padding-top:clamp(24px,4vw,48px)">
  <div class="wrap wk">
   <article>
    <div class="crumb"><a href="{h}#portfolio">{l['back']}</a></div>
    <div class="lbl">{esc(meta_line)}</div>
    <h1>{t['t']}</h1>
    {apod}{light}{coord}{stats}
    {paras}
   </article>
   <aside class="side">{edbox}{spec}{ig}</aside>
  </div>
  <div class="wrap wnav">{navl(prev, 'pv', l['prev'])}{navl(nxt, 'nx', l['next'])}</div>
 </section>
</main>
<footer id="contatti">
  <h2 style="font-size:clamp(30px,4vw,44px)">{l['contact_h']}</h2>
  <p style="margin:16px 0 26px">{l['contact_p']}</p>
  <a class="btn fr" href="https://www.instagram.com/g.tedesco_/" target="_blank" rel="noopener">{ICON} {l['ig_btn']}</a>
  <p style="margin-top:44px">{l['copy']}</p>
</footer>
<div id="zoom" role="dialog" aria-modal="true" aria-label="{esc(strip(t['t']))}"><img id="zimg" src="/img/{w['img']}" alt="" width="{w['w']}" height="{w['h']}"><button class="vb fr" id="zclose" aria-label="{l['close']}">✕</button><div class="zh">{l['hint']}</div></div>
<script>
{{
const $=s=>document.querySelector(s),reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
requestAnimationFrame(()=>$('#hero').classList.add('in'));
/* menu */
const hd=$('#top'),mb=$('#menu');mb.onclick=()=>{{const o=hd.classList.toggle('open');mb.setAttribute('aria-expanded',o);mb.textContent=o?'{l['close']}':'Menu'}};
/* moon */
{{const d2r=Math.PI/180,T=(Date.now()/864e5+2440587.5-2451545)/36525,n=x=>((x%360)+360)%360;
 const D=n(297.8501921+445267.1114034*T),M=n(357.5291092+35999.0502909*T),Mp=n(134.9633964+477198.8675055*T);
 const i=180-D-6.289*Math.sin(Mp*d2r)+2.1*Math.sin(M*d2r)-1.274*Math.sin((2*D-Mp)*d2r)-.658*Math.sin(2*D*d2r)-.214*Math.sin(2*Mp*d2r)-.11*Math.sin(D*d2r);
 const k=(1+Math.cos(i*d2r))/2,wax=D<180,pc=Math.round(k*100),rx=Math.abs(1-2*k).toFixed(3);
 $('#moonP').setAttribute('d',wax?`M0,-1 A1,1 0 0 0 0,1 A${{rx}},1 0 0 ${{k<.5?0:1}} 0,-1Z`:`M0,-1 A1,1 0 0 1 0,1 A${{rx}},1 0 0 ${{k<.5?1:0}} 0,-1Z`);
 const ph=pc>=99?'{phases[0]}':pc<=1?'{phases[1]}':wax?'{phases[2]}':'{phases[3]}';
 $('#moonT').innerHTML=`{l['moon_t']} <b>${{pc}}%</b> · ${{ph}}`;$('#moon').setAttribute('aria-label',`{l['moon_aria']}`.replace('{{p}}',pc).replace('{{ph}}',ph))}}
/* stars */
const cv=$('#sky'),cx=cv.getContext('2d');let S=[];
const size=()=>{{const d=Math.min(devicePixelRatio||1,2),W=innerWidth,H=innerHeight;cv.width=W*d;cv.height=H*d;cx.setTransform(d,0,0,d,0,0);cx.clearRect(0,0,W,H);
 for(let i=0;i<W*H/2600;i++){{const z=Math.random();cx.globalAlpha=.25+z*.6;cx.fillStyle=Math.random()<.1?'#ffb3a3':Math.random()<.3?'#c6d9ff':'#fff';cx.beginPath();cx.arc(Math.random()*W,Math.random()*H,z*1.3+.2,0,6.28);cx.fill()}}}};
size();addEventListener('resize',size);
/* reticle tilt */
let mx=0,my=0,sR=0,gy=false,cur=0,vel=0,last=performance.now();const ret=$('.wk-hero .ret');
addEventListener('pointermove',e=>{{mx=e.clientX/innerWidth-.5;my=e.clientY/innerHeight-.5}});
if(window.DeviceOrientationEvent&&!reduce){{addEventListener('deviceorientation',e=>{{if(e.gamma==null)return;gy=true;sR+=(Math.max(-30,Math.min(30,e.gamma))*.5-sR)*.12}});
 if(typeof DeviceOrientationEvent.requestPermission==='function')addEventListener('click',()=>{{try{{DeviceOrientationEvent.requestPermission().catch(()=>{{}})}}catch(e){{}}}},{{once:true}})}}
const fine=matchMedia('(pointer:fine)').matches;
const tick=()=>{{const now=performance.now(),k=Math.min(3,(now-last)/16.7);last=now;const tg=gy?sR:fine?mx*16:0;vel=vel*Math.pow(.84,k)+(tg-cur)*.03*k;cur+=vel*k;ret.style.setProperty('--h',cur.toFixed(2)+'deg');requestAnimationFrame(tick)}};
if(!reduce)requestAnimationFrame(tick);
/* zoom */
const Z=$('#zoom'),zi=$('#zimg');let sc=1,tx=0,ty=0,fit=1;
const ap=()=>zi.style.transform=`translate(${{tx}}px,${{ty}}px) scale(${{sc}})`;
const rs=()=>{{fit=Math.min(innerWidth/{w['w']},innerHeight/{w['h']})*.94;sc=fit;tx=(innerWidth-{w['w']}*sc)/2;ty=(innerHeight-{w['h']}*sc)/2;ap()}};
const za=(f,px,py)=>{{const n=Math.max(fit*.8,Math.min(fit*8,sc*f));tx=px-(px-tx)*n/sc;ty=py-(py-ty)*n/sc;sc=n;ap()}};
$('#zbtn').onclick=()=>{{Z.classList.add('open');document.documentElement.style.overflow='hidden';rs();$('#zclose').focus()}};
const zc=()=>{{Z.classList.remove('open');document.documentElement.style.overflow='';$('#zbtn').focus()}};
$('#zclose').onclick=zc;addEventListener('keydown',e=>{{if(e.key==='Escape'&&Z.classList.contains('open'))zc()}});addEventListener('resize',()=>{{if(Z.classList.contains('open'))rs()}});
Z.addEventListener('wheel',e=>{{e.preventDefault();za(Math.exp(-e.deltaY*.0015),e.clientX,e.clientY)}},{{passive:false}});
Z.addEventListener('dblclick',e=>{{sc>fit*1.2?rs():za(2.5,e.clientX,e.clientY)}});
const P=new Map();let pd=0;
Z.addEventListener('pointerdown',e=>{{if(e.target.closest('button'))return;Z.setPointerCapture(e.pointerId);P.set(e.pointerId,[e.clientX,e.clientY]);if(P.size===2){{const[a,b]=[...P.values()];pd=Math.hypot(a[0]-b[0],a[1]-b[1])}}}});
Z.addEventListener('pointermove',e=>{{if(!P.has(e.pointerId))return;const p=P.get(e.pointerId);if(P.size===1){{tx+=e.clientX-p[0];ty+=e.clientY-p[1];ap()}}P.set(e.pointerId,[e.clientX,e.clientY]);
 if(P.size===2){{const[a,b]=[...P.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]);if(pd)za(d/pd,(a[0]+b[0])/2,(a[1]+b[1])/2);pd=d}}}});
const up=e=>{{P.delete(e.pointerId);if(P.size<2)pd=0}};Z.addEventListener('pointerup',up);Z.addEventListener('pointercancel',up);
}}
</script>
</body>
</html>
'''

def sitemap():
    urls = [(HOME['en'], HOME['it'])] + [(work_url(w, 'en'), work_url(w, 'it')) for w in WORKS if w['en']['body']]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for en, it in urls:
        for u in (en, it):
            out.append(f'  <url><loc>{SITE}{u}</loc><xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/><xhtml:link rel="alternate" hreflang="it" href="{SITE}{it}"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{en}"/></url>')
    out.append('</urlset>')
    return '\n'.join(out) + '\n'

def write(path, text):
    p = os.path.join(OUT, path.lstrip('/'))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(text)

CSS = main_css()
if __name__ == '__main__':
    for lang in LANGS:
        write(HOME[lang] + 'index.html', build_main(lang))
        for i, w in enumerate(WORKS):
            write(work_url(w, lang) + 'index.html', work_page(w, lang, WORKS[i - 1], WORKS[(i + 1) % len(WORKS)]))
    write('sitemap.xml', sitemap())
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    write('CNAME', 'giovannitedesco.it\n')
    write('.nojekyll', '')
    if os.path.isdir(os.path.join(SRC, 'img')):
        shutil.copytree(os.path.join(SRC, 'img'), os.path.join(OUT, 'img'), dirs_exist_ok=True)
    print('ok', OUT)
