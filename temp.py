import pyglet



def test():
    pass

if __name__ == '__main__':
    player = pyglet.media.Player()
    music = pyglet.resource.media('res/sounds/Jump.wav', streaming = True)
    player.queue(music)
    player.eos_action = player.EOS_LOOP
    player.play()
    while True:
        pass