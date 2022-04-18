from copy import deepcopy
from ..load_extractors import load_recording_extractor, load_sorting_extractor


class SFRecording:
    def __init__(self, recording_record: dict) -> None:
        self._recording_record = recording_record
    @property
    def recording_record(self):
        return deepcopy(self._recording_record)
    @property
    def recording_name(self):
        return self._recording_record['name']
    @property
    def study_name(self):
        return self._recording_record['studyName']
    @property
    def study_set_name(self):
        return self._recording_record['studySetName']
    @property
    def sampling_frequency(self):
        return self._recording_record['sampleRateHz']
    @property
    def num_channels(self):
        return self._recording_record['numChannels']
    @property
    def duration_sec(self):
        return self._recording_record['durationSec']
    @property
    def num_true_units(self):
        return self._recording_record['numTrueUnits']
    @property
    def sorting_true_object(self):
        return deepcopy(self._recording_record['sortingTrueObject'])
    @property
    def recording_object(self):
        return deepcopy(self._recording_record['recordingObject'])
    def get_sorting_true_extractor(self):
        return load_sorting_extractor(self.sorting_true_object)
    def get_recording_extractor(self):
        return load_recording_extractor(self.recording_object)