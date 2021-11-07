# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: user.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='user.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\nuser.proto\"\x1e\n\x0fUserPostRequest\x12\x0b\n\x03msg\x18\x01 \x01(\t\"#\n\x10UserPostResponse\x12\x0f\n\x07success\x18\x01 \x01(\t\"\x1d\n\x0eUserGetRequest\x12\x0b\n\x03get\x18\x01 \x01(\x08\"\x1e\n\x0fUserGetResponse\x12\x0b\n\x03msg\x18\x01 \x03(\t2f\n\x0bUserService\x12-\n\x06\x61ppend\x12\x10.UserPostRequest\x1a\x11.UserPostResponse\x12(\n\x03get\x12\x0f.UserGetRequest\x1a\x10.UserGetResponseb\x06proto3'
)




_USERPOSTREQUEST = _descriptor.Descriptor(
  name='UserPostRequest',
  full_name='UserPostRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='msg', full_name='UserPostRequest.msg', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=14,
  serialized_end=44,
)


_USERPOSTRESPONSE = _descriptor.Descriptor(
  name='UserPostResponse',
  full_name='UserPostResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='UserPostResponse.success', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=46,
  serialized_end=81,
)


_USERGETREQUEST = _descriptor.Descriptor(
  name='UserGetRequest',
  full_name='UserGetRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='get', full_name='UserGetRequest.get', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=83,
  serialized_end=112,
)


_USERGETRESPONSE = _descriptor.Descriptor(
  name='UserGetResponse',
  full_name='UserGetResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='msg', full_name='UserGetResponse.msg', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=114,
  serialized_end=144,
)

DESCRIPTOR.message_types_by_name['UserPostRequest'] = _USERPOSTREQUEST
DESCRIPTOR.message_types_by_name['UserPostResponse'] = _USERPOSTRESPONSE
DESCRIPTOR.message_types_by_name['UserGetRequest'] = _USERGETREQUEST
DESCRIPTOR.message_types_by_name['UserGetResponse'] = _USERGETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

UserPostRequest = _reflection.GeneratedProtocolMessageType('UserPostRequest', (_message.Message,), {
  'DESCRIPTOR' : _USERPOSTREQUEST,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:UserPostRequest)
  })
_sym_db.RegisterMessage(UserPostRequest)

UserPostResponse = _reflection.GeneratedProtocolMessageType('UserPostResponse', (_message.Message,), {
  'DESCRIPTOR' : _USERPOSTRESPONSE,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:UserPostResponse)
  })
_sym_db.RegisterMessage(UserPostResponse)

UserGetRequest = _reflection.GeneratedProtocolMessageType('UserGetRequest', (_message.Message,), {
  'DESCRIPTOR' : _USERGETREQUEST,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:UserGetRequest)
  })
_sym_db.RegisterMessage(UserGetRequest)

UserGetResponse = _reflection.GeneratedProtocolMessageType('UserGetResponse', (_message.Message,), {
  'DESCRIPTOR' : _USERGETRESPONSE,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:UserGetResponse)
  })
_sym_db.RegisterMessage(UserGetResponse)



_USERSERVICE = _descriptor.ServiceDescriptor(
  name='UserService',
  full_name='UserService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=146,
  serialized_end=248,
  methods=[
  _descriptor.MethodDescriptor(
    name='append',
    full_name='UserService.append',
    index=0,
    containing_service=None,
    input_type=_USERPOSTREQUEST,
    output_type=_USERPOSTRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='get',
    full_name='UserService.get',
    index=1,
    containing_service=None,
    input_type=_USERGETREQUEST,
    output_type=_USERGETRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_USERSERVICE)

DESCRIPTOR.services_by_name['UserService'] = _USERSERVICE

# @@protoc_insertion_point(module_scope)
