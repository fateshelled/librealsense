# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2022 Intel Corporation. All Rights Reserved.

set(CONTROL_TOPIC_HEADER_FILES
   "${CMAKE_CURRENT_LIST_DIR}/controlPubSubTypes.h"
   "${CMAKE_CURRENT_LIST_DIR}/controlTypeObject.h"
   "${CMAKE_CURRENT_LIST_DIR}/control.h"
   "${CMAKE_CURRENT_LIST_DIR}/control-msg.h"
)
set(CONTROL_TOPIC_SOURCE_FILES
   "${CMAKE_CURRENT_LIST_DIR}/controlPubSubTypes.cpp"
   "${CMAKE_CURRENT_LIST_DIR}/controlTypeObject.cpp"
   "${CMAKE_CURRENT_LIST_DIR}/control.cpp"
)
set( CONTROL_TOPIC_FILES ${CONTROL_TOPIC_HEADER_FILES} )
