from odoo import models, fields
import requests
from odoo.exceptions import ValidationError
from datetime import datetime

class ImportButton(models.TransientModel):

    _name = 'import.button'
    _description = 'Import worker from 1C'

    by_number = fields.Boolean(string='By Number', default=True)
    by_name = fields.Boolean(string='By Name', default=False)

    employee_name = fields.Char(string='Name')
    employee_id = fields.Char(string='Табельный номер')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def substitute_the_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.isdigit() and len(rec.employee_id) in range(1, 6):
                rec.employee_id = f"0000-{rec.employee_id.zfill(5)}"
            else:
                rec.employee_id = ''
        return rec.employee_id
    def import_from_1c(self):
        baseUrl = 'http://localhost/data/hs/personaldata/v1/getpassportdata'
        worker = self.env['hr.employee'].browse(self._context.get('active_id'))
        correct_employee_id = self.substitute_the_id()
        url = baseUrl + f"?Name={self.employee_name if self.employee_name else ''}&ServiceNumber={correct_employee_id}&Initiator=&Reason"
        try:
            response = requests.get(url,auth=('Admin',''))
            response.raise_for_status()
            data = response.json()

            full_passport = ", ".join([
                data.get('PassportSeries', ''),
                data.get('PassportNumber', ''),
                data.get('PassportIssued', ''),
                data.get('PassportDateOfIssue', ''),
                data.get('PassportDivisionCode', '')
            ])
            worker.name = data['FullName']
            worker.private_phone = data['PhoneNumber']
            worker.private_street = data['ResidentialAddress']
            worker.snils = data['Snils']
            worker.citizenship = data['Citizenship']
            worker.inn = data['Inn']
            worker.passport_data = full_passport
            worker.birthday = datetime.strptime(data['DateOfBirth'], '%d.%m.%Y').date()



        except requests.exceptions.RequestException as req_exc:
            raise ValidationError(f"Ошибка при выполнении запроса: {req_exc}")
        except ValueError as val_err:
            raise ValidationError(f"Ошибка при обработке JSON: {val_err}")
        except KeyError as key_err:
            raise ValidationError(f"Ошибка: Отсутствует ключ в данных: {key_err}")