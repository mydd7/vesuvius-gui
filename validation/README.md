CT validation for the prepared reader, cache, GUI and renderer fixes.

CT panels use measured output images and nearest-neighbor enlargement. PNG metadata is empty. JSON files record the real inputs, hashes and platform limits. Each source fix remains a separate pull request.

Source reproduction

Apply combined-validation.patch to a fresh checkout of commit bf08725f038399ff7ecba3bcfa85dd64b749875e. It reconstructs exactly source tree 519920b25df2796081514152e7495b6ccb3f3c19, used for combined commit 9bfc896e7eda42ff643d884dfdd648ef04233af6. The patch is a reproduction aid and is separate from every individual source PR.

Run Cargo from the workspace root so .cargo/config.toml is loaded. The main MSVC validation covers 20 reader/codec tests, 23 renderer tests, five model tests, 91 cache tests and three GUI argument tests. Three cache tests are ignored. Cache tests must run in separate processes on Windows because retained shard mappings exhaust commit in one process.

The supplied runner builds and isolates those cache tests:

    python verify-cache.py CHECKOUT

It creates a fresh temporary session for test files and removes that session after all child processes exit. It was executed successfully: 91 passed and three ignored. --target can select an installed native Rust target with its compiler and runtime on PATH.

The other selections use cargo test with these package/target filters:

    -p vesuvius-zarr -p vesuvius-c3d --lib --tests
    -p vesuvius-render --bin vesuvius-render
    -p vesuvius-rs --lib model::
    -p vesuvius-gui --bin vesuvius-gui

The additional GNU validation excludes GUI arguments and adds 11 overlay tests. Four TIFXYZ tests have a separate run with a local fixture-path override; its exact scope is recorded in surface-fixture-validation.json. The author-specific external Zarr experiment is not part of these selections.

Windows MSVC and Windows GNU/GCC16.1 were tested. Linux and macOS were not run. GUI display confirmation remains manual. CLI CT checks and their input URLs and hashes are recorded in the individual JSON files.
