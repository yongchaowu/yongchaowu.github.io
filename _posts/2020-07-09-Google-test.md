---
layout: post
title: "Google test"
date: 2020-07-09 08:07:00
categories: ["Open source library"]
tags: ["GoogleTest", "Open source library", "Test Engineer&QC"]
---

## Building
- [Github](https://github.com/google/googletest.git)
- 配置使用Cmake
- 测试项目:
    1.创建Win32控制台应用程序，创建完成后把include和lib文件夹拷贝到项目路径下
    2.项目配置：
        点击项目属性》c/c++》代码生成中运行库中修改为“多线程调试(/MTd)”
        点击项目属性》c/c++》常规中附加包含目录中添加头文件路径
        点击项目属性》链接器》常规中附加包含目录中添加lib路径
        点击项目属性》链接器》输入中附加依赖项中添加gtestd.lib

<!--more-->
## Introduction
[Googletest入门](https://www.cnblogs.com/zjutzz/p/10304075.html)

## Code Test
- Test struct
  ```
  struct T1 {
  int a;
  };
  class FooTest : public ::testing::TestWithParam<struct T1> {
  // You can implement all the usual fixture class members here.
  // To access the test parameter, call GetParam() from class
  // TestWithParam<T>.
  //在这里面可以实现fixture类的所有成员
  protected:
      FooTest() {
        // You can do set-up work for each test here.
      }

      ~FooTest() override {
        // You can do clean-up work that doesn't throw exceptions here.
      }

      // If the constructor and destructor are not enough for setting up
      // and cleaning up each test, you can define the following methods:

      void SetUp() override {
        // Code here will be called immediately after the constructor (right
        // before each test).
      }

      void TearDown() override {
        // Code here will be called immediately after each test (right
        // before the destructor).
      }

    public:
      struct T1 m_T;
    };
   //第二步
    TEST_P(FooTest, DoesBlah) {
      // Inside a test, access the test parameter with the GetParam() method
      // of the TestWithParam<T> class:
      //在测试中，使用TestWithParam <T>类的GetParam（）方法访问测试参数：
      T1 n = GetParam();
      std::cout << m_T.a<<"----"<< n.a <<std::endl;
      //...
    }

    //第三步
    //第一个参数是前缀；第二个是类名；第三个是参数生成器
    INSTANTIATE_TEST_SUITE_P(MyPrimeParamTest, FooTest, ::testing::Values(T1{1}));

    int main(int argc, char** argv) 
    {
      testing::InitGoogleTest(&argc, argv);
      return RUN_ALL_TESTS();
    }
	```