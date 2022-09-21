# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Geo Secretariat.
#
# geo-comments is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Comment schemas."""

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode


#
# Base comment schema
#
class CommentSchema(BaseRecordSchema):
    """Comment schema class."""

    id = fields.UUID(dump_only=True)

    content = SanitizedHTML(required=True)

    status = SanitizedUnicode(
        validate=lambda obj: (validate.OneOf(choices=["A", "D"]))(obj),
        dump_only=True,
        required=True,
    )

    user = fields.Integer(required=True, dump_only=True, attribute="user")
    record = SanitizedUnicode(required=True, dump_only=True, attribute="record")


#
# Specialized comments schema
#

# Feedback
class FeedbackTopicSchema(Schema):
    """Feedback Topic schema class."""

    rating = fields.Number(required=True)
    name = SanitizedUnicode(required=True)


class FeedbackCommentSchema(CommentSchema):
    """Comment schema class."""

    topics = fields.List(
        cls_or_instance=fields.Nested(FeedbackTopicSchema()), required=True
    )
