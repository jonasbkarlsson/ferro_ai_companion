"""Update the manifest file."""
import json
import os
import sys


def update_manifest():
    """Update the manifest file."""
    version = "0.0.0"
    for index, value in enumerate(sys.argv):
        if value in ["--version", "-V"]:
            version = sys.argv[index + 1]

    # pylint: disable=unspecified-encoding
    with open(
        f"{os.getcwd()}/custom_components/ferro_ai_companion/manifest.json"
    ) as manifestfile:
        manifest = json.load(manifestfile)

    manifest["version"] = version

    with open(
        f"{os.getcwd()}/custom_components/ferro_ai_companion/manifest.json", "w"
    ) as manifestfile:
        manifestfile.write(json.dumps(manifest, indent=4, sort_keys=True))


update_manifest()
