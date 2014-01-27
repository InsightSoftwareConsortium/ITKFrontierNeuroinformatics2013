cmake_minimum_required( VERSION 2.8 )

project( Registration )

find_package( ITK REQUIRED COMPONENTS SkullStrip ITKIOMINC )
include( ${ITK_USE_FILE} )

add_executable( Registration Registration.cxx )
target_link_libraries( Registration ${ITK_LIBRARIES} )
