from flask import Blueprint, send_file, request, flash, redirect, url_for
from flask_login import login_required, current_user
from services.report_service import generate_pdf_report
from datetime import datetime

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports/pdf')
@login_required
def generate_pdf():
    date_from_str = request.args.get('date_from', '')
    date_to_str = request.args.get('date_to', '')

    date_from = None
    date_to = None

    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    try:
        pdf_buffer = generate_pdf_report(current_user, date_from, date_to)
        filename = f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))
