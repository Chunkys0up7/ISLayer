#!/usr/bin/env python3
"""MDA Intent Layer CLI -- Transform BPMN into agent-executable intent specifications."""

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mda",
        description="MDA Intent Layer -- BPMN to Intent Spec transformation pipeline",
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--config", type=Path, help="Path to mda.config.yaml")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Project Management ---
    init_parser = subparsers.add_parser("init", help="Scaffold a new process repository")
    init_parser.add_argument("name", help="Process name (e.g., income-verification)")
    init_parser.add_argument("--domain", help="Process domain")
    init_parser.add_argument("--prefix", help="2-3 letter ID prefix (e.g., IV)")
    init_parser.add_argument("--output-dir", type=Path, help="Output directory")

    config_parser = subparsers.add_parser("config", help="Show or edit configuration")
    config_parser.add_argument(
        "--show", action="store_true", default=True, help="Show current config"
    )
    config_parser.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Set a config value",
    )
    config_parser.add_argument("--get", metavar="KEY", help="Get a config value")
    config_parser.add_argument(
        "--validate", action="store_true", help="Validate config"
    )

    # --- BPMN Ingestion ---
    parse_parser = subparsers.add_parser(
        "parse", help="Parse BPMN XML into typed object model"
    )
    parse_parser.add_argument("bpmn_file", type=Path, help="Path to BPMN 2.0 XML file")
    parse_parser.add_argument("--output", type=Path, help="Output file path")
    parse_parser.add_argument(
        "--format", choices=["yaml", "json"], default="yaml", help="Output format"
    )

    ingest_parser = subparsers.add_parser(
        "ingest", help="Full pipeline: BPMN to triples"
    )
    ingest_parser.add_argument(
        "bpmn_file", type=Path, help="Path to BPMN 2.0 XML file"
    )
    ingest_parser.add_argument(
        "--skip-llm", action="store_true", help="Skip LLM calls, produce template stubs"
    )
    ingest_parser.add_argument(
        "--stages",
        help="Comma-separated stage numbers to run (e.g., 1,2,3)",
    )
    ingest_parser.add_argument(
        "--no-validate", action="store_true", help="Skip validation stage"
    )

    reingest_parser = subparsers.add_parser(
        "reingest", help="Re-ingest updated BPMN with diff"
    )
    reingest_parser.add_argument(
        "bpmn_file", type=Path, help="Path to updated BPMN XML"
    )
    reingest_parser.add_argument(
        "--force", action="store_true", help="Force regeneration without diff"
    )

    # --- Corpus Management ---
    corpus_parser = subparsers.add_parser("corpus", help="Manage knowledge corpus")
    corpus_sub = corpus_parser.add_subparsers(dest="corpus_command")

    corpus_sub.add_parser("index", help="Regenerate corpus.config.yaml")

    corpus_add = corpus_sub.add_parser("add", help="Scaffold a new corpus document")
    corpus_add.add_argument(
        "type",
        choices=[
            "procedure",
            "policy",
            "regulation",
            "rule",
            "data-dictionary",
            "system",
            "training",
            "glossary",
        ],
    )
    corpus_add.add_argument("--domain", help="Document domain")
    corpus_add.add_argument("--title", help="Document title")

    corpus_search = corpus_sub.add_parser("search", help="Search corpus documents")
    corpus_search.add_argument("query", help="Search query")
    corpus_search.add_argument("--type", help="Filter by document type")
    corpus_search.add_argument("--domain", help="Filter by domain")
    corpus_search.add_argument("--tags", help="Filter by tags (comma-separated)")
    corpus_search.add_argument("--limit", type=int, default=10, help="Max results")

    corpus_sub.add_parser("validate", help="Validate all corpus documents")

    # --- Triple Management ---
    validate_parser = subparsers.add_parser("validate", help="Validate triples")
    validate_parser.add_argument("path", nargs="?", type=Path, help="Path to validate")
    validate_parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low"],
        help="Exit non-zero on this severity",
    )

    subparsers.add_parser("status", help="Show triple status summary")

    gaps_parser = subparsers.add_parser("gaps", help="List gaps across triples")
    gaps_parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity",
    )
    gaps_parser.add_argument("--type", help="Filter by gap type")
    gaps_parser.add_argument("--process", help="Filter by process ID")

    graph_parser = subparsers.add_parser("graph", help="Generate process graph")
    graph_parser.add_argument(
        "--format", choices=["yaml", "mermaid", "dot"], default="yaml"
    )
    graph_parser.add_argument("--output", type=Path, help="Output file")

    # --- Verification ---
    test_parser = subparsers.add_parser(
        "test", help="Run verification checks on the current process repository"
    )
    test_parser.add_argument(
        "--quick", action="store_true", help="Run only fast checks (B01-B02, T01, T04, C01-C02)"
    )
    test_parser.add_argument(
        "--bpmn", action="store_true", help="Run only BPMN checks (B01-B08)"
    )
    test_parser.add_argument(
        "--triples", action="store_true", help="Run only triple checks (T01-T11)"
    )
    test_parser.add_argument(
        "--corpus", action="store_true", help="Run only corpus checks (C01-C06)"
    )
    test_parser.add_argument(
        "--report", type=Path, metavar="PATH", help="Write YAML report to file"
    )

    # --- Documentation ---
    docs_parser = subparsers.add_parser("docs", help="Generate and serve process documentation")
    docs_sub = docs_parser.add_subparsers(dest="docs_command")
    docs_sub.add_parser("generate", help="Generate MkDocs config and docs/ overlay")
    docs_sub.add_parser("build", help="Generate + build static site")
    docs_serve = docs_sub.add_parser("serve", help="Generate + serve locally")
    docs_serve.add_argument("--port", type=int, default=8000, help="Port to serve on")

    # --- LLM-Powered ---
    enrich_parser = subparsers.add_parser(
        "enrich", help="Enrich parsed model with corpus"
    )
    enrich_parser.add_argument(
        "model", type=Path, help="Path to parsed model YAML/JSON"
    )
    enrich_parser.add_argument(
        "--corpus-path", type=Path, help="Path to corpus directory"
    )
    enrich_parser.add_argument("--output", type=Path, help="Output file path")

    generate_parser = subparsers.add_parser(
        "generate", help="Generate triple artifacts via LLM"
    )
    generate_parser.add_argument(
        "type", choices=["capsule", "intent", "contract", "all"]
    )
    generate_parser.add_argument(
        "--enriched-model", type=Path, help="Path to enriched model"
    )
    generate_parser.add_argument(
        "--nodes", help="Comma-separated node IDs to generate for"
    )
    generate_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing files"
    )

    review_parser = subparsers.add_parser(
        "review", help="LLM-assisted quality review"
    )
    review_parser.add_argument(
        "triple_path", type=Path, help="Path to triple directory"
    )
    review_parser.add_argument(
        "--aspect",
        choices=["completeness", "accuracy", "consistency", "all"],
        default="all",
    )
    review_parser.add_argument(
        "--output", type=Path, help="Output file for findings"
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load config
    from config.loader import load_config

    config = load_config(getattr(args, "config", None))

    # Dispatch to command handlers
    try:
        if args.command == "init":
            from commands.init_cmd import run_init

            run_init(args, config)
        elif args.command == "config":
            from commands.config_cmd import run_config

            run_config(args, config)
        elif args.command == "parse":
            from commands.parse_cmd import run_parse

            run_parse(args, config)
        elif args.command == "ingest":
            from commands.ingest_cmd import run_ingest

            run_ingest(args, config)
        elif args.command == "reingest":
            from commands.ingest_cmd import run_reingest

            run_reingest(args, config)
        elif args.command == "corpus":
            from commands.corpus_cmd import run_corpus

            run_corpus(args, config)
        elif args.command == "test":
            from commands.test_cmd import run_test

            run_test(args, config)
        elif args.command == "validate":
            from commands.validate_cmd import run_validate

            run_validate(args, config)
        elif args.command == "status":
            from commands.status_cmd import run_status

            run_status(args, config)
        elif args.command == "gaps":
            from commands.gaps_cmd import run_gaps

            run_gaps(args, config)
        elif args.command == "graph":
            from commands.graph_cmd import run_graph

            run_graph(args, config)
        elif args.command == "docs":
            from commands.docs_cmd import run_docs

            run_docs(args, config)
        elif args.command == "enrich":
            from commands.enrich_cmd import run_enrich

            run_enrich(args, config)
        elif args.command == "generate":
            from commands.generate_cmd import run_generate

            run_generate(args, config)
        elif args.command == "review":
            from commands.review_cmd import run_review

            run_review(args, config)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)
    except Exception as e:
        if getattr(args, "json", False):
            from output.json_output import output_json_error

            output_json_error(str(e))
        else:
            from output.console import print_error

            print_error(str(e))
        if getattr(args, "verbose", False):
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
