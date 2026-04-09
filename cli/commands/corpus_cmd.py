"""mda corpus index|add|search|validate -- Manage knowledge corpus."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_corpus(args, config):
    """Dispatch to the appropriate corpus subcommand."""
    cmd = args.corpus_command
    if cmd == "index":
        _corpus_index(args, config)
    elif cmd == "add":
        _corpus_add(args, config)
    elif cmd == "search":
        _corpus_search(args, config)
    elif cmd == "validate":
        _corpus_validate(args, config)
    else:
        from output.console import print_error

        print_error("Usage: mda corpus {index|add|search|validate}")


def _corpus_index(args, config):
    """Regenerate corpus.config.yaml from .corpus.md files."""
    from datetime import datetime
    from mda_io.frontmatter import read_frontmatter_file
    from mda_io.yaml_io import write_yaml
    from output.console import print_success, print_error, get_progress
    from output.json_output import output_json

    corpus_dir = config.corpus_dir
    if not corpus_dir.exists():
        print_error(f"Corpus directory not found: {corpus_dir}")
        return

    # Scan all .corpus.md files
    corpus_files = sorted(corpus_dir.rglob("*.corpus.md"))

    documents = []
    with get_progress() as progress:
        task = progress.add_task("Indexing corpus...", total=len(corpus_files))
        for f in corpus_files:
            fm, _ = read_frontmatter_file(f)
            rel_path = str(f.relative_to(corpus_dir)).replace("\\", "/")
            entry = {
                "corpus_id": fm.get("corpus_id", ""),
                "title": fm.get("title", ""),
                "doc_type": fm.get("doc_type", ""),
                "domain": fm.get("domain", ""),
                "subdomain": fm.get("subdomain"),
                "path": rel_path,
                "tags": fm.get("tags", []),
                "applies_to": fm.get("applies_to", {}),
                "status": fm.get("status", "draft"),
            }
            documents.append(entry)
            progress.update(task, advance=1)

    # Write index
    index = {
        "version": "1.0",
        "generated_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "document_count": len(documents),
        "documents": documents,
    }
    index_path = corpus_dir / "corpus.config.yaml"
    write_yaml(index_path, index)

    if getattr(args, "json", False):
        output_json({"indexed": len(documents), "path": str(index_path)})
    else:
        print_success(f"Indexed {len(documents)} corpus documents -> {index_path}")


def _corpus_add(args, config):
    """Scaffold a new corpus document."""
    from datetime import datetime
    from mda_io.frontmatter import write_frontmatter_file
    from mda_io.yaml_io import read_yaml
    from output.console import print_success

    corpus_dir = config.corpus_dir

    # Map doc_type to subdirectory
    type_to_dir = {
        "procedure": "procedures",
        "policy": "policies",
        "regulation": "regulations",
        "rule": "rules",
        "data-dictionary": "data-dictionary",
        "system": "systems",
        "training": "training",
        "glossary": "glossary",
    }

    # Map doc_type to ID prefix
    type_to_prefix = {
        "procedure": "PRC",
        "policy": "POL",
        "regulation": "REG",
        "rule": "RUL",
        "data-dictionary": "DAT",
        "system": "SYS",
        "training": "TRN",
        "glossary": "GLO",
    }

    subdir = type_to_dir.get(args.type, args.type)
    prefix = type_to_prefix.get(args.type, "UNK")

    # Generate next sequence number
    target_dir = corpus_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = list(target_dir.glob("*.corpus.md"))
    seq = str(len(existing) + 1).zfill(3)

    domain_code = (args.domain or "GEN")[:3].upper()
    corpus_id = f"CRP-{prefix}-{domain_code}-{seq}"
    title = args.title or f"New {args.type.replace('-', ' ').title()}"
    slug = title.lower().replace(" ", "-").replace("(", "").replace(")", "")

    frontmatter = {
        "corpus_id": corpus_id,
        "title": title,
        "slug": slug,
        "doc_type": args.type,
        "domain": args.domain or "Unspecified",
        "subdomain": "",
        "tags": [],
        "applies_to": {
            "process_ids": [],
            "task_types": [],
            "task_name_patterns": [],
            "goal_types": [],
            "roles": [],
        },
        "version": "1.0",
        "status": "draft",
        "effective_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "review_date": "",
        "supersedes": None,
        "superseded_by": None,
        "author": "",
        "last_modified": datetime.utcnow().strftime("%Y-%m-%d"),
        "last_modified_by": "",
        "source": "internal",
        "source_ref": None,
        "related_corpus_ids": [],
        "regulation_refs": [],
        "policy_refs": [],
    }

    # Load expected body sections from taxonomy
    body = f"# {title}\n\n<!-- Fill in the content sections below -->\n"
    taxonomy_path = config.ontology_dir / "corpus-taxonomy.yaml"
    if taxonomy_path.exists():
        taxonomy = read_yaml(taxonomy_path)
        doc_types = taxonomy.get("doc_types", [])
        for dt in doc_types:
            if dt.get("id") == args.type:
                for section in dt.get("expected_body_sections", []):
                    body += f"\n## {section}\n\n<!-- TODO: Add content -->\n"
                break

    output_path = target_dir / f"{slug}.corpus.md"
    write_frontmatter_file(output_path, frontmatter, body)
    print_success(f"Created {output_path}")


def _corpus_search(args, config):
    """Search corpus index by keyword."""
    from mda_io.yaml_io import read_yaml
    from output.console import print_header, print_table, print_info, print_error
    from output.json_output import output_json

    index_path = config.corpus_dir / "corpus.config.yaml"
    if not index_path.exists():
        print_error("Corpus index not found. Run 'mda corpus index' first.")
        return

    index = read_yaml(index_path)
    documents = index.get("documents", [])

    query_lower = args.query.lower()
    results = []
    for doc in documents:
        score = 0
        # Score by title match
        if query_lower in doc.get("title", "").lower():
            score += 2
        # Score by tag match
        for tag in doc.get("tags", []):
            if query_lower in tag.lower():
                score += 1
        # Score by domain/subdomain
        if query_lower in doc.get("domain", "").lower():
            score += 0.5
        if query_lower in (doc.get("subdomain") or "").lower():
            score += 0.5

        # Apply filters
        if args.type and doc.get("doc_type") != args.type:
            continue
        if args.domain and args.domain.lower() not in doc.get("domain", "").lower():
            continue
        if args.tags:
            filter_tags = set(t.strip() for t in args.tags.split(","))
            doc_tags = set(doc.get("tags", []))
            if not filter_tags.intersection(doc_tags):
                continue

        if score > 0:
            results.append((score, doc))

    results.sort(key=lambda x: x[0], reverse=True)
    results = results[: args.limit]

    if getattr(args, "json", False):
        output_json([doc for _, doc in results])
    else:
        print_header(f"Search: '{args.query}' ({len(results)} results)")
        if results:
            rows = []
            for _score, doc in results:
                rows.append([
                    doc["corpus_id"],
                    doc["doc_type"],
                    doc["title"],
                    str(doc.get("status", "")),
                ])
            print_table("Results", ["ID", "Type", "Title", "Status"], rows)
        else:
            print_info("No matching documents found.")


def _corpus_validate(args, config):
    """Validate all corpus documents against schema."""
    from mda_io.frontmatter import read_frontmatter_file
    from mda_io.schema_validator import SchemaValidator
    from output.console import (
        print_header,
        print_success,
        print_error,
        print_warning,
        get_progress,
    )
    from output.json_output import output_json

    corpus_dir = config.corpus_dir
    schemas_dir = config.schemas_dir

    if not schemas_dir.exists():
        print_error(f"Schemas directory not found: {schemas_dir}")
        return

    validator = SchemaValidator(schemas_dir)
    corpus_files = sorted(corpus_dir.rglob("*.corpus.md"))

    all_errors = {}
    with get_progress() as progress:
        task = progress.add_task("Validating...", total=len(corpus_files))
        for f in corpus_files:
            fm, _ = read_frontmatter_file(f)
            errors = validator.validate_corpus_document(fm)
            if errors:
                rel = str(f.relative_to(corpus_dir))
                all_errors[rel] = [
                    {"path": e.path, "message": e.message} for e in errors
                ]
            progress.update(task, advance=1)

    if getattr(args, "json", False):
        output_json({"files": len(corpus_files), "errors": all_errors})
    else:
        print_header(f"Corpus Validation ({len(corpus_files)} files)")
        if all_errors:
            for file, errors in all_errors.items():
                print_error(f"{file}:")
                for e in errors:
                    print_warning(f"  {e['path']}: {e['message']}")
        else:
            print_success(
                f"All {len(corpus_files)} corpus documents pass schema validation"
            )
