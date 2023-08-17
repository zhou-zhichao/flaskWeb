from datatool import *
# business_result_file_path = 'file/input/学工_1.1/学工_1.1_重要业务结果.xlsx'
# sep_on_sheet(business_result_file_path)

# code_check("file/standard/标准代码.xlsx", "file/input/学工_1.2/学工_1.2_自定义代码.xlsx")
# sep_on_field(business_result_file_path)
# first_sheet_write('file/input/学工_1.1/学工_1.1_重要业务结果.xlsx','output/test.xlsx')

# file = ['file\\confirm\\学工_1.2_重要业务结果\\学工_1.2_自定义代码.xlsx',
#         'file\\confirm\\学工_1.1_重要业务结果\\学工_1.1_对外数据要求检查.xlsx',
#         'file\\confirm\\学工_1.1_重要业务结果\\学工_1.1_外供数据检查.xlsx',
#         'file\\confirm\\学工_1.1_外供数据检查确认.xlsx']
# out = confirm_list_to_tuple(file)
# print(out)

zip_files("test",'file/confirm/学工_1.3_外供数据检查确认.xlsx','file/confirm/学工_1.3_重要业务结果/学工_1.3_对外数据要求检查.xlsx')