#pragma once
#include <vector>
#include <string>

class Engine {
private:
    std::string name;
    int maxCapacity;
    int* cacheBuffer;

public:
    Engine(const std::string& engineName, int capacity);
    ~Engine();

    int processBuffer(const std::vector<int>& data);
    std::string getStatus() const;
};
