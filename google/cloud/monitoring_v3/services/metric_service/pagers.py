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
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    Sequence,
    Tuple,
    Optional,
)

from google.api import metric_pb2  # type: ignore
from google.api import monitored_resource_pb2  # type: ignore
from google.cloud.monitoring_v3.types import metric as gm_metric
from google.cloud.monitoring_v3.types import metric_service


class ListMonitoredResourceDescriptorsPager:
    """A pager for iterating through ``list_monitored_resource_descriptors`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``resource_descriptors`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListMonitoredResourceDescriptors`` requests and continue to iterate
    through the ``resource_descriptors`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., metric_service.ListMonitoredResourceDescriptorsResponse],
        request: metric_service.ListMonitoredResourceDescriptorsRequest,
        response: metric_service.ListMonitoredResourceDescriptorsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsRequest):
                The initial request object.
            response (google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = metric_service.ListMonitoredResourceDescriptorsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(
        self,
    ) -> Iterable[metric_service.ListMonitoredResourceDescriptorsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[monitored_resource_pb2.MonitoredResourceDescriptor]:
        for page in self.pages:
            yield from page.resource_descriptors

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListMonitoredResourceDescriptorsAsyncPager:
    """A pager for iterating through ``list_monitored_resource_descriptors`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``resource_descriptors`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListMonitoredResourceDescriptors`` requests and continue to iterate
    through the ``resource_descriptors`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[
            ..., Awaitable[metric_service.ListMonitoredResourceDescriptorsResponse]
        ],
        request: metric_service.ListMonitoredResourceDescriptorsRequest,
        response: metric_service.ListMonitoredResourceDescriptorsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsRequest):
                The initial request object.
            response (google.cloud.monitoring_v3.types.ListMonitoredResourceDescriptorsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = metric_service.ListMonitoredResourceDescriptorsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(
        self,
    ) -> AsyncIterable[metric_service.ListMonitoredResourceDescriptorsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(
        self,
    ) -> AsyncIterable[monitored_resource_pb2.MonitoredResourceDescriptor]:
        async def async_generator():
            async for page in self.pages:
                for response in page.resource_descriptors:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListMetricDescriptorsPager:
    """A pager for iterating through ``list_metric_descriptors`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.monitoring_v3.types.ListMetricDescriptorsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``metric_descriptors`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListMetricDescriptors`` requests and continue to iterate
    through the ``metric_descriptors`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.monitoring_v3.types.ListMetricDescriptorsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., metric_service.ListMetricDescriptorsResponse],
        request: metric_service.ListMetricDescriptorsRequest,
        response: metric_service.ListMetricDescriptorsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.monitoring_v3.types.ListMetricDescriptorsRequest):
                The initial request object.
            response (google.cloud.monitoring_v3.types.ListMetricDescriptorsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = metric_service.ListMetricDescriptorsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[metric_service.ListMetricDescriptorsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[ga_metric.MetricDescriptor]:
        for page in self.pages:
            yield from page.metric_descriptors

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListMetricDescriptorsAsyncPager:
    """A pager for iterating through ``list_metric_descriptors`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.monitoring_v3.types.ListMetricDescriptorsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``metric_descriptors`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListMetricDescriptors`` requests and continue to iterate
    through the ``metric_descriptors`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.monitoring_v3.types.ListMetricDescriptorsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[metric_service.ListMetricDescriptorsResponse]],
        request: metric_service.ListMetricDescriptorsRequest,
        response: metric_service.ListMetricDescriptorsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.monitoring_v3.types.ListMetricDescriptorsRequest):
                The initial request object.
            response (google.cloud.monitoring_v3.types.ListMetricDescriptorsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = metric_service.ListMetricDescriptorsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(
        self,
    ) -> AsyncIterable[metric_service.ListMetricDescriptorsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[ga_metric.MetricDescriptor]:
        async def async_generator():
            async for page in self.pages:
                for response in page.metric_descriptors:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListTimeSeriesPager:
    """A pager for iterating through ``list_time_series`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.monitoring_v3.types.ListTimeSeriesResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``time_series`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListTimeSeries`` requests and continue to iterate
    through the ``time_series`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.monitoring_v3.types.ListTimeSeriesResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., metric_service.ListTimeSeriesResponse],
        request: metric_service.ListTimeSeriesRequest,
        response: metric_service.ListTimeSeriesResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.monitoring_v3.types.ListTimeSeriesRequest):
                The initial request object.
            response (google.cloud.monitoring_v3.types.ListTimeSeriesResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = metric_service.ListTimeSeriesRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[metric_service.ListTimeSeriesResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[gm_metric.TimeSeries]:
        for page in self.pages:
            yield from page.time_series

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListTimeSeriesAsyncPager:
    """A pager for iterating through ``list_time_series`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.monitoring_v3.types.ListTimeSeriesResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``time_series`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListTimeSeries`` requests and continue to iterate
    through the ``time_series`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.monitoring_v3.types.ListTimeSeriesResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[metric_service.ListTimeSeriesResponse]],
        request: metric_service.ListTimeSeriesRequest,
        response: metric_service.ListTimeSeriesResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.monitoring_v3.types.ListTimeSeriesRequest):
                The initial request object.
            response (google.cloud.monitoring_v3.types.ListTimeSeriesResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = metric_service.ListTimeSeriesRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[metric_service.ListTimeSeriesResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[gm_metric.TimeSeries]:
        async def async_generator():
            async for page in self.pages:
                for response in page.time_series:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)
