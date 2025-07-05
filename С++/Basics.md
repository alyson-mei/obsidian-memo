## 2.1 
	#include <iostream>
	int main() {
	}

	std::cout << "abc\n"
	std::cin >> a

	#include <string>
	...
	int value;
	std::string name, surname;
	...

	std::string name;
	std::cin >> name; //до разделителя
	std::getline(std::cin, name) //полностью

	std::cin >> a >> b >> c;
## 2.2
Область видимости

	int x = 1
	std::count << x << "\n";    //1
	{
		int x = 2;                   
		std::cout << x << "\n";  //2
	}
	std::cout << x << "\n";	//1
}
Инициализация
Типы данных

	short int si = 17;
	long li
	long long lli
	double d
	long double 1d = 1e15;

	std::cout << "char: " << sizeof(char) << "\n"

signed: $-2^{n-1}$..$2^{n-1}-1$ 
unsigned: $2^{n}-1$ 

	unsigned int ui = 4294967295; //2^(4*8) - 1

	#include <limits>
	...
	std::cout << "min" << std::numeric_limits<int>::min() << "\n"

Неопределённое поведение

Арифметические операции

	a / b;
	a % b;
	static_cast<double>(a) / b;

	char c = 'A';
	c += 25;
	std::cout <<c << "\n"; //Z

	"a" + "b";
	x += 3;
	x *= x;
	++x;
	--x;

IEEE 754: 1 бит знак, 8 бит порядок, 23 бита мантисса
0.15625 = $1.01_2 \cdot 2^{-3}$
Экспонента (смещение 127): -3 + 127 = 124
Мантисса: берём дробную часть числа (без ведущей 1)

	0 | 011111000 | 010..00

Автоматический вывод типа

## 2.3
	while (n <= 10) {
	        std::cout << n << "\t" << n * n << "\n";
	        ++n;
	    }

	for (int i = 1; i <= 10; ++i) {
        std::cout << i << "\t" << i * i << "\n";
    }

	int main() {
	    std::string line;
	    std::getline(std::cin, line);
	    for (char symbol : line) {
	        std::cout << symbol << "\t" << static_cast<int>(symbol) << "\n";
	    }
	}


	#include <iostream> int main() { 
		int sum = 0; int x; 
		while (std::cin >> x) { 
			sum += x; 
		} 
		std::cout << sum << "\n"; 
	}


	#include <iostream> 
	#include <string> 
	int main() { 
		std::string name; 
		while (std::getline(std::cin, name)) 
		{ 
			std::cout << "Hello, " << name << "!\n"; 
		} 
	}