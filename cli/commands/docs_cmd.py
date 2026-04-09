"""mda docs build|serve|generate — Generate and serve MkDocs documentation."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_docs(args, config):
    cmd = args.docs_command
    if cmd == "generate":
        _docs_generate(args, config)
    elif cmd == "build":
        _docs_generate(args, config)
        _docs_build(args, config)
    elif cmd == "serve":
        _docs_generate(args, config)
        _docs_serve(args, config)
    else:
        from output.console import print_error
        print_error("Usage: mda docs {generate|build|serve}")

def _docs_generate(args, config):
    from pipeline.docs_generator import generate_docs
    from output.console import print_header, print_success
    from pathlib import Path

    project_root = config.project_root

    # Find engine root
    schemas_val = config.get("pipeline.schemas")
    if isinstance(schemas_val, str):
        engine_root = (project_root / schemas_val).resolve().parent
    elif isinstance(schemas_val, dict):
        first_schema = next(iter(schemas_val.values()), "../../schemas/capsule.schema.json")
        engine_root = (project_root / first_schema).resolve().parent.parent
    else:
        engine_root = project_root.parent.parent

    mkdocs_path = generate_docs(project_root, config, engine_root)
    print_success(f"Generated MkDocs config at {mkdocs_path}")
    print_success(f"Generated docs/ overlay at {project_root / 'docs'}")

def _docs_build(args, config):
    import subprocess
    from output.console import print_info, print_success, print_error

    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build"],
        cwd=str(config.project_root),
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print_success(f"Site built at {config.project_root / 'site'}")
    else:
        print_error(f"MkDocs build failed: {result.stderr}")

def _docs_serve(args, config):
    import subprocess
    from output.console import print_info

    port = getattr(args, 'port', 8000) or 8000
    print_info(f"Serving at http://localhost:{port} (Ctrl+C to stop)")

    try:
        subprocess.run(
            [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", f"localhost:{port}"],
            cwd=str(config.project_root),
        )
    except KeyboardInterrupt:
        pass
