from getStudentInfo.getStudentInfo import getAllClassSchedule, login
from getStudentInfo.handleJson import generate_term_class_excel
# 返回值(login.status_code, cookies)
login_info=login()
if(login_info[0] == 200):
    print('登录成功')
    cookies = login_info[1]
    schedules = getAllClassSchedule(cookies)
    generate_term_class_excel(schedules)
