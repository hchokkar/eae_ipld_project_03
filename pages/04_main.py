# main.py
import argparse
import yaml
import os
from checks.policy_checks import run_all_checks
from checks.policy_checks_cis import check_mapping
from utils.report import save_report_json, print_summary

def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="ISO/CIS Policy Alignment Checker")
    parser.add_argument("--policy-text", default="examples/policy_access_control.txt", help="Path to policy text file")
    parser.add_argument("--policy-meta", default="examples/policy_metadata.yaml", help="Path to policy metadata yaml")
    parser.add_argument("--mappings", default="mappings_cis.yaml", help="Mappings YAML")
    parser.add_argument("--output", default="report.json", help="Report output JSON path")
    args = parser.parse_args()

    if not os.path.exists(args.policy_text):
        raise FileNotFoundError(args.policy_text)
    if not os.path.exists(args.policy_meta):
        raise FileNotFoundError(args.policy_meta)
    if not os.path.exists(args.mappings):
        raise FileNotFoundError(args.mappings)

    policy_text = load_text_file(args.policy_text)
    metadata = load_yaml(args.policy_meta)
    mappings = load_yaml(args.mappings)

    # run general policy checks (metadata + clause heuristics)
    basic_results = run_all_checks(policy_text, metadata)

    # run CIS mapping-based checks
    cis_results = {}
    for key, mapping in mappings.get("mappings", {}).items():
        cis_results[key] = check_mapping(policy_text, mapping)

    # merge results for report
    combined = {**cis_results}
    # optionally include basic results under different keys
    for k, v in basic_results.items():
        combined[f"basic_{k}"] = {"ok": v.get("ok"), "score": 1 if v.get("ok") else 0, "evidence": [v.get("evidence")]}

    save_report_json(combined, metadata, mappings, args.output)
    print_summary(combined, mappings)
    print("Report saved to", args.output)

if __name__ == "__main__":
    main()
