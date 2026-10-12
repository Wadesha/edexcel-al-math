# -*- coding: utf-8 -*-
"""生成入口页 index.html。"""
import os
from _common import BASE, CONTENT, TOPICS, GROUP_TITLE, CSS, md_to_html, parse_topic, slug, MJAX_HEAD, verify_mathjax
from _build_slides import build_deck


def build():
    data = []
    for fn, grp, label in TOPICS:
        d = parse_topic(os.path.join(CONTENT, fn))
        d['group'] = grp
        d['key'] = slug(fn.replace('.md', ''))
        d['n_ex'] = len(d['examples'])
        d['n_q'] = len(d['questions'])
        data.append(d)

    tot_ex = sum(d['n_ex'] for d in data)
    tot_q = sum(d['n_q'] for d in data)
    tot_sl = sum(len(build_deck(d)['slides']) for d in data)

    groups = []
    for g in ['P', 'S', 'M']:
        rows = ''.join(
            '<tr><td><a href="as_math_guide.html#%s">%s</a></td><td>%d</td>'
            '<td><a href="as_math_practice.html" onclick="sessionStorage.setItem(\'deck\',\'%s\')">%d 题</a></td>'
            '<td><a href="as_math_slides.html" onclick="sessionStorage.setItem(\'deck\',\'%s\')">课件</a></td></tr>'
            % (d['key'], d['title'], d['n_ex'], d['key'], d['n_q'], d['key'])
            for d in data if d['group'] == g)
        groups.append('<h3>%s</h3><table><thead><tr><th>专题</th><th>例题</th><th>练习</th><th>课件</th></tr></thead>'
                      '<tbody>%s</tbody></table>' % (GROUP_TITLE[g], rows))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>爱德思 AS 数学 · 学习套件</title>
{MJAX_HEAD}
<link rel="stylesheet" href="_theme.css">
<style>
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:18px 0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px}}
.card:hover{{border-color:var(--acc)}}
.card h3{{margin:0 0 6px;color:var(--acc);font-size:17px}}
.card p{{color:var(--dim);font-size:13.5px;margin:4px 0 0}}
.stat{{display:flex;gap:22px;flex-wrap:wrap;margin:12px 0}}
.stat div{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 16px}}
.stat b{{display:block;font-size:22px;color:var(--acc2)}}
.stat span{{font-size:12.5px;color:var(--dim)}}
</style></head>
<body>
<div class="wrap">
<div class="side">
  <h1>爱德思 AS 数学<br>学习套件</h1>
  <div class="sub">Edexcel AS Mathematics · 8MA0</div>
  <div class="grp">四个页面</div>
  <a class="item" href="as_math_slides.html">① 课堂课件</a>
  <a class="item" href="as_math_guide.html">② 讲解指南</a>
  <a class="item" href="as_math_formula.html">③ 公式手册</a>
  <a class="item" href="as_math_practice.html">④ 练习题</a>
  <div class="grp" style="margin-top:16px">专题索引</div>
  {''.join('<a class="item" href="as_math_guide.html#%s">%s</a>' % (d['key'], d['title']) for d in data)}
</div>
<div class="main">
<div class="hero">
<h1>爱德思 AS 数学 · 学习套件</h1>
<div class="meta">Pearson Edexcel AS Mathematics（8MA0）｜依据官方考纲 Specification Issue 3（2025）
与《Mathematical Formulae and Statistical Tables》编写<br>
讲解中文 + 术语保留英文；公式用 MathJax 渲染；全部内容离线可看（公式渲染需联网加载一次）。</div>
</div>

<div class="stat">
<div><b>{len(data)}</b><span>专题</span></div>
<div><b>{tot_ex}</b><span>例题（含详解）</span></div>
<div><b>{tot_q}</b><span>练习题（可隐藏答案）</span></div>
<div><b>{tot_sl}</b><span>课件幻灯片</span></div>
<div><b>2</b><span>考试卷（Paper 1 / Paper 2）</span></div>
</div>

<div class="cards">
<a class="card" href="as_math_slides.html" style="color:inherit">
  <h3>① 课堂课件</h3>
  <p>443 张幻灯片（17 个专题）：概念页 → 例题（先题后解）→ 当堂练习（先题后答案）。
  全屏投屏、键盘翻页，Ctrl+P 可直接打印成 PDF 讲义。</p>
</a>
<a class="card" href="as_math_guide.html" style="color:inherit">
  <h3>② 讲解指南</h3>
  <p>17 个专题逐条讲解：考纲要求清单 + 知识点推导 + 例题详解。左侧目录跳转，例题解答可一键折叠。</p>
</a>
<a class="card" href="as_math_formula.html" style="color:inherit">
  <h3>③ 公式手册</h3>
  <p>分清"考场会发的"与"必须背的"；附二项分布累积表、正态分布百分位点表与在线计算器。</p>
</a>
<a class="card" href="as_math_practice.html" style="color:inherit">
  <h3>④ 练习题</h3>
  <p>按专题逐题播放，答案默认隐藏；← → 翻题、空格显答案、Esc 返回。适合课堂投屏与自测。</p>
</a>
</div>

<h2>考试结构</h2>
<table>
<thead><tr><th>卷</th><th>内容</th><th>时长</th><th>分值</th><th>权重</th></tr></thead>
<tbody>
<tr><td>Paper 1（8MA0/01）</td><td>纯数 Pure：证明、代数与函数、坐标几何、数列与二项展开、三角、指数与对数、微分、积分、向量</td><td>2 小时</td><td>100</td><td>62.5%</td></tr>
<tr><td>Paper 2（8MA0/02）</td><td>统计 Statistics（抽样、数据呈现、概率、分布、假设检验）+ 力学 Mechanics（量与单位、运动学、力与牛顿定律）</td><td>1 小时 15 分</td><td>60</td><td>37.5%</td></tr>
</tbody></table>
<p class="note">三份试卷均允许使用计算器；公式册随卷发放。Paper 2 的统计部分涉及 Pearson 官方"大数据集"（large data set），
考纲要求熟悉其术语与背景。</p>

<h2>专题索引</h2>
{''.join(groups)}

<div class="footer">
源：Pearson Edexcel Level 3 Advanced Subsidiary GCE in Mathematics Specification（Issue 3, 2025）；
Pearson《Mathematical Formulae and Statistical Tables》（2017）。讲解、例题与练习题为本页原创编写。
</div>
</div></div>
</body></html>"""

    out = os.path.join(BASE, 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('written', out, len(html))
    verify_mathjax(out)


if __name__ == '__main__':
    build()
