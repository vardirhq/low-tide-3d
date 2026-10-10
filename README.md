# Low Tide 3D

A separate 3D crawler experiment for Sindri. The isometric POC now renders the
committed Astra cutaway GLB as an external model asset in native and WebGPU
Sindri runtimes.

See [the proof, limitations and reproduction commands](docs/POC.md). Requires
[engine PR #504](https://github.com/vardirhq/sindri-engine/pull/504).

![Crawler in Sindri](docs/proof/crawler-browser.png)

## 3D assets

The [Last Signal salvage pack](assets/salvage/README.md) adds 14 reusable GLB
models: radio and tide equipment, recoverable machinery, storage and modular
wreck pieces. It includes editable source, sockets, collision proposals, a
combined diorama and a separate `salvage-catalog.scene` for inspection.

![Last Signal asset study](assets/salvage/preview_diorama.png)
