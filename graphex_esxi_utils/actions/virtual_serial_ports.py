from graphex import Boolean, String, Node, InputSocket, OutputSocket, OptionalInputSocket, EnumInputSocket
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


class EsxiVirtualDeviceAddSerialPortNetworkBacking(Node):
    name: str = "ESXi VirtualDevice Add Serial Port (Network Backing)"
    description: str = "Add a new Serial Port to the VM's devices. The VM must be powered off. Serial Ports can be configured to either log to files or as network outputing devices. This node is for outputting to a log file over a network. Additional configuration is required by the connection on the other end from ESXi. For adding a file backed node instead, please see the node: 'ESXi VirtualDevice Add Serial Port (File Backing)'."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VM

    vm = InputSocket(datatype=datatypes.VirtualMachine, name="Virtual Machine", description="The Virtual Machine to use.")

    service_uri = InputSocket(datatype=String, name="Service URI", description="The URI that defines how the serial port connects over the network (e.g.: 'tcp://:7000' ESXi listens on port 7000 (when direction='server'), 'tcp://10.0.0.10:7000' ESXi connects to 10.0.0.10:7000 (when direction='client', 'telnet://...')")
    direction = EnumInputSocket(datatype=String, name="Direction", description="Controls whether ESXi listens locally or connects outward.", input_field="server",enum_members=['server','client'])
    yield_on_poll = InputSocket(datatype=Boolean, name="Yield on Poll", description="When True, the virtual device yields CPU when the guest polls the serial port while no data is available. This can reduce CPU usage for guests that aggressively poll the serial port.", input_field=True)
    start_connected = InputSocket(datatype=Boolean, name="Start Connected", description="Whether this serial port should be connected when the VM powers on or not.", input_field=True)
    allow_guest_control = InputSocket(datatype=Boolean, name="Allow Guest Control", description="When True, the guest is permitted (where supported) to connect/disconnect the serial device. When False, connection state is controlled only by ESXi/vSphere configuration/UI/API.", input_field=True)
    idempotent = InputSocket(datatype=Boolean, name="Idempotent", description="When True, the method checks whether a serial port already exists with the same file backing path and returns that existing port rather than adding a duplicate. When False, the method will always attempt to add a new serial port, which can create duplicates if called multiple times with the same filepath.", input_field=True)
    proxy_uri = OptionalInputSocket(datatype=String, name="Proxy URI", description="Optional proxy endpoint for the serial connection. Set this to a stable, client-reachable endpoint (DNS name/IP:port) that represents a serial “front door” for the VM in a vCenter cluster, so users/tools don’t need to connect to whatever ESXi host is currently running the VM. Use it when the VM can vMotion/DRS and direct host access is undesirable or impossible. In practice this is the address of a TCP proxy/bastion/load balancer (or other serial-proxy service) that will forward traffic to the active ESXi host’s service_uri. Leave it as None if clients can safely connect directly to the ESXi host address/port described by service_uri.")
    proxy_direction = EnumInputSocket(datatype=String, name="Proxy Direction", description="Optional proxy direction, typically 'server' or 'client'. Usually left as none unless proxy_uri is set and your environment requires it. Set this to match how the proxy_uri endpoint behaves: use 'server' if clients connect to the proxy (the proxy listens) and then the proxy relays to ESXi, which is the common vCenter/cluster pattern. Use 'client' only if your proxy is the side that initiates an outbound connection to the next hop rather than listening for inbound client connections. Typically you set proxy_direction only when proxy_uri is set, and it usually matches the main direction in clustered “stable endpoint” deployments.", input_field="none",enum_members=['none', 'server','client'])

    output = OutputSocket(datatype=datatypes.VirtualDevice, name="SerialPort VirtualDevice", description="The `VirtualDevice` object for the newly added Serial Port.")

    def log_prefix(self):
        return f"[{self.name} - {self.vm.name}] "

    def run(self):
        self.log(f"Adding Serial Port with network/URI backing...")
        direction = self.direction.lower().strip()
        valid_directions = ["server", "client"]
        valid_proxy_directions = ["none", "server", "client"]
        if direction not in valid_directions:
            raise graphex_exceptions.InvalidParameterError(self.name, "Direction", direction, valid_directions)
        proxy_direction = self.proxy_direction.lower().strip() if self.proxy_direction else None
        if proxy_direction and proxy_direction not in valid_proxy_directions:
            raise graphex_exceptions.InvalidParameterError(self.name, "Proxy Direction", proxy_direction, valid_proxy_directions)
        if proxy_direction is "none":
            proxy_direction = None
        self.output = self.vm.serial_ports.add_uri_backing(self.service_uri, self.direction, self.yield_on_poll, self.start_connected, self.allow_guest_control, self.idempotent, self.proxy_uri if self.proxy_uri else None, proxy_direction)

class EsxiVirtualDeviceSerialPortGetBackingType(Node):
    name: str = "ESXi Serial Port Get Backing Type"
    description: str = "Gets the 'backing type' for this Serial Port Virtual Device Object. This is set only when the serial port is created on the VM and can be either the string 'file' (for a serial port that logs to a datastore file) or 'uri' (for a serial port that outputs over a network connection). In rare cases (if something goes wrong in ESXi), the backing type may become 'other'."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=String, name="Backing Type", description="This is set only when the serial port is created on the VM and can be either the string 'file' (for a serial port that logs to a datastore file) or 'uri' (for a serial port that outputs over a network connection).")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        self.output = self.vd.backing_type

class EsxiVirtualDeviceSerialPortBackingTypeIsFile(Node):
    name: str = "ESXi Serial Port Backing Type Is File"
    description: str = "Outputs True if the 'backing type' for this Serial Port Virtual Device Object is set to 'file' (also see 'ESXi Serial Port Get Backing Type'). Otherwise this node will output False (indicating the backing type is a different type)."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=Boolean, name="Has File Backing Type", description="This is set only when the serial port is created on the VM and can be either the string 'file' (for a serial port that logs to a datastore file) or 'uri' (for a serial port that outputs over a network connection).")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        self.output = (self.vd.backing_type == 'file')

class EsxiVirtualDeviceSerialPortBackingTypeIsNetwork(Node):
    name: str = "ESXi Serial Port Backing Type Is URI Network"
    description: str = "Outputs True if the 'backing type' for this Serial Port Virtual Device Object is set to 'uri' (also see 'ESXi Serial Port Get Backing Type'). Otherwise this node will output False (indicating the backing type is a different type)."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=Boolean, name="Has URI Backing Type", description="This is set only when the serial port is created on the VM and can be either the string 'file' (for a serial port that logs to a datastore file) or 'uri' (for a serial port that outputs over a network connection).")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        self.output = (self.vd.backing_type == 'uri')

class EsxiVirtualDeviceSerialPortGetYieldOnPoll(Node):
    name: str = "ESXi Serial Port Get Yield On Poll"
    description: str = "Gets the value of the 'Yield on Poll' setting for this Serial Port Virtual Device Object. When True, the virtual device yields CPU when the guest polls the serial port while no data is available. This can reduce CPU usage for guests that aggressively poll the serial port."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=Boolean, name="Is Yielding On Poll", description="When True, the virtual device yields CPU when the guest polls the serial port while no data is available. This can reduce CPU usage for guests that aggressively poll the serial port.")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        self.output = self.vd.yield_on_poll

class EsxiVirtualDeviceSerialPortSetYieldOnPoll(Node):
    name: str = "ESXi Serial Port Set Yield On Poll"
    description: str = "Sets the value of the 'Yield on Poll' setting for this Serial Port Virtual Device Object. When True, the virtual device yields CPU when the guest polls the serial port while no data is available. This can reduce CPU usage for guests that aggressively poll the serial port."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    use_yop = InputSocket(datatype=Boolean, name="Yield On Poll", description="When set to True, the virtual device yields CPU when the guest polls the serial port while no data is available. This can reduce CPU usage for guests that aggressively poll the serial port.")

    vdo = OutputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The same Serial Port that was input. Simply provided here as an output for easy reuse.")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        self.vd.yield_on_poll = self.use_yop
        self.vdo = self.vd

class EsxiVirtualDeviceSerialPortGetFile(Node):
    name: str = "ESXi Serial Port Get File"
    description: str = "Gets the DatastoreFile object for this Serial Port Virtual Device Object. This node assumes your serial port is the 'file' backing type and was created using the 'ESXi VirtualDevice Add Serial Port (File Backing)' node. If your serial port has a different backing type, then this node will raise a 'WrongSerialPortBackingError' exception when executed."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=datatypes.DatastoreFile, name="DatastoreFile", description="The DatastoreFile object for this Serial Port Virtual Device Object. This is effectively the path to the file in the datastore containing the logs streamed to this serial port adapter.")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        if self.vd.backing_type != 'file':
            raise exceptions.WrongSerialPortBackingError(self.name, 'file', self.vd.backing_type)
        self.output = self.vd.file

class EsxiVirtualDeviceSerialPortGetUri(Node):
    name: str = "ESXi Serial Port Get URI"
    description: str = "Gets the URI string for this Serial Port Virtual Device Object. This node assumes your serial port is the network 'uri' backing type and was created using the 'ESXi VirtualDevice Add Serial Port (Network Backing)' node. If your serial port has a different backing type, then this node will raise a 'WrongSerialPortBackingError' exception when executed."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=String, name="URI", description="The URI that defines how the serial port connects over the network (e.g.: 'tcp://:7000' ESXi listens on port 7000 (when direction='server'), 'tcp://10.0.0.10:7000' ESXi connects to 10.0.0.10:7000 (when direction='client', 'telnet://...')")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        if self.vd.backing_type != 'uri':
            raise exceptions.WrongSerialPortBackingError(self.name, 'uri', self.vd.backing_type)
        self.output = self.vd.uri_service

class EsxiVirtualDeviceSerialPortGetUriDirection(Node):
    name: str = "ESXi Serial Port Get URI Direction"
    description: str = "Gets the URI direction string for this Serial Port Virtual Device Object. This node assumes your serial port is the network 'uri' backing type and was created using the 'ESXi VirtualDevice Add Serial Port (Network Backing)' node. If your serial port has a different backing type, then this node will raise a 'WrongSerialPortBackingError' exception when executed."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=String, name="URI Direction", description="Values are typically 'server' or 'client'. Controls whether ESXi listens locally or connects outward.")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        if self.vd.backing_type != 'uri':
            raise exceptions.WrongSerialPortBackingError(self.name, 'uri', self.vd.backing_type)
        self.output = self.vd.uri_direction

class EsxiVirtualDeviceSerialPortGetUriProxy(Node):
    name: str = "ESXi Serial Port Get Proxy URI"
    description: str = "Gets the URI proxy string for this Serial Port Virtual Device Object. This node assumes your serial port is the network 'uri' backing type and was created using the 'ESXi VirtualDevice Add Serial Port (Network Backing)' node. If your serial port has a different backing type, then this node will raise a 'WrongSerialPortBackingError' exception when executed."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=String, name="Proxy URI", description="Optional proxy endpoint for the serial connection. This will be an 'empty string' if this was not set or is not in use.")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        if self.vd.backing_type != 'uri':
            raise exceptions.WrongSerialPortBackingError(self.name, 'uri', self.vd.backing_type)
        self.output = self.vd.uri_proxy_service if self.vd.uri_proxy_service else ""

class EsxiVirtualDeviceSerialPortGetUriProxy(Node):
    name: str = "ESXi Serial Port Get Proxy URI Direction"
    description: str = "Gets the URI proxy direction string for this Serial Port Virtual Device Object. This node assumes your serial port is the network 'uri' backing type and was created using the 'ESXi VirtualDevice Add Serial Port (Network Backing)' node. If your serial port has a different backing type, then this node will raise a 'WrongSerialPortBackingError' exception when executed."
    categories: typing.List[str] = ["ESXi", "Virtual Machine", "Hardware", "Virtual Devices", "Serial Port"]
    color: str = esxi_constants.COLOR_VIRT_SERIAL_PORT

    vd = InputSocket(datatype=datatypes.VirtualDevice, name="Serial Port Virtual Device", description="The Serial Port Virtual Device to use.")
    output = OutputSocket(datatype=String, name="Proxy URI Direction", description="Optional proxy direction, typically 'server' or 'client'. This will be an 'empty string' if this was not set, was set to 'none' originally, or is not in use.")

    def run(self):
        assert isinstance(self.vd, esxi_utils.vm.hardware.VirtualSerialPort), "Not a VirtualSerialPort"
        if self.vd.backing_type != 'uri':
            raise exceptions.WrongSerialPortBackingError(self.name, 'uri', self.vd.backing_type)
        self.output = self.vd.uri_proxy_direction if self.vd.uri_proxy_direction else ""
