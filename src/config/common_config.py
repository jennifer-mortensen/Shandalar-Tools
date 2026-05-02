from common import common_const
from dataclasses import dataclass

@dataclass
class CommonConfig:
    data_shandalar_card_pool: str = "shandalar_2016"
    io_encoding_scan: common_const.EncodingScanMode = common_const.EncodingScanMode.AUTO
    log_preview_limit: int = 5
    log_overwrite: bool = True