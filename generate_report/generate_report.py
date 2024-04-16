import datetime

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches
from docx.oxml.shared import OxmlElement, qn


def set_indent(paragraph, left_indent=None, right_indent=None, first_line_indent=None, hanging_indent=None):
    """设置缩进，单位为字符

    :param paragraph: 某段落
    :param left_indent: 左缩进
    :param right_indent: 右缩进
    :param first_line_indent: 首行缩进
    :param hanging_indent: 悬挂缩进
    """
    assert not all([first_line_indent, hanging_indent]), '首行缩进与悬挂缩进不可同时设置'
    pPr = paragraph._element.get_or_add_pPr()
    ind = OxmlElement('w:ind')
    if left_indent:
        ind.set(qn('w:leftChars'), str(left_indent * 100))
    if right_indent:
        ind.set(qn('w:rightChars'), str(right_indent * 100))
    if first_line_indent:
        ind.set(qn('w:firstLineChars'), str(first_line_indent * 100))
    if hanging_indent:
        ind.set(qn('w:hangingChars'), str(hanging_indent * 100))
    pPr.append(ind)

############################################## 1.获取需要填充的参数
domain = 'www.neu.edu.cn'
start_time = datetime.date.today()
resolved = True

document = Document()
############################################## 2.设置报告标题
document.add_heading('网站 IPv6 支持度检测报告', level=0)

paragraph = document.add_paragraph('')
run = paragraph.add_run('网站域名: ')
font = run.font
font.name = '宋体'
font.bold = True
run = paragraph.add_run(domain)
font = run.font
font.name = 'Times New Roman'
font.bold = True
font.underline = True

paragraph = document.add_paragraph('')
run = paragraph.add_run('支持IPV6: ')
support = '   支持    '
font = run.font
font.name = '宋体'
font.bold = True
run = paragraph.add_run(support)
font = run.font
font.name = 'Times New Roman'
font.bold = True
font.underline = True

paragraph = document.add_paragraph('')
run = paragraph.add_run('检测时间: ')
font = run.font
font.name = '宋体'
font.bold = True
run = paragraph.add_run(str(start_time))
font = run.font
font.name = 'Times New Roman'
font.bold = True
font.underline = True

############################################## 3.标题1及下面内容
document.add_heading('1.检测依据', level=1)
content = ('网站IPv6支持度评测指标与测试方法是基于中华人民共和国通信行业标准YD/T3118-2016《网站IPv6支持度评测指标与测试方法》。该标准规定了网站IPv6支持度评测指标与测试方法，适用于IPv6'
           '网络环境下的Web网站，以及IPv6和IPv4共存网络环境下支持双栈模式的Web网站。')
paragraph = document.add_paragraph()
set_indent(paragraph, left_indent=0, right_indent=0, first_line_indent=2)
run = paragraph.add_run(content)
font = run.font
font.name = '宋体'


############################################## 4.标题2及下面内容
# 根据ipv6的支持度数据填充到一个表格中
document.add_heading('2.检测报告', level=1)
table = document.add_table(13, 2, style='Light Shading Accent 1')
heading_cells = table.rows[0].cells
heading_cells[0].text = '域名'
heading_cells[1].text = 'www.baidu.com'
cells = table.rows[1].cells
cells[0].text = '是否可以被解析'
cells[1].text = '不支持'
cells = table.rows[2].cells
cells[0].text = '是否可以被访问'
cells[1].text = '不支持'
cells = table.rows[3].cells
cells[0].text = '支持度'
cells[1].text = '99%'
cells = table.rows[4].cells
cells[0].text = '连通性'
cells[1].text = '可以连通'
cells = table.rows[5].cells
cells[0].text = '域名解析时延'
cells[1].text = '0.75s'
cells = table.rows[6].cells
cells[0].text = 'TCP建立解析时延指标'
cells[1].text = '0.75s'
cells = table.rows[7].cells
cells[0].text = '服务器相应首包时延指标'
cells[1].text = '0.75s'
cells = table.rows[8].cells
cells[0].text = '服务器相应首页时延指标'
cells[1].text = '0.75s'
cells = table.rows[9].cells
cells[0].text = 'ipv6访问稳定性'
cells[1].text = '不稳定'
cells = table.rows[10].cells
cells[0].text = '是否具有ipv6授权体系'
cells[1].text = '0.75s'
cells = table.rows[11].cells
cells[0].text = '计算开始时间'
cells[1].text = '0.75s'
cells = table.rows[12].cells
cells[0].text = '计算结束时间'
cells[1].text = '0.75s'

document.add_heading('3.不支持IPV6的链接', level=1)
document.add_heading('3.1 不支持IPV6的二级链接', level=2)
secondary_links = []
table1 = document.add_table(1, 2, style='Light Shading Accent 1')
heading_cells = table1.add_row().cells
heading_cells[0].text = '二级链接'
heading_cells[1].text = '是否支持ipv6'

for link in secondary_links:
    cells = table1.add_row().cells
    cells[0].text = link[0]
    cells[1].text = '不支持'

document.add_heading('3.2 不支持IPV6的三级链接', level=2)
tertiary_links = []
table = document.add_table(1, 2, style='Light Shading Accent 1')
heading_cells = table.add_row().cells
heading_cells[0].text = '三级链接'
heading_cells[1].text = '是否支持ipv6'

for link in secondary_links:
    cells = table.add_row().cells
    cells[0].text = link[0]
    cells[1].text = '不支持'

document.save('generate_report.docx')
