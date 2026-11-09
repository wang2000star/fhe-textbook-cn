#!/usr/bin/env python3
"""Build and measure the optional real OpenFHE Meta-BTS experiment.

Requires a checkout of the pinned public OpenFHE release, CMake, and a C++
compiler. Uses a local installation prefix; no system installation is needed.
This experiment is separate from the quick, deterministic CI algebra checks.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
UPSTREAM = "b59e1f291965f14fbee5172cd83a20f5b856204f"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openfhe-source", type=Path, required=True)
    parser.add_argument("--openfhe-build", type=Path)
    parser.add_argument("--work-dir", type=Path, default=ROOT / "build/openfhe-review")
    parser.add_argument("--output", type=Path, default=ROOT / "build/openfhe-review/results.json")
    parser.add_argument("--cmake", default="cmake")
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--skip-library-build", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.trials < 1:
        parser.error("jobs and trials must be positive")
    source, work = args.openfhe_source.resolve(), args.work_dir.resolve()
    upstream = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if upstream != UPSTREAM:
        parser.error(f"expected OpenFHE v1.6.1 commit {UPSTREAM}, got {upstream}")
    if subprocess.check_output(["git", "-C", str(source), "diff", "--name-only"], text=True).strip():
        parser.error("the upstream tracked source files must be unmodified")
    work.mkdir(parents=True, exist_ok=True)
    library_build = args.openfhe_build.resolve() if args.openfhe_build else work / "library-build"
    prefix = work / "install"
    commands = []

    def run(command, logname):
        commands.append(command)
        with (work / logname).open("w") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)

    if not args.skip_library_build:
        run([args.cmake, "-S", str(source), "-B", str(library_build),
             "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_UNITTESTS=OFF",
             "-DBUILD_BENCHMARKS=OFF", "-DBUILD_EXAMPLES=OFF",
             "-DBUILD_SHARED=ON", "-DBUILD_STATIC=OFF", "-DWITH_OPENMP=ON",
             "-DNATIVE_SIZE=64"], "library-configure.log")
        run([args.cmake, "--build", str(library_build), "--target", "OPENFHEpke",
             "--parallel", str(args.jobs)], "library-build.log")
    run([args.cmake, "--install", str(library_build), "--prefix", str(prefix)], "library-install.log")
    driver = work / "driver-source"
    driver.mkdir(exist_ok=True)
    shutil.copyfile(HERE / "openfhe-CMakeLists.txt", driver / "CMakeLists.txt")
    shutil.copyfile(HERE / "openfhe_meta_bts.cpp", driver / "openfhe_meta_bts.cpp")
    build = work / "driver-build"
    run([args.cmake, "-S", str(driver), "-B", str(build), "-DCMAKE_BUILD_TYPE=Release",
         "-DCMAKE_PREFIX_PATH=" + str(prefix)], "driver-configure.log")
    run([args.cmake, "--build", str(build), "--parallel", str(args.jobs)], "driver-build.log")
    environment = os.environ.copy()
    environment["OMP_NUM_THREADS"] = str(args.jobs)
    executable = build / "fhe-textbook-meta-bts"
    results = []
    for trial in range(1, args.trials + 1):
        process = subprocess.run([str(executable)], capture_output=True, text=True,
                                 env=environment, timeout=600)
        (work / f"trial-{trial}.log").write_text(process.stdout + process.stderr)
        records = [json.loads(line[5:]) for line in process.stdout.splitlines() if line.startswith("DATA ")]
        result = {"trial": trial, "returncode": process.returncode, "records": records}
        results.append(result)
        print(json.dumps({"trial": trial, "returncode": process.returncode,
                          "data_records": len(records)}), flush=True)
        # Preserve failure data, rather than silently omitting failed runs.
        output = {
            "schema_version": 1, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "upstream_repository": "https://github.com/openfheorg/openfhe-development",
            "upstream_tag": "v1.6.1", "upstream_commit": upstream,
            "platform": platform.platform(), "omp_threads": args.jobs,
            "cmake_version": subprocess.check_output([args.cmake, "--version"], text=True).splitlines()[0],
            "requested_trials": args.trials, "completed_trials": len(results),
            "source_sha256": {p.name: sha256(p) for p in
                              [HERE / "openfhe_meta_bts.cpp", HERE / "openfhe-CMakeLists.txt",
                               HERE / "run_openfhe_meta_bts.py"]},
            "upstream_evaluator_sha256": sha256(source / "src/pke/lib/scheme/ckksrns/ckksrns-fhe.cpp"),
            "randomness": "Fixed measurement inputs; fresh default library key/encryption randomness per process. Not bitwise deterministic.",
            "scope": "Real encrypted evaluation via public bootstrap keys. HEStd_NotSet and N=4096 are an experimental configuration, not a security certification.",
            "calibration": "A separate known calibration ciphertext chooses the precision argument with a five-bit empirical buffer; this is not a worst-case parameter proof.",
            "represented_perturbation": "One case encrypts m+2^-10 as a model of pre-existing represented error. It does not claim to sample a particular encryption-noise distribution.",
            "commands": commands, "trials": results,
            "all_completed_trials_pass": all(
                r["returncode"] == 0 and len(r["records"]) == 5 and
                r["records"][-1].get("configured_cases_pass") and
                r["records"][-1].get("rejects_three_iterations") for r in results),
        }
        args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        if not output["all_completed_trials_pass"]:
            raise SystemExit("Experiment failed; recorded data and logs retained.")


if __name__ == "__main__":
    main()
