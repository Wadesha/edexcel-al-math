# -*- coding: utf-8 -*-
"""生成公式手册页 as_math_formula.html
数据来源：官方《Mathematical Formulae and Statistical Tables》（AS 部分）
          + 官方考纲 Appendix 1（必须背诵、公式册不提供的公式）
"""
import os
import math
from _common import BASE, CSS, MJAX_HEAD, verify_mathjax

# ---------- 数据 ----------
BOOKLET = [
    ('Pure Mathematics · 纯数', [
        ('Mensuration 求积', [
            ('球的表面积', r'4\pi r^{2}'),
            ('圆锥侧面积', r'\pi r \times \text{slant height}（\pi r \times 母线长）'),
        ]),
        ('Binomial series 二项展开', [
            (r'(a+b)^{n}', r'a^{n}+\binom{n}{1}a^{n-1}b+\binom{n}{2}a^{n-2}b^{2}+\dots'
                            r'+\binom{n}{r}a^{n-r}b^{r}+\dots+b^{n}\quad (n\in\mathbb{N})'),
            (r'\binom{n}{r}', r'{}^{n}C_{r}=\frac{n!}{r!(n-r)!}'),
        ]),
        ('Logarithms and exponentials 对数与指数', [
            ('换底公式', r'\log_{a}x=\frac{\log_{b}x}{\log_{b}a}'),
            ('指数改写', r'\mathrm{e}^{x\ln a}=a^{x}'),
        ]),
        ('Differentiation 微分', [
            ('第一原理', r"\mathrm{f}'(x)=\lim_{h\to 0}\frac{\mathrm{f}(x+h)-\mathrm{f}(x)}{h}"),
        ]),
    ]),
    ('Statistics · 统计', [
        ('Probability 概率', [
            ('对立事件', r"\mathrm{P}(A^{\prime})=1-\mathrm{P}(A)"),
        ]),
        ('Standard deviation 标准差', [
            ('标准差与方差', r'\text{标准差}=\sqrt{\text{方差}}'),
            ('四分位距', r'\mathrm{IQR}=Q_{3}-Q_{1}'),
            ('Sxx', r'S_{xx}=\sum(x_{i}-\bar{x})^{2}=\sum x_{i}^{2}-\frac{(\sum x_{i})^{2}}{n}'),
            ('标准差', r'\sqrt{\frac{S_{xx}}{n}}=\sqrt{\frac{\sum x^{2}}{n}-\bar{x}^{2}}'),
        ]),
        ('Statistical tables 统计表', [
            ('考场提供', 'Binomial Cumulative Distribution Function（二项累积分布函数表）'),
            ('考场提供', 'Random Numbers（随机数表）'),
        ]),
    ]),
    ('Mechanics · 力学', [
        ('Kinematics 运动学（匀加速直线运动）', [
            ('速度公式', r'v=u+at'),
            ('位移公式', r's=ut+\tfrac{1}{2}at^{2}'),
            ('位移公式（末速）', r's=vt-\tfrac{1}{2}at^{2}'),
            ('速度—位移', r'v^{2}=u^{2}+2as'),
            ('平均速度', r's=\tfrac{1}{2}(u+v)t'),
        ]),
    ]),
]

RECALL = [
    ('Quadratic equations 二次方程', [
        ('求根公式', r'ax^{2}+bx+c=0\ \Rightarrow\ x=\frac{-b\pm\sqrt{b^{2}-4ac}}{2a}'),
    ]),
    ('Laws of indices 指数律', [
        (r'a^{x}a^{y}', r'a^{x+y}'),
        (r'a^{x}\div a^{y}', r'a^{x-y}'),
        (r'(a^{x})^{y}', r'a^{xy}'),
    ]),
    ('Laws of logarithms 对数律', [
        (r'\log_{a}x+\log_{a}y', r'\log_{a}(xy)'),
        (r'\log_{a}x-\log_{a}y', r'\log_{a}\!\left(\frac{x}{y}\right)'),
        (r'k\log_{a}x', r'\log_{a}(x^{k})'),
        ('对数定义', r'\log_{a}x=n\iff x=a^{n}\quad(a>0,\ x>0)'),
    ]),
    ('Coordinate geometry 坐标几何', [
        ('点斜式', r'y-y_{1}=m(x-x_{1})'),
        ('垂直条件', r'm_{1}m_{2}=-1'),
        ('两点距离', r'\sqrt{(x_{2}-x_{1})^{2}+(y_{2}-y_{1})^{2}}'),
        ('圆', r'(x-a)^{2}+(y-b)^{2}=r^{2}'),
    ]),
    ('Trigonometry 三角', [
        ('正弦定理', r'\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}'),
        ('余弦定理', r'a^{2}=b^{2}+c^{2}-2bc\cos A'),
        ('面积', r'\text{Area}=\tfrac{1}{2}ab\sin C'),
        ('恒等式', r'\cos^{2}A+\sin^{2}A\equiv 1,\qquad \tan\theta\equiv\frac{\sin\theta}{\cos\theta}'),
    ]),
    ('Mensuration 求积', [
        ('圆周长 / 面积', r'C=2\pi r=\pi d,\qquad A=\pi r^{2}'),
        ('勾股定理', r'c^{2}=a^{2}+b^{2}'),
        ('梯形面积', r'\tfrac{1}{2}(a+b)h'),
        ('棱柱体积', r'\text{截面积}\times \text{长度}'),
    ]),
    ('Calculus 微积分', [
        ('求导', r'\frac{\mathrm{d}}{\mathrm{d}x}(x^{n})=nx^{n-1},\qquad \frac{\mathrm{d}}{\mathrm{d}x}(\mathrm{e}^{kx})=k\mathrm{e}^{kx}'),
        ('积分', r'\int x^{n}\,\mathrm{d}x=\frac{x^{n+1}}{n+1}+c\ (n\neq-1),\qquad \int \mathrm{e}^{kx}\,\mathrm{d}x=\frac{1}{k}\mathrm{e}^{kx}+c'),
        ('和差规则', r"[\mathrm{f}(x)\pm\mathrm{g}(x)]'=\mathrm{f}'(x)\pm\mathrm{g}'(x)"),
        ('曲线下面积', r'\text{Area}=\int_{a}^{b}y\,\mathrm{d}x\ (y\geq 0)'),
    ]),
    ('Vectors 向量', [
        ('模', r'|x\mathbf{i}+y\mathbf{j}+z\mathbf{k}|=\sqrt{x^{2}+y^{2}+z^{2}}（二维时去掉 z 项）'),
        ('分量与模', r'\begin{pmatrix}r\cos\theta\\ r\sin\theta\end{pmatrix}\ \leftrightarrow\ |\mathbf{a}|=r'),
    ]),
    ('Statistics 统计', [
        ('均值', r'\bar{x}=\frac{\sum x}{n}=\frac{\sum fx}{\sum f}'),
    ]),
    ('Mechanics 力学', [
        ('重量', r'W=mg'),
        ('摩擦', r'F\leq \mu R'),
        ('牛顿第二定律', r'F=ma'),
        ('变加速运动', r'v=\frac{\mathrm{d}r}{\mathrm{d}t},\quad a=\frac{\mathrm{d}v}{\mathrm{d}t}=\frac{\mathrm{d}^{2}r}{\mathrm{d}t^{2}},\quad r=\int v\,\mathrm{d}t,\quad v=\int a\,\mathrm{d}t'),
    ]),
]

NORMAL_POINTS = [
    (0.5000, 0.0000), (0.4000, 0.2533), (0.3000, 0.5244), (0.2000, 0.8416),
    (0.1000, 1.2816), (0.0500, 1.6449), (0.0250, 1.9600), (0.0100, 2.3263),
    (0.0050, 2.5758), (0.0010, 3.0902), (0.0005, 3.2905),
]


def binom_cdf(r, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, r + 1))


def build_binom_table():
    ns = [5, 10, 15, 20]
    ps = [round(0.05 * i, 2) for i in range(1, 11)]
    blocks = []
    for n in ns:
        rows = []
        head = ''.join('<th>p=%.2f</th>' % p for p in ps)
        for r in range(0, n + 1):
            tds = ''.join('<td>%.4f</td>' % binom_cdf(r, n, p) for p in ps)
            rows.append('<tr><th class="rk">%d</th>%s</tr>' % (r, tds))
        blocks.append(
            '<h4>n = %d</h4><table class="bt"><thead><tr><th class="rk">r \\ p</th>%s</tr></thead><tbody>%s</tbody></table>'
            % (n, head, ''.join(rows)))
    return ''.join(blocks)


TOC = [
    ('booklet', '一、考场发放（公式册 AS 部分）'),
    ('recall', '二、必须背诵（公式册没有）'),
    ('binom', '三、二项分布累积表'),
    ('calc', '四、计算器（二项 / 正态）'),
    ('normal', '五、正态分布百分位点表'),
]


def cell(s):
    """含 LaTeX 标记的包成显示公式，否则按普通文本输出。"""
    s = html_escape(s)
    if '\\' in s or '^' in s or '_' in s:
        return '$$%s$$' % s
    return s


def html_escape(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def table(items):
    rows = ''.join('<tr><td class="lb">%s</td><td>%s</td></tr>' % (cell(lb), cell(fx))
                   for lb, fx in items)
    return '<table class="fx"><tbody>%s</tbody></table>' % rows


def render_group(groups):
    """支持两种结构：(组, [(小节, [(标签, 公式)])]) 或 (组, [(标签, 公式)])。"""
    out = []
    for gname, subs in groups:
        out.append('<h3>%s</h3>' % gname)
        rows = []
        for entry in subs:
            if isinstance(entry[1], str):
                rows.append(entry)
            else:
                if rows:
                    out.append(table(rows))
                    rows = []
                out.append('<h4>%s</h4>' % entry[0])
                out.append(table(entry[1]))
        if rows:
            out.append(table(rows))
    return ''.join(out)


def main():
    booklet_html = render_group(BOOKLET)
    recall_html = render_group(RECALL)

    toc = ''.join('<a href="#%s">%s</a>' % (i, t) for i, t in TOC)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>爱德思 AS 数学 · 公式手册</title>
{MJAX_HEAD}
<link rel="stylesheet" href="_theme.css">
<style>
table.fx{{width:100%;font-size:15px}}
table.fx td{{border:1px solid var(--line);padding:7px 10px;vertical-align:middle}}
table.fx td.lb{{width:34%;color:var(--dim);background:var(--panel2)}}
table.bt{{font-size:12.5px;margin-bottom:18px}}
table.bt th,table.bt td{{padding:3px 6px;text-align:center}}
table.bt .rk{{background:var(--panel2);color:var(--acc2)}}
.tocbar{{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 18px}}
.tocbar a{{background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:5px 10px;font-size:13px}}
.calc{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}}
.calc label{{font-size:13.5px;color:var(--dim);margin-right:6px}}
.calc input{{background:var(--bg);border:1px solid var(--line);color:var(--fg);
 border-radius:5px;padding:4px 8px;width:90px;margin-right:12px}}
.calc .res{{margin-top:10px;font-size:15px}}
.calc .res b{{color:var(--acc2)}}
.badge{{display:inline-block;background:var(--panel2);border:1px solid var(--line);
 border-radius:5px;padding:1px 8px;font-size:12.5px;color:var(--warn);margin-left:8px}}
</style></head>
<body>
<div class="wrap">
<div class="side">
  <h1>爱德思 AS 数学<br>公式手册</h1>
  <div class="sub">Edexcel AS Mathematics 8MA0</div>
  <div class="grp">本页目录</div>
  {toc}
  <div class="grp" style="margin-top:16px">其他页</div>
  <a class="item" href="index.html">← 总目录</a>
  <a class="item" href="as_math_slides.html">课堂课件</a>
  <a class="item" href="as_math_guide.html">讲解指南</a>
  <a class="item" href="as_math_practice.html">练习题</a>
</div>
<div class="main">
<div class="hero">
<h1>公式手册 · Formula Book</h1>
<div class="meta">
按官方《Mathematical Formulae and Statistical Tables》与考纲 8MA0 Appendix 1 整理：
<b>第一部分</b>是考场会发的公式册内容（不用背），<b>第二部分</b>是公式册里没有、必须自己记住的内容。
</div>
</div>

<h2 id="booklet">一、考场发放（公式册 AS 部分）</h2>
<p class="note">考试当天随卷发放，无需背诵，但必须会用——尤其是 $S_{{xx}}$ 与匀加速的五个公式。</p>
{booklet_html}

<h2 id="recall">二、必须背诵（公式册没有）</h2>
<p class="note">考纲 Appendix 1 明确列出："这些公式学生应掌握，不会出现在公式册中。"
求根公式、指数律、对数律、正弦/余弦定理都属于这一类。</p>
{recall_html}

<h2 id="binom">三、二项分布累积表</h2>
<p class="note">表内为 $\\mathrm{{P}}(X\\le r)$，其中 $X\\sim\\mathrm{{B}}(n,p)$。由程序生成（Python math.comb），
与官方表一致；考场上直接使用官方发放的表。</p>
{build_binom_table()}

<h2 id="calc">四、计算器（二项 / 正态）</h2>
<div class="calc">
<h4>二项分布 $X\\sim\\mathrm{{B}}(n,p)$</h4>
<div>
<label>n =</label><input id="bn" value="12" type="number">
<label>p =</label><input id="bp" value="0.35" type="number" step="0.01">
<label>r =</label><input id="br" value="4" type="number">
<button class="btn" onclick="bcalc()">计算</button>
</div>
<div class="res" id="bres">—</div>
</div>
<div class="calc">
<h4>正态分布 $Z\\sim\\mathrm{{N}}(0,1)$ <span class="badge">A-Level 内容</span></h4>
<div>
<label>z =</label><input id="nz" value="1.96" type="number" step="0.01">
<button class="btn" onclick="ncalc()">计算</button>
</div>
<div class="res" id="nres">—</div>
</div>

<h2 id="normal">五、正态分布百分位点表</h2>
<p class="note">表中为满足 $\\mathrm{{P}}(Z&gt;z)=p$ 的 $z$ 值。<span class="badge">A-Level 内容</span></p>
<table><thead><tr><th>p</th>{''.join('<th>%.4f</th>' % p for p, _ in NORMAL_POINTS)}</tr></thead>
<tbody><tr><th>z</th>{''.join('<td>%.4f</td>' % z for _, z in NORMAL_POINTS)}</tr></tbody></table>

<div class="footer">
公式正文来源：Pearson《Mathematical Formulae and Statistical Tables》（2017）与 Pearson Edexcel AS Mathematics (8MA0) Specification Appendix 1。
二项累积表与计算器由本页程序生成，仅供核对。
</div>
</div></div>
<script>
function comb(n,k){{if(k<0||k>n)return 0;let r=1;for(let i=1;i<=k;i++)r=r*(n-k+i)/i;return r;}}
function bcdf(r,n,p){{let s=0;for(let k=0;k<=r;k++)s+=comb(n,k)*Math.pow(p,k)*Math.pow(1-p,n-k);return s;}}
function bcalc(){{
  const n=parseInt(document.getElementById('bn').value);
  const p=parseFloat(document.getElementById('bp').value);
  const r=parseInt(document.getElementById('br').value);
  const le=bcdf(r,n,p), eq=comb(n,r)*Math.pow(p,r)*Math.pow(1-p,n-r);
  document.getElementById('bres').innerHTML=
    'P(X ≤ '+r+') = <b>'+le.toFixed(4)+'</b> &nbsp;|&nbsp; P(X = '+r+') = <b>'+eq.toFixed(4)+
    '</b> &nbsp;|&nbsp; P(X ≥ '+r+') = <b>'+(1-le+eq).toFixed(4)+'</b> &nbsp;|&nbsp; P(X > '+r+') = <b>'+(1-le).toFixed(4)+'</b>';
}}
function ncdf(z){{
  // Abramowitz-Stegun 7.1.26 近似
  const t=1/(1+0.2316419*Math.abs(z));
  const d=0.3989423*Math.exp(-z*z/2);
  const p=d*t*(0.3193815+t*(-0.3565638+t*(1.781478+t*(-1.821256+t*1.330274))));
  return z>0?1-p:p;
}}
function ncalc(){{
  const z=parseFloat(document.getElementById('nz').value);
  const F=ncdf(z);
  document.getElementById('nres').innerHTML=
    'P(Z ≤ '+z+') = <b>'+F.toFixed(4)+'</b> &nbsp;|&nbsp; P(Z > '+z+') = <b>'+(1-F).toFixed(4)+'</b>';
}}
</script>
</body></html>"""

    out = os.path.join(BASE, 'as_math_formula.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('written', out, len(html))
    verify_mathjax(out)


if __name__ == '__main__':
    main()
