from invoke import task
import os
import shutil
import re
from datetime import datetime

PLUGINS = {
    "plugin.video.annatel.tv": {
        "dir": "plugin.video.annatel.tv",
        "repo_dir": "repo/plugin.video.annatel.tv",
        "version_file": "plugin.video.annatel.tv/version.txt"
    },
    "plugin.video.annatel.tvvod": {
        "dir": "plugin.video.annatel.tvvod",
        "repo_dir": "repo/plugin.video.annatel.tvvod",
        "version_file": "plugin.video.annatel.tvvod/version.txt"
    }
}

REPOSITORY = {
    "dir": "repository.reouvenannatel",
    "repo_dir": "repo/repository.reouvenannatel",
    "version_file": "repository.reouvenannatel/version.txt"
}

@task
def create_version_file(ctx, version_file, initial_version="1.0.0"):
    """Create version file if it doesn't exist"""
    if not os.path.exists(version_file):
        os.makedirs(os.path.dirname(version_file), exist_ok=True)
        with open(version_file, "w") as f:
            f.write(initial_version)
        print(f"Created {version_file} with initial version {initial_version}")

@task
def get_current_version(ctx, version_file):
    """Get the current version from version.txt"""
    create_version_file(ctx, version_file)
    with open(version_file, "r") as f:
        return f.read().strip()

@task
def bump_version(ctx, version_file, part="patch"):
    """Bump the version number (major, minor, or patch)"""
    current = get_current_version(ctx, version_file)
    major, minor, patch = map(int, current.split("."))
    
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    with open(version_file, "w") as f:
        f.write(new_version)
    print(f"Bumped version from {current} to {new_version}")
    return new_version

@task
def build_plugin(ctx, plugin_name, version=None):
    """Build a specific plugin and create a zip in its repo directory"""
    plugin_info = PLUGINS[plugin_name]
    if version is None:
        version = get_current_version(ctx, plugin_info["version_file"])
    
    # Ensure repo directory exists
    os.makedirs(plugin_info["repo_dir"], exist_ok=True)
    
    # Create zip filename
    zip_name = f"{plugin_name}-{version}.zip"
    zip_path = os.path.join(plugin_info["repo_dir"], zip_name)
    
    # Create the zip archive
    base_name = os.path.join(plugin_info["repo_dir"], f"{plugin_name}-{version}")
    shutil.make_archive(
        base_name,
        "zip",
        plugin_info["dir"],
        lambda x: not any(
            pattern in x for pattern in [
                "__pycache__",
                ".DS_Store",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".Python",
                "env",
                "venv",
                ".env",
                ".venv",
                "pip-log.txt",
                "pip-delete-this-directory.txt",
                ".tox",
                ".coverage",
                ".coverage.*",
                ".cache",
                "nosetests.xml",
                "coverage.xml",
                "*.cover",
                "*.log",
                ".pytest_cache",
                ".env",
                ".venv",
                "env/",
                "venv/",
                "ENV/",
                "env.bak/",
                "venv.bak/",
                "dist/",
                "build/",
                "*.egg-info/",
                ".installed.cfg",
                "*.egg",
            ]
        )
    )
    print(f"Created plugin zip: {zip_path}")
    return zip_name

@task
def build_repository(ctx, version=None):
    """Build the repository and create a zip"""
    if version is None:
        version = get_current_version(ctx, REPOSITORY["version_file"])
    
    # Ensure repo directory exists
    os.makedirs(REPOSITORY["repo_dir"], exist_ok=True)
    
    # Create zip filename
    zip_name = f"{REPOSITORY['dir']}-{version}.zip"
    zip_path = os.path.join(REPOSITORY["repo_dir"], zip_name)
    
    # Create the zip archive
    shutil.make_archive(
        os.path.join(REPOSITORY["repo_dir"], f"{REPOSITORY['dir']}-{version}"),
        "zip",
        REPOSITORY["dir"],
        lambda x: not any(
            pattern in x for pattern in [
                "__pycache__",
                ".DS_Store",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".Python",
                "env",
                "venv",
                ".env",
                ".venv",
                "pip-log.txt",
                "pip-delete-this-directory.txt",
                ".tox",
                ".coverage",
                ".coverage.*",
                ".cache",
                "nosetests.xml",
                "coverage.xml",
                "*.cover",
                "*.log",
                ".pytest_cache",
                ".env",
                ".venv",
                "env/",
                "venv/",
                "ENV/",
                "env.bak/",
                "venv.bak/",
                "dist/",
                "build/",
                "*.egg-info/",
                ".installed.cfg",
                "*.egg",
            ]
        )
    )
    print(f"Created repository zip: {zip_path}")
    return zip_name

@task
def release_plugin(ctx, plugin_name, part="patch"):
    """Create a new release for a specific plugin"""
    plugin_info = PLUGINS[plugin_name]
    new_version = bump_version(ctx, plugin_info["version_file"], part)
    zip_name = build_plugin(ctx, plugin_name, new_version)
    print(f"Created release {new_version} for {plugin_name} with archive {zip_name}")

@task
def release_repository(ctx, part="patch"):
    """Create a new release for the repository"""
    new_version = bump_version(ctx, REPOSITORY["version_file"], part)
    zip_name = build_repository(ctx, new_version)
    print(f"Created repository release {new_version} with archive {zip_name}")

@task
def release_all(ctx, part="patch"):
    """Create new releases for all plugins and repository"""
    for plugin_name in PLUGINS:
        release_plugin(ctx, plugin_name, part)
    release_repository(ctx, part)

@task
def clean(ctx):
    """Clean up build artifacts"""
    # Clean plugin zips
    for plugin_info in PLUGINS.values():
        if os.path.exists(plugin_info["repo_dir"]):
            for file in os.listdir(plugin_info["repo_dir"]):
                if file.endswith(".zip"):
                    os.remove(os.path.join(plugin_info["repo_dir"], file))
    
    # Clean repository zips
    if os.path.exists(REPOSITORY["repo_dir"]):
        for file in os.listdir(REPOSITORY["repo_dir"]):
            if file.endswith(".zip"):
                os.remove(os.path.join(REPOSITORY["repo_dir"], file))
    
    print("Cleaned all zip files") 