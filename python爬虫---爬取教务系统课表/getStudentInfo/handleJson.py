import xlwt
import json

## 获取每个课属于哪一大节的
class_time_map = {'0102':'1', '0304':'2', '0506':'3', '0708':'4', '0910':'5', '1112':'6'}
# 读取文件
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as  f:
        json_str = json.load(f)
    #print(json_str)
    return json_str

# 表的样式
def set_style(name, height, bold=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font
    return style

# 生成每周的课表, 一个 sheet 代表一个星期
def write_class(sheet, week_class):
    row0 = [" ", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    # 生成行
    for i in range(len(row0)):
        sheet.write(0, i, row0[i], set_style('宋体', 280))
    # 生成列
    for i in range(1, 7):
        sheet.write_merge( 1+(2*(i-1)), 2+(2*(i-1)), 0, 0, i)
    # 将课表数据写入到 excel
    for class_ in week_class:
        #获取课程的时长,有可能会出现两大节连在一起的课程
        jcdm = class_['jcdm']
        if len(jcdm) == 4:
            class_time = int(class_time_map[class_['jcdm']])
            #计算并合并格数
            row0 = class_time + (class_time-1)
            col = int(class_['xq'])
            content = '{0},{1},{2}'.format(class_['kcmc'], class_['jxcdmc'], class_['teaxms'])
            sheet.write_merge(row0, row0+1, col, col, content, set_style('宋体', 200))
            #print("写入内容：", content)
        elif len(jcdm) == 8:
            first_time_str = class_['jcdm'][0:4]
            first_class_time = int(class_time_map[first_time_str])
            content = '{0},{1},{2}'.format(class_['kcmc'], class_['jxcdmc'], class_['teaxms'])
            row0 = first_class_time + (first_class_time - 1)
            col = int(class_['xq'])
            sheet.write_merge(row0, row0+3, col, col, content, set_style('宋体', 200))
            #print("写入内容：", content)

#生成整个学期的课表
def generate_term_class_excel(term_class_data):
    f = xlwt.Workbook()
    # 生成多个 sheet 表格
    sheet_list = []
    for i in range(len(term_class_data)):
        sheet = f.add_sheet('周{}'.format(i+1), cell_overwrite_ok=True)
        sheet_list.append(sheet)
    print('sheet_list len:', len(sheet_list))
    # 获取处理 term_class_data 后的数据
    term_class_list = []
    # 整个学年的课表
    for week_class in term_class_data:
        print('week_class:', week_class)
        week_class_list = []
        for class_ in week_class:
            one_class = {}
            one_class['kcmc'] = class_['kcmc']
            one_class['jxcdmc'] = class_['jxcdmc']
            one_class['teaxms'] = class_['teaxms']
            one_class['jcdm'] = class_['jcdm']
            one_class['xq'] = class_['xq']
            week_class_list.append(one_class)
        term_class_list.append(week_class_list)
    print('term_class_list:', len(term_class_list))
    # 将每周的课表数据写入到相应的sheet中
    for sheet, week_class in zip(sheet_list,term_class_list):
        #print(week_class)
        write_class(sheet, week_class)
    # 将课表保存
    f.save('term_class.xls')
    print('课表生成成功！','\n')

