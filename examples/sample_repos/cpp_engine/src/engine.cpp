#include "engine.h"
#include <iostream>
#include <numeric>

Engine::Engine(const std::string& engineName, int capacity)
    : name(engineName), maxCapacity(capacity) {
    cacheBuffer = new int[capacity];
}

Engine::~Engine() {
    // BUG 1: Memory leak - forgot delete[] cacheBuffer!
}

int Engine::processBuffer(const std::vector<int>& data) {
    // BUG 2: Loop condition i <= data.size() causes out-of-bounds access and buffer overflow!
    for (size_t i = 0; i <= data.size(); ++i) {
        if (i < maxCapacity) {
            cacheBuffer[i] = data[i] * 2;
        }
    }
    
    int total = 0;
    for (size_t i = 0; i < data.size(); ++i) {
        total += cacheBuffer[i];
    }
    return total;
}

std::string Engine::getStatus() const {
    return "Engine [" + name + "] operational.";
}
