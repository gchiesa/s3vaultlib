#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from io import BytesIO

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"
#
# HEAD_OBJECT = {
#     'DeleteMarker': True,
#     'AcceptRanges': 'string',
#     'Expiration': 'string',
#     'Restore': 'string',
#     'LastModified': datetime(2015, 1, 1),
#     'ContentLength': 123,
#     'ETag': 'string',
#     'MissingMeta': 123,
#     'VersionId': 'string',
#     'CacheControl': 'string',
#     'ContentDisposition': 'string',
#     'ContentEncoding': 'string',
#     'ContentLanguage': 'string',
#     'ContentType': 'string',
#     'Expires': datetime(2015, 1, 1),
#     'WebsiteRedirectLocation': 'string',
#     'ServerSideEncryption': 'aws:kms',
#     'Metadata': {
#         'string': 'string'
#     },
#     'SSECustomerAlgorithm': 'string',
#     'SSECustomerKeyMD5': 'string',
#     'SSEKMSKeyId': 'string',
#     'StorageClass': 'STANDARD',
#     'RequestCharged': 'requester',
#     'ReplicationStatus': 'COMPLETE',
#     'PartsCount': 123
# }
#
# OBJECTS = [
#     {
#         'data': {
#             'Body': BytesIO(u'κόσμε'.encode('utf-8')),
#             'DeleteMarker': True,
#             'AcceptRanges': 'string',
#             'Expiration': 'string',
#             'Restore': 'string',
#             'LastModified': datetime(2015, 1, 1),
#             'ContentLength': 123,
#             'ETag': 'string',
#             'MissingMeta': 123,
#             'VersionId': 'string',
#             'CacheControl': 'string',
#             'ContentDisposition': 'string',
#             'ContentEncoding': 'string',
#             'ContentLanguage': 'string',
#             'ContentRange': 'string',
#             'ContentType': 'string',
#             'Expires': datetime(2015, 1, 1),
#             'WebsiteRedirectLocation': 'string',
#             'ServerSideEncryption': 'aws:kms',
#             'Metadata': {
#                 'string': 'string'
#             },
#             'SSECustomerAlgorithm': 'string',
#             'SSECustomerKeyMD5': 'string',
#             'SSEKMSKeyId': 'string',
#             'StorageClass': 'STANDARD',
#             'RequestCharged': 'requester',
#             'ReplicationStatus': 'COMPLETE',
#             'PartsCount': 123,
#             'TagCount': 123
#         },
#         'expect_body': bytes(b'\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5')
#     },
#     {'data': {
#         'Body': BytesIO(b'\x04\xf8\x00P'),
#         'DeleteMarker': True,
#         'AcceptRanges': 'string',
#         'Expiration': 'string',
#         'Restore': 'string',
#         'LastModified': datetime(2015, 1, 1),
#         'ContentLength': 123,
#         'ETag': 'string',
#         'MissingMeta': 123,
#         'VersionId': 'string',
#         'CacheControl': 'string',
#         'ContentDisposition': 'string',
#         'ContentEncoding': 'string',
#         'ContentLanguage': 'string',
#         'ContentRange': 'string',
#         'ContentType': 'string',
#         'Expires': datetime(2015, 1, 1),
#         'WebsiteRedirectLocation': 'string',
#         'ServerSideEncryption': 'aws:kms',
#         'Metadata': {
#             'string': 'string'
#         },
#         'SSECustomerAlgorithm': 'string',
#         'SSECustomerKeyMD5': 'string',
#         'SSEKMSKeyId': 'string',
#         'StorageClass': 'STANDARD',
#         'RequestCharged': 'requester',
#         'ReplicationStatus': 'COMPLETE',
#         'PartsCount': 123,
#         'TagCount': 123
#     },
#         'expect_body': bytes(b'\x04\xf8\x00P')
#     }
# ]
#
# OBJECT_DATA = [
#     {'Key': 'test_name',
#      'LastModified': datetime(2015, 1, 1),
#      'ETag': 'string',
#      'Size': 123,
#      'StorageClass': 'STANDARD',
#      'Owner': {
#          'DisplayName': 'owner',
#          'ID': 'id_string'
#      }},
#     {'Key': 'path/test_name',
#      'LastModified': datetime(2015, 1, 1),
#      'ETag': 'string',
#      'Size': 123,
#      'StorageClass': 'STANDARD',
#      'Owner': {
#          'DisplayName': 'owner',
#          'ID': 'id_string'
#      }}
# ]

# ----

LIST_OBJECTS_V2 = [
    {'Key': 'test_name',
     'LastModified': datetime(2015, 1, 1),
     'ETag': 'string',
     'Size': 123,
     'StorageClass': 'STANDARD',
     'Owner': {
         'DisplayName': 'owner',
         'ID': 'id_string'
     }
     },
    {'Key': 'path/test_name2',
     'LastModified': datetime(2015, 1, 1),
     'ETag': 'string',
     'Size': 123,
     'StorageClass': 'STANDARD',
     'Owner': {
         'DisplayName': 'owner',
         'ID': 'id_string'
     }
     }
]

GET_OBJECT = [
    {
        'Body': BytesIO(u'κόσμε'.encode('utf-8')),
        'DeleteMarker': True,
        'AcceptRanges': 'string',
        'Expiration': 'string',
        'Restore': 'string',
        'LastModified': datetime(2015, 1, 1),
        'ContentLength': 123,
        'ETag': 'string',
        'MissingMeta': 123,
        'VersionId': 'string',
        'CacheControl': 'string',
        'ContentDisposition': 'string',
        'ContentEncoding': 'string',
        'ContentLanguage': 'string',
        'ContentRange': 'string',
        'ContentType': 'string',
        'Expires': datetime(2015, 1, 1),
        'WebsiteRedirectLocation': 'string',
        'ServerSideEncryption': 'aws:kms',
        'Metadata': {
            'string': 'string'
        },
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'StorageClass': 'STANDARD',
        'RequestCharged': 'requester',
        'ReplicationStatus': 'COMPLETE',
        'PartsCount': 123,
        'TagCount': 123
    },
    {
        'Body': BytesIO(b'\x04\xf8\x00P'),
        'DeleteMarker': True,
        'AcceptRanges': 'string',
        'Expiration': 'string',
        'Restore': 'string',
        'LastModified': datetime(2015, 1, 1),
        'ContentLength': 123,
        'ETag': 'string',
        'MissingMeta': 123,
        'VersionId': 'string',
        'CacheControl': 'string',
        'ContentDisposition': 'string',
        'ContentEncoding': 'string',
        'ContentLanguage': 'string',
        'ContentRange': 'string',
        'ContentType': 'string',
        'Expires': datetime(2015, 1, 1),
        'WebsiteRedirectLocation': 'string',
        'ServerSideEncryption': 'aws:kms',
        'Metadata': {
            'string': 'string'
        },
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'StorageClass': 'STANDARD',
        'RequestCharged': 'requester',
        'ReplicationStatus': 'COMPLETE',
        'PartsCount': 123,
        'TagCount': 123
    }
]

HEAD_OBJECT = {
    'DeleteMarker': True,
    'AcceptRanges': 'string',
    'Expiration': 'string',
    'Restore': 'string',
    'LastModified': datetime(2015, 1, 1),
    'ContentLength': 123,
    'ETag': 'string',
    'MissingMeta': 123,
    'VersionId': 'string',
    'CacheControl': 'string',
    'ContentDisposition': 'string',
    'ContentEncoding': 'string',
    'ContentLanguage': 'string',
    'ContentType': 'string',
    'Expires': datetime(2015, 1, 1),
    'WebsiteRedirectLocation': 'string',
    'ServerSideEncryption': 'aws:kms',
    'Metadata': {
        'string': 'string'
    },
    'SSECustomerAlgorithm': 'string',
    'SSECustomerKeyMD5': 'string',
    'SSEKMSKeyId': 'string',
    'StorageClass': 'STANDARD',
    'RequestCharged': 'requester',
    'ReplicationStatus': 'COMPLETE',
    'PartsCount': 123
}

S3_OBJECTS = {
    'test_name': {
        'head_object': HEAD_OBJECT,
        'get_object': GET_OBJECT[0],
        'list_objects_v2': LIST_OBJECTS_V2[0],
        '_expect_body': bytes(b'\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5')
    },
    'test_name2': {
        'head_object': HEAD_OBJECT,
        'get_object': GET_OBJECT[1],
        'list_objects_v2': LIST_OBJECTS_V2[1],
        '_expect_body': bytes(b'\x04\xf8\x00P')
    }
}
