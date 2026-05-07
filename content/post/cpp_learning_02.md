---
title: C++ 学习笔记（二）
date: 2026-05-07T12:34:48+08:00
lastmod: 2026-05-07T23:11:40+08:00
description: "左值&右值"
summary: "左值&右值"
tags: ["学习", "开发"]
categories: ["学习笔记"]
cover: images/smiling_maple.webp
---

**本文参考 cppreference，节选了一些目前对我来说比较重要的部分，并加入了一点自己的思考。如果想了解更全面的有关值类别的知识，直接去看 cppreference 就行！**

每个 C++ **表达式**（运算符及其操作数、字面量、变量名等）都由两个独立的属性来描述：一个**类型**和一个**值类别**。每个表达式都精确地属于三种主要值类别之一：**prvalue（纯右值）**、**xvalue（亡值）** 和 **lvalue（左值）**。

在介绍三个概念之前，需要引入 **glvalue（广义左值）** 的概念。它是左值和亡值的并集，或者说左值和亡值是它的一个划分。如果说一个表达式是广义左值，等价于它求值确定了一个对象或函数的身份，或者说它返回的东西是有地址的。C++ 规定左值是可以取地址的，但是亡值不能取地址（这点和纯右值一样）。这也是为什么我们说右值**不能取地址**，而不是说右值没有地址。
* 一个 **prvalue** 是一个表达式，其为计算内置运算符操作数的值（没有结果对象），或者初始化一个对象（有结果对象）；
* 一个 **xvalue** 表示一个其资源可以被重用的对象；
* 一个 **lvalue** 是一个不是 xvalue 的 glvalue。
  
### 左值&右值的命名来源
左值可以出现在赋值表达式的左侧，右值可以出现在赋值表达式的右侧。尽管名称是“值”，但是这些术语是用来分类表达式的。请看下方代码：
```cpp
void foo();
 
void baz()
{
    int a; // Expression `a` is lvalue
    a = 4; // OK, could appear on the left-hand side of an assignment expression
 
    int &b{a}; // Expression `b` is lvalue
    b = 5; // OK, could appear on the left-hand side of an assignment expression
 
    const int &c{a}; // Expression `c` is lvalue
    c = 6;           // ill-formed, assignment of read-only reference
 
    // Expression `foo` is lvalue
    // address may be taken by built-in address-of operator
    void (*p)() = &foo;
 
    foo = baz; // ill-formed, assignment of function
}
```
```cpp
#include <iostream>
 
struct S
{
    S() : m{42} {}
    S(int a) : m{a} {}
    int m;
};
 
int main()
{
    S s;
 
    // Expression `S{}` is prvalue
    // May appear on the right-hand side of an assignment expression
    s = S{};
 
    std::cout << s.m << '\n';
 
    // Expression `S{}` is prvalue
    // Can be used on the left-hand side too
    std::cout << (S{} = S{7}).m << '\n';
}
```
我想我得解释一下`(S{} = S{7}).m`这个表达式。`S{}`、`S{7}`都是纯右值，`=`是赋值操作。对于内置类型，是不能给右值赋值的（`5 = 6`非法），但对于**类类型（Class Type）**，默认的赋值运算符`=`是一个成员函数：`S& operator=(const S&)`（拷贝赋值）或`S& operator=(S&&)`（移动赋值）。它们通常返回`*this`的引用，所以`S{}=S{7}`这个表达式的结果是一个**左值**！

但这是一个怪异的写法，在这个完整的表达式结束之前，`S{}`产生的临时对象是存在的，所以`(S{}=S{7}).m`可以正常访问成员，且这个表达式的结果是左值。但这个表达式一结束，临时对象就销毁了。如果你拿到了`m`的引用或地址，它会立即变成悬空引用或悬空指针。

再看几行代码找找感觉，你可以先不看答案自己推导一下哪些表达式是左值，哪些是右值：
```cpp
    int a{42};
    int& b{a};
    int&& r{std::move(a)};
```
上述例子中，`a`是左值，`42`是纯右值，`b`是左值引用，还是左值，`std::move(a)`是亡值，`r`虽然是右值引用，但它是左值。

### lvalue
以下表达式是 *lvalue* 表达式：
* **变量、函数、非类型模板参数对象（C++20 起）或数据成员的名称**，无论类型如何，如`std::cin`或`std::endl`。即使变量的类型是右值引用，由其名称组成的表达式也是一个 lvalue 表达式；
  ```cpp
  void foo() {}
 
  void baz()
  {
      // `foo` is lvalue
      // address may be taken by built-in address-of operator
      void (*p)() = &foo;
  } 
  ```
  ```cpp
  struct foo {};
 
  template <foo a>
  void baz()
  {
      const foo* obj = &a;  // `a` is an lvalue, template parameter object
  }
  ```
  上述例子中，可以声明一个函数指针`p`指向`foo`的地址，但是不能这样写：`foo = baz`，因为函数名是只读的左值。另外，函数名会隐式转换为函数指针，转换结果是一个临时右值。
* 返回类型为**左值引用**的**函数调用或重载运算符表达式**，如`std::getline(std::cin,str)`、`std::cout << 1`、`str1=str2`或`++it`（注：`std::getline`返回引用传递的输入流对象，所以可以放到`while`循环里面作为条件）；
  ```cpp
  int& a_ref()
  {
      static int a{3};
      return a;
  }
 
  void foo()
  {
      a_ref() = 5;  // `a_ref()` is lvalue, function call whose return type is lvalue reference
  }
  ```
  上述例子中，`a_ref()`返回的是静态局部变量`a`的引用（`static`保证`a`在函数调用间保持存在），因此可以对其赋值。
* `a = b`、`a+=b`以及所有其他内置**赋值**和**复合赋值**表达式，此时返回被赋值对象本身的左值引用（依旧参见引用折叠规则，防止引用的引用发生）；
* `++a`等内置的**前置增量**和**前置减量**表达式；
* `*p`和`a[n]`等内置的**解引用表达式**和**下标表达式**，注意数组名本身不是左值，大多数情况下退化成指针右值。
* `a.m`，**对象的成员**表达式，除了`m`是成员枚举器或非静态成员函数，或者`a`是右值且`m`是对象类型的非静态数据成员（这个有点点复杂，后面会有总结的！）。
  ```cpp
  struct foo
  {
      enum bar
      {
          m // member enumerator
      };
  };
 
  void baz()
  {
      foo a;
      a.m = 42; // ill-formed, lvalue required as left operand of assignment
  }
  ```
  ```cpp
  struct foo
  {
      void m() {} // non-static member function
  };
 
  void baz()
  {
      foo a;
 
      // `a.m` is a prvalue, hence the address cannot be taken by built-in
      // address-of operator
      void (foo::*p1)() = &a.m; // ill-formed
 
      void (foo::*p2)() = &foo::m; // OK: pointer to member function
  }
  ```
  ```cpp
  struct foo
  {
      static void m() {} // static member function
  };
 
  void baz()
  {
      foo a;
      void (*p1)() = &a.m;     // `a.m` is an lvalue
      void (*p2)() = &foo::m;  // the same
  }
  ```
* `p->m`，内置的**指针成员**表达式，除了`m`是成员枚举器或非静态成员函数；
* `a.*mp`，**指向对象成员的指针**表达式，其中`a`是左值且`mp`是指向数据成员的指针；
* `p->*mp`，内置的**指向指针成员的指针**表达式，其中`mp`是指向数据成员的指针；
  
上述几个表达式都是指如何访问成员。`p->m`等价于`(*p).m`,`p->*mp`等价于`(*p.*mp)`。它们返回的是成员`m`或者`mp`指向的那个成员。还有一个挺矛盾的点：当写下`a.*mp`时，编译器实际上是计算`&a + mp`并访问那个地址上的数据。那么这似乎就要求`a`必须是能取地址的左值了？实则不然，底层实现确实是取地址没错，但是语法层面上 `a` 可以不是左值，或者说语法层面上规定`a`是左值只意味着`a`可以显式取地址。cpp 允许`a`为右值，这是为了支持临时对象的访问。

* `a, b`，内置的**逗号**表达式，其中`b`是左值（逗号表达式的规则是从左到右依次求值，它返回最后一个表达式的值，所以该结果的值类别由最后一个表达式决定）；
* **字符串字面量**，如`"Hello, world!"`，它们存储在内存中的只读数据段（.rodata）。

### prvalue
以下表达式是 *prvalue* 表达式：
* **字面量**（**字符串字面量**除外），例如`42`、`true`或`nullptr`；
* 返回类型为**非引用**（即按值返回）的函数调用或重载运算符表达式，例如`str.substr(1, 2)`、`str1+str2`或`it++`；
* `a++`等内置的**后置增量**和**后置减量**表达式；
* `a + b`、`a & b`、`a << b`以及所有其他内置**算术**表达式；
* `a && b`、`!a`以及其他所有内置**比较**表达式；
* `&a`，内置的**取地址**表达式；
* `a.m`，**对象的成员**表达式，其中`m`是成员枚举器或非静态成员函数；
* `p->m`，内置的**指针成员**表达式，其中`m`是成员枚举器或非静态成员函数；
* `a.*mp`，**指向对象成员的指针**表达式，其中`mp`是指向成员函数的指针（注意，`a`仍然是左值）；
* `p->*mp`，内置的**指向指针成员的指针**，其中`mp`是指向成员函数的指针；
* `a, b`，内置的**逗号**表达式，其中`b`是 prvalue；
* **this**指针；
* **枚举器**；
* **lambda 表达式**。

### xvalue
以下表达式是 *xvalue* 表达式：
* `a.m`，**对象的成员**表达式，其中`a`是右值，`m`是对象类型的非静态数据成员；
* `a.*mp`，**指向对象成员的指针**表达式，其中`a`是右值，`mp`是指向数据成员的指针；
* `a, b`，内置的**逗号**表达式，其中`b`是 xvalue。

### 一些总结与思考
前文是根据三种值类别来划分的，但是笔者注意到有些东西反复出现，所以接下来笔者会总结几个重要的容易混淆的表达式的值类别具体该如何划分：

首先我们先来想象一下有个成员访问，如果它是**直接访问（`.`和`->`）**，那么访问的东西包括**实例绑定成员**和**类绑定成员**。实例绑定成员包括**非静态数据成员**和**非静态成员函数**；类绑定成员包括静态数据成员、静态成员函数、成员枚举器和嵌套类型定义（如`typedef`或`using`）。如果是通过**指针到成员操作符（`.*`和`->*`）**访问，那么访问的东西只有**实例绑定成员**（即非静态数据成员和非静态成员函数）。

直接成员访问（`.`和`->`）：
* `a.m`：
  
  如果`m`是非静态数据成员：
  * 如果`a`是左值，结果是 **lvalue**；
  * 如果`a`是右值（xvalue 或 prvalue），结果是 **xvalue**。
  * 如果`m`是静态成员（包括数据成员和成员函数）：结果始终是 **lvalue**（静态成员独立于对象实例存在，所以和`a`是左右值无关）。
  
  如果`m`是非静态成员函数或者成员枚举器：结果是 **prvalue**

  如果`m`是引用类型：结果始终是 **lvalue**（引用本身代表一个确定的对象）。
* `p->m`：

  语法上等价于`(*p).m`，因为`*p`永远是一个 lvalue，所以它的规则参照上述`a.m`中`a`为左值的情况。

指针到成员访问（`.*`和`->*`），成员指针不能指向静态成员或者枚举器，所以情况会简单一些）：
* `a.*mp`：
  
  如果`mp`指向数据成员：
  * 如果`a`是左值，结果是 **lvalue**。
  * 如果`a`是右值，结果是 **xvalue**。
  
  如果`mp`指向成员函数：结果是 **prvalue**。

* `p->mp`：
  
  语法上等价于`(*p).*mp`，同理，由于`*p`是左值，结果遵循`a.*mp`中`a`为左值的情况。

* 为什么`a.m`在`a`是右值的时候返回 **xvalue**？
  这是 C++11 为了支持移动语义而做出的深思熟虑。
  ```cpp
  struct Foo { std::string data; };
  Foo getFoo(); // 返回 prvalue

  // 这里的 getFoo().data 结果是 xvalue
  // 它允许 std::string 的移动构造函数接管这个临时对象的 data 成员
  std::string s = getFoo().data;
  ```
  如果`getFoo().data`还是左值，你就得写`std::move(getFoo().data)`才能触发移动。C++ 标准规定此时它是亡值（xvalue），意味着它即将销毁，你可以放心地把它“偷”走。

  即便`a`是`const`或者是`volatile`，上述值类别的规则依然适用。值类别描述的是“能不能取地址/是不是临时对象”，而`const`描述的是“能不能修改”，这两者是正交的（互不影响）。
* 最后一点冷门知识
  
  遗漏的**嵌套类型（Nested Types）**，请看代码：
  ```cpp
  struct S {
      struct Inner { int x; };
  };
  ```
  你不能通过`a.Inner`来访问这个类型（例如`a.Inner var;` 是非法的），你必须使用作用域运算符`S::Inner`。这是`. / ->`与`::`的一个重要区别：前者只能访问**值（Values/Functions/Constants）**，不能访问**类型（Types）**。