from typing import Final

from questionpy_common.misc import Bytes, ByteSize

# Request.
MAX_BYTES_PACKAGE: Final[Bytes] = Bytes(20, ByteSize.MiB)
MAX_BYTES_QUESTION_STATE: Final[Bytes] = Bytes(2, ByteSize.MiB)
