from dataclasses import dataclass
from typing import Union, Sequence, List


@dataclass
class SyncConfig:
    excludes: Union[List[str], None] = None
    local_to_remote: bool = False
    remote_to_local: bool = False
    delete_missing: bool = False
    allow_overwrite: bool = True
    allow_replace: bool = False
    copy_links: bool = False
    dry_run: bool = False
    time_range: Union[Sequence[int], None] = None
    del_source: bool = False
