from lorepo.permission.decorators import has_space_access


class HasSpacePermissionMixin(object):

    permission = None
    is_company = False

    def dispatch(self, request, *args, **kwargs):
        has_space_access(self.permission, is_company=self.is_company)
        return super(HasSpacePermissionMixin, self).dispatch(request, *args, **kwargs)
