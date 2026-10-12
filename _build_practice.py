# -*- coding: utf-8 -*-
"""生成练习题互动页 as_math_practice.html（逐题播放、可隐藏答案、键盘操作）。"""
import os
import json
from _common import (BASE, CONTENT, TOPICS, GROUP_TITLE, load_css, parse_topic,
                     slug, md_to_html, MJAX_HEAD, verify_mathjax)

# 菜单/卡片网格/进度条/导航等组件样式与课件页共用，统一取自 teaching-kit
# 工具包（load_css(slides=True) = theme.css + slides.css），禁止在脚本里重抄。
CSS = load_css(slides=True)


def build():
    decks = []
    gmeta = {}
    order = []
    for fn, grp, label in TOPICS:
        d = parse_topic(os.path.join(CONTENT, fn))
        key = slug(fn.replace('.md', ''))
        qs = []
        for i, qa in enumerate(d['questions'], 1):
            qs.append({
                'n': i,
                'q': md_to_html(qa['q']).strip(),
                'a': md_to_html(qa['a']).strip(),
            })
        decks.append({'key': key, 'title': d['title'], 'group': grp, 'qs': qs})
        gmeta[grp] = {'title': GROUP_TITLE[grp], 'label': label}
        order.append(grp)
    grank = []
    for g in order:
        if g not in grank:
            grank.append(g)

    total = sum(len(d['qs']) for d in decks)
    data_js = json.dumps({'decks': decks, 'gmeta': gmeta, 'grank': grank},
                         ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>爱德思 AS 数学 · 练习题</title>
{MJAX_HEAD}
<link rel="stylesheet" href="_theme.css">
<link rel="stylesheet" href="_theme_slides.css">
<style>
/* 以下仅为练习题页独有布局；菜单/卡片网格/进度条/导航均来自 teaching-kit 工具包 */
.grid{{margin-top:8px}}
.qbox{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:26px 28px;min-height:230px}}
.qhead{{color:var(--dim);font-size:13px;margin-bottom:8px}}
.qtext{{font-size:18px;line-height:1.85}}
.abox{{margin-top:18px;border-left:3px solid var(--acc2);padding:12px 16px;display:none}}
.abox.on{{display:block}}
.kbd{{color:var(--dim);font-size:12.5px;margin-top:10px}}
.kbd b{{background:var(--panel2);border:1px solid var(--line);border-radius:4px;padding:1px 6px}}
</style></head>
<body>
<div class="wrap">
<div class="side">
  <h1>爱德思 AS 数学<br>练习题</h1>
  <div class="sub">共 {len(decks)} 个专题 · {total} 题</div>
  <div class="grp">操作</div>
  <a class="item" href="#" onclick="backMenu();return false;">← 回到专题菜单</a>
  <div class="grp" style="margin-top:16px">其他页</div>
  <a class="item" href="index.html">← 总目录</a>
  <a class="item" href="as_math_slides.html">课堂课件</a>
  <a class="item" href="as_math_guide.html">讲解指南</a>
  <a class="item" href="as_math_formula.html">公式手册</a>
</div>
<div class="main">

<div class="menu on" id="menu">
  <div class="hero">
  <h1>练习题 · Practice</h1>
  <div class="meta">按专题选一组题，进入后逐题播放。默认隐藏答案，
  按<b>空格</b>显示/隐藏，<b>← →</b> 翻题，<b>Esc</b> 返回本菜单。</div>
  </div>
  <div id="groups"></div>
</div>

<div class="stage" id="stage">
  <div class="toolbar">
    <button class="btn" onclick="backMenu()">← 菜单</button>
    <button class="btn" onclick="toggleAns()">显示/隐藏答案</button>
    <button class="btn" onclick="prev()">上一题</button>
    <button class="btn" onclick="next_()">下一题</button>
    <span class="btn" id="pos">—</span>
  </div>
  <div class="bar"><i id="prog"></i></div>
  <div class="qbox">
    <div class="qhead" id="qhead">—</div>
    <div class="qtext" id="qtext">—</div>
    <div class="abox" id="abox"><b style="color:var(--acc2)">答案</b>
      <div id="atext" style="margin-top:6px"></div></div>
  </div>
  <div class="nav">
    <button class="btn" onclick="prev()">← 上一题</button>
    <button class="btn" onclick="toggleAns()">空格：答案</button>
    <button class="btn" onclick="next_()">下一题 →</button>
  </div>
  <div class="kbd">快捷键：<b>←</b> 上一题 · <b>→</b> 下一题 · <b>空格</b> 答案 · <b>Esc</b> 返回菜单</div>
</div>

</div></div>
<script>
const DATA = {data_js};
let cur = null, idx = 0, showAns = false;

/* MathJax 异步加载：动态插入内容后必须重新排版。用单一 Promise 链串行化，
   避免快速翻题时 MathJax 报 "Typeset already in progress"；未加载完则轮询重试。 */
let _tp = Promise.resolve();
function typeset(id){{
  const run = function() {{
    const el = id ? [document.getElementById(id)] : undefined;
    return window.MathJax.typesetPromise(el);
  }};
  if (window.MathJax && window.MathJax.typesetPromise) {{
    _tp = _tp.then(run).catch(function(e){{ /* 忽略局部排版异常 */ }});
  }} else {{
    setTimeout(function(){{ typeset(id); }}, 120);
  }}
}}

function renderMenu(){{
  const box = document.getElementById('groups');
  let h = '';
  DATA.grank.forEach(function(g){{
    h += '<h3>' + DATA.gmeta[g].title + '</h3><div class="grid">';
    DATA.decks.filter(function(d){{return d.group===g;}}).forEach(function(d){{
      h += '<div class="card" onclick="openDeck(\\'' + d.key + '\\')"><div class="t">' +
           d.title + '</div><div class="c">' + d.qs.length + ' 题</div></div>';
    }});
    h += '</div>';
  }});
  box.innerHTML = h;
  typeset('groups');
}}

function openDeck(key){{
  cur = DATA.decks.find(function(d){{return d.key===key;}});
  idx = 0; showAns = false;
  document.getElementById('menu').classList.remove('on');
  document.getElementById('stage').classList.add('on');
  render();
}}
function backMenu(){{
  document.getElementById('stage').classList.remove('on');
  document.getElementById('menu').classList.add('on');
}}
function render(){{
  const q = cur.qs[idx];
  document.getElementById('qhead').textContent = cur.title + '　第 ' + q.n + ' / ' + cur.qs.length + ' 题';
  document.getElementById('qtext').innerHTML = q.q;
  document.getElementById('atext').innerHTML = q.a;
  document.getElementById('abox').classList.toggle('on', showAns);
  document.getElementById('pos').textContent = (idx+1) + ' / ' + cur.qs.length;
  document.getElementById('prog').style.width = ((idx+1)/cur.qs.length*100) + '%';
  typeset('qbox');
}}
function toggleAns(){{ showAns = !showAns; document.getElementById('abox').classList.toggle('on', showAns);
  if (showAns) typeset('atext'); }}
function prev(){{ if(!cur) return; idx = (idx - 1 + cur.qs.length) % cur.qs.length; showAns=false; render(); }}
function next_(){{ if(!cur) return; idx = (idx + 1) % cur.qs.length; showAns=false; render(); }}
document.addEventListener('keydown', function(e){{
  if(!cur) return;
  if(e.key === 'ArrowRight'){{ next_(); }}
  else if(e.key === 'ArrowLeft'){{ prev(); }}
  else if(e.key === ' '){{ e.preventDefault(); toggleAns(); }}
  else if(e.key === 'Escape'){{ backMenu(); }}
}});
renderMenu();
</script>
</body></html>"""

    out = os.path.join(BASE, 'as_math_practice.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('written', out, len(html), 'bytes;', len(decks), 'decks,', total, 'questions')
    verify_mathjax(out)


if __name__ == '__main__':
    build()
