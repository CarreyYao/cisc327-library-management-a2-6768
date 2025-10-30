"""
Borrower Status Routes
"""

from flask import Blueprint, render_template, request
from library_service import get_patron_status_report
from jinja2 import TemplateNotFound, TemplateSyntaxError  # 添加这行导入

# 创建蓝图并设置模板文件夹路径
borrower_status_bp = Blueprint('borrower_status', __name__)
#@borrower_status_bp.route('/borrower_status')
#borrower_status_bp = Blueprint('borrower_status', __name__, template_folder='routes')
#@borrower_status_bp.route('/borrower_status', methods=['GET', 'POST'])
@borrower_status_bp.route('/borrower_status', methods=['GET', 'POST'], endpoint='status')


def borrower_status():
	#return "Borrower Status Page - Working!"
	'''
    try:
        # 测试简单的模板渲染
        return render_template('borrower_status.html')
        
    except TemplateNotFound as e:
        return f"Template not found: {str(e)}", 404
    except TemplateSyntaxError as e:
        return f"Template syntax error: {str(e)}", 500
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return f"Unexpected error: {str(e)}\n\n{error_traceback}", 500
	'''

	if request.method == 'POST' and request.form.get('action') == 'query':
		patron_id = request.form.get('patron_id')
        
        # 验证patron_id格式
		if not patron_id or len(patron_id) != 6 or not patron_id.isdigit():
			return render_template('borrower_status.html', 
                                 error_message="Invalid patron ID format. Please enter a 6-digit number.")
        
        # 调用library_service获取借阅者状态
		try:
			status_report = get_patron_status_report(patron_id)
			return render_template('borrower_status.html', 
                                 status_report=status_report, 
                                 patron_id=patron_id)
		except Exception as e:
			return render_template('borrower_status.html', 
                                 error_message=f"Error retrieving patron status: {str(e)}", 
                                 patron_id=patron_id)
    
    # GET请求或取消操作
	return render_template('borrower_status.html')

