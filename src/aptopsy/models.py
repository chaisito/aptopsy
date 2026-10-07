from dataclasses import dataclass, field

@dataclass
class PackageInfo:
	name: str
	version: str | None = None
	architecture: str | None = None
	status: str | None = None
	installed_size_kb: int | None = None
	manually_installes : bool | None = None

	dependencies: list[str] = field(default_factory=list)
	reverse_dependencies: list[str] = field(default_factory=list)
	files: list[str] = field(default_factory=list)
	config_files: list[str] = field(default_factory=list)
