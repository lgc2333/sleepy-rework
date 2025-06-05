from collections.abc import Generator, Sequence
from datetime import datetime
from io import IOBase
from os import PathLike
from typing import Any, BinaryIO, ClassVar, Literal, Self, overload

from _typeshed import Incomplete, ReadableBuffer

DEFAULT_CHARSET: str
WINDOW_NORMAL: str
WINDOW_MAXIMIZED: str
WINDOW_MINIMIZED: str
DRIVE_UNKNOWN: str
DRIVE_NO_ROOT_DIR: str
DRIVE_REMOVABLE: str
DRIVE_FIXED: str
DRIVE_REMOTE: str
DRIVE_CDROM: str
DRIVE_RAMDISK: str
ROOT_MY_COMPUTER: str
ROOT_MY_DOCUMENTS: str
ROOT_NETWORK_SHARE: str
ROOT_NETWORK_SERVER: str
ROOT_NETWORK_PLACES: str
ROOT_NETWORK_DOMAIN: str
ROOT_INTERNET: str
RECYCLE_BIN: str
ROOT_CONTROL_PANEL: str
ROOT_USER: str
ROOT_UWP_APPS: str
TYPE_FOLDER: str
TYPE_FILE: str

def read_byte(buf: BinaryIO) -> int: ...
def read_short(buf: BinaryIO) -> int: ...
def read_int(buf: BinaryIO) -> int: ...
def read_double(buf: BinaryIO) -> float: ...
def read_cunicode(buf: BinaryIO) -> str: ...
def read_cstring(buf: BinaryIO, padding: bool = False) -> str: ...
@overload
def read_sized_string(buf: BinaryIO, string: Literal[False]) -> bytes: ...
@overload
def read_sized_string(buf: BinaryIO, string: Literal[True] = True) -> str: ...
@overload
def read_sized_string(buf: BinaryIO, string: bool) -> str | bytes: ...
def get_bits(value: int, start: int, count: int, length: int = 16) -> int: ...
def read_dos_datetime(buf: BinaryIO) -> None: ...
def write_byte(val: int, buf: BinaryIO) -> None: ...
def write_short(val: int, buf: BinaryIO) -> None: ...
def write_int(val: int, buf: BinaryIO) -> None: ...
def write_double(val: float, buf: BinaryIO) -> None: ...
def write_cstring(val: str, buf: BinaryIO, padding: bool = False) -> None: ...
def write_cunicode(val: str, buf: BinaryIO) -> None: ...
@overload
def write_sized_string(
    val: bytes,
    buf: BinaryIO,
    string: Literal[False],
) -> None: ...
@overload
def write_sized_string(
    val: str,
    buf: BinaryIO,
    string: Literal[True] = True,
) -> None: ...
@overload
def write_sized_string(
    val: str | bytes,
    buf: BinaryIO,
    string: bool,
) -> None: ...
def put_bits(
    bits: int,
    target: int,
    start: int,
    count: int,
    length: int = 16,
) -> None: ...
def write_dos_datetime(val: None, buf: BinaryIO) -> None: ...
def convert_time_to_unix(windows_time: float) -> datetime: ...
def convert_time_to_windows(unix_time: datetime | float) -> int: ...

class FormatException(Exception): ...
class MissingInformationException(Exception): ...
class InvalidKeyException(Exception): ...

def guid_from_bytes(bytes: str) -> str: ...
def bytes_from_guid(guid: str) -> bytes: ...
def assert_lnk_signature(f: BinaryIO) -> None: ...
def is_lnk(f: BinaryIO) -> bool: ...
def path_levels(p: str) -> Generator[str, Any, None]: ...
def is_drive(data: str) -> bool: ...

class Flags:
    def __init__(self, flag_names: tuple[str, ...], flags_bytes: int = 0) -> None: ...
    def set_flags(self, flags_bytes: int) -> None: ...
    @property
    def bytes(self) -> int: ...
    def __getitem__(self, key: str) -> bool: ...
    def __setitem__(self, key: str, value: bool) -> None: ...
    def __getattr__(self, key: str) -> bool: ...
    def __setattr__(self, key: str, value: bool) -> None: ...

class ModifierKeys(Flags):
    def __init__(self, flags_bytes: int = 0) -> None: ...

class RootEntry:
    root: str
    guid: str
    def __init__(self, root: str) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class DriveEntry:
    drive: str
    def __init__(self, drive: str) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class PathSegmentEntry:
    type: str | None
    file_size: int | None
    modified: datetime | None
    short_name: str | None
    created: datetime | None
    accessed: datetime | None
    full_name: str | None
    # localized_name: str | None  # this attr may not be defined
    def __init__(self, bytes: BinaryIO | None = None) -> None: ...
    @classmethod
    def create_for_path(cls, path: PathLike) -> Self: ...
    @property
    def bytes(self) -> bytes | None: ...

class UwpSubBlock:
    block_names: ClassVar[dict[int, str]]
    block_types: ClassVar[dict[str, int]]
    type: str
    value: str
    name: str | None
    def __init__(
        self,
        bytes: BinaryIO | None = None,
        type: str | None = None,
        value: str | None = None,
    ) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class UwpMainBlock:
    magic: ClassVar[bytes]
    guid: str
    def __init__(
        self,
        bytes: BinaryIO | None = None,
        guid: str | None = None,
        blocks: list[UwpSubBlock] | None = None,
    ) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class UwpSegmentEntry:
    magic: ClassVar[bytes]
    header: ClassVar[bytes]
    def __init__(self, bytes: ReadableBuffer | None = None) -> None: ...
    @property
    def bytes(self) -> bytes: ...
    @classmethod
    def create(
        cls,
        package_family_name: str,
        target: str,
        location: str | None = None,
        logo44x44: str | None = None,
    ) -> Self: ...

class LinkTargetIDList:
    items: list[PathSegmentEntry | DriveEntry | UwpSegmentEntry]
    def __init__(self, bytes: ReadableBuffer | None = None) -> None: ...
    def get_path(self) -> str: ...
    @property
    def bytes(self) -> bytes: ...

class LinkInfo:
    # start: int | None  # this attr may not be defined
    size: int | None
    header_size: int
    local: int
    remote: int
    offs_local_volume_table: int
    offs_local_base_path: int
    offs_network_volume_table: int
    offs_base_name: int
    drive_type: str | None
    drive_serial: int | None
    volume_label: str | None
    local_base_path: str | None
    network_share_name: str | None
    base_name: str | None
    def __init__(self, lnk: BinaryIO | None = None) -> None: ...
    def make_path(self) -> None: ...
    def write(self, lnk: BinaryIO) -> None: ...
    @property
    def path(self) -> str | None: ...

EXTRA_DATA_TYPES: dict[str, int] = ...

class ExtraData_Unparsed:
    data: Incomplete
    @overload
    def __init__(
        self,
        bytes: bytes | None = None,
        signature: int | None = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *,
        signature: int | None = None,
        data: bytes | None = None,
    ) -> None: ...
    def bytes(self) -> bytes: ...

def padding(val: bytes, size: int, byte: bytes = b"\x00") -> bytes: ...

class ExtraData_IconEnvironmentDataBlock:
    target_ansi: str | None
    target_unicode: str | None
    def __init__(self, bytes: ReadableBuffer | None = None) -> None: ...
    def read(self, bytes: ReadableBuffer) -> None: ...
    def bytes(self) -> bytes: ...

def guid_to_str(guid: bytes) -> str: ...

class TypedPropertyValue:
    type: int | None
    value: bytes | None
    def __init__(
        self,
        bytes: bytes | None = None,
        type: int | None = None,
        value: bytes | None = None,
    ) -> None: ...
    def set_string(self, value: str) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class PropertyStore:
    is_strings: bool
    properties: list[TypedPropertyValue]
    format_id: bytes | None
    def __init__(
        self,
        bytes: BinaryIO | None = None,
        properties: list[TypedPropertyValue] | None = None,
        format_id: bytes | None = None,
        is_strings: bool = False,
    ) -> None: ...
    def read(self, bytes_io: BinaryIO) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class ExtraData_PropertyStoreDataBlock:
    stores: list[PropertyStore]
    def __init__(
        self,
        bytes: ReadableBuffer | None = None,
        stores: list[PropertyStore] | None = None,
    ) -> None: ...
    def read(self, bytes: ReadableBuffer) -> None: ...
    def bytes(self) -> bytes: ...

class ExtraData_EnvironmentVariableDataBlock:
    target_ansi: str | None
    target_unicode: str | None
    def __init__(self, bytes: ReadableBuffer | None = None) -> None: ...
    def read(self, bytes: ReadableBuffer) -> None: ...
    def bytes(self) -> bytes: ...

EXTRA_DATA_TYPES_CLASSES: dict[
    str,
    type[
        ExtraData_IconEnvironmentDataBlock
        | ExtraData_PropertyStoreDataBlock
        | ExtraData_EnvironmentVariableDataBlock
    ],
]

class ExtraData:
    blocks: list[
        ExtraData_Unparsed
        | ExtraData_IconEnvironmentDataBlock
        | ExtraData_PropertyStoreDataBlock
        | ExtraData_EnvironmentVariableDataBlock
    ]
    def __init__(
        self,
        lnk: BinaryIO | None = None,
        blocks: list[
            ExtraData_Unparsed
            | ExtraData_IconEnvironmentDataBlock
            | ExtraData_PropertyStoreDataBlock
            | ExtraData_EnvironmentVariableDataBlock
        ]
        | None = None,
    ) -> None: ...
    @property
    def bytes(self) -> bytes: ...

class Lnk:
    file: str | None
    link_flags: Flags
    file_flags: Flags
    creation_time: datetime
    access_time: datetime
    modification_time: datetime
    file_size: int
    icon_index: int
    hot_key: str | None
    description: str | None
    relative_path: str | None
    work_dir: str | None
    arguments: str | None
    icon: str | None
    extra_data: ExtraData | None
    def __init__(self, f: str | BinaryIO | None = None) -> None: ...
    def save(self, f: str | IOBase | None = None, force_ext: bool = False) -> None: ...
    def write(self, lnk: BinaryIO) -> None: ...
    @property
    def shell_item_id_list(self) -> LinkTargetIDList: ...
    @shell_item_id_list.setter
    def shell_item_id_list(self, value: LinkTargetIDList) -> None: ...
    @property
    def link_info(self) -> LinkInfo: ...
    @link_info.setter
    def link_info(self, value: LinkInfo) -> None: ...
    @property
    def working_dir(self) -> Any: ...
    @working_dir.setter
    def working_dir(self, value: Any) -> None: ...
    @property
    def window_mode(self) -> str: ...
    @window_mode.setter
    def window_mode(self, value: str) -> None: ...
    @property
    def show_command(self) -> str: ...
    @show_command.setter
    def show_command(self, value: str) -> None: ...
    @property
    def path(self) -> str: ...
    def specify_local_location(
        self,
        path: str,
        drive_type: str | None = None,
        drive_serial: str | None = None,
        volume_label: str | None = None,
    ) -> None: ...
    def specify_remote_location(
        self,
        network_share_name: str,
        base_name: str,
    ) -> None: ...

def parse(lnk: str | BinaryIO) -> Lnk: ...
def create(f: str | BinaryIO | None = None) -> Lnk: ...
def for_file(
    target_file: str,
    lnk_name: str | BinaryIO | None = None,
    arguments: str | None = None,
    description: str | None = None,
    icon_file: str | None = None,
    icon_index: int = 0,
    work_dir: str | None = None,
    window_mode: str | None = None,
) -> Lnk: ...
def from_segment_list(
    data: list[str | dict] | tuple[str | dict, ...],
    lnk_name: str | BinaryIO | None = None,
) -> Lnk: ...
def build_uwp(
    package_family_name: str,
    target: str,
    location: str | None = None,
    logo44x44: str | None = None,
    lnk_name: str | BinaryIO | None = None,
) -> Lnk: ...
def get_prop(obj: object, prop_queue: Sequence[str]) -> Any: ...
def cli() -> None: ...
