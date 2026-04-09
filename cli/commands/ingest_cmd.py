"""mda ingest <bpmn-file> -- Full pipeline: BPMN to triples.
   mda reingest <bpmn-file> -- Re-ingest updated BPMN with diff."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_ingest(args, config):
    """Run the full ingest pipeline: BPMN -> parse -> enrich -> capsules -> intents -> contracts -> validate."""
    from pipeline.orchestrator import run_ingest as pipeline_ingest
    from output.console import print_header, print_success, print_info, print_warning, print_table
    from output.json_output import output_json

    bpmn_path = args.bpmn_file
    if not bpmn_path.exists():
        raise FileNotFoundError(f"BPMN file not found: {bpmn_path}")

    skip_llm = getattr(args, "skip_llm", False)
    no_validate = getattr(args, "no_validate", False)

    # Parse stages argument
    stages = None
    if hasattr(args, "stages") and args.stages:
        stages = [int(s.strip()) for s in args.stages.split(",")]

    # Get LLM provider if needed
    llm_provider = None
    if not skip_llm:
        try:
            from llm.provider import get_provider
            llm_provider = get_provider(config)
        except Exception as e:
            if not skip_llm:
                from output.console import print_warning
                print_warning(f"LLM provider unavailable ({e}), using template stubs")
            skip_llm = True

    # Run the pipeline
    results = pipeline_ingest(
        bpmn_path=bpmn_path,
        config=config,
        llm_provider=llm_provider,
        skip_llm=skip_llm,
        stages=stages,
        no_validate=no_validate,
    )

    if getattr(args, "json", False):
        # Convert Path objects to strings for JSON serialization
        json_results = dict(results)
        json_results["files_created"] = [str(f) for f in results.get("files_created", [])]
        output_json(json_results)
        return

    # Display results
    print_header(f"Ingest: {bpmn_path.name}")

    # Stage 1 summary
    if 1 in results.get("stages", {}):
        s1 = results["stages"][1]
        print_info(f"\n  Stage 1 (Parse): {s1.get('total_nodes', 0)} nodes, {s1.get('edges', 0)} edges")

    # Stage 2 summary
    if 2 in results.get("stages", {}):
        s2 = results["stages"][2]
        print_info(f"  Stage 2 (Enrich): {s2.get('total', 0)} gaps found")

    # Stage 3 summary
    if 3 in results.get("stages", {}):
        s3 = results["stages"][3]
        print_info(f"  Stage 3 (Capsules): {s3.get('capsules_created', 0)} created")

    # Stage 4 summary
    if 4 in results.get("stages", {}):
        s4 = results["stages"][4]
        print_info(f"  Stage 4 (Intents): {s4.get('intents_created', 0)} created")

    # Stage 5 summary
    if 5 in results.get("stages", {}):
        s5 = results["stages"][5]
        print_info(f"  Stage 5 (Contracts): {s5.get('contracts_created', 0)} created")

    # Stage 6 summary
    if 6 in results.get("stages", {}):
        s6 = results["stages"][6]
        passed = s6.get("passed", 0)
        failed = s6.get("failed", 0)
        total = s6.get("triple_count", 0)
        result_str = s6.get("overall_result", "unknown")
        print_info(f"  Stage 6 (Validate): {passed}/{total} passed, {failed} failed [{result_str}]")

    # Files created
    files = results.get("files_created", [])
    if files:
        print_info(f"\n  Total files created: {len(files)}")

    # Gap warning
    gaps = results.get("gaps", 0)
    if gaps > 0:
        print_warning(f"\n  {gaps} gaps detected -- run 'mda gaps' for details")

    if not results.get("stages"):
        print_warning("No stages were executed")

    # LLM mode indicator
    if skip_llm:
        print_info("\n  Mode: template stubs (--skip-llm)")
    else:
        print_info("\n  Mode: LLM-assisted generation")

    print_success("Ingest complete")


def run_reingest(args, config):
    """Re-ingest an updated BPMN file, comparing with existing triples."""
    from pipeline.stage1_parser import run_parser, get_parse_summary
    from output.console import print_header, print_success, print_info, print_warning, print_table
    from output.json_output import output_json

    bpmn_path = args.bpmn_file
    if not bpmn_path.exists():
        raise FileNotFoundError(f"BPMN file not found: {bpmn_path}")

    force = getattr(args, "force", False)

    # Parse the new model
    new_model = run_parser(bpmn_path, config.ontology_dir)
    new_summary = get_parse_summary(new_model)

    triples_dir = config.resolve_path("paths.triples")
    decisions_dir = config.resolve_path("paths.decisions")

    if getattr(args, "json", False):
        output_json({"new_model": new_summary, "mode": "force" if force else "diff"})
        return

    print_header(f"Reingest: {bpmn_path.name}")
    print_info(f"  New model: {new_summary['total_nodes']} nodes, {new_summary['edges']} edges")

    if force:
        print_warning("  --force: regenerating all triples")
        # Run full ingest with the new model
        from pipeline.orchestrator import run_ingest as pipeline_ingest

        llm_provider = None
        try:
            from llm.provider import get_provider
            llm_provider = get_provider(config)
        except Exception:
            pass

        results = pipeline_ingest(
            bpmn_path=bpmn_path,
            config=config,
            llm_provider=llm_provider,
            skip_llm=(llm_provider is None),
        )

        files = results.get("files_created", [])
        print_info(f"  Files created: {len(files)}")
        print_success("Reingest complete (forced)")
    else:
        # Diff mode: compare existing triples with new model
        existing_task_ids = set()
        for base_dir in [triples_dir, decisions_dir]:
            if base_dir.exists():
                for d in base_dir.iterdir():
                    if d.is_dir():
                        for cap in d.glob("*.cap.md"):
                            from mda_io.frontmatter import read_frontmatter_file
                            fm, _ = read_frontmatter_file(cap)
                            task_id = fm.get("bpmn_task_id")
                            if task_id:
                                existing_task_ids.add(task_id)

        new_task_ids = {n.id for n in new_model.nodes}
        added = new_task_ids - existing_task_ids
        removed = existing_task_ids - new_task_ids
        unchanged = new_task_ids & existing_task_ids

        rows = []
        if added:
            for tid in sorted(added):
                node = new_model.get_node(tid)
                rows.append([tid, node.name or "-", "ADDED"])
        if removed:
            for tid in sorted(removed):
                rows.append([tid, "-", "REMOVED"])
        if unchanged:
            for tid in sorted(unchanged):
                node = new_model.get_node(tid)
                rows.append([tid, node.name or "-", "unchanged"])

        if rows:
            print_table("Diff", ["Task ID", "Name", "Status"], rows)

        print_info(f"\n  Added: {len(added)}, Removed: {len(removed)}, Unchanged: {len(unchanged)}")

        if added:
            print_info("  Run 'mda ingest' with --stages=1,2,3,4,5 to generate triples for new tasks")
        if removed:
            print_warning("  Removed tasks still have triples on disk -- review and delete manually")

        print_success("Reingest diff complete")
