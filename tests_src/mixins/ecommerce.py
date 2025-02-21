from mcurriculum.schools.assign_license_manager import AssignLicenseManager
from mcurriculum.schools.models import AssignCoursesLog


class EcommerceAssignAccessMixin(object):
    def assign_course_for_user(self, code_details, user):
        """
        Assign license for one user
        Args:
            code_details: database CodeDetails with configured Codes
            user: database User entity
        """
        self.assign_course_for_users(code_details, [user])

    def assign_course_for_users(self, code_details, users):
        """
        Assign license for provided users/
        Args:
            code_details: database CodeDetails with configured Codes
            users: List of user
        """
        code_details.aquire_lock()
        assign_courses_log = AssignCoursesLog.objects.create(
            users=[user.pk for user in users],
            code_detail=code_details,
            assignee_type='school_class'
        )

        assign_license_manager = AssignLicenseManager(assign_courses_log, code_details)
        assign_license_manager.initialize()
        assign_license_manager.assign_licenses()
        assign_courses_log.delete()
        code_details.release_lock()