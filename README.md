# SpikeForest

> :warning: This project is under construction.

Spike sorting benchmarking system. See our [eLife paper](https://elifesciences.org/articles/55167).

This Python project allows you to download a subset of the [SpikeForest](http://spikeforest.flatironinstitute.org/) recordings, the associated ground truth sortings, and the outputs of the spike sorting runs, and load these into SpikeInterface recording and sorting extractors.

> Note: only a subset of the SpikeForest recordings are available at this time.

All data are pinned to [IPFS](https://ipfs.io/) and available on the [kachery-cloud](https://github.com/scratchrealm/kachery-cloud) network.

# Setup

It is recommended that you use a conda environment with Python >= 3.8 and numpy

Clone this repository and install via pip

```bash
git clone <repo>
cd spikeforest
pip install -e .
```

Configure your kachery-cloud client

```bash
kachery-cloud-init
# follow the instructions to associate your client with your Google user name on kachery-cloud
```

# Getting started

* List all recordings with ground truth: [examples/list_all_recordings.py](examples/list_all_recordings.py)
* Load a recording and sorting extractors for a recording with ground truth: [examples/load_extractors_for_recording.py](examples/load_extractors_for_recording.py)
* List all sorting outputs: [examples/list_all_sorting_outputs.py](examples/list_all_sorting_outputs.py)
* Load sorting extractor for a sorting output: [examples/load_extractor_for_sorting_output.py](examples/load_extractor_for_sorting_output.py)
* Running spike sorting: [examples/test_mountainsort4.py](examples/test_mountainsort4.py)

## Frequently asked questions

### How can I download the SpikeForest recordings and ground truth sorting data?

See example above.

### How can I download the SpikeForest sorting outputs?

See example above.

### How can I run spike sorting on the SpikeForest recordings?

Use [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html). See example above.

See also [this example notebook](https://spikeinterface.readthedocs.io/en/latest/modules/sorters/plot_1_sorters_example.html#sphx-glr-modules-sorters-plot-1-sorters-example-py).

## Questions to be answered later

### How can I visualize a SpikeForest sorting using sortingview?

### How can I run containerized spike sorting on my own computer?