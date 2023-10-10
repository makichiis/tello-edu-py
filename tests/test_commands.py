from tello_edu_protocol import commands

def test_command() -> None:
    cmd, _ = commands.command()
    assert cmd == 'command'


def test_takeoff() -> None:
    cmd, _ = commands.takeoff()
    assert cmd == 'takeoff'


def test_up() -> None:
    cmd, _ = commands.up(100)
    assert cmd == 'up 100'

    try:
        commands.up(10)
        assert False

    except commands.RTFM:
        pass


def test_down() -> None:
    cmd, _ = commands.down(300)
    assert cmd == 'down 300'

    try:
        commands.down(-50)
        assert False
    
    except commands.RTFM:
        pass
