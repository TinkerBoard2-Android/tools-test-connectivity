# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: bluetooth_metric.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='bluetooth_metric.proto',
  package='wireless.android.platform.testing.bluetooth.metrics',
  syntax='proto2',
  serialized_pb=_b('\n\x16\x62luetooth_metric.proto\x12\x33wireless.android.platform.testing.bluetooth.metrics\"\xe8\x01\n\x13\x42luetoothTestDevice\x12\x14\n\x0c\x64\x65vice_class\x18\x01 \x01(\t\x12\x14\n\x0c\x64\x65vice_model\x18\x02 \x01(\t\x12\x18\n\x10hardware_version\x18\x03 \x01(\t\x12\x18\n\x10software_version\x18\x04 \x01(\t\x12\x1a\n\x12\x61ndroid_build_type\x18\x05 \x01(\t\x12\x1b\n\x13\x61ndroid_branch_name\x18\x06 \x01(\t\x12\x1c\n\x14\x61ndroid_build_number\x18\x07 \x01(\t\x12\x1a\n\x12\x61ndroid_release_id\x18\x08 \x01(\t\"\x83\x02\n#BluetoothContinuousTestResultHeader\x12\x16\n\x0etest_date_time\x18\x01 \x01(\x03\x12`\n\x0eprimary_device\x18\x02 \x01(\x0b\x32H.wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice\x12\x62\n\x10\x63onnected_device\x18\x03 \x01(\x0b\x32H.wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice\"\xe0\x03\n\x1c\x42luetoothReconnectTestResult\x12t\n\x12\x63onfiguration_data\x18\x01 \x01(\x0b\x32X.wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader\x12 \n\x18\x63onnection_attempt_count\x18\x02 \x01(\x05\x12#\n\x1b\x63onnection_successful_count\x18\x03 \x01(\x05\x12\x1f\n\x17\x63onnection_failed_count\x18\x04 \x01(\x05\x12\"\n\x1a\x63onnection_max_time_millis\x18\x05 \x01(\x05\x12\"\n\x1a\x63onnection_min_time_millis\x18\x06 \x01(\x05\x12\"\n\x1a\x63onnection_avg_time_millis\x18\x07 \x01(\x05\x12&\n\x1e\x61\x63l_connection_max_time_millis\x18\x08 \x01(\x05\x12&\n\x1e\x61\x63l_connection_min_time_millis\x18\t \x01(\x05\x12&\n\x1e\x61\x63l_connection_avg_time_millis\x18\n \x01(\x05\"\xc7\x03\n!BluetoothPairAndConnectTestResult\x12t\n\x12\x63onfiguration_data\x18\x01 \x01(\x0b\x32X.wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader\x12\x1a\n\x12pair_attempt_count\x18\x02 \x01(\x05\x12\x1d\n\x15pair_successful_count\x18\x03 \x01(\x05\x12\x19\n\x11pair_failed_count\x18\x04 \x01(\x05\x12\x1c\n\x14pair_max_time_millis\x18\x05 \x01(\x05\x12\x1c\n\x14pair_min_time_millis\x18\x06 \x01(\x05\x12\x1c\n\x14pair_avg_time_millis\x18\x07 \x01(\x05\x12(\n first_connection_max_time_millis\x18\x08 \x01(\x05\x12(\n first_connection_min_time_millis\x18\t \x01(\x05\x12(\n first_connection_avg_time_millis\x18\n \x01(\x05\"\xae\x04\n\x18\x42luetoothAudioTestResult\x12t\n\x12\x63onfiguration_data\x18\x01 \x01(\x0b\x32X.wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader\x12q\n\raudio_profile\x18\x02 \x01(\x0e\x32Z.wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.AudioProfile\x12 \n\x18\x61udio_latency_min_millis\x18\x03 \x01(\x05\x12 \n\x18\x61udio_latency_max_millis\x18\x04 \x01(\x05\x12 \n\x18\x61udio_latency_avg_millis\x18\x05 \x01(\x05\x12\x1c\n\x14\x61udio_glitches_count\x18\x06 \x01(\x05\x12\"\n\x1a\x61udio_missed_packets_count\x18\x07 \x01(\x05\x12,\n$total_harmonic_distortion_plus_noise\x18\x08 \x01(\x02\x12\'\n\x1f\x61udio_streaming_duration_millis\x18\t \x01(\x03\"*\n\x0c\x41udioProfile\x12\x08\n\x04\x41\x32\x44P\x10\x00\x12\x07\n\x03HFP\x10\x01\x12\x07\n\x03HAP\x10\x02\"\xd5\x04\n\x17\x42luetoothDataTestResult\x12t\n\x12\x63onfiguration_data\x18\x01 \x01(\x0b\x32X.wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader\x12\x81\x01\n\x16\x64\x61ta_transfer_protocol\x18\x02 \x01(\x0e\x32\x61.wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.DataTransferProtocol\x12\x1f\n\x17\x64\x61ta_latency_min_millis\x18\x03 \x01(\x05\x12\x1f\n\x17\x64\x61ta_latency_max_millis\x18\x04 \x01(\x05\x12\x1f\n\x17\x64\x61ta_latency_avg_millis\x18\x05 \x01(\x05\x12,\n$data_throughput_min_bytes_per_second\x18\x06 \x01(\x05\x12,\n$data_throughput_max_bytes_per_second\x18\x07 \x01(\x05\x12,\n$data_throughput_avg_bytes_per_second\x18\x08 \x01(\x05\x12\x18\n\x10\x64\x61ta_packet_size\x18\t \x01(\x05\"9\n\x14\x44\x61taTransferProtocol\x12\n\n\x06RFCOMM\x10\x00\x12\t\n\x05L2CAP\x10\x01\x12\n\n\x06LE_COC\x10\x02')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_BLUETOOTHAUDIOTESTRESULT_AUDIOPROFILE = _descriptor.EnumDescriptor(
  name='AudioProfile',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.AudioProfile',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='A2DP', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HFP', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HAP', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=2034,
  serialized_end=2076,
)
_sym_db.RegisterEnumDescriptor(_BLUETOOTHAUDIOTESTRESULT_AUDIOPROFILE)

_BLUETOOTHDATATESTRESULT_DATATRANSFERPROTOCOL = _descriptor.EnumDescriptor(
  name='DataTransferProtocol',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.DataTransferProtocol',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='RFCOMM', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='L2CAP', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LE_COC', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=2619,
  serialized_end=2676,
)
_sym_db.RegisterEnumDescriptor(_BLUETOOTHDATATESTRESULT_DATATRANSFERPROTOCOL)


_BLUETOOTHTESTDEVICE = _descriptor.Descriptor(
  name='BluetoothTestDevice',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='device_class', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.device_class', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='device_model', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.device_model', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hardware_version', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.hardware_version', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='software_version', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.software_version', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='android_build_type', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.android_build_type', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='android_branch_name', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.android_branch_name', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='android_build_number', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.android_build_number', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='android_release_id', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice.android_release_id', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=80,
  serialized_end=312,
)


_BLUETOOTHCONTINUOUSTESTRESULTHEADER = _descriptor.Descriptor(
  name='BluetoothContinuousTestResultHeader',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='test_date_time', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader.test_date_time', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='primary_device', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader.primary_device', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connected_device', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader.connected_device', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=315,
  serialized_end=574,
)


_BLUETOOTHRECONNECTTESTRESULT = _descriptor.Descriptor(
  name='BluetoothReconnectTestResult',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='configuration_data', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.configuration_data', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connection_attempt_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.connection_attempt_count', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connection_successful_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.connection_successful_count', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connection_failed_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.connection_failed_count', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connection_max_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.connection_max_time_millis', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connection_min_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.connection_min_time_millis', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='connection_avg_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.connection_avg_time_millis', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='acl_connection_max_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.acl_connection_max_time_millis', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='acl_connection_min_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.acl_connection_min_time_millis', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='acl_connection_avg_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult.acl_connection_avg_time_millis', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=577,
  serialized_end=1057,
)


_BLUETOOTHPAIRANDCONNECTTESTRESULT = _descriptor.Descriptor(
  name='BluetoothPairAndConnectTestResult',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='configuration_data', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.configuration_data', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_attempt_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.pair_attempt_count', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_successful_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.pair_successful_count', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_failed_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.pair_failed_count', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_max_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.pair_max_time_millis', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_min_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.pair_min_time_millis', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_avg_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.pair_avg_time_millis', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='first_connection_max_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.first_connection_max_time_millis', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='first_connection_min_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.first_connection_min_time_millis', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='first_connection_avg_time_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult.first_connection_avg_time_millis', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1060,
  serialized_end=1515,
)


_BLUETOOTHAUDIOTESTRESULT = _descriptor.Descriptor(
  name='BluetoothAudioTestResult',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='configuration_data', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.configuration_data', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_profile', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_profile', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_latency_min_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_latency_min_millis', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_latency_max_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_latency_max_millis', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_latency_avg_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_latency_avg_millis', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_glitches_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_glitches_count', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_missed_packets_count', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_missed_packets_count', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='total_harmonic_distortion_plus_noise', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.total_harmonic_distortion_plus_noise', index=7,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_streaming_duration_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult.audio_streaming_duration_millis', index=8,
      number=9, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _BLUETOOTHAUDIOTESTRESULT_AUDIOPROFILE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1518,
  serialized_end=2076,
)


_BLUETOOTHDATATESTRESULT = _descriptor.Descriptor(
  name='BluetoothDataTestResult',
  full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='configuration_data', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.configuration_data', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_transfer_protocol', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_transfer_protocol', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_latency_min_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_latency_min_millis', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_latency_max_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_latency_max_millis', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_latency_avg_millis', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_latency_avg_millis', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_throughput_min_bytes_per_second', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_throughput_min_bytes_per_second', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_throughput_max_bytes_per_second', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_throughput_max_bytes_per_second', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_throughput_avg_bytes_per_second', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_throughput_avg_bytes_per_second', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_packet_size', full_name='wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult.data_packet_size', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _BLUETOOTHDATATESTRESULT_DATATRANSFERPROTOCOL,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2079,
  serialized_end=2676,
)

_BLUETOOTHCONTINUOUSTESTRESULTHEADER.fields_by_name['primary_device'].message_type = _BLUETOOTHTESTDEVICE
_BLUETOOTHCONTINUOUSTESTRESULTHEADER.fields_by_name['connected_device'].message_type = _BLUETOOTHTESTDEVICE
_BLUETOOTHRECONNECTTESTRESULT.fields_by_name['configuration_data'].message_type = _BLUETOOTHCONTINUOUSTESTRESULTHEADER
_BLUETOOTHPAIRANDCONNECTTESTRESULT.fields_by_name['configuration_data'].message_type = _BLUETOOTHCONTINUOUSTESTRESULTHEADER
_BLUETOOTHAUDIOTESTRESULT.fields_by_name['configuration_data'].message_type = _BLUETOOTHCONTINUOUSTESTRESULTHEADER
_BLUETOOTHAUDIOTESTRESULT.fields_by_name['audio_profile'].enum_type = _BLUETOOTHAUDIOTESTRESULT_AUDIOPROFILE
_BLUETOOTHAUDIOTESTRESULT_AUDIOPROFILE.containing_type = _BLUETOOTHAUDIOTESTRESULT
_BLUETOOTHDATATESTRESULT.fields_by_name['configuration_data'].message_type = _BLUETOOTHCONTINUOUSTESTRESULTHEADER
_BLUETOOTHDATATESTRESULT.fields_by_name['data_transfer_protocol'].enum_type = _BLUETOOTHDATATESTRESULT_DATATRANSFERPROTOCOL
_BLUETOOTHDATATESTRESULT_DATATRANSFERPROTOCOL.containing_type = _BLUETOOTHDATATESTRESULT
DESCRIPTOR.message_types_by_name['BluetoothTestDevice'] = _BLUETOOTHTESTDEVICE
DESCRIPTOR.message_types_by_name['BluetoothContinuousTestResultHeader'] = _BLUETOOTHCONTINUOUSTESTRESULTHEADER
DESCRIPTOR.message_types_by_name['BluetoothReconnectTestResult'] = _BLUETOOTHRECONNECTTESTRESULT
DESCRIPTOR.message_types_by_name['BluetoothPairAndConnectTestResult'] = _BLUETOOTHPAIRANDCONNECTTESTRESULT
DESCRIPTOR.message_types_by_name['BluetoothAudioTestResult'] = _BLUETOOTHAUDIOTESTRESULT
DESCRIPTOR.message_types_by_name['BluetoothDataTestResult'] = _BLUETOOTHDATATESTRESULT

BluetoothTestDevice = _reflection.GeneratedProtocolMessageType('BluetoothTestDevice', (_message.Message,), dict(
  DESCRIPTOR = _BLUETOOTHTESTDEVICE,
  __module__ = 'bluetooth_metric_pb2'
  # @@protoc_insertion_point(class_scope:wireless.android.platform.testing.bluetooth.metrics.BluetoothTestDevice)
  ))
_sym_db.RegisterMessage(BluetoothTestDevice)

BluetoothContinuousTestResultHeader = _reflection.GeneratedProtocolMessageType('BluetoothContinuousTestResultHeader', (_message.Message,), dict(
  DESCRIPTOR = _BLUETOOTHCONTINUOUSTESTRESULTHEADER,
  __module__ = 'bluetooth_metric_pb2'
  # @@protoc_insertion_point(class_scope:wireless.android.platform.testing.bluetooth.metrics.BluetoothContinuousTestResultHeader)
  ))
_sym_db.RegisterMessage(BluetoothContinuousTestResultHeader)

BluetoothReconnectTestResult = _reflection.GeneratedProtocolMessageType('BluetoothReconnectTestResult', (_message.Message,), dict(
  DESCRIPTOR = _BLUETOOTHRECONNECTTESTRESULT,
  __module__ = 'bluetooth_metric_pb2'
  # @@protoc_insertion_point(class_scope:wireless.android.platform.testing.bluetooth.metrics.BluetoothReconnectTestResult)
  ))
_sym_db.RegisterMessage(BluetoothReconnectTestResult)

BluetoothPairAndConnectTestResult = _reflection.GeneratedProtocolMessageType('BluetoothPairAndConnectTestResult', (_message.Message,), dict(
  DESCRIPTOR = _BLUETOOTHPAIRANDCONNECTTESTRESULT,
  __module__ = 'bluetooth_metric_pb2'
  # @@protoc_insertion_point(class_scope:wireless.android.platform.testing.bluetooth.metrics.BluetoothPairAndConnectTestResult)
  ))
_sym_db.RegisterMessage(BluetoothPairAndConnectTestResult)

BluetoothAudioTestResult = _reflection.GeneratedProtocolMessageType('BluetoothAudioTestResult', (_message.Message,), dict(
  DESCRIPTOR = _BLUETOOTHAUDIOTESTRESULT,
  __module__ = 'bluetooth_metric_pb2'
  # @@protoc_insertion_point(class_scope:wireless.android.platform.testing.bluetooth.metrics.BluetoothAudioTestResult)
  ))
_sym_db.RegisterMessage(BluetoothAudioTestResult)

BluetoothDataTestResult = _reflection.GeneratedProtocolMessageType('BluetoothDataTestResult', (_message.Message,), dict(
  DESCRIPTOR = _BLUETOOTHDATATESTRESULT,
  __module__ = 'bluetooth_metric_pb2'
  # @@protoc_insertion_point(class_scope:wireless.android.platform.testing.bluetooth.metrics.BluetoothDataTestResult)
  ))
_sym_db.RegisterMessage(BluetoothDataTestResult)


# @@protoc_insertion_point(module_scope)
