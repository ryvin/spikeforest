from argparse import ArgumentParser
from typing import Any, Dict, List, Tuple, NamedTuple

import hither2 as hi
import sortingview as sv

from spikeforest._common.calling_framework import GROUND_TRUTH_URI_KEY, StandardArgs, add_standard_args, call_cleanup, parse_shared_configuration
from spikeforest.sorting_utilities.run_sortings import SortingMatrixEntry, init_sorting_args, parse_argsdict, load_study_records, parse_sorters, extract_hither_config, populate_sorting_matrix, sorting_loop, SortingJob, SortingMatrixDict
from spikeforest.sorting_utilities.prepare_workspace import FullRecordingEntry, add_entry_to_workspace, add_workspace_selection_args, establish_workspace, get_known_recording_id, get_labels, TRUE_SORT_LABEL, sortings_are_in_workspace

class Params(NamedTuple):
    study_source_file: str
    sorter_spec_file:  str
    workspace_uri:     str

class HydratedObjects(NamedTuple):
    workspace: sv.Workspace
    recording: sv.LabboxEphysRecordingExtractor
    gt_sort:   sv.LabboxEphysSortingExtractor
    sorting:   sv.LabboxEphysSortingExtractor

def init_configuration() -> Tuple[Params, StandardArgs]:
    description = "Runs all known sorters against configured SpikeForest recordings, and loads the " + \
        "results into a (new or existing) workspace for display."
    parser = ArgumentParser(description=description)
    parser = add_workspace_selection_args(parser)
    parser = init_sorting_args(parser)
    parser = add_standard_args(parser)
    parsed = parser.parse_args()
    sortings_args = parse_argsdict(parsed)
    std_args = parse_shared_configuration(parsed)
    workspace_uri = establish_workspace(parsed)
    params = Params(
        study_source_file = sortings_args["study_source_file"],
        sorter_spec_file  = sortings_args["sorter_spec_file"],
        workspace_uri     = workspace_uri
    )
    print(f"Using workspace uri {params.workspace_uri}")
    return (params, std_args)

def remove_preexisting_records(matrix: SortingMatrixDict, w_uri: str) -> SortingMatrixDict:
    workspace = sv.load_workspace(w_uri)
    new_matrix: SortingMatrixDict = {}
    for sorter_name in matrix.keys():
        (sorter, recording_list) = matrix[sorter_name]
        for recording in recording_list:
            (_, gt_label, s_label) = get_labels(recording.study_name, recording.recording_name, TRUE_SORT_LABEL, sorter_name)
            (_, sorting_exists) = sortings_are_in_workspace(workspace, gt_label, s_label)
            if (sorting_exists): continue
            if sorter_name not in new_matrix:
                new_matrix[sorter_name] = SortingMatrixEntry(sorter_record=sorter, requested_recordings=[])
            new_matrix[sorter_name].requested_recordings.append(recording)
    return new_matrix

def populate_extractors(workspace_uri: str, rec_uri: str, gt_uri: str, sorting_result: Any) -> HydratedObjects:
    workspace = sv.load_workspace(workspace_uri)
    recording = sv.LabboxEphysRecordingExtractor(rec_uri, download=True)
    sample_rate = recording.get_sampling_frequency()
    gt_sort = sv.LabboxEphysSortingExtractor(gt_uri, samplerate=sample_rate)
    sorting = sv.LabboxEphysSortingExtractor(sorting_result, samplerate=sample_rate)
    return HydratedObjects(
        workspace = workspace,
        recording = recording,
        gt_sort   = gt_sort,
        sorting   = sorting
    )

@hi.function(
    'hi_post_result_to_workspace', '0.1.0',
    modules=['sortingview', 'spikeforest'],
    kachery_support=True
)
def hi_post_result_to_workspace(
    sorting_entry: SortingJob,
    workspace_uri: str
) -> None:
    # Python does not round-trip namedtuples effectively :(
    entry = SortingJob(
        recording_name=sorting_entry[0],
        recording_uri=sorting_entry[1],
        ground_truth_uri=sorting_entry[2],
        study_name=sorting_entry[3],
        sorter_name=sorting_entry[4],
        params=sorting_entry[5],
        sorting_job=sorting_entry[6]
    )
    items = populate_extractors(workspace_uri,
                                entry.recording_uri,
                                entry.ground_truth_uri,
                                # within a hither Job, other Jobs are replaced with Job.result.return_value
                                entry.sorting_job)
    (r_label, gt_label, s_label) = get_labels(entry.study_name,
                                              entry.recording_name,
                                              TRUE_SORT_LABEL,
                                              entry.sorter_name)
    R_id = get_known_recording_id(items.workspace, r_label)
    (gt_exists, sorting_exists) = sortings_are_in_workspace(items.workspace, gt_label, s_label)
    entry = FullRecordingEntry(
        r_label, gt_label, s_label, R_id,
        items.recording, items.gt_sort, items.sorting,
        gt_exists, sorting_exists
    )
    add_entry_to_workspace(re=entry, workspace=items.workspace)

def main():
    (params, std_args) = init_configuration()
    study_sets = load_study_records(params.study_source_file)
    study_matrix = parse_sorters(params.sorter_spec_file, list(study_sets.keys()))
    sorting_matrix = populate_sorting_matrix(study_matrix, study_sets)
    sorting_matrix = remove_preexisting_records(sorting_matrix, params.workspace_uri)
    hither_config = extract_hither_config(std_args)
    jobs: hi.Job = []

    try:
        with hi.Config(**hither_config):
            sortings = list(sorting_loop(sorting_matrix))
            with hi.Config(job_handler=None, job_cache=None):
                for sorting in sortings:
                    p = {
                        'sorting_entry': sorting,
                        'workspace_uri': params.workspace_uri
                    }
                    jobs.append(hi.Job(hi_post_result_to_workspace, p))
        hi.wait(None)
    finally:
        call_cleanup(hither_config)


if __name__ == "__main__":
    main()