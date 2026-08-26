---
layout: post
title: "Cryptology-3DES（Triple DES） -1981 American"
date: 2020-07-08 23:58:00
categories: ["Cryptology"]
tags: ["Triple DES", "Cryptology"]
---

[百度百科](https://baike.baidu.com/item/3DES/6368161?fr=aladdin)

<!--more-->
3DES（或称为Triple DES）是三重数据加密算法（TDEA，Triple Data Encryption Algorithm）块密码的通称。它相当于是对每个数据块应用三次DES加密算法。由于计算机运算能力的增强，原版DES密码的密钥长度变得容易被暴力破解；3DES即是设计用来提供一种相对简单的方法，即通过增加DES的密钥长度来避免类似的攻击，而不是设计一种全新的块密码算法。

## 算法介绍
3DES又称Triple DES，是DES加密算法的一种模式，它使用2条(*++至少两条,k1可以等于k3,此时牺牲加密密钥长度，长度降为112位++*)不同的56位的密钥对数据进行三次加密。数据加密标准（DES）是美国的一种由来已久的加密标准，它使用对称密钥加密法，并于1981年被ANSI组织规范为ANSI X.3.92。DES使用56位密钥和密码块的方法，而在密码块的方法中，文本被分成64位大小的文本块然后再进行加密。比起最初的DES，3DES更为安全。
3DES（即Triple DES）是DES向AES过渡的加密算法（1999年，NIST将3-DES指定为过渡的加密标准），加密算法，其具体实现如下：
```
    设Ek()和Dk()代表DES算法的加密和解密过程，K代表DES算法使用的密钥，M代表明文，C代表密文，这样：
    3DES加密过程为：C=Ek3(Dk2(Ek1(M)))
    3DES解密过程为：M=Dk1(EK2(Dk3(C)))
    K1、K2、K3决定了算法的安全性，若三个密钥互不相同，本质上就相当于用一个长为168位的密钥进行加密。多年来，它在对付强力攻击时是比较安全的。若数据对安全性要求不那么高，K1可以等于K3。在这种情况下，密钥的有效长度为112位。
```