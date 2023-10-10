from tello_edu_protocol import DroneState

def test_DroneState_from_raw() -> None:
    state = 'mid:-1;x:0;y:0;z:0;mpry:0,0,0;pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:79;temph:82;tof:6553;h:0;bat:89;baro:51.81;time:0;agx:-8.00;agy:4.00;agz:-1050.00;'
    state = DroneState.from_raw(state)

    assert state == DroneState(
        mid=-1,
        x=0,
        y=0,
        z=0,
        mpry=(0, 0, 0),
        pitch=0,
        roll=0,
        yaw=0,
        vgx=0,
        vgy=0,
        vgz=0,
        templ=79,
        temph=82,
        tof=6553,
        h=0,
        bat=89,
        baro=51.81,
        time=0,
        agx=-8.0,
        agy=4.0,
        agz=-1050.0
    )

if __name__ == "__main__":
    test_DroneState_from_raw()
