# -*- coding: utf-8 -*-
"""生成讲解指南页 as_math_guide.html（中文精讲 + MathJax 公式 + 侧边目录）。"""
import os
import re
from _common import (BASE, CONTENT, TOPICS, GROUP_TITLE, CSS, md_to_html,
                     parse_topic, slug, inline, MJAX_HEAD, verify_mathjax)

CN_NUM = {'P': '第一部分', 'S': '第二部分', 'M': '第三部分'}

SOL_RE = re.compile(r'^\*\*解\*\*\s*:?\s*(.*)$')


def split_solution(body):
    """把例题正文在 **解** 处切开：题干 + 可折叠解答。"""
    lines = body.split('\n')
    for i, ln in enumerate(lines):
        m = SOL_RE.match(ln.strip())
        if m:
            stem = '\n'.join(lines[:i])
            sol_lines = [m.group(1)] if m.group(1) else []
            sol_lines += lines[i + 1:]
            sol = ('<details open><summary>解答（点击展开/收起）</summary>'
                   '<div class="sol">%s</div></details>' % md_to_html('\n'.join(sol_lines)))
            return stem, sol
    return body, ''


def build():
    data = []
    for fn, grp, _ in TOPICS:
        p = os.path.join(CONTENT, fn)
        d = parse_topic(p)
        d['group'] = grp
        d['key'] = slug(fn.replace('.md', ''))
        data.append(d)

    # 侧栏
    side = ['<h1>爱德思 AS 数学<br>讲解指南</h1>',
            '<div class="sub">Edexcel AS Mathematics 8MA0 · 17 个专题全覆盖</div>']
    last = None
    for d in data:
        if d['group'] != last:
            side.append('<div class="grp">%s</div>' % GROUP_TITLE[d['group']])
            last = d['group']
        side.append('<a class="item" href="#%s">%s</a>' % (d['key'], d['title']))
        side.append('<a class="mini" href="#%s-ex">↳ 例题</a>' % d['key'])
    side.append('<div class="grp" style="margin-top:16px">其他页</div>')
    side.append('<a class="item" href="index.html">← 总目录</a>')
    side.append('<a class="item" href="as_math_slides.html">课堂课件</a>')
    side.append('<a class="item" href="as_math_formula.html">公式手册</a>')
    side.append('<a class="item" href="as_math_practice.html">练习题</a>')
    side_html = '\n'.join(side)

    total_ex = sum(len(d['examples']) for d in data)
    total_q = sum(len(d['questions']) for d in data)

    main = []
    main.append(f"""<div class="hero">
<h1>爱德思 AS 数学 · 讲解指南</h1>
<div class="meta">
Specification 8MA0｜Paper 1 纯数（2 小时，100 分，62.5%）+ Paper 2 统计与力学（1 小时 15 分，60 分，37.5%）<br>
共 {len(data)} 个专题 · {total_ex} 道例题（含详解）· 练习题见<a href="as_math_practice.html">练习页</a>（{total_q} 题）<br>
内容按官方考纲（Specification Issue 3, 2025）逐条编写；术语保留英文原名。
</div></div>
<div class="toolbar">
<button class="btn" onclick="toggleAll(false)">收起全部解答</button>
<button class="btn" onclick="toggleAll(true)">展开全部解答</button>
<a class="btn" href="as_math_formula.html">公式手册</a>
<a class="btn" href="as_math_practice.html">练习题</a>
</div>""")

    for d in data:
        main.append('<h2 id="%s">%s</h2>' % (d['key'], d['title']))
        if d['note']:
            main.append('<p class="note">%s</p>' % inline(d['note']))

        for name, raw in d['sections']:
            if name == '考纲要求':
                items = [l[2:].strip() for l in raw.split('\n') if l.strip().startswith('- ')]
                lis = ''.join('<li>%s</li>' % md_to_html(x).strip() for x in items)
                main.append('<h3>考纲要求 · What students need to learn</h3>')
                main.append('<ul class="chk">%s</ul>' % lis)
            elif name == '知识点':
                main.append('<h3>知识点</h3>')
                main.append(md_to_html(raw))
            elif name == '例题':
                main.append('<h3 id="%s-ex">例题（%d 道）</h3>' % (d['key'], len(d['examples'])))
                for num, body in d['examples']:
                    stem, sol = split_solution(body)
                    main.append('<div class="ex"><h4>例 %s</h4>%s%s</div>'
                                % (num, md_to_html(stem), sol))
            elif name == '练习':
                main.append('<h3>练习</h3>')
                main.append('<p>本专题的 %d 道练习题已放入<a href="as_math_practice.html#%s">练习页</a>，'
                            '可隐藏答案自测。</p>' % (len(d['questions']), d['key']))

    main.append('<div class="footer">内容依据 Pearson Edexcel AS Mathematics (8MA0) Specification '
                '（Issue 3, 2025）与官方公式手册编写；例题与练习为原创编写，用于讲练配套。</div>')

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>爱德思 AS 数学 · 讲解指南</title>
{MJAX_HEAD}
<link rel="stylesheet" href="_theme.css">
<style>
.ex .sol{{border-left:3px solid var(--acc2);padding-left:12px;margin-top:6px}}
</style></head>
<body>
<div class="wrap">
<div class="side">{side_html}</div>
<div class="main">{''.join(main)}</div>
</div>
<script>
function toggleAll(open){{
  document.querySelectorAll('details').forEach(function(d){{ d.open = open; }});
}}
</script>
</body></html>"""

    out = os.path.join(BASE, 'as_math_guide.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('written', out, len(html), 'bytes;', len(data), 'topics,', total_ex, 'examples')
    verify_mathjax(out)


if __name__ == '__main__':
    build()
