# Technical review / 技术事实复核

> Review date: 2026-09-25
> Scope: curated guides and the source notes they synthesize. This is an editorial cross-check, not a claim that every historical command was reproduced in a matching environment.

## Verified or clarified

| Area | Cross-check | Result |
| --- | --- | --- |
| CMake targets and packages | [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html), [cmake-packages](https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html) | `find_package(... CONFIG REQUIRED)`, imported targets, install/export and relocatable interface paths are consistent with the official model. The guide remains illustrative, not a complete project recipe. |
| Dynamic-library diagnosis | [ldd(1)](https://man7.org/linux/man-pages/man1/ldd.1.html) | The warning against running `ldd` on untrusted executables is confirmed. The troubleshooting guide now uses `file`, `readelf` and `objdump` as first-line checks. |
| SQLite transactions | [Transaction Control Syntax](https://www.sqlite.org/lang_transaction.html) | Explicit transactions, savepoints and error/rollback behavior are engine-specific. The database guide now presents pseudocode and avoids presenting one transaction snippet as universal. |
| C++ condition variables | [cppreference: std::condition_variable](https://en.cppreference.com/w/cpp/thread/condition_variable) | Predicate waits, mutex ownership and notification boundaries are described consistently. The guide is not a platform-specific stress-test report. |
| vLLM serving | [vLLM official documentation](https://docs.vllm.ai/en/latest/) | Current capabilities and deployment guidance are moving targets; historical throughput, port and hardware claims remain version-sensitive and are not treated as current guarantees. |
| New API | [official repository](https://github.com/QuantumNous/new-api), [installation docs](https://docs.newapi.ai/en/docs/installation) | New API is a gateway/control plane. The historical built-in-worker mode and `MODEL_PATH`/`WORKERS`/`DB_*` example are explicitly deprecated; the official `calciumion/new-api` image and external inference/channel model are used for the correction. |
| VitePress alpha.20 | [site config reference](https://vitepress.dev/reference/site-config) | `appearance` is a site-level option, the Yarn example now uses the same `@next` prerelease channel, and the alpha.20 image option is named `lazyLoad`. The guide remains version-sensitive. |
| BehaviorTree.CPP | [official documentation](https://www.behaviortree.dev/) | The normal executor's sequential traversal wording is now qualified: `ThreadedAction` executes `tick()` in a separate thread and requires an explicit synchronization/lifecycle contract. |
| LLM capacity arithmetic | arithmetic cross-check of the source page | `1,000,000 × 500 = 500,000,000` tokens/day, approximately `5,800` tokens/s; the old 500B/5.8M figures are marked as an erratum. HPA examples now require a custom GPU/queue metric rather than treating `nvidia.com/gpu` allocation as utilization. |

## Editorial consequences

- AI-assisted and imported sources are marked in `_data/post_editorial.yml` and shown in source notes.
- `reported-tested` means a source declared a test environment; it does not mean an independent reproduction occurred.
- Version-sensitive guides use `review-required` and/or `caution` rather than presenting themselves as universally current.
- The LLM arithmetic discrepancy is documented as an erratum in the historical source and the curated serving checklist rather than silently presenting the old figures as valid.
- The New API, VitePress and BehaviorTree source pages carry visible correction notices or targeted corrections; each changed historical blob is recorded in `_data/format_fixes.yml`.
- The Agent map distinguishes containerized/local orchestration from genuinely air-gapped model access.

## Still requiring human or environment-specific review

- GPU, driver, CUDA, model, image and provider versions in historical deployment notes.
- Performance and capacity numbers that lack attached commands, logs, model digests or test dates.
- Upstream authorship and license details that are not present in the repository or linked source remain explicitly unverified.
- Claim-level citation mapping is now checked for the 15 content-bearing curated guides; future source-list edits must keep numbered anchors and citations synchronized.
