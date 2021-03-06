# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction, connection, OperationalError
from django.utils.functional import cached_property

from mex.rpc import get_client


class StreamPaginator(Paginator):
    """Paginator that gets its total count via chain api. """

    def __init__(self, stream, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = stream

    @cached_property
    def count(self):
        api = get_client()
        try:
            stream_info = api.getstreaminfo(self.stream)
            return int(stream_info.get("items"))
        except Exception:
            return 999999


class TimeLimitedPaginator(Paginator):
    """
   Paginator that enforces a timeout on the count operation.
   If the operations times out, a fake bogus value is
   returned instead.
   """

    @cached_property
    def count(self):
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout TO 200;")
            try:
                return super().count
            except OperationalError:
                return 9999999
