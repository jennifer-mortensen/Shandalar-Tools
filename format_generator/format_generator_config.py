from common import common_const
from dataclasses import dataclass

@dataclass
class FormatGeneratorConfig:
    encoding_scan: common_const.EncodingScanMode = common_const.EncodingScanMode.AUTO