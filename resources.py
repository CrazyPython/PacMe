class Cache(dict):
    '''
    A class used for caching queries. Nothing fancy, no expiration etc as this is a small game
    '''
    def __init__(self):
        '''
        Nothing here to see other than intialisation...
        '''
        dict.__init__(self)

    def __getitem__(self, item):
        '''
        First make a cache request and on miss cache the requested resource
        '''
        if item in self:
            return dict.__getitem__(self, item)
        else:
            dict.__setitem__(self, item, self.__fn(item))
            return dict.__getitem__(self, item)