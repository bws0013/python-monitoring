# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import proto  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.monitoring.v3", manifest={"DroppedLabels",},
)


class DroppedLabels(proto.Message):
    r"""A set of (label, value) pairs which were dropped during
    aggregation, attached to google.api.Distribution.Exemplars in
    google.api.Distribution values during aggregation.

    These values are used in combination with the label values that
    remain on the aggregated Distribution timeseries to construct
    the full label set for the exemplar values.  The resulting full
    label set may be used to identify the specific task/job/instance
    (for example) which may be contributing to a long-tail, while
    allowing the storage savings of only storing aggregated
    distribution values for a large group.

    Note that there are no guarantees on ordering of the labels from
    exemplar-to-exemplar and from distribution-to-distribution in
    the same stream, and there may be duplicates.  It is up to
    clients to resolve any ambiguities.

    Attributes:
        label (Sequence[~.dropped_labels.DroppedLabels.LabelEntry]):
            Map from label to its value, for all labels
            dropped in any aggregation.
    """

    label = proto.MapField(proto.STRING, proto.STRING, number=1)


__all__ = tuple(sorted(__protobuf__.manifest))
