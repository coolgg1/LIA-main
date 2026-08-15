from daemon.device import DeviceRegistry


def test_register_device_creates_record(tmp_path):
    registry = DeviceRegistry(str(tmp_path / "devices.json"))
    device = registry.register_device("test-device", {"platform": "linux"})

    assert device.device_id
    assert device.name == "test-device"
    assert registry.get_device(device.device_id).name == "test-device"
    assert registry.list_devices()[0]["metadata"]["platform"] == "linux"
