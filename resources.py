import pyglet
        
class PygletSoundCache(dict):
    def __init__(self):
        '''
        Initialisation.
        
        @param fn: A function or function pointer that will be used on cache misses 
        '''
        dict.__init__(self)

    def __getitem__(self, item):
        '''
        First make a cache request and on miss cache the requested resource
        '''
        if item in self:
            return dict.__getitem__(self, item)
        else:
            dict.__setitem__(self, item, pyglet.resource.media(item, streaming = False))
            return dict.__getitem__(self, item)

    