#include "pdf_parser.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <filesystem>
#include <algorithm>
#include <chrono>

int main(int argc, char* argv[]) {
    std::cout << "PDF Parser C++ - Single File Mode" << std::endl;
    std::cout << "=================================" << std::endl;
    
    std::string input_pdf = "input.pdf";
    std::string output_txt = "output.txt";
    
    // Проверяем существование входного файла
    if (!std::filesystem::exists(input_pdf)) {
        std::cerr << "ОШИБКА: Файл " << input_pdf << " не найден!" << std::endl;
        std::cerr << "Текущая директория: " << std::filesystem::current_path() << std::endl;
        return 1;
    }
    
    std::cout << "Входной файл: " << input_pdf << std::endl;
    std::cout << "Выходной файл: " << output_txt << std::endl;
    
    PDFParser parser;
    std::string extracted_text;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Парсим файл
    if (parser.parsePDF(input_pdf, extracted_text)) {
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        std::cout << "PDF успешно обработан за " << duration.count() << " мс" << std::endl;
        
        // Сохраняем результат в output.txt
        std::ofstream out_file(output_txt);
        if (out_file.is_open()) {
            out_file << extracted_text;
            out_file.close();
            std::cout << "Готово! Результат записан в: " << output_txt << std::endl;
            
            // Показываем статистику
            size_t char_count = extracted_text.length();
            size_t line_count = std::count(extracted_text.begin(), extracted_text.end(), '\n');
            std::cout << "Статистика: " << char_count << " символов, " << line_count << " строк" << std::endl;
            
        } else {
            std::cerr << "Ошибка сохранения в файл: " << output_txt << std::endl;
            return 1;
        }
    } else {
        std::cerr << "Не удалось обработать файл: " << input_pdf << std::endl;
        return 1;
    }
    // Очистка от лишних символов
    extracted_text.erase(std::remove(extracted_text.begin(), extracted_text.end(), '\r'), extracted_text.end());
    extracted_text.erase(std::remove(extracted_text.begin(), extracted_text.end(), '\0'), extracted_text.end());

    // Удаление лишних пустых строк в конце
    while (!extracted_text.empty() && (extracted_text.back() == '\n' || extracted_text.back() == ' ')) {
        extracted_text.pop_back();
    }
    
    return 0;
}