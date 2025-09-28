#ifndef PDF_PARSER_H
#define PDF_PARSER_H

#include <string>
#include <vector>
#include <memory>

class PDFParser {
public:
    PDFParser();
    ~PDFParser();
    
    bool parsePDF(const std::string& pdf_path, std::string& output_text);
    bool parseMultiplePDFs(const std::vector<std::string>& pdf_files, 
                          std::vector<std::pair<std::string, std::string>>& results);
    
private:
    bool tryPdftotext(const std::string& pdf_path, std::string& output_text);
    bool parseWithPoppler(const std::string& pdf_path, std::string& output_text);
    std::string extractTextFromPage(const void* page);
};

#endif