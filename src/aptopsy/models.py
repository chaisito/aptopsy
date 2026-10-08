from dataclasses import dataclass, field


@dataclass
class IntegrityIssue:
    path: str
    flags: str
    is_config: bool = False
    missing: bool = False
    error: str | None = None

    @property
    def content_changed(self) -> bool:
        return (
            not self.missing
            and len(self.flags) >= 3
            and self.flags[2] == "5"
        )

    @property
    def mode_check_failed(self) -> bool:
        return (
            not self.missing
            and len(self.flags) >= 2
            and self.flags[1] == "M"
        )

@dataclass
class RepositoryInfo:
    installed: str | None = None
    candidate: str | None = None
    priority: int | None = None

    source: str | None = None
    suite: str | None = None
    component: str | None = None
    architecture: str | None = None

@dataclass
class WhyInfo:
    package: str
    install_type: str
    install_date: str

    required_by: list[str] = field(default_factory=list)
    manual_paths: list[list[str]] = field(default_factory=list)

@dataclass
class PackageInfo:
    name: str
    version: str | None = None
    architecture: str | None = None
    status: str | None = None
    installed_size_kb: int | None = None
    manually_installed: bool | None = None

    dependencies: list[str] = field(default_factory=list)
    reverse_dependencies: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)

    integrity_issues: list[IntegrityIssue] = field(
        default_factory=list
    )
