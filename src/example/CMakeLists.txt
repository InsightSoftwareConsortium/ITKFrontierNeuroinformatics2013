cmake_minimum_required( VERSION 2.8 )

project( Registration )

find_package( ITK REQUIRED COMPONENTS SkullStrip ITKIOMINC )
include( ${ITK_USE_FILE} )

add_executable( StripSkull StripSkull.cxx )
target_link_libraries( StripSkull ${ITK_LIBRARIES} )
