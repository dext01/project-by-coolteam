cmake_minimum_required(VERSION 3.10)
project(PDFParser)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Поиск необходимых библиотек
find_package(PkgConfig REQUIRED)

pkg_check_modules(POPPLER_CPP REQUIRED poppler-cpp)
pkg_check_modules(TESSERACT REQUIRED tesseract)
pkg_check_modules(LEPTONICA REQUIRED lept)
find_package(OpenCV REQUIRED)

# Добавление исполняемого файла
add_executable(pdf_parser 
    main.cpp 
    pdf_parser.cpp
)

# Подключение библиотек
target_include_directories(pdf_parser PRIVATE
    ${POPPLER_CPP_INCLUDE_DIRS}
    ${TESSERACT_INCLUDE_DIRS}
    ${LEPTONICA_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
)

target_link_libraries(pdf_parser
    ${POPPLER_CPP_LIBRARIES}
    ${TESSERACT_LIBRARIES}
    ${LEPTONICA_LIBRARIES}
    ${OpenCV_LIBRARIES}
    stdc++fs  # Добавьте эту строку для поддержки filesystem
)

target_compile_options(pdf_parser PRIVATE ${POPPLER_CPP_CFLAGS_OTHER})