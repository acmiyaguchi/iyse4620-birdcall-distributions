"""Walk through the data directory to create a list of all paths.

This makes it possible for the client application to find all the images and
data.
"""
import json
from argparse import ArgumentParser
from pathlib import Path


def parse_args():
    """Parse the location of the root directory and the manifest output path."""
    parser = ArgumentParser()
    parser.add_argument("root", type=str, help="Path to the root directory")
    parser.add_argument("output", type=str, help="Path to the output manifest")
    return parser.parse_args()


def main():
    """Walk through the root directory and generate a manifest of all files."""
    args = parse_args()
    root = Path(args.root)
    output = Path(args.output)
    manifest = []
    for path in root.glob("**/*"):
        # find a directory that contains a trace and ppc json file.
        if path.is_file() or not (
            len(list(path.glob("trace*.json"))) > 0
            and len(list(path.glob("ppc*.json"))) > 0
        ):
            continue

        # based on the data in the ppc file, figure out what metadata to
        # associate with the current path
        ppc_path = list(path.glob("ppc*.json"))[0]
        data = json.loads(ppc_path.read_text())
        row = data[0]
        label = row["primary_label"]
        item = {
            "path": path.relative_to(root).as_posix(),
            "images": {
                "observed_linear": f"observed_{label}.png",
                "observed_log": f"observed_{label}_log.png",
                "ppc_linear": f"ppc_{label}_linear.png",
                "ppc_log": f"ppc_{label}_log.png",
            },
            "traces": {
                "trace": f"trace_{label}.json",
                "ppc": f"ppc_{label}.json",
            },
            "primary_label": row["primary_label"],
            "region": row["region"],
            "grid_size": row["grid_size"],
            "model": path.parts[-4],
        }
        manifest.append(item)

    Path(output).write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
