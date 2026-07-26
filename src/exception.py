import sys
class ProjectException:

    def __init__(self,error_msg,error_info:sys):
        self.error_msg = error_msg

        _ , _ ,err_tb = error_info.exc_info()

        self.line_no = err_tb.tb_lineno
        self.file_name = err_tb.tb_frame.f_code.co_filename
        self.function_name = err_tb.tb_frame.f_code.co_name

    def __str__(self):
        return f"Error occured in python script [{self.file_name}] at function [{self.function_name}] line number [{self.line_no}] error message [{self.error_msg}]"