#include <iostream>
#include <vector>
#include "engine.h"

int main() {
    std::cout << "Starting High Performance Engine..." << std::endl;
    Engine engine("CoreV8", 100);

    std::vector<int> sampleData = {10, 20, 30, 40, 50};
    int result = engine.processBuffer(sampleData);

    std::cout << "Processing Result: " << result << std::endl;
    std::cout << engine.getStatus() << std::endl;
    return 0;
}
