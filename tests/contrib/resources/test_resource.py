# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Geo Secretariat.
#
# geo-comments is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test contrib services."""

import pytest
from pytest_lazyfixture import lazy_fixture

from geo_comments.comments.records.api import CommentStatus
from geo_comments.contrib.packages.comments.api import PackageComment
from geo_comments.contrib.packages.feedbacks.api import PackageFeedback
from geo_comments.contrib.resources.comments.api import ResourceComment
from geo_comments.contrib.resources.feedbacks.api import ResourceFeedback


@pytest.mark.parametrize(
    "service_prefix,service_resource,comment_cls,record,comment_content",
    [
        (
            "/packages",
            "/comments",
            PackageComment,
            lazy_fixture("record_package_simple"),
            lazy_fixture("comment_record_data"),
        ),
        (
            "/packages",
            "/feedbacks",
            PackageFeedback,
            lazy_fixture("record_package_simple"),
            lazy_fixture("feedback_record_data"),
        ),
        (
            "/records",
            "/comments",
            ResourceComment,
            lazy_fixture("record_resource_simple"),
            lazy_fixture("comment_record_data"),
        ),
        (
            "/records",
            "/feedbacks",
            ResourceFeedback,
            lazy_fixture("record_resource_simple"),
            lazy_fixture("feedback_record_data"),
        ),
    ],
)
def test_resource_basic_commenting_workflow(
    client,
    client_logged_as,
    service_prefix,
    service_resource,
    comment_cls,
    record,
    comment_content,
):
    """Test basic commenting workflow using service."""
    # 1. Log in with the basic user.
    client_with_login = client_logged_as("basic@example.org")

    # 2. Create comment
    base_comments_url = f"{service_prefix}/{record.pid.pid_value}{service_resource}"

    response = client_with_login.post(base_comments_url, json=comment_content)

    assert response.status_code == 201
    assert response.json.get("content") == comment_content.get("content")

    # 3. Reading the comment
    # 3.1. User who created the comment can read it
    comment_id = response.json["id"]

    comment_url = f"{base_comments_url}/{comment_id}"

    response_two = client_with_login.get(comment_url)

    assert response_two.status_code == 200
    assert response_two.json == response.json

    # 3.2. Trying to read the denied comment with an authenticated user
    client_with_login = client_logged_as("basic2@example.org")

    response_two = client.get(comment_url)

    assert response_two.status_code == 403

    # 4. Allowing the comment in the system
    allow_comment_url = f"{comment_url}/actions/allow"

    # 4.1. Trying using an authenticated user
    response_two = client_with_login.post(allow_comment_url)

    assert response_two.status_code == 403

    # 4.2. (ToDo) Trying using an unauthenticated user
    # response_two = client.post(allow_comment_url)
    # assert response_two.status_code == 403

    # 4.3. Trying using an admin user
    client_with_login_admin = client_logged_as("admin@example.org")

    response_two = client_with_login_admin.post(allow_comment_url)

    assert response_two.status_code == 200
    assert response_two.json["status"] == CommentStatus.ALLOWED.value

    comment_cls.index.refresh()

    # 4.4. Checking the comment with changed state
    # 4.4.1. Reading with the owner of the comment
    response_two = client_with_login.get(comment_url)

    assert response_two.status_code == 200
    assert response_two.json["status"] == CommentStatus.ALLOWED.value

    # 4.4.2. (ToDo) Reading with an unauthenticated user

    # 5. Searching for the comment by record
    search_result = client_with_login.get(base_comments_url)

    assert search_result.status_code == 200
    assert search_result.json["hits"]["total"] != 0
