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

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api import distribution_pb2 as distribution  # type: ignore
from google.api import label_pb2 as label  # type: ignore
from google.api import launch_stage_pb2 as launch_stage  # type: ignore
from google.api import metric_pb2 as ga_metric  # type: ignore
from google.api import metric_pb2 as metric  # type: ignore
from google.api import monitored_resource_pb2 as monitored_resource  # type: ignore
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.monitoring_v3.services.metric_service import MetricServiceAsyncClient
from google.cloud.monitoring_v3.services.metric_service import MetricServiceClient
from google.cloud.monitoring_v3.services.metric_service import pagers
from google.cloud.monitoring_v3.services.metric_service import transports
from google.cloud.monitoring_v3.types import common
from google.cloud.monitoring_v3.types import metric as gm_metric
from google.cloud.monitoring_v3.types import metric_service
from google.oauth2 import service_account
from google.protobuf import any_pb2 as gp_any  # type: ignore
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert MetricServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        MetricServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        MetricServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        MetricServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        MetricServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        MetricServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [MetricServiceClient, MetricServiceAsyncClient]
)
def test_metric_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "monitoring.googleapis.com:443"


def test_metric_service_client_get_transport_class():
    transport = MetricServiceClient.get_transport_class()
    assert transport == transports.MetricServiceGrpcTransport

    transport = MetricServiceClient.get_transport_class("grpc")
    assert transport == transports.MetricServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (MetricServiceClient, transports.MetricServiceGrpcTransport, "grpc"),
        (
            MetricServiceAsyncClient,
            transports.MetricServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    MetricServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetricServiceClient),
)
@mock.patch.object(
    MetricServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetricServiceAsyncClient),
)
def test_metric_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(MetricServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(MetricServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (MetricServiceClient, transports.MetricServiceGrpcTransport, "grpc", "true"),
        (
            MetricServiceAsyncClient,
            transports.MetricServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (MetricServiceClient, transports.MetricServiceGrpcTransport, "grpc", "false"),
        (
            MetricServiceAsyncClient,
            transports.MetricServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    MetricServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetricServiceClient),
)
@mock.patch.object(
    MetricServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetricServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_metric_service_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            ssl_channel_creds = mock.Mock()
            with mock.patch(
                "grpc.ssl_channel_credentials", return_value=ssl_channel_creds
            ):
                patched.return_value = None
                client = client_class(client_options=options)

                if use_client_cert_env == "false":
                    expected_ssl_channel_creds = None
                    expected_host = client.DEFAULT_ENDPOINT
                else:
                    expected_ssl_channel_creds = ssl_channel_creds
                    expected_host = client.DEFAULT_MTLS_ENDPOINT

                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=expected_host,
                    scopes=None,
                    ssl_channel_credentials=expected_ssl_channel_creds,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    with mock.patch(
                        "google.auth.transport.grpc.SslCredentials.ssl_credentials",
                        new_callable=mock.PropertyMock,
                    ) as ssl_credentials_mock:
                        if use_client_cert_env == "false":
                            is_mtls_mock.return_value = False
                            ssl_credentials_mock.return_value = None
                            expected_host = client.DEFAULT_ENDPOINT
                            expected_ssl_channel_creds = None
                        else:
                            is_mtls_mock.return_value = True
                            ssl_credentials_mock.return_value = mock.Mock()
                            expected_host = client.DEFAULT_MTLS_ENDPOINT
                            expected_ssl_channel_creds = (
                                ssl_credentials_mock.return_value
                            )

                        patched.return_value = None
                        client = client_class()
                        patched.assert_called_once_with(
                            credentials=None,
                            credentials_file=None,
                            host=expected_host,
                            scopes=None,
                            ssl_channel_credentials=expected_ssl_channel_creds,
                            quota_project_id=None,
                            client_info=transports.base.DEFAULT_CLIENT_INFO,
                        )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    is_mtls_mock.return_value = False
                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=client.DEFAULT_ENDPOINT,
                        scopes=None,
                        ssl_channel_credentials=None,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (MetricServiceClient, transports.MetricServiceGrpcTransport, "grpc"),
        (
            MetricServiceAsyncClient,
            transports.MetricServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_metric_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (MetricServiceClient, transports.MetricServiceGrpcTransport, "grpc"),
        (
            MetricServiceAsyncClient,
            transports.MetricServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_metric_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_metric_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.monitoring_v3.services.metric_service.transports.MetricServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = MetricServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_list_monitored_resource_descriptors(
    transport: str = "grpc",
    request_type=metric_service.ListMonitoredResourceDescriptorsRequest,
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListMonitoredResourceDescriptorsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_monitored_resource_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.ListMonitoredResourceDescriptorsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMonitoredResourceDescriptorsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_monitored_resource_descriptors_from_dict():
    test_list_monitored_resource_descriptors(request_type=dict)


@pytest.mark.asyncio
async def test_list_monitored_resource_descriptors_async(
    transport: str = "grpc_asyncio",
):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.ListMonitoredResourceDescriptorsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListMonitoredResourceDescriptorsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_monitored_resource_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMonitoredResourceDescriptorsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_monitored_resource_descriptors_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.ListMonitoredResourceDescriptorsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        call.return_value = metric_service.ListMonitoredResourceDescriptorsResponse()

        client.list_monitored_resource_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_monitored_resource_descriptors_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.ListMonitoredResourceDescriptorsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListMonitoredResourceDescriptorsResponse()
        )

        await client.list_monitored_resource_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_monitored_resource_descriptors_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListMonitoredResourceDescriptorsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_monitored_resource_descriptors(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_list_monitored_resource_descriptors_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_monitored_resource_descriptors(
            metric_service.ListMonitoredResourceDescriptorsRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_list_monitored_resource_descriptors_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListMonitoredResourceDescriptorsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListMonitoredResourceDescriptorsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_monitored_resource_descriptors(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_list_monitored_resource_descriptors_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_monitored_resource_descriptors(
            metric_service.ListMonitoredResourceDescriptorsRequest(), name="name_value",
        )


def test_list_monitored_resource_descriptors_pager():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="ghi",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", ""),)),
        )
        pager = client.list_monitored_resource_descriptors(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(
            isinstance(i, monitored_resource.MonitoredResourceDescriptor)
            for i in results
        )


def test_list_monitored_resource_descriptors_pages():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_monitored_resource_descriptors), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="ghi",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_monitored_resource_descriptors(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_monitored_resource_descriptors_async_pager():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_monitored_resource_descriptors),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="ghi",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_monitored_resource_descriptors(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, monitored_resource.MonitoredResourceDescriptor)
            for i in responses
        )


@pytest.mark.asyncio
async def test_list_monitored_resource_descriptors_async_pages():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_monitored_resource_descriptors),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
                next_page_token="ghi",
            ),
            metric_service.ListMonitoredResourceDescriptorsResponse(
                resource_descriptors=[
                    monitored_resource.MonitoredResourceDescriptor(),
                    monitored_resource.MonitoredResourceDescriptor(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_monitored_resource_descriptors(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_monitored_resource_descriptor(
    transport: str = "grpc",
    request_type=metric_service.GetMonitoredResourceDescriptorRequest,
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_monitored_resource_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = monitored_resource.MonitoredResourceDescriptor(
            name="name_value",
            type_="type__value",
            display_name="display_name_value",
            description="description_value",
            launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,
        )

        response = client.get_monitored_resource_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.GetMonitoredResourceDescriptorRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, monitored_resource.MonitoredResourceDescriptor)

    assert response.name == "name_value"

    assert response.type_ == "type__value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED


def test_get_monitored_resource_descriptor_from_dict():
    test_get_monitored_resource_descriptor(request_type=dict)


@pytest.mark.asyncio
async def test_get_monitored_resource_descriptor_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.GetMonitoredResourceDescriptorRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_monitored_resource_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            monitored_resource.MonitoredResourceDescriptor(
                name="name_value",
                type_="type__value",
                display_name="display_name_value",
                description="description_value",
                launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,
            )
        )

        response = await client.get_monitored_resource_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, monitored_resource.MonitoredResourceDescriptor)

    assert response.name == "name_value"

    assert response.type_ == "type__value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED


def test_get_monitored_resource_descriptor_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.GetMonitoredResourceDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_monitored_resource_descriptor), "__call__"
    ) as call:
        call.return_value = monitored_resource.MonitoredResourceDescriptor()

        client.get_monitored_resource_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_monitored_resource_descriptor_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.GetMonitoredResourceDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_monitored_resource_descriptor), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            monitored_resource.MonitoredResourceDescriptor()
        )

        await client.get_monitored_resource_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_monitored_resource_descriptor_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_monitored_resource_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = monitored_resource.MonitoredResourceDescriptor()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_monitored_resource_descriptor(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_monitored_resource_descriptor_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_monitored_resource_descriptor(
            metric_service.GetMonitoredResourceDescriptorRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_monitored_resource_descriptor_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_monitored_resource_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = monitored_resource.MonitoredResourceDescriptor()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            monitored_resource.MonitoredResourceDescriptor()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_monitored_resource_descriptor(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_monitored_resource_descriptor_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_monitored_resource_descriptor(
            metric_service.GetMonitoredResourceDescriptorRequest(), name="name_value",
        )


def test_list_metric_descriptors(
    transport: str = "grpc", request_type=metric_service.ListMetricDescriptorsRequest
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_metric_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListMetricDescriptorsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_metric_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.ListMetricDescriptorsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMetricDescriptorsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_metric_descriptors_from_dict():
    test_list_metric_descriptors(request_type=dict)


@pytest.mark.asyncio
async def test_list_metric_descriptors_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.ListMetricDescriptorsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_metric_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListMetricDescriptorsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_metric_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMetricDescriptorsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_metric_descriptors_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.ListMetricDescriptorsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_metric_descriptors), "__call__"
    ) as call:
        call.return_value = metric_service.ListMetricDescriptorsResponse()

        client.list_metric_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_metric_descriptors_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.ListMetricDescriptorsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_metric_descriptors), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListMetricDescriptorsResponse()
        )

        await client.list_metric_descriptors(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_metric_descriptors_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_metric_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListMetricDescriptorsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_metric_descriptors(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_list_metric_descriptors_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_metric_descriptors(
            metric_service.ListMetricDescriptorsRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_list_metric_descriptors_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_metric_descriptors), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListMetricDescriptorsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListMetricDescriptorsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_metric_descriptors(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_list_metric_descriptors_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_metric_descriptors(
            metric_service.ListMetricDescriptorsRequest(), name="name_value",
        )


def test_list_metric_descriptors_pager():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_metric_descriptors), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[ga_metric.MetricDescriptor(),],
                next_page_token="ghi",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", ""),)),
        )
        pager = client.list_metric_descriptors(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, ga_metric.MetricDescriptor) for i in results)


def test_list_metric_descriptors_pages():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_metric_descriptors), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[ga_metric.MetricDescriptor(),],
                next_page_token="ghi",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_metric_descriptors(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_metric_descriptors_async_pager():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_metric_descriptors),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[ga_metric.MetricDescriptor(),],
                next_page_token="ghi",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_metric_descriptors(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, ga_metric.MetricDescriptor) for i in responses)


@pytest.mark.asyncio
async def test_list_metric_descriptors_async_pages():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_metric_descriptors),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[], next_page_token="def",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[ga_metric.MetricDescriptor(),],
                next_page_token="ghi",
            ),
            metric_service.ListMetricDescriptorsResponse(
                metric_descriptors=[
                    ga_metric.MetricDescriptor(),
                    ga_metric.MetricDescriptor(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_metric_descriptors(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_metric_descriptor(
    transport: str = "grpc", request_type=metric_service.GetMetricDescriptorRequest
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = ga_metric.MetricDescriptor(
            name="name_value",
            type_="type__value",
            metric_kind=ga_metric.MetricDescriptor.MetricKind.GAUGE,
            value_type=ga_metric.MetricDescriptor.ValueType.BOOL,
            unit="unit_value",
            description="description_value",
            display_name="display_name_value",
            launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,
            monitored_resource_types=["monitored_resource_types_value"],
        )

        response = client.get_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.GetMetricDescriptorRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, ga_metric.MetricDescriptor)

    assert response.name == "name_value"

    assert response.type_ == "type__value"

    assert response.metric_kind == ga_metric.MetricDescriptor.MetricKind.GAUGE

    assert response.value_type == ga_metric.MetricDescriptor.ValueType.BOOL

    assert response.unit == "unit_value"

    assert response.description == "description_value"

    assert response.display_name == "display_name_value"

    assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED

    assert response.monitored_resource_types == ["monitored_resource_types_value"]


def test_get_metric_descriptor_from_dict():
    test_get_metric_descriptor(request_type=dict)


@pytest.mark.asyncio
async def test_get_metric_descriptor_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.GetMetricDescriptorRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            ga_metric.MetricDescriptor(
                name="name_value",
                type_="type__value",
                metric_kind=ga_metric.MetricDescriptor.MetricKind.GAUGE,
                value_type=ga_metric.MetricDescriptor.ValueType.BOOL,
                unit="unit_value",
                description="description_value",
                display_name="display_name_value",
                launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,
                monitored_resource_types=["monitored_resource_types_value"],
            )
        )

        response = await client.get_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, ga_metric.MetricDescriptor)

    assert response.name == "name_value"

    assert response.type_ == "type__value"

    assert response.metric_kind == ga_metric.MetricDescriptor.MetricKind.GAUGE

    assert response.value_type == ga_metric.MetricDescriptor.ValueType.BOOL

    assert response.unit == "unit_value"

    assert response.description == "description_value"

    assert response.display_name == "display_name_value"

    assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED

    assert response.monitored_resource_types == ["monitored_resource_types_value"]


def test_get_metric_descriptor_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.GetMetricDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_metric_descriptor), "__call__"
    ) as call:
        call.return_value = ga_metric.MetricDescriptor()

        client.get_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_metric_descriptor_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.GetMetricDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_metric_descriptor), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            ga_metric.MetricDescriptor()
        )

        await client.get_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_metric_descriptor_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = ga_metric.MetricDescriptor()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_metric_descriptor(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_metric_descriptor_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_metric_descriptor(
            metric_service.GetMetricDescriptorRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_metric_descriptor_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = ga_metric.MetricDescriptor()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            ga_metric.MetricDescriptor()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_metric_descriptor(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_metric_descriptor_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_metric_descriptor(
            metric_service.GetMetricDescriptorRequest(), name="name_value",
        )


def test_create_metric_descriptor(
    transport: str = "grpc", request_type=metric_service.CreateMetricDescriptorRequest
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = ga_metric.MetricDescriptor(
            name="name_value",
            type_="type__value",
            metric_kind=ga_metric.MetricDescriptor.MetricKind.GAUGE,
            value_type=ga_metric.MetricDescriptor.ValueType.BOOL,
            unit="unit_value",
            description="description_value",
            display_name="display_name_value",
            launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,
            monitored_resource_types=["monitored_resource_types_value"],
        )

        response = client.create_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.CreateMetricDescriptorRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, ga_metric.MetricDescriptor)

    assert response.name == "name_value"

    assert response.type_ == "type__value"

    assert response.metric_kind == ga_metric.MetricDescriptor.MetricKind.GAUGE

    assert response.value_type == ga_metric.MetricDescriptor.ValueType.BOOL

    assert response.unit == "unit_value"

    assert response.description == "description_value"

    assert response.display_name == "display_name_value"

    assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED

    assert response.monitored_resource_types == ["monitored_resource_types_value"]


def test_create_metric_descriptor_from_dict():
    test_create_metric_descriptor(request_type=dict)


@pytest.mark.asyncio
async def test_create_metric_descriptor_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.CreateMetricDescriptorRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            ga_metric.MetricDescriptor(
                name="name_value",
                type_="type__value",
                metric_kind=ga_metric.MetricDescriptor.MetricKind.GAUGE,
                value_type=ga_metric.MetricDescriptor.ValueType.BOOL,
                unit="unit_value",
                description="description_value",
                display_name="display_name_value",
                launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,
                monitored_resource_types=["monitored_resource_types_value"],
            )
        )

        response = await client.create_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, ga_metric.MetricDescriptor)

    assert response.name == "name_value"

    assert response.type_ == "type__value"

    assert response.metric_kind == ga_metric.MetricDescriptor.MetricKind.GAUGE

    assert response.value_type == ga_metric.MetricDescriptor.ValueType.BOOL

    assert response.unit == "unit_value"

    assert response.description == "description_value"

    assert response.display_name == "display_name_value"

    assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED

    assert response.monitored_resource_types == ["monitored_resource_types_value"]


def test_create_metric_descriptor_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.CreateMetricDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_metric_descriptor), "__call__"
    ) as call:
        call.return_value = ga_metric.MetricDescriptor()

        client.create_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_metric_descriptor_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.CreateMetricDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_metric_descriptor), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            ga_metric.MetricDescriptor()
        )

        await client.create_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_create_metric_descriptor_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = ga_metric.MetricDescriptor()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_metric_descriptor(
            name="name_value",
            metric_descriptor=ga_metric.MetricDescriptor(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].metric_descriptor == ga_metric.MetricDescriptor(
            name="name_value"
        )


def test_create_metric_descriptor_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_metric_descriptor(
            metric_service.CreateMetricDescriptorRequest(),
            name="name_value",
            metric_descriptor=ga_metric.MetricDescriptor(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_metric_descriptor_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = ga_metric.MetricDescriptor()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            ga_metric.MetricDescriptor()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_metric_descriptor(
            name="name_value",
            metric_descriptor=ga_metric.MetricDescriptor(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].metric_descriptor == ga_metric.MetricDescriptor(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_create_metric_descriptor_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_metric_descriptor(
            metric_service.CreateMetricDescriptorRequest(),
            name="name_value",
            metric_descriptor=ga_metric.MetricDescriptor(name="name_value"),
        )


def test_delete_metric_descriptor(
    transport: str = "grpc", request_type=metric_service.DeleteMetricDescriptorRequest
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.DeleteMetricDescriptorRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_metric_descriptor_from_dict():
    test_delete_metric_descriptor(request_type=dict)


@pytest.mark.asyncio
async def test_delete_metric_descriptor_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.DeleteMetricDescriptorRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_metric_descriptor_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.DeleteMetricDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_metric_descriptor), "__call__"
    ) as call:
        call.return_value = None

        client.delete_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_metric_descriptor_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.DeleteMetricDescriptorRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_metric_descriptor), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_metric_descriptor(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_metric_descriptor_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_metric_descriptor(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_metric_descriptor_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_metric_descriptor(
            metric_service.DeleteMetricDescriptorRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_metric_descriptor_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_metric_descriptor), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_metric_descriptor(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_metric_descriptor_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_metric_descriptor(
            metric_service.DeleteMetricDescriptorRequest(), name="name_value",
        )


def test_list_time_series(
    transport: str = "grpc", request_type=metric_service.ListTimeSeriesRequest
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListTimeSeriesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.ListTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTimeSeriesPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_time_series_from_dict():
    test_list_time_series(request_type=dict)


@pytest.mark.asyncio
async def test_list_time_series_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.ListTimeSeriesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListTimeSeriesResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTimeSeriesAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_time_series_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.ListTimeSeriesRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_time_series), "__call__"
    ) as call:
        call.return_value = metric_service.ListTimeSeriesResponse()

        client.list_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_time_series_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.ListTimeSeriesRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListTimeSeriesResponse()
        )

        await client.list_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_time_series_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListTimeSeriesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_time_series(
            name="name_value",
            filter="filter_value",
            interval=common.TimeInterval(end_time=timestamp.Timestamp(seconds=751)),
            view=metric_service.ListTimeSeriesRequest.TimeSeriesView.HEADERS,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].filter == "filter_value"

        assert args[0].interval == common.TimeInterval(
            end_time=timestamp.Timestamp(seconds=751)
        )

        assert (
            args[0].view == metric_service.ListTimeSeriesRequest.TimeSeriesView.HEADERS
        )


def test_list_time_series_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_time_series(
            metric_service.ListTimeSeriesRequest(),
            name="name_value",
            filter="filter_value",
            interval=common.TimeInterval(end_time=timestamp.Timestamp(seconds=751)),
            view=metric_service.ListTimeSeriesRequest.TimeSeriesView.HEADERS,
        )


@pytest.mark.asyncio
async def test_list_time_series_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metric_service.ListTimeSeriesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metric_service.ListTimeSeriesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_time_series(
            name="name_value",
            filter="filter_value",
            interval=common.TimeInterval(end_time=timestamp.Timestamp(seconds=751)),
            view=metric_service.ListTimeSeriesRequest.TimeSeriesView.HEADERS,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].filter == "filter_value"

        assert args[0].interval == common.TimeInterval(
            end_time=timestamp.Timestamp(seconds=751)
        )

        assert (
            args[0].view == metric_service.ListTimeSeriesRequest.TimeSeriesView.HEADERS
        )


@pytest.mark.asyncio
async def test_list_time_series_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_time_series(
            metric_service.ListTimeSeriesRequest(),
            name="name_value",
            filter="filter_value",
            interval=common.TimeInterval(end_time=timestamp.Timestamp(seconds=751)),
            view=metric_service.ListTimeSeriesRequest.TimeSeriesView.HEADERS,
        )


def test_list_time_series_pager():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_time_series), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListTimeSeriesResponse(
                time_series=[
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[], next_page_token="def",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(),], next_page_token="ghi",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(), gm_metric.TimeSeries(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", ""),)),
        )
        pager = client.list_time_series(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, gm_metric.TimeSeries) for i in results)


def test_list_time_series_pages():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_time_series), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListTimeSeriesResponse(
                time_series=[
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[], next_page_token="def",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(),], next_page_token="ghi",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(), gm_metric.TimeSeries(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_time_series(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_time_series_async_pager():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_time_series),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListTimeSeriesResponse(
                time_series=[
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[], next_page_token="def",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(),], next_page_token="ghi",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(), gm_metric.TimeSeries(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_time_series(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, gm_metric.TimeSeries) for i in responses)


@pytest.mark.asyncio
async def test_list_time_series_async_pages():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_time_series),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metric_service.ListTimeSeriesResponse(
                time_series=[
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                    gm_metric.TimeSeries(),
                ],
                next_page_token="abc",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[], next_page_token="def",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(),], next_page_token="ghi",
            ),
            metric_service.ListTimeSeriesResponse(
                time_series=[gm_metric.TimeSeries(), gm_metric.TimeSeries(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_time_series(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_create_time_series(
    transport: str = "grpc", request_type=metric_service.CreateTimeSeriesRequest
):
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.create_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == metric_service.CreateTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_create_time_series_from_dict():
    test_create_time_series(request_type=dict)


@pytest.mark.asyncio
async def test_create_time_series_async(transport: str = "grpc_asyncio"):
    client = MetricServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = metric_service.CreateTimeSeriesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.create_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_create_time_series_field_headers():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.CreateTimeSeriesRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_time_series), "__call__"
    ) as call:
        call.return_value = None

        client.create_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_time_series_field_headers_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metric_service.CreateTimeSeriesRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.create_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_create_time_series_flattened():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_time_series(
            name="name_value",
            time_series=[
                gm_metric.TimeSeries(metric=ga_metric.Metric(type_="type__value"))
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].time_series == [
            gm_metric.TimeSeries(metric=ga_metric.Metric(type_="type__value"))
        ]


def test_create_time_series_flattened_error():
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_time_series(
            metric_service.CreateTimeSeriesRequest(),
            name="name_value",
            time_series=[
                gm_metric.TimeSeries(metric=ga_metric.Metric(type_="type__value"))
            ],
        )


@pytest.mark.asyncio
async def test_create_time_series_flattened_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_time_series(
            name="name_value",
            time_series=[
                gm_metric.TimeSeries(metric=ga_metric.Metric(type_="type__value"))
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].time_series == [
            gm_metric.TimeSeries(metric=ga_metric.Metric(type_="type__value"))
        ]


@pytest.mark.asyncio
async def test_create_time_series_flattened_error_async():
    client = MetricServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_time_series(
            metric_service.CreateTimeSeriesRequest(),
            name="name_value",
            time_series=[
                gm_metric.TimeSeries(metric=ga_metric.Metric(type_="type__value"))
            ],
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.MetricServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = MetricServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.MetricServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = MetricServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.MetricServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = MetricServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.MetricServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = MetricServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.MetricServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.MetricServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.MetricServiceGrpcTransport,
        transports.MetricServiceGrpcAsyncIOTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = MetricServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.MetricServiceGrpcTransport,)


def test_metric_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.MetricServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_metric_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.monitoring_v3.services.metric_service.transports.MetricServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.MetricServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "list_monitored_resource_descriptors",
        "get_monitored_resource_descriptor",
        "list_metric_descriptors",
        "get_metric_descriptor",
        "create_metric_descriptor",
        "delete_metric_descriptor",
        "list_time_series",
        "create_time_series",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_metric_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.monitoring_v3.services.metric_service.transports.MetricServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.MetricServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/monitoring",
                "https://www.googleapis.com/auth/monitoring.read",
                "https://www.googleapis.com/auth/monitoring.write",
            ),
            quota_project_id="octopus",
        )


def test_metric_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, "default") as adc, mock.patch(
        "google.cloud.monitoring_v3.services.metric_service.transports.MetricServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.MetricServiceTransport()
        adc.assert_called_once()


def test_metric_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        MetricServiceClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/monitoring",
                "https://www.googleapis.com/auth/monitoring.read",
                "https://www.googleapis.com/auth/monitoring.write",
            ),
            quota_project_id=None,
        )


def test_metric_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.MetricServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/monitoring",
                "https://www.googleapis.com/auth/monitoring.read",
                "https://www.googleapis.com/auth/monitoring.write",
            ),
            quota_project_id="octopus",
        )


def test_metric_service_host_no_port():
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="monitoring.googleapis.com"
        ),
    )
    assert client._transport._host == "monitoring.googleapis.com:443"


def test_metric_service_host_with_port():
    client = MetricServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="monitoring.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "monitoring.googleapis.com:8000"


def test_metric_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.MetricServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"


def test_metric_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.MetricServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.MetricServiceGrpcTransport,
        transports.MetricServiceGrpcAsyncIOTransport,
    ],
)
def test_metric_service_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=(
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/monitoring",
                    "https://www.googleapis.com/auth/monitoring.read",
                    "https://www.googleapis.com/auth/monitoring.write",
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.MetricServiceGrpcTransport,
        transports.MetricServiceGrpcAsyncIOTransport,
    ],
)
def test_metric_service_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=(
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/monitoring",
                    "https://www.googleapis.com/auth/monitoring.read",
                    "https://www.googleapis.com/auth/monitoring.write",
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.MetricServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = MetricServiceClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.MetricServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = MetricServiceClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
