---
title: C++ 学习笔记（一）
date: 2026-05-06T12:06:32+08:00
lastmod:  2026-05-06T13:42:02+08:00
description: cpp 的引用
tags: 学习 开发
categories: 学习笔记
cover: images/smiling_coffee.webp
---

本文参考 cppreference 以及 Gemini 网页版生成的回答。
### 引用

* 概念
  声明一个命名变量为引用，即一个已存在的对象或函数的别名。使用时类似变量，作为参数时能传递引用。

  **引用不是对象**，它们可以不占用存储，尽管编译器可能会在必要时分配存储空间以实现所需语义（比如引用类型的非静态数据成员通常会使类的大小增加存储内存地址所需的量）。

  * 不存在引用的数组
  * 不存在指向引用的指针
  * 不存在引用的引用
  * cpp不存在引用为空的概念，即引用必须被定义

* 引用折叠
  
  允许通过模板或`typedef`中的类型操作形成对引用的引用，这种情况下，右值引用到右值引用折叠为右值引用，其他组合形成左值引用。
  ```cpp
  typedef int&  lref;
  typedef int&& rref;
  int n;
 
  lref&  r1 = n; // type of r1 is int&
  lref&& r2 = n; // type of r2 is int&
  rref&  r3 = n; // type of r3 is int&
  rref&& r4 = 1; // type of r4 is int&&
  ```

* 左值引用
  
  左值引用声明为`S& D`，用于别名现有对象。
  ```cpp
  #include <iostream>
  #include <string>
 
  int main()
  {
      std::string s = "Ex";
      std::string& r1 = s;
      const std::string& r2 = s;
 
      r1 += "ample";           // modifies s
  //  r2 += "!";               // error: cannot modify through reference to const
      std::cout << r2 << '\n'; // prints s, which now holds "Example"
  }
  ```
* 右值引用
  
  右值引用声明为`S&& D`(涉及到所有权的转移，即`move`),可用于延长临时对象的生命周期（指向`const`的左值引用也能延长临时对象的生命周期，但不能通过它们进行修改）。
  ```cpp
  #include <iostream>
  #include <string>
 
  int main()
  {
      std::string s1 = "Test";
  //  std::string&& r1 = s1;           // error: can't bind to lvalue
 
      const std::string& r2 = s1 + s1; // okay: lvalue reference to const extends lifetime
  //  r2 += "Test";                    // error: can't modify through reference to const
 
      std::string&& r3 = s1 + s1;      // okay: rvalue reference extends lifetime
      r3 += "Test";                    // okay: can modify through reference to non-const
      std::cout << r3 << '\n';
  }
  ```

* 转发引用
  
  也被称为“万能引用”，它允许一个函数参数既能接受左值，也能接受右值，并通过完美转发保留其原始的属性。它声明为`T&& D`，看起来和右值引用一样，但是它必须发生在类型推导（Type Deduction）的语境中。之所以万能，可以参见前文提到的引用折叠规则。

  特征：
  * 必须是模板参数：`template <typename T> void func(T&& param);`
  * 或者使用`auto`：`auto&& x= ...;`
  * 不能有`const`或`volatile`修饰：必须是纯粹的`T&&`。
  
  即便有了转发引用，但是在函数体内部，命名的参数永远是左值。为了保留其原始属性，我们需要使用`std::forward<T>(arg)`，将参数还原为它原始的左值或右值属性。
  ```cpp
  #include <iostream>
  #include <utility>

  void process(int& x) { std::cout << "处理左值\n"; }
  void process(int&& x) { std::cout << "处理右值\n"; }

  template <typename T>
  void logAndProcess(T&& param) {
      std::cout << "记录日志... ";
      // 使用 std::forward 完美转发
      process(std::forward<T>(param));
  }

  int main() {
      int a = 10;
      logAndProcess(a);    // 输出：记录日志... 处理左值
      logAndProcess(20);   // 输出：记录日志... 处理右值
  }
  ```
* stl容器的引用
  
  这部分就以`vector`容器为例。先看代码：
  ```cpp
  template <typename T>
  void perfect(T&& param);          // 转发引用

  template <typename T>
  void strictlyRvalue(std::vector<T>&& param); // 右值引用

  int main() {
      std::vector<int> v = {1, 2, 3};

      perfect(v);            // ✅ 成功！T 推导为 std::vector<int>&，折叠后 param 是左值引用
    
      // strictlyRvalue(v);  // ❌ 报错！
                             // 编译器说：我需要一个右值引用（vector<T>&&），
                             // 但你给了我一个左值（v）。
    
      strictlyRvalue(std::move(v)); // ✅ 成功！必须手动转为右值
  }  
  ```
  在`std::vector<T>&& param`中，`&&`修饰的是`std::vector<T>`这个整体，而不是直接修饰模板参数`T`，这个整体的形状已经固定了，即右值引用。当传给右值引用一个左值时，编译器会报错，这是为了防止无意中破坏了原本不该移动的数据。

* 悬空引用

  引用在初始化时总是引用有效的对象或函数，但在程序运行过程中可能被引用对象的生命周期结束，但引用仍然可访问（悬空）。
  ```cpp
  std::string& f()
  {
      std::string s = "Example";
      return s; // exits the scope of s:
                // its destructor is called and its storage deallocated
  }
 
  std::string& r = f(); // dangling reference
  std::cout << r;       // undefined behavior: reads from a dangling reference
  std::string s = f();  // undefined behavior: copy-initializes from a dangling reference
  ```
* 有关引用的初始化和绑定

  引用的初始化逻辑是在编译阶段确定的，但真正的绑定动作是在程序运行阶段执行的。只有一种情况可以看作是编译阶段完成的：全局/静态变量的常量引用。
  ```cpp
  int g_val = 100;
   int &g_ref = g_val; // 全局引用
  ```
  编译器在生成可执行文件时，就已经在数据段（Data Segment）中把`g_ref`指向了`g_val`的地址。虽然严格来说这也属于“静态初始化”阶段（程序启动时），但从逻辑上讲，它在程序还没开始跑 main 之前就已经确定了。
  
  编译器在处理代码时，并不分配真正的内存地址，它做的是逻辑映射。

    - 编译器检查在定义引用的同时是否进行了初始化，如果没有就会报错。

    - 编译器记录这个引用名是哪个变量名的别名（符号表映射）。

    - 编译器生成底层机器指令，通常被实现为指向目标的常量指针（`Type* const ptr`）。编译器生成的指令逻辑是：“以后凡是看到`ref`，就去访问它所绑定的那个地址”。

  当函数运行时，程序在栈上为局部变量开辟空间。

    - 如果是局部引用，程序运行到定义引用的那一行时，会将目标变量的内存地址存入引用（底层指针）所在的内存空间。

    - 如果绑定的是右值（如 const int &a = 10;），运行时会在栈上创建一个临时变量存放 10，然后让 a 指向它。