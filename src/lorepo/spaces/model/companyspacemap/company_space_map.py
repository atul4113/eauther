from src.libraries.utility import cacheproxy as cache
from src.lorepo.spaces.model.companyspacemap.multitasks_locker import CompanySpaceMapTaskLocker
from src.lorepo.spaces.util import get_cached_kids


# a whole cached map of company spaces represented as a list of tuples
# each space is represented by id, parent id, list of child spaces

class CompanySpaceMap(object):

    CACHE_PREFIX = "company_space_map_%s"

    def __init__(self, company_space_id=None):
        self.space_dict = {}
        if company_space_id:
            self.space_dict[str(company_space_id)] = (company_space_id, None, [])
            self._get_leaves(company_space_id)


    @staticmethod
    def fresh(space_id):
        cache.delete(CompanySpaceMap.CACHE_PREFIX % space_id )
        return CompanySpaceMap(space_id)

    @staticmethod
    def is_in_cache(company_space_id):
        return cache.get( CompanySpaceMap.CACHE_PREFIX % (company_space_id, ) )

    @staticmethod
    def cached(company_space_id):
        data = cache.get( CompanySpaceMap.CACHE_PREFIX % (company_space_id, ) )
        if data:
            csm = CompanySpaceMap()
            csm._parse( data )
        else:
            csm = CompanySpaceMap(company_space_id)
            cache.set(CompanySpaceMap.CACHE_PREFIX  % (company_space_id), csm._serialize())
            CompanySpaceMapTaskLocker(company_space_id).close()
        return csm

    def _get_leaves(self, node_space_id):
        spaces = get_cached_kids(node_space_id)
        for space in spaces:
            self.space_dict[str(node_space_id)][2].append(space.id)
            self.space_dict[str(space.id)] = (space.id, space.parent_id, [])
        for space in spaces:
            self._get_leaves(space.id)

    def _parse(self,data):
        import bz2, json
        self.space_dict = json.loads(bz2.decompress(data))

    def _serialize(self):
        import bz2, json
        return bz2.compress(json.dumps(self.space_dict))

    def set_private(self, space):
        try:
            self.space_dict[str(space.id)] = (space.id, None, [])
        except:
            self.space_dict = {}
            self.space_dict[str(space.id)] = (space.id, None, [])
        self._get_leaves(space.id)

    def space(self, space_id):
        space = self.space_dict[str(space_id)] #this dict holds tuples (id, parent_id, [kids_ids])
        return {'id': space[0],
                'parent_id': space[1],
                'kids': space[2]}

    def descendants_for_space_id(self, space_id):
        try:
            descendants = self.space_dict[str(space_id)][2]
        except:
            descendants = [] #private user space might not be in the space_dict
        for desc_id in descendants:
            descendants.extend(self.space_dict[str(desc_id)][2])
        return list(set(descendants))