import datetime

from odoo import models, fields, api


class StudentReg(models.Model):
    _name = 'student.registration'
    _description = 'student registration'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade', index=True)
    firstName = fields.Char(string='First Name', required=True)
    middleName = fields.Char(string='Middle Name')
    lastName = fields.Char(string='Last Name', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    birthDate = fields.Date(required=True)
    # age = fields.Integer()
    motherTongue = fields.Char()
    nationality = fields.Char(string='Nationality')
    phone = fields.Char(string='Contact Number')
    mobile = fields.Char(string='Mobile Number')
    email = fields.Char()
    admissionDate = fields.Date(default=fields.Date.today(), readonly=True)
    maritalStatus = fields.Selection([('Married', 'Married'), ('Unmarried', 'Unmarried')])
    course_id = fields.Many2one('student.course', string='Course')

    attendance_records = fields.One2many('student.attendance.record', 'student_id', string='Attendance Records')


    # for permanent address
    street1_p = fields.Char()
    street2_p = fields.Char()
    country_p = fields.Many2one('res.country', required=True)
    city_p = fields.Char(required=True)
    state_p = fields.Many2one('res.country.state', required=True)
    zip_p = fields.Char()

    # for contact address
    street1_c = fields.Char()
    street2_c = fields.Char()
    country_c = fields.Many2one('res.country', required=True)
    city_c = fields.Char(required=True)
    state_c = fields.Many2one('res.country.state', required=True)
    zip_c = fields.Char()

    # parents Details

    father = fields.Char(string='Father')
    father_qualification = fields.Char(string='Qualification of Father')
    father_job = fields.Char(string='Job of Father')
    father_no = fields.Char(string='Mobile no of Father')
    mother = fields.Char(string='Mother')
    mother_qualification = fields.Char(string='Qualification of Mother')
    mother_job = fields.Char(string='Job of Mother')
    mother_no = fields.Char(string='Mobile no of Mother')

    # additional information
    category = fields.Char(string='Category')
    cast = fields.Char(string='Cast')
    religion = fields.Char(string='Religion')
    disability = fields.Selection([('Yes', 'yes'), ('No', 'no')], string='Person with Disability')

    # documents upload
    image = fields.Image(string='Photo')
    # Emergency contact details
    guardian = fields.Char(String='Name of Guardian')
    relationship = fields.Char(String='Relationship')
    emergencyContact = fields.Char(string='Phone no')
    emergencyMob = fields.Char(string='Mobile no')

    education_ids = fields.One2many('student.education', 'student_id', string='Education History')

    checkin_time = fields.Datetime(string='Check-in Time', readonly=True)
    checkout_time = fields.Datetime(string='Check-out Time', readonly=True)
    attendance_status = fields.Selection([('checked_in', 'Checked In'), ('checked_out', 'Checked Out')],
                                         string='Attendance Status', default='checked_out', readonly=True)

    @api.model
    def action_student_checkin(self, student_id):
        student = self.browse(student_id)
        if student.attendance_status == 'checked_out':
            student.write({
                'checkin_time': fields.Datetime.now(),
                'attendance_status': 'checked_in'
            })
    def action_student_checkout(self):
        for student in self:
            if student.attendance_status == 'checked_in':
                student.write({'attendance_status': 'checked_out'})
                self.env['student.attendance'].create({'student_id': student.id})

    @api.model
    def create(self, values):
        # Create a partner record with given values
        partner_values = {
            'name': values.get('firstName', '') + ' ' + values.get('lastName', ''),
            'street': values.get('street1_p', ''),
            'street2': values.get('street2_p', ''),
            'country_id': values.get('country_p', False),
            'state_id': values.get('state_p', False),
            'city': values.get('city_p', ''),
            'zip': values.get('zip_p', ''),
            'phone': values.get('phone', ''),
            'mobile': values.get('mobile', ''),
            'email': values.get('email', ''),
            'image_1920': values.get('image', ''),
            # Populate other fields accordingly
        }
        partner = self.env['res.partner'].create(partner_values)
        values['partner_id'] = partner.id

        return super(StudentReg, self).create(values)

    def write(self, values):
        for rec in self:
            if rec.partner_id:  # Check if the record has a partner already
                partner_values = {
                    'name': values.get('firstName', rec.firstName) + ' ' + values.get('lastName', rec.lastName),
                    'street': values.get('street1_p', rec.street1_p),
                    'image_1920': values.get('image', rec.image),
                    'street2': values.get('street2_p', rec.street2_p),
                    'country_id': values.get('country_p', rec.country_p.id),
                    'state_id': values.get('state_p', rec.state_p.id),
                    'city': values.get('city_p', rec.city_p),
                    'zip': values.get('zip_p', rec.zip_p),
                    'phone': values.get('phone',rec.phone),
                    'mobile': values.get('mobile',rec.mobile),
                    'email': values.get('email',rec.email),
                    # Update other fields accordingly
                }
                rec.partner_id.write(partner_values)
            else:  # For new records, create the partner record
                country_id = values.get('country_p') or False
                state_id = values.get('state_p') or False

                partner_values = {
                    'name': values.get('name', ''),
                    'street': values.get('street1_p', ''),
                    'image_1920': values.get('image', ''),
                    'street2': values.get('street2_p', ''),
                    'country_id': country_id,
                    'state_id': state_id,
                    'city': values.get('city_p', ''),
                    'zip': values.get('zip_p', ''),
                    'phone': values.get('phone', ''),
                    'mobile': values.get('mobile', ''),
                    'email': values.get('email', ''),
                    # Populate other fields accordingly
                }

                partner = self.env['res.partner'].create(partner_values)
                rec.partner_id = partner.id

        return super(StudentReg, self).write(values)

    def action_report_print_booking(self):
        building_meterial = self.env.ref(
            'student.action_report_print_students')
        print('building_meterial', building_meterial)
        if building_meterial:
            report_id = self.env.ref(
                'student.action_report_print_students').id
            printer = self.env.ref(
                'student.action_report_print_students').default_print_option
            rep_name = self.env.ref(
                'student.action_report_print_students').report_name
            result = {'type': 'ir.actions.report', 'id': report_id,
                      'report_type': "qweb-pdf",
                      'binding_type': 'report',
                      'attachment': "",
                      'print_report_name': "(object._get_report_base_filename())",
                      'report_file': "report_print_students",
                      'report_name': rep_name,
                      'default_print_option': printer,
                      'multi': 'false',
                      'binding_view_types': "list,form",
                      'model': 'student.registration',
                      'xml_id': "student.action_report__print_students",
                      'context': ({'active_id': self.id,
                                   'active_ids': self.ids,
                                   'active_model': 'student.registration'})}
            return result

class StudentCourse(models.Model):
    _name = 'student.course'
    _description = 'Student Course'

    name = fields.Char(string='Course Name', required=True)
    duration = fields.Integer(string='Duration (in months)')
    fees = fields.Float(string='Fees')

class StudentEducation(models.Model):
    _name = 'student.education'
    _description = 'Student Education'

    student_id = fields.Many2one('student.registration', string='Student')
    education = fields.Char(string='Education')
    university = fields.Char(string='University')
    year_of_passing = fields.Char(string='Year of Passing')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    ugc_institute = fields.Char(string='Institution')
    cgpa_obtained = fields.Float(string='CGPA')