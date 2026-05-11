---
title: C++ 学习笔记（三）
date: 2026-05-11T20:49:24+08:00
lastmod: 2026-05-11T23:20:25+08:00
description: "cpp 的 static"
summary: "cpp 的 static"
tags: ["学习", "开发"]
categories: ["学习笔记"]
cover: images/space_robot.webp
---

重新读了一遍自己之前写的两篇 cpp 学习笔记，发现实在是有点难懂，因为很多都是照搬 cppreference 的内容，而cppreference 就像是一本新华字典，很权威，但是学起来困难且效率低下。所以为了避免这个问题，我打算以后还是多参考一些入门书籍来写，这样思路更清晰，并且读者也会更容易看懂。

C++ 的 static 关键字是**存储类说明符**之一，存储类说明符表示存储数据的方式，不同的 C++ 存储方式是通过**存储持续性**、**作用性**和**链接性**来描述的，所以我们先从这几个概念开始。

### 概念引入
* **存储持续性**
  
  C++ 使用四种不同的方案来存储数据，这些方案的区别就在于数据保留在内存中的**时间**。

  * **自动存储持续性**：在函数定义中声明的变量（包括函数参数）的存储持续性为自动的。它们在程序开始执行其所属的函数或代码块（代码块就是用花括号括起来的一系列语句，例如函数体就是代码块）时被创建；在执行完函数或代码块时，它们使用的内存被释放。
  * **静态存储持续性**：这就是本文的主角了。在函数定义外定义的变量和使用关键字 static 定义的变量的存储持续性都为静态，即它们在程序整个运行过程都存在。
  * **线程存储持续性**：目前来说课内用不到这个概念，可以自行了解。
  * **动态存储连续性**：用 new 运算符分配的内存将一直存在，直到使用 delete 运算符将其释放或程序结束为止。通过这种方式分配的内存被称为堆（heap）。

* **作用域**
  
  作用域（scope）描述了名称在文件的多大范围内**可见**。例如，函数中定义的变量可在该函数中使用，但不能在其他函数中使用；在文件中的函数定义之前定义的变量则可在所有函数中使用。
  
  * C++ ***变量*** 的作用域有多种：作用域为局部的变量只在定义它的代码块中可用；作用域为全局（也叫文件作用域）的变量在定义位置到文件结尾之间都可用。下面介绍一些常见变量名称的作用域：

    自动变量的作用域为局部，静态变量的作用域是全局还是局部取决于它是如何被定义的。在类中声明的成员的作用域为整个类。在命名空间中声明的变量的作用域为整个命名空间。

  * C++ ***函数*** 的作用域可以是整个类或者整个命名空间（包括全局的），但不能是局部的（如果是局部，那么就不能被其他函数调用，这样的函数将无法运行）。

* **链接性**

  链接性（linkage）描述了名称如何在不同单元（文件）中**共享**。链接性为外部的名称可在不同文件间共享，链接性为内部的名称只能由一个文件中的函数共享。自动变量的名称没有链接性，因为它们不能共享。
### 静态持续变量
C++ 为静态存储持续性变量提供了 3 种链接性：**外部链接性**（可在其他文件中访问）、**内部链接性**（只能在当前文件中访问）和**无链接性**（只能在当前函数或代码块中访问）。这 3 种变量在整个程序执行期间都存在，比自动变量的寿命更长。由于静态变量的数目在程序运行期间是不变的，编译器将分配固定的内存块来存储所有的静态变量（不是栈）。另外，如果没有显式地初始化静态变量，编译器将把它设置为 0。

那么我们该如何创建这 3 种静态持续变量呢？要想创建链接性为外部的静态持续变量，必须在代码块的外面声明它；要创建链接性为内部的静态持续变量，必须在代码块的外面声明它并使用 static 限定符；要创建没有链接性的静态持续变量，必须在代码块内声明它并使用 static 限定符。可以看下方的代码片段加深理解：
```cpp
int global = 100;         // 链接性为外部的静态持续变量（或者说是全局变量）
static int one_file = 50; // 链接性为内部的静态持续变量

void func(int n)
{
    static int count = 0; // 无链接性的静态持续变量
}
```
上述例子中，`global`、`one_file`和`count`在整个程序执行期间都存在。在`func()`中声明的变量`count`的作用域为局部，没有链接性，这意味着只能在`func()`函数中使用它。`global`和`one_file`的作用域为整个文件，即在从声明位置到文件结尾的范围内都可以使用。由于`one_file`的链接性为内部，因此只能在上述代码的文件中使用它；由于`global`的链接性为外部，因此可以在程序的其他文件中使用它（其他文件需使用 extern 关键字声明它才能使用）。

接下来介绍 C++ 的**单定义规则（One Definition）**，这对我们理解变量的声明和初始化有帮助。该规则指出，变量只能有一次定义。为满足这种需求，C++ 提供了两种变量声明。一种是定义声明（或者简称为“定义”），它给变量分配存储空间；另一种是引用声明（或者简称为“声明”，话说这种取名真的很容易混淆啊！），它不给变量分配存储空间，因为它引用已有的变量。引用声明使用关键字 extern，且不进行初始化；如果使用 extern 的同时进行了初始化，引用声明就变成定义，导致分配存储空间。注意，程序中可以包含多个同名的变量（例如局部变量隐藏全局变量），但是每个变量都**只有一个定义**！

举几个例子：
```cpp
// file01.cpp
int cats = 10;    // 定义
extern dogs = 20; // 依旧定义，因为有初始化
// file02.cpp
extern int cats;  // 引用
extern int dogs;  // 引用
```
```cpp
//file1
int errors = 20; 
//file2
int errors = 10;
void froobish()
{
    cout << errors; // 报错，因为这里 errors 定义了两次！
}
```
```cpp
//file1
int errors = 20;
//file2
static int errors = 10;
void froobish()
{
    cout << errors; // 成功，因为 static 指出 errors 的链接性为内部，因此并非要提供外部定义
}
```
下面再讲一下无链接性的静态局部变量。正如前文所说，只要将 static 用于在代码块中定义的变量，我们就能创建一个无链接性的静态局部变量了。这意味着虽然该变量只在该代码块中可用，但它在该代码块不处于活动状态时**仍然存在**。因此在两次函数调用之间，静态局部变量的值将保持不变。另外，如果初始化了静态局部变量，则程序只在启动时进行一次初始化。下面举个例子，正好可以了解一下`cin.get()`的用法。
```cpp
#include <iostream>

const int Size = 10;

void strcount(const char * str);

int main()
{
    using namespace std;
    char input[Size];          // Size 大小的缓冲区用于存储每一行输入
    char next;

    cout << "Enter a line:\n"; // 准备读取第一行
    cin.get(input, Size);      // cin.get() 一直读取输入存入 input 数组，直到读取了 Size-1 个字符或者到达行尾，并在末尾自动添加\0，换行符留在输入缓冲区中
    while (cin)                // 循环读取输入行，直到读取到空行导致 cin 为 false，循环终止。
    {
        do
        {
            cin.get(next);     // cin.get() 会读取单个字符（不会跳过任何字符，包括空格和换行符），并将其赋给 next
        } while (next != '\n'); // 使用循环来丢弃多余的字符
                              
        strcount(input);       // 记录当前输入行的字符数以及总共输入的字符数
        cout << "Enter next line (empty line to quit):\n";
        cin.get(input, Size);  // 继续读取下一行
    }
    cout << "Bye\n";
    return 0;
}

void strcount(const char * str)
{
    using namespace std;
    static int total = 0;     // 声明静态局部变量，用于记录总共读取的字符数
    int count = 0;            // 声明局部变量，用于记录当前行的字符数

    cout << "\"" << str <<"\" contains ";
    while (*str++) count++;
    total += count;
    cout << count << " characters\n";
    cout << total << " characters total\n";
}
```
下面是该程序的输出：
```
Enter a line:
thanks
"thanks" contains 6 characters
6 characters total
Enter next line (empty line to quit):
nice pant
"nice pant" contains 9 characters
15 characters total
Enter next line (empty line to quit):
parting is such sweet sorrow
"parting i" contains 9 characters
24 characters total
Enter next line (empty line to quit):

Bye
```
### 类的静态成员
首先我们来看看静态数据成员是如何声明和初始化的：
```cpp
// string.h
#include <iostream>
#ifndef STRING_H
#define STRING_H
class String
{
private:
    char * str;     // 指向字符串的指针
    int len;        // 字符串的长度
    static int num; // 对象的数量
public:
    String(const char * str);
    String();
    ~String();

    friend std::ostream & operator<<(std::ostream & os, const String & st);
}
#endif
// string.cpp
#include <cstring>
#include "string.h"
using std::cout;

int String::num = 0;

String::String(const char * str)
{
    len = std::strlen(s); 
    str = new char[len+1];
    std::strcpy(str, s);
    num++;
    cout << num << ":\"" << str
         << "\" object created\n";
}
...
```
请注意`int String::num = 0`这条语句，它将静态成员`num`的值初始化为0。我们不能在类声明中初始化静态成员变量（除了静态成员是 const 整数类型或枚举型的情况；事实上，从 C++17 起可以用`inline`关键字进行类内初始化），声明描述了如何分配内存，但并不分配内存。我们可以在类声明之外使用单独的语句来进行初始化，这是因为静态类成员是单独存储的，而不是对象的组成部分。请注意，初始化语句指出了类型，并使用了作用域运算符，但**没有**使用关键字 static！

初始化是在方法文件中，而不是在类声明文件中进行的（这个我们作业和考试碰到过很多次了），这是因为类声明位于头文件中，程序可能将头文件包括在其他几个文件中。如果在头文件中初始化了静态成员，那么将出现多个初始化语句副本，从而引发错误。

最后，C++11 起函数内的 static 局部变量是线程安全的，编译器保证只初始化一次。

下面介绍静态类成员函数：

可以将成员函数声明为静态的（函数声明必须包含关键字 static，但如果函数定义是独立的，则其中不能包含关键字 static，这个后续会举例子说明），这样做会有两个重要的后果：
* 不能通过对象调用静态成员函数；实际上，静态成员函数甚至不能使用 this 指针。如果静态成员函数是在公有部分声明的，则可以使用类名和作用域解析运算符来调用它。举个例子：
  ```cpp
  //string.h
  static int HowMany() { return num; }
  ```
  这是在类声明中内联定义静态成员函数。我们也可以在类的实现文件中定义该函数，注意，此时不能再用 static 修饰（这点和 explicit 相同）：
  ```cpp
  //string.h
  static int HowMany();                // 头文件中仅仅是声明
  //string.cpp
  int String::HowMany(){ return num; } // 在类外部定义
  ```
  调用它的方式如下：
  ```cpp
  int count = String::HowMany();
  ```
* 由于静态成员函数不与特定的对象相关联，因此只能使用静态数据成员。例如，静态方法`HowMany()`可以访问静态成员`num`，但不能访问`str`和`len`。



