"""
Grader for the reasoning-reliability benchmark. The oracle is the source of truth;
there is no LLM anywhere in the scoring path.

Usage:
    python run.py tasks/word_wrap results/word_wrap_sonnet
    python run.py tasks/apply_ops results/apply_ops_sonnet

Loads <task_dir>/oracle.py and grades every *.py in <submissions_dir> with its
grade(path) -> (categories, failures). A submission PASSES only if it is correct
on every category (the discriminating cases that a wrong frame fails, plus basic
and edge cases). Prints per-submission rows and a per-arm summary.
"""
import importlib.util, sys, os, glob, collections


def load_oracle(task_dir):
    path = os.path.join(task_dir, "oracle.py")
    spec = importlib.util.spec_from_file_location("oracle_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    task_dir, subs_dir = sys.argv[1], sys.argv[2]
    oracle = load_oracle(task_dir)
    rows = []
    arms = collections.defaultdict(lambda: [0, 0])
    for path in sorted(glob.glob(os.path.join(subs_dir, "*.py"))):
        name = os.path.splitext(os.path.basename(path))[0]
        arm = name.rsplit("_", 1)[0]
        try:
            cats, _ = oracle.grade(path)
        except Exception as e:
            rows.append((name, "IMPORT-ERR", str(e)[:60]))
            continue
        full = all(cats[c][0] == cats[c][1] for c in cats)
        arms[arm][1] += 1
        arms[arm][0] += int(full)
        detail = "  ".join(f"{c}={cats[c][0]}/{cats[c][1]}" for c in cats)
        rows.append((name, "PASS" if full else "FAIL", detail))

    for name, verdict, detail in rows:
        print(f"  {name:<22}{verdict:<6}{detail}")
    print("\nper-arm (PASS = full oracle: all discriminating + basic + edge):")
    for arm in sorted(arms):
        ok, tot = arms[arm]
        print(f"  {arm:<18}{ok}/{tot}")


if __name__ == "__main__":
    main()
