#include "pdf_parser.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <cstdlib>
#include <algorithm>
#include <filesystem>

PDFParser::PDFParser() {
}

PDFParser::~PDFParser() {
}

bool PDFParser::parsePDF(const std::string& pdf_path, std::string& output_text) {
    std::cout << "Пытаемся извлечь текст из PDF..." << std::endl;
    
    // Сначала пробуем pdftotext
    if (tryPdftotext(pdf_path, output_text)) {
        return true;
    }
    
    // Если pdftotext не сработал, используем Poppler
    std::cout << "pdftotext не сработал, используем Poppler..." << std::endl;
    return parseWithPoppler(pdf_path, output_text);
}

bool PDFParser::tryPdftotext(const std::string& pdf_path, std::string& output_text) {
    // Создаем временный файл с уникальным именем
    std::string temp_file = "/tmp/pdf_temp_" + std::to_string(std::time(nullptr)) + ".txt";
    
    // Команда для pdftotext
    std::string command = "pdftotext -enc UTF-8 \"" + pdf_path + "\" \"" + temp_file + "\"";
    std::cout << "Пробуем: " << command << std::endl;
    
    int result = system(command.c_str());
    if (result == 0 && std::filesystem::exists(temp_file)) {
        // Читаем результат из временного файла
        std::ifstream in_file(temp_file);
        if (in_file.is_open()) {
            std::stringstream buffer;
            buffer << in_file.rdbuf();
            output_text = buffer.str();
            in_file.close();
            
            // Удаляем временный файл
            std::filesystem::remove(temp_file);
            
            if (!output_text.empty()) {
                std::cout << "pdftotext успешно извлек " << output_text.length() << " символов" << std::endl;
                return true;
            }
        }
    }
    
    // Удаляем временный файл если он создался
    if (std::filesystem::exists(temp_file)) {
        std::filesystem::remove(temp_file);
    }
    
    return false;
}

bool PDFParser::parseWithPoppler(const std::string& pdf_path, std::string& output_text) {
    // Упрощенная версия без Poppler
    std::cout << "Poppler метод пока не реализован" << std::endl;
    return false;
}

std::string PDFParser::extractTextFromPage(const void* page) {
    // Заглушка
    return "";
}

bool PDFParser::parseMultiplePDFs(const std::vector<std::string>& pdf_files, 
                                 std::vector<std::pair<std::string, std::string>>& results) {
    results.clear();
    
    for (const auto& pdf_file : pdf_files) {
        std::cout << "Обработка: " << pdf_file << std::endl;
        
        std::string text;
        if (parsePDF(pdf_file, text)) {
            results.emplace_back(pdf_file, text);
        } else {
            results.emplace_back(pdf_file, "ОШИБКА: Не удалось обработать файл");
        }
    }
    
    return !results.empty();
}