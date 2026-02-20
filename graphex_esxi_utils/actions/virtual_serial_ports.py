from graphex import Boolean, String, Number, Node, InputSocket, OutputSocket, ListOutputSocket, OptionalInputSocket, EnumInputSocket
from graphex_esxi_utils import esxi_constants, datatypes, exceptions
from graphex import exceptions as graphex_exceptions
import esxi_utils
import typing

class EsxiVirtualDeviceAddSerialPortFileBacking(Node):
    name: str = "ESXi VirtualDevice Add Serial Port (File Backing)"
    description: str = "Add a new Serial Port to the VM's devices. The VM must be powered off. Serial Ports can be configured to either log to files or as network outputing devices. This node is for outputting to a log file in a provided ESXi datastore. The file in the datastore could then be 'followed' over SSH to the ESXi host itself. For adding a network backed node instead, please see the node: 'ESXi VirtualDevice Add Serial Port (Network Backing)'."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VM

    vm = InputSocket(datatype=datatypes.VirtualMachine, name="Virtual Machine", description="The Virtual Machine to use.")
    filepath = InputSocket(
        datatype=datatypes.DatastoreFile, name="DatastoreFile Path", description="The path to the file to create/use in the datastore as a DatastoreFile object."
    )
    yield_on_poll = InputSocket(datatype=Boolean, name="Yield on Poll", description="When True, the virtual device yields CPU when the guest polls the serial port while no data is available. This can reduce CPU usage for guests that aggressively poll the serial port.", input_field=True)
    start_connected = InputSocket(datatype=Boolean, name="Start Connected", description="Whether this serial port should be connected when the VM powers on or not.", input_field=True)
    allow_guest_control = InputSocket(datatype=Boolean, name="Allow Guest Control", description="When True, the guest is permitted (where supported) to connect/disconnect the serial device. When False, connection state is controlled only by ESXi/vSphere configuration/UI/API.", input_field=True)
    idempotent = InputSocket(datatype=Boolean, name="Idempotent", description="When True, the method checks whether a serial port already exists with the same file backing path and returns that existing port rather than adding a duplicate. When False, the method will always attempt to add a new serial port, which can create duplicates if called multiple times with the same filepath.", input_field=True)

    output = OutputSocket(datatype=datatypes.VirtualDevice, name="SerialPort VirtualDevice", description="The `VirtualDevice` object for the newly added Serial Port.")

    def log_prefix(self):
        return f"[{self.name} - {self.vm.name}] "

    def run(self):
        self.log(f"Adding Serial Port with file backing at datastore path: {self.filepath.path}")
        self.output = self.vm.serial_ports.add_file_backing(self.filepath, self.yield_on_poll, self.start_connected, self.allow_guest_control, self.idempotent)

# TODO
# class EsxiVirtualDeviceAddSerialPortNetworkBacking(Node):
#     name: str = "ESXi VirtualDevice Add Serial Port (Network Backing)"
#     description: str = "Add a new Serial Port to the VM's devices. The VM must be powered off. Serial Ports can be configured to either log to files or as network outputing devices. This node is for outputting to a log file over a network. Additional configuration is required by the connection on the other end from ESXi. For adding a file backed node instead, please see the node: 'ESXi VirtualDevice Add Serial Port (File Backing)'."
#     categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
#     color: str = esxi_constants.COLOR_VM

# TODO more nodes (this is just a copy paste to template off of)
# class EsxiVirtualDeviceVideoCardRAMSize(Node):
#     name: str = "ESXi Video Card VirtualDevice Get VRAM Size"
#     description: str = "Get the RAM size of this Video Card in KB."
#     categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Video Card"]
#     color: str = esxi_constants.COLOR_VIRT_VIDEO_CARD

#     vd = InputSocket(datatype=datatypes.VirtualDevice, name="Video Card Virtual Device", description="The Video Card Virtual Device to use.")
#     output = OutputSocket(datatype=Number, name="RAM Size (KB)", description="The size of this video card's VRAM in KB.")

#     def run(self):
#         assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualVideoCard), "Not a VirtualVideoCard"
#         self.output = self.vd.videoRamSizeKB
