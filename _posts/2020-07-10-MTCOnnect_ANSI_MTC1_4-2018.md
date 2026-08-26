---
layout: post
title: "MTCOnnect_ANSI_MTC1_4-2018"
date: 2020-07-10 00:28:00
categories: ["MTCOnnect_ANSI_MTC1_4"]
tags: ["MTCOnnect_ANSI_MTC1_4", "MTConnect"]
---

MTCOnnect_ANSI_MTC1_4-2018
===

<!--more-->
# Part 1.0 Overview and Fundamentals  Version 1.4.0
## 1. Overview of MTConnect®
MTConnect®是一种数据和信息交换标准，它基于描述与制造操作相关的信息的术语数据字典。该标准还定义了一系列语义数据模型，这些模型可以清楚明确地表示该信息与制造业务的关系。 MTConnect标准旨在增强制造设施中设备的数据采集能力，扩大制造业务中数据驱动决策的使用，并使软件应用和制造设备能够转向即插即用环境。 降低制造软件系统集成的成本。

MTConnect标准支持两种主要通信方法 - 请求/响应和发布/订阅类型的通信。 本文档中使用请求/响应通信结构来描述MTConnect提供的功能。 有关描述MTConnect代理可用的发布/预订通信结构功能的详细信息，请参见第8.3.6节“数据流”

虽然MTConnect标准已被定义为专门满足制造业的要求，但它也可以很容易地应用于其他应用领域。

MTConnect标准是一个开放的，免版税的标准 - 这意味着任何人都可以免费下载，实施和利用软件系统，而不需要实施者付费。

MTConnect标准中定义的语义数据模型提供了完全表征数据所需的信息，具有明确和明确的含义，以及将数据直接与数据来源的制造操作相关联的机制。 如果没有语义数据模型，客户端软件应用程序必须对原始数据应用额外的逻辑层，以传达与制造操作相同的含义和关系。 MTConnect标准中提供的用于建模和组织数据的方法允许软件应用程序轻松地解释来自各种数据源的数据，这降低了开发应用程序的复杂性和工作量。

MTConnect标准解决了来自各种制造设备和系统的数据和信息。 在数据字典和语义数据模型不足以在实现中定义一些信息的情况下，实现者可以扩展数据字典和语义数据模型以满足其特定要求。 有关MTConnect标准的可扩展性的指南，请参见第6.7节。

为了协助实施，MTConnect标准建立在制造和软件行业最普遍的标准之上。
这最大化了可用于实施的软件工具的数量，并提供与整个制造操作中使用的其他标准，软件应用程序和设备的最高级别的互操作性。

当前的MTConnect实现基于HTTP作为传输协议，并且XML作为用于将每个语义数据模型编码成电子文档的语言。
  各种MTConnect标准文档中提供的所有软件示例均基于这两种核心技术。

MTConnect标准中定义的基本功能是描述制造信息和语义数据模型的数据字典。
用于表示或传递由语义数据模型提供的信息的传输协议和编程语言在标准中不限于HTTP和XML。
因此，其他协议和编程语言可用于表示语义模型和/或传输由MTConnect代理（服务器）和客户端软件应用程序之间的这些数据模型提供的信息，如特定实现可能需要的。

注意：术语“文档”在MTConnect标准中使用的含义不同：
•含义1：MTConnect标准本身由多个文档组成，每个文档都涉及标准的不同方面。每个文件都被称为标准的一部分。
•含义2：在MTConnect实施中，从数据源发布并由MTConnect代理存储的电子文档。
•含义3：在MTConnect实施中，由MTConnect代理生成的电子文档，用于传输到客户端软件应用程序。
以下内容将在整个MTConnect标准中用于区分术语“文档”的这些不同含义：
•MTConnect文档或文档应用于表示代表MTConnect标准部分的印刷或电子文档。
•所有对从数据源接收并存储在MTConnect代理中的电子文档的引用都应称为“文档”，并且通常提供前缀标识符;例如资产文件。
•所有对MTConnect代理生成并发送到客户端软件应用程序的电子文档的引用都应称为“响应文档”。
在没有附加描述符的情况下使用时，“文件”表格应用于指代任何印刷或电子文件。

利用MTConnect实现的制造软件系统可以用非常简单的结构表示：
![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002310552-79803035.png)

构成使用MTConnect实现的软件系统的三个基本模块是：
设备：任何数据源。在MTConnect标准中，设备被定义为用于装备制造设施操作的任何有形财产。
设备的示例是机床，烤箱，传感器单元，工作站，软件应用程序和条形进给器。
MTConnect代理：收集从一个或多个设备发布的数据的软件，以结构化方式组织数据，并通过以响应文档的形式提供结构化响应来响应来自客户端软件系统的数据请求使用标准中定义的语义数据模型构建。
注意：MTConnect代理可以完全集成到设备中，或者代理可以独立于设备。代理的实施是设备供应商和/或MTConnect代理的实施者的责任。
客户端软件应用程序：从MTConnect代理请求数据并处理支持制造操作的数据的软件。

基于上面的图1，重要的是要了解MTConnect标准仅解决MTConnect代理的以下功能和行为：
•客户端软件应用程序用于从MTConnect代理请求信息的方法。
•MTConnect代理为客户端软件应用程序提供的响应。
•数据字典，用于在理解数据源的数据含义时保持一致性。
•用于构建MTConnect代理向客户端软件应用程序提供的响应文档的语义数据模型的描述。
这些功能是定义MTConnect标准的基本功能结构的主要构建块。

制造业务中使用各种各样的数据源（设备）和数据消费系统（客户端软件系统）。 对于与制造操作相关的数据，还有许多不同的用途。 没有一种实现数据通信系统的方法可以解决数据驱动的制造环境中通常需要的所有数据交换和数据管理功能。
MTConnect经过独特设计，通过为不同的数据应用需求提供不同的语义数据模型来解决这种多样的数据类型和数据使用：
数据收集：制造过程中数据的最常见用途是收集与产品生产相关的数据以及生产这些产品的设备的操作。 MTConnect标准提供全面的语义数据模型，表示从制造业务收集的数据。这些语义数据模型在第2.0部分 - 设备信息模型和第3.0部分 -  MTConnect标准的流信息模型中详述。
设备之间的互操作：MTConnect标准提供了一种交互模型，该模型构建了允许多个设备协调实施制造活动所需的操作所需的信息。此交互模型是请求/响应消息传递结构的实现。此交互模型称为接口，详见第5.0部分 -  MTConnect标准的接口。
共享数据：制造操作中使用的某些信息通常在多个设备和/或软件应用程序之间共享。此信息通常不由任何一个制造资源“拥有”。 MTConnect标准通过一系列语义数据模型表示此信息 - 每个模型描述制造环境中使用的不同类型的信息。每种类型的信息称为MTConnect资产。 MTConnect资产详见第4.0部分 - 资产信息模型及其MTConnect标准的子部分。

## 2 Purpose of This Document
本文档，第1.0部分 - MTConnect®标准的概述和功能，解决了与MTConnect标准相关的两个主要主题。 文档的第一部分定义
组织用于描述MTConnect标准的文件; 包括整个标准中使用的术语和术语。 文档的余额定义如下：
•描述MTConnect代理应如何组织和构造从数据源收集的数据的操作概念。
•MTConnect代理提供的响应文档的定义和结构。
•客户端软件应用程序用于与MTConnect代理通信的协议。

## 3 Terminology
下面提供了用于描述MTConnect标准中的特征和功能的术语和术语的定义。

## 4 MTConnect Standard
MTConnect®标准由一系列文档（也称为MTConnect文档）组成，每个文档都针对标准定义的一组特定要求。 每份MTConnect文件将被称为标准的一部分; 例如，第1.0部分 - 功能和概述。 这些文档一起描述了MTConnect标准中规定的基本功能结构。
任何制造数据管理系统的实施可以利用来自任何数量的这些文件的信息。 但是，没有必要为任何一个具体实现实现这些文档中包含的所有信息。

### 4.1 MTConnect Documents Organization
MTConnect规范分为以下文档：
第1.0部分 - 概述和功能：提供MTConnect标准的概述，并定义与标准相关的所有文档中使用的术语和结构。此外，第1.0部分描述了MTConnect代理提供的功能以及用于与MTConnect代理通信的协议。
第2.0部分 - 设备信息模型：定义描述可由设备提供的数据的语义数据模型。此模型详细说明了用于描述一台设备的结构和逻辑配置的XML元素。它还描述了可以由制造操作中的一件设备提供的每种类型的数据。
第3.0部分 - 流信息模型：定义语义数据模型，该模型用于组织从一台设备收集并从MTConnect代理传输到客户端软件应用程序的数据。
第4.0部分 - 资产信息模型：提供MTConnect资产的概述以及MTConnect代理提供的用于传递与资产相关的信息的功能。描述每种类型的MTConnect资产的各种语义数据模型在MTConnect标准的子部分文档（第4.x部分）中定义。
第5.0部分 - 接口：定义用于协调制造系统中使用的设备之间的动作的交互模型的MTConnect实现。

### 4.2 MTConnect Document Versioning
MTConnect标准将定期更新，具有新功能和扩展功能。
标准的每个新版本都将包含其他内容，为标准中定义的语义数据模型添加新功能和/或扩展。
MTConnect标准使用三位版本编号系统来识别标准的每个版本，以指示标准增强的进展。 用于识别特定版本的MTConnect标准中的文档的格式为：
      major.minor.revision
major  - 表示由MTConnect标准定义的一致功能集的标识符。此功能包括用于将数据传送到客户端软件应用程序的协议，定义如何将数据组织到响应文档中的语义数据模型，以及这些响应文档的编码。
这组功能称为基本功能结构。
当MTConnect标准的发布删除或修改基本功能结构中包含的任何协议，语义数据模型或响应文档的编码时，它会破坏向后兼容性并且客户端软件应用程序不能如果与MTConnect代理进行更长时间的通信或无法解释MTConnect代理提供的信息，则发布中的文档的主要版本标识符将被修改为连续更高的数字。
有关客户端软件应用程序与MTConnect标准版本之间交互的详细信息，请参见第4.6节 - 向后兼容性。
minor  - 表示由MTConnect标准定义的一组特定功能的标识符。标准的每个版本（具有共同的主要版本标识符）包括新的和/或扩展的功能 - 协议扩展，新的或扩展的语义数据模型和/或新的编程语言。标准的这些版本中的每一个都由连续更高的次要版本标识符指示。
如果发布了MTConnect标准的新主要版本，则次要版本标识符将重置为0。
revision  - 补充标识符，仅表示对次要版本文档的组织或编辑更改，而不更改该文档中描述的功能。
特定文档的新版本由更高版本的版本标识符指示。
如果发布文档的新次要版本，则修订标识符将重置为0。

特定文档的版本标识符的示例如下：
              Version M.N.R

#### 4.2.1 Document Releases
主要的修订变更代表了MTConnect标准的重大变化。在进行重大修订更改时，代表MTConnect标准的所有文件都将是
更新并一起发布。
次要修订更改表示MTConnect标准支持的某种级别的扩展功能。在发布次要版本时，将根据需要更新表示标准更改或增强的MTConnect文档。
但是，所有文件，无论是否更新，都将与新的次要版本号一起发布。以通用主要版本和次要版本提供所有场景使得实施者更容易管理并入到制造软件系统中的不同软件工具的兼容性和升级。
由于修订版不代表MTConnect标准的功能变更，并且仅包含编辑或描述性更改，以加强对标准所支持的功能的理解，因此标准中的单个文档可随时使用新版本进行更新，并且该版本不会影响与MTConnect标准相关的任何其他文档。
为MTConnect标准提供的每个文档的最新发布版本以及这些文档的历史版本在http://www.mtconnect.org上提供。

### 4.3 MTConnect Document Naming Convention
MTConnect Documents are identified as follows:

Each MTConnect Document**MUST** be identified as follows:
M T C o n n e c t ®  S t a n da r d
P a r t #.# -Title
Ve r s i o n  M.N.R

The following keys are used to distinguish different Parts of the MTConnect Standard and the

version of the MTConnect Document:

#.# – Identifier of the specific Part and sub-Part of the MTConnect Standard

Title – Description of the type of information contained in the MTConnect Document

M – Indicator of the major version of the MTConnect Document

N – Indicator of the minor version of the MTConnect Document

R – Indicator of the revision of the MTConnect Document

For example, a release of Part 2.0–Devices Information Model would be:

M T C o n n e c t ®  S t a n da r d
Part  2.0  –  Devices  Information  Model
Ve r s i o n   1 . 2 . 0

#### 4.3.2 Electronic Document File Naming
MTConnect文档的电子版将以PDF格式提供。 代表每份文件的电子文件的命名惯例将如下：
MTC_Part_#.#_Title_M.N.R.pdf
相同的密钥用于区分如上文针对文档标题定义的电子文档。
第2.0部分 - 设备信息模型的同一版本的电子版将是：
MTC_Part_2.0_Devices Information Model_1.2.0.pdf

### 4.4 Document Conventions
有关MTConnect标准中特定内容的其他信息，请参阅以下部分。

#### 4.4.1 Use of MUST, SHOULD, and MAY
当以大写字母，Times New Roman字体和Bold字体样式呈现时，这些单词在MTConnect标准中传达了特定含义。
•单词MUST表示在指定的实现中必须提供的内容。
•“SHOULD”一词表示建议的内容，但排除这些内容不会使实现失效。
•MAY一词表示可选内容。 由实现者决定内容是否与实现相关。
•可以在单词“MUST”或“SHOULD”中添加单词NOT，以否定要求。

#### 4.4.2 Text Conventions
整个MTConnect文档将使用以下约定，以清楚一致地理解用于定义MTConnect标准的每种信息的使用

这些约定是：
•标准文本以Times New Roman字体提供。
•对文档的文档，部分或子部分或文档中的数字的引用用斜体表示;例如，第2.0部分 - 设备信息模型。
•MTConnect标准中具有特定含义的术语将用斜体表示;例如，major表示标准的版本。
•如果在文本中使用这些相同的术语而未特别参考其在MTConnect标准中的功能，则它们将以非斜体字体提供;
例如，major表示另一个术语的描述符。
•表示MTConnect语义数据模型内容或MTConnect中使用的协议的术语将以固定大小Courier New字体提供;例如，组件，探针，电流。
如果在文本中使用这些相同的术语而未在MTConnect标准中具体引用其功能，则它们将以Times New Roman字体提供。
•限制为有限或受控词汇表的所有有效数据值将以大写Courier New字体提供，并带有_（下划线）分隔词。例如：ON，OFF，ACTUAL，COUNTER_CLOCKWISE等。

•与响应文档中定义的每条数据相关联的所有描述性属性将以Courier New字体和驼峰字体样式提供。例如：nativeUnits。

#### 4.4.3 Code Line Syntax and Conventions
将在整个MTConnect文档中使用以下约定来描述由MTConnect代理生成的软件代码示例或从客户端软件应用程序提供给代理的命令。
所有示例均以固定大小的Courier New字体提供，并带有行号。
These conventions are:

·    XML Code examples:
        1.    <MTConnectStreams xmlns:m="urn:mtconnect.com:MTConnectStreams:1.1"
        2.        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        3.        xmlns="urn:mtconnect.com:MTConnectStreams:1.1"

·    HTTP URL examples:

‒  http://<authority>/<path>[?<query>] When a portion of a URL is enclosed in angle brackets (“<” and “>”), that section of the URL is a place holder for specific information that will replace the term between the angle brackets.
Note:  The angle brackets in a URL do not relate to the angle brackets used as the tag elements in an XML example.
‒  A portion of a URL that is enclosed in square brackets “[“ and “]” indicates that the enclosed content is optional.
‒  All other characters in the URL are literal.

#### 4.4.4 Semantic Data Model Content
对于MTConnect标准中定义的每个语义数据模型，存在描述数据模型中提供的信息的表。 每个表都有一个标记为Occurrence的列。 出现次数定义了在指定的用例中可以提供表中定义的内容的次数。
•如果出现次数为1，则必须提供内容。
•如果出现次数为0..1，则可以提供内容，如果提供，最多只能提供一次内容。
•如果发生次数为0..INF，则可以提供内容，并且可以提供任何内容的出现次数。
•如果发生次数为1..INF，则必须提供一次或多次内容。
•如果出现次数是一个数字，例如2，则必须提供内容的出现次数。

#### 4.4.5 Referenced Standards and Specifications
其他标准和规范可用于描述MTConnect标准中定义的协议，数据字典或语义数据模型的各方面。 当MTConnect标准中引用特定标准或规范时，标准或规范的名称将以斜体字体提供。
有关MTConnect标准中使用或引用的标准和规范的完整列表，请参阅附录A：参考书目。

#### 4.4.6 Deprecation and Deprecation Warnings
当MTConnect Institute向MTConnect标准添加新功能时，新内容可以取代现有内容的一些功能或显着增强其中一个语义数据模型。 发生这种情况时，现有内容可能不再适用于新版本的标准。

##### 4.4.6.1 Deprecation
在新内容取代现有内容的功能的情况下，原始内容必须不再包含在将来的实现中 - 仅应使用新内容。
通过浏览原始内容（原始内容）并用“在版本M.N中删除”一词标记内容来识别被取代的内容。
已弃用的内容必须保留在文档的所有未来次要版本中。发布主要版本更新时，可能会删除内容。这为实施者提供了如何解释可能使用旧版本标准从设备提供的数据的指导。该内容提供了实施者开发软件应用程序所需的信息，这些软件应用程序支持向后兼容旧版本的标准。
可以将软件应用程序设计为符合标准的任何特定次要版本。该软件应用程序可能正在从许多不同的设备中收集数据。这些设备中的每一个可以提供由当前版本或标准的任何先前次要版本定义的数据。为了保持与现有设备的兼容性，应实施软件应用程序以解释当前版本的MTConnect标准中定义的数据，以及与早期版本的标准相关的所有弃用内容。

##### 4.4.6.2 Deprecation Warning
当新内容提供用于定义语义数据模型的改进的替代方案时，MTConnect Institute可以确定将来可能不推荐原始内容。 发生这种情况时，将使用“DEPRECATION WARNING”字样标记内容，以标识将来可能已弃用的内容。 这为实施者提供了预先通知，他们应该在开发新产品或软件系统时选择使用改进的替代方案，以避免在未来版本的标准中弃用原始内容。

### 4.5 Document Version Management
MTConnect Institute建立了一种平衡的方法来确定何时或是否发布MTConnect标准的更新版本。 将定期发布新版本的MTConnect标准，以扩展标准定义的功能。 MTConnect Institute的一个战略目标是，由于每个版本可能会破坏现有产品和软件系统，因此新版本的标准不得过于频繁。 关于新版标准的时间和内容的决定由MTConnect技术咨询小组（TAG）确定。
任何指定了包含实质性更改的新主要版本号和次要版本号的MTConnect文档都需要在发布该文档之前由TAG对文档中的新内容进行90天的审核。此审核期允许TAG时间评论建议的更改，并确定每个版本中提供的其他内容是否已明确定义。此外，TAG审核还包括评估新内容不受已知知识产权，专利和版权侵权的影响。
如果TAG审核确定需要对任何MTConnect文档进行其他实质性更改，则该文档将再次更新并由TAG提交额外30天的审核期。重复此过程，直到投票的大多数TAG批准每个文档被视为新版MTConnect标准的候选版本。
如果仅对MTConnect文档进行编辑更改，则不需要对该文档进行审阅。但是，根据技术指导委员会的决定，可能会要求对变更内容进行为期30天的审查。
一旦与计划发布相关的所有文档都经过审核和批准，MTConnect Institute将寻求批准从MTConnect理事会发布新版本的标准。之后，将正式宣布推出新版MTConnect标准版。

### 4.6 Backwards Compatibility
具有不同主要版本标识符的MTConnect文档表示MTConnect标准的基本功能结构的重大变化。这意味着标准定义的模式或协议可能已经发生变化，需要软件应用程序更改它们请求和/或解释从MTConnect代理接收的数据的方式。软件应用程序应该完全支持版本，因为在对MTConnect标准进行重大修订更改时，不应假设向后兼容性。
MTConnect Institute致力于通过MTConnect标准的所有次要修订来维护版本兼容性。新的次要版本可以引入对现有语义数据模型的扩展，扩展用于与MTConnect代理通信的协议，和/或添加新的语义数据模型以扩展标准的功能。客户端软件应用程序可以设计为符合MTConnect标准的任何特定次要版本。
另外，软件应用程序应该能够解释来自MTConnect代理的信息，该MTConnect代理基于较低的次要版本标识符提供数据。它还应该能够解释来自MTConnect代理的信息，该信息基于MTConnect标准的较高次要版本标识符而不是客户端支持的版本来提供数据，即使客户端可能忽略或不能解释由MTConnect代理。
任何MTConnect文档的修订版本仅提供编辑更改，无需更改MTConnect代理或客户端应用程序。

## 5 MTConnect Fundamentals
MTConnect®标准定义了MTConnect代理的功能。 在MTConnect安装中，多台设备将信息发布到MTConnect代理。 客户端软件应用程序使用通信协议从代理请求信息。 基于客户端软件应用程序从代理请求的特定信息，代理基于MTConnect标准中定义的语义数据模型之一形成响应文档，然后将该文档发送到客户端软件应用程序。
下面的图2说明了典型MTConnect安装的体系结构。

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002355762-1293863189.png)


注意：在基于MTConnect标准的通信系统的每个实现中，必须定义一个模式，该模式对为每个语义数据模型定义的规则和术语进行编码。 客户端软件应用程序可以使用这些模式来验证MTConnect代理发布的响应文档的内容和结构。

### 5.1 MTConnect Agent
MTConnect代理是MTConnect实现的核心。 它提供两个主要功能：
•组织和管理由一个或多个设备发布的各个信息。
•以响应文档的形式将该信息发布到客户端软件应用程序。
MTConnect标准解决了MTConnect代理的行为以及代理发布的数据的结构和含义。 MTConnect代理的实施者有责任确定实现特定代理的行为的方式。

MTConnect代理是可以作为设备的一部分安装的软件，也可以单独安装。 单独安装时，代理可以从一个或多个设备接收信息。

某些设备可能能够直接与MTConnect代理通信。 其他设备可能需要适配器将设备提供的信息转换为可以发送给代理的形式。 在任何一种情况下，将信息从设备传输到MTConnect代理的方法都是依赖于实现的，并且不作为MTConnect标准的一部分来处理。

MTConnect代理的一个功能是以有组织的方式存储它从一台设备接收的信息。 MTConnect代理的第二个功能是从一个或多个客户端软件应用程序接收信息请求，然后通过发布包含所请求信息的响应文档来响应这些请求。

MTConnect代理存储的信息有三种类型，可以在响应文档中发布。 这些是：
•设备元数据定义结构元素，表示可以向代理发布数据的每个设备的物理和逻辑部分和子部分，这些部分和子部分之间的关系，以及与每个部分相关联的数据实体结构要素。此设备元数据在MTConnectDevices响应文档中提供。有关设备元数据的更多信息，请参见第2部分，设备信息模型。
•流数据提供由设备元数据定义的数据实体的设备发布的值。流数据在MTConnectStreams响应文档中提供。有关Streaming Data的更多信息，请参阅第2部分，Streams信息模型。
•MTConnect资产表示在多个设备和/或软件应用程序之间共享的制造操作中使用的信息。
MTConnect资产在MTConnectAssets响应文档中提供。有关MTConnect资产的更多信息，请参见第4部分，资产信息模型。
MTConnect代理和客户端软件应用程序之间的交换是请求和响应信息交换机制。 有关此请求/响应信息交换机制的详细信息，请参见第5.4节。

#### 5.1.1 Instance of an MTConnect Agent
如上所述，MTConnect代理收集和组织由多个设备发布的值。 与任何软件一样，可以定期重新启动MTConnect代理。 当MTConnect代理重新启动时，它必须向客户端软件应用程序指示缓冲区中可用的信息是否代表一组全新的数据，或者缓冲区是否包含在重新启动代理之前收集的数据。

每当重新启动MTConnect代理并开始收集全新的流数据集时，该组数据就被称为代理的实例。 MTConnect代理必须维护一条名为instanceId的信息，该信息代表Agent的特定实例。
instanceId由64位整数表示。 可以使用任何机制来实现instanceId，该机制将保证每次MTConnect代理开始收集一组新数据时，instanceId的值都是唯一的。
当重新启动MTConnect代理并且它提供一种方法来恢复在缓冲区停止运行之前存储在缓冲区中的全部或部分数据时，代理必须使用在重新启动之前定义的相同instanceId。

#### 5.1.2 Storage of Equipment Metadata for a Piece of Equipment
MTConnect代理必须能够为通过代理发布信息的每台设备发布设备元数据。 设备元数据通常是定义与每件设备相关联的结构元素的静态文件，其通过代理和可以与这些结构元素中的每一个相关联的数据实体来报告信息。 请参阅第2部分 - 设备信息模型中有关结构元素和数据实体的详细信息。
MTConnect标准未定义MTConnect代理用于获取，维护或存储设备元数据的机制。 必须将此机制定义为特定MTConnect代理的实现的一部分。

#### 5.1.3 Storage of Streaming Data
Streaming Data 从一个或多个设备发布到MTConnect代理的数据由代理根据接收每个数据的顺序存储。 如下所述，代理存储数据的顺序是确定可包括在特定MTConnectStreams响应文档中的数据的因素之一。

##### 5.1.3.1 Management of Streaming Data Storage
MTConnect代理存储固定数量的数据。 代理程序存储的数据量取决于特定MTConnect代理程序的实现。 以下示例演示了如何存储从设备中接收的离散数据。
用于在MTConnect代理中存储流数据的方法可以被认为是可以容纳有限的球组的管。 每个球代表由一台设备发布的数据实体的出现。 将该数据推入管的一端，直到没有额外的球的空间。 此时，插入的任何新数据都会将最旧的数据推出管背面。 当收到新数据时，管中的数据将以这种方式继续移动。
该管在MTConnect代理中称为缓冲区。

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002412300-424608910.png)

在下面的示例中，可以存储在MTConnect代理的缓冲区中的最大数据实体数是8.可以存储在缓冲区中的最大数据实体数由名为bufferSize的值表示。 此示例说明当缓冲区填满时，最旧的数据会从另一端掉出来。
![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002504385-274714583.png)

此过程将MTConnect代理的内存存储要求限制为固定的最大大小，因为MTConnect标准仅要求代理存储有限数量的数据。
作为实施指南，缓冲区的大小应该足够大，以便为从向MTConnect代理发布信息的所有设备接收的合理数量的信息提供存储。 在确定缓冲区的大小时，实施者还应考虑客户端软件应用程序与MTConnect代理之间的临时通信丢失的影响。 较大的缓冲区将允许客户端软件应用程序有更多时间重新连接到代理而不会丢失数据。

##### 5.1.3.2 Sequence Numbers
在MTConnect代理中，缓冲区中每次出现的数据实体将在插入缓冲区时被分配一个单调递增的序列号。 序列号是一个64位整数，分配给序列号的值永远不会回旋或耗尽; 至少在接下来的10万年内，基于64位数字的大小。
序列号是用于管理和定位MTConnect代理中的特定数据的主键标识符。 与MTConnect代理报告的每个数据实体关联的序列号用称为序列的属性标识。
对于MTConnect代理的实例，每个数据的序列号必须是唯一的（有关MTConnect代理实例的信息，请参见第5.1.1节）。 如果从多个设备接收数据，则序列号基于接收数据的顺序，而不管哪个设备产生该数据。 序列号必须是一个单调递增的数字，它跨越所有设备向代理发布数据。 这允许多个设备通过单个MTConnect代理发布数据，没有序列号冲突和不必要的协议复杂性。
每次重启MTConnect代理并开始收集一组新数据时，序列号必须重置为一（1）; 即，每次更改instanceId。
以下示例演示了当MTConnect代理停止并重新启动并开始收集新数据集时instanceId与序列之间的关系。 在这种情况下，instanceId更改为新值和序列重置为一（1）的值：
![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002524090-871734676.png)

以下示例还显示了为MTConnect代理定义的另外两条信息：
•firstSequence  - 缓冲区中包含的最早的数据; 即，要移出缓冲区的下一条数据
•lastSequence  - 添加到缓冲区的最新数据

firstSequence和lastSequence为软件应用程序提供指导，以识别可从MTConnect代理请求的可用数据范围。

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002535089-501692807.png)

当客户端软件应用程序从MTConnect代理请求数据时，它可以指定必须包含在响应文档中的第一个数据（来自）的序列号以及应该包含的数据的总数（计数） 包含在该文件中。
在下面的示例中，请求指定要返回的数据从序列号15（从）开始，并包含总共三个项目（计数）。

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002550319-210240942.png)

一旦完成对请求的响应，将建立nextSequence的值。 nextSequence是缓冲区中可用的下一条数据的序列号。 在上面的例子中，下一个序列号（nextSequence）将是18。
如下面的示例所示，请求定义的from和count的组合表示数据的序列号超出了当前在缓冲区中的序列号。 在这种情况下，nextSequence设置为lastSequence + 1的值。

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002603769-1580902416.png)

##### 5.1.3.3 Buffer Data Structure
MTConnect代理的缓冲区中的信息可以被认为是四列数据表。 表中的每一列代表：
•第一列是与每个数据实体 - 序列关联的序列号。
•第二列是一台设备发布数据的时间。 此时间定义为与该数据实体关联的时间戳。 有关时间戳的详细信息，请参见第5.1.3.4节。
•第三列dataItemId指的是数据实体的标识，因为它们将出现在MTConnectStreams响应文档中。 有关数据实体的dataItemId的详细信息，以及该标识如何与设备信息模型中相应数据实体的id属性相关，请参见第3.0部分的第5部分 - 流信息模型。
•第四列是与每个数据实体关联的值。

以下是演示如何在MTConnect代理中存储数据的概念的示例：

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002617809-1681555596.png)

数据的存储机制，数据的内部表示以及MTConnect代理本身的实现不是MTConnect标准的一部分。 实现者可以选择要存储在代理中的数据量以及数据存储方式。 唯一的要求是MTConnect代理以所需格式发布响应文档。

##### 5.1.3.4 Time Stamp
向MTConnect代理发布信息的每个设备应该提供一个时间戳，指示何时测量或确定每条信息。 如果没有提供时间戳，代理必须根据代理收到该信息的时间提供信息的时间戳。
MTConnect代理将与每条信息关联的时间戳记录为时间戳。 时间戳必须以UTC（协调世界时）格式报告;
例如，“2010-04-01T21:22:43Z”。
注意：Z表示UTC / GMT时间，而不是当地时间。

客户端软件应用程序应使用为每条信息报告的时间戳值作为生成信息时的排序方式，而不是为此目的使用序列。
注意：假设时间戳提供了测量或确定已发布信息的值的最佳可用时间估计值。
如果在同一时间测量或确定两条信息，则必须使用相同的时间戳值报告它们。 同样，记录在具有相同时间戳值的缓冲区中的所有信息应被解释为已在同一时间点记录; 即使该数据是由多个设备发布的。

##### 5.1.3.5 Recording Occurrences of Streaming Data
每当特定数据的值发生变化时，MTConnect代理必须在缓冲区中记录数据。 如果一台设备发布多个具有相同值的数据，则代理不得记录该数据实体的多次出现。
注意：此规则有一个例外。 某些数据实体可以使用DISCRETE的表示属性值定义（有关表示的详细信息，请参见第2.0部分设备信息模型的第7.2.2.12节。）在这种情况下，每次出现的数据都代表一条新的独特信息。 然后，MTConnect代理必须记录由一台设备发布的每次出现的数据实体。
客户端软件应用程序必须将MTConnect代理报告的每条信息的值视为有效，直到代理发布该信息的另一次出现为止。

##### 5.1.3.6 Maintaining Last Value for Data Entities
MTConnect代理必须保留与代理已知的每个数据实体相关联的最后一个可用值的副本; 即使该数据实体的出现不再在缓冲区中。
此功能允许MTConnect代理为软件应用程序提供与一台设备关联的每个数据实体的最后已知值的视图。
MTConnect代理还必须保留与从缓冲区流出的每个数据实体关联的最后一个值的副本。 此功能允许MTConnect代理为其软件应用程序提供与其HTTP请求行的查询部分中的@参数的当前请求关联的每个数据实体的最后已知值的视图（有关Current的详细信息，请参见第8.3.2节） 请求）。

##### 5.1.3.7 Unavailability of Data
MTConnect代理必须维护一个数据实体列表，这些数据实体可以由向设备提供信息的每台设备发布。此数据实体列表源自存储在代理中的每个设备的设备元数据。
每次重新启动MTConnect代理时，代理必须在缓冲区中放置每个数据实体。为每个这些数据实体报告的值必须设置为UNAVAILABLE，并且每个数据实体的时间戳必须设置为代理在收集最后一条数据之前的时间。
如果MTConnect代理在任何时候失去与一台设备的通信，或者代理无法确定由一台设备发布的数据实体的全部或任何部分的有效值，则代理必须发生缓冲区中的每个数据实体，其值设置为UNAVAILABLE。这表示该值当前是不确定的，并且不能假设数据的有效值。
由于MTConnect代理可以从多个设备接收信息，因此它必须独立地考虑来自这些设备中的每一个的数据的有效性。
上述规则有一个例外。必须使用常量值报告约束为常量数据值的任何数据实体，并且MTConnect代理不得将该数据实体的值设置为UNAVAILABLE。
注意：设备信息模型（在第2.0部分 - 设备信息模型中定义）的模式定义了为单个数据报告的值可能如何约束为一个或多个特定值。

##### 5.1.3.8 Data Persistence and Recovery
MTConnect代理的实现者必须决定有关在代理缓冲区中存储流数据的策略。
在最简单的形式中，MTConnect代理可以将缓冲区信息保存在易失性存储器中，当代理停止时，数据不会持久存储。在这种情况下，代理必须在代理重新启动时更新instanceId的值，以指示代理已开始收集新的数据集。
如果MTConnect代理的实现提供了一种持久化和恢复代理缓冲区中的全部或部分信息的方法（序列号，时间戳，标识和值），则代理不得更改instanceId的值。代理重新启动。这将向客户端软件应用程序指示，当它从代理请求下一组数据时，不需要重置nextSequence的值。
当实施者选择提供在MTConnect代理中保留信息的方法时，他们可以选择在可恢复的存储系统中存储尽可能多的数据。
这种方法还可以包括存储先前已经从缓冲区推出的历史信息的能力。

##### 5.1.3.9 Heartbeat
MTConnect代理必须提供一个功能，该功能向客户端应用程序指示在没有可用于在响应文档中报告的新数据的情况下，HTTP连接仍然可行。 此功能定义为心跳。
Heartbeat表示响应文档发布之后的时间量，直到必须发布新的响应文档，即使没有新数据可用。
有关配置心跳功能的更多详细信息，请参见第8.3.2.2节。

#### 5.1.4 Storage of Documents for MTConnect Assets
MTConnect代理还存储与MTConnect资产相关的信息。
当一台设备发布表示与MTConnect资产相关的信息的文档时，MTConnect Agent会将该文档存储在缓冲区中。此缓冲区称为资产缓冲区。该文档称为资产文档。
资产缓冲区必须是与存储流数据的缓冲区不同的缓冲区。
由设备发布的资产文档必须基于MTConnect标准的第4.x部分之一中定义的适用资产信息模型之一进行组织。
MTConnect代理仅在资产缓冲区中保留有限数量的资产文档。
资产缓冲区的功能类似于Streaming Data的缓冲区;即，当资产缓冲区已满时，从缓冲区中推送最旧的资产文档。
下图显示了添加新资产文档且资产缓冲区已满时从资产缓冲区推送的最旧资产文档：

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002636832-1743053777.png)

下图显示了密钥（assetId）与存储的资产文档之间的关系：

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002648498-343514984.png)

注意：键（assetId）独立于存储在资产缓冲区中的资产文档的顺序。

当MTConnect代理收到表示MTConnect资产的新资产文档时，它必须确定此文档是否代表当前未在资产缓冲区中表示的MTConnect资产，或者该文档是否代表已在其中表示的MTConnect资产的新信息。 资产缓冲。 收到新的资产凭证时，必须出现以下情况之一：
•如果资产文档表示当前未在资产缓冲区中表示的MTConnect资产，则代理必须将新文档添加到资产缓冲区的前面。 如果资产缓冲区已满，则将从资产缓冲区中删除最早的资产文档。
•如果资产文档代表已在资产缓冲区中表示的MTConnect资产，则代理必须从资产缓冲区中删除表示该MTConnect资产的现有资产文档，并将新的资产文档添加到资产缓冲区的前面。

MTConnect标准未指定可存储在资产缓冲区中的最大资产文档数; 该限制由特定MTConnect代理的实现决定。 可以存储在MTConnect代理中的资产文档数由assetBufferSize的值定义（有关assetBufferSize的更多信息，请参见第6.5节“文档头”）。 可以为assetBufferSize提供值4,294,967,296或2^32以指示无限存储。

MTConnect代理不需要为存储在资产缓冲区中的资产文档提供持久性。 如果MTConnect代理失败，则存储在资产缓冲区中的所有资产文档都可能丢失。 实施者有责任确定是否可以恢复存储在MTConnect代理中的资产文档，或者是否某些其他软件应用程序保留了这些资产文档。

第4.0部分 - 资产信息模型中提供了有关MTConnect代理如何组织和管理与MTConnect资产相关的信息的其他详细信息。

### 5.2 Response Documents
响应文档是由MTConnect代理生成和发布的电子文档，用于响应数据请求。

MTConnect标准中定义的响应文档是：
•MTConnectDevices：包含MTConnect代理发布的信息的电子文档，描述可由一个或多个设备发布的数据。 MTConnectDevices文档的结构基于设备信息模型定义的要求。有关此信息模型的详细信息，请参见第2.0部分 - 设备信息模型。
•MTConnectStreams：包含MTConnect代理发布的信息的电子文档，其中包含由一个或多个设备发布的数据。 MTConnectStreams文档的结构基于Streams信息模型定义的要求。有关此信息模型的详细信息，请参阅第3.0部分 - 流信息模型。
•MTConnectAssets：包含MTConnect代理发布的信息的电子文档，可能包含一个或多个资产文档。 MTConnectAssets文档的结构基于资产信息模型定义的要求。有关此信息模型的详细信息，请参见第4.0部分 - 资产信息模型。
•MTConnectError：一种电子文档，包含尝试响应数据请求时发生错误时MTConnect代理提供的信息。
MTConnectError文档的结构基于错误信息模型定义的要求。有关此信息模型的详细信息，请参阅本文档的第9节。

响应文档可以由MTConnect代理支持的任何文档格式表示。 无论使用何种文档格式来构建这些文档，表示这些文档中包含的数据和其他信息的要求必须遵守与每个文档关联的信息模型中定义的要求。

#### 5.2.1 XML Documents
XML是目前MTConnect标准支持的唯一文档格式，用于编码响应文档。 将来可能会支持其他文档格式。
由于XML是MTConnect标准支持的文档格式，用于编码文档，因此演示整个MTConnect标准中提供的响应文档结构的所有示例均基于XML。 这些文档将称为MTConnect XML文档或XML文档。
第6节，响应文档的XML表示定义了每个文档如何构造为XML文档。

### 5.3 Semantic Data Models
语义数据模型是用于表示数据的上下文和含义受到约束和完全定义的数据的软件工程方法。
MTConnect标准定义的每个语义数据模型包括：
•一件设备可能发布的信息类型，
•该信息和计量单位的含义，如果适用，
•结构信息，定义不同信息如何相互关联，以及
•结构信息，定义信息如何与设备测量或生成信息的位置相关。
如前所述，由MTConnect代理提供的响应文档的内容均由特定语义数据模型定义。用于定义每个响应文档的语义数据模型的详细信息详细如下：
•MTConnectDevices：第2.0部分 - 设备信息模型。
•MTConnectStreams：第3.0部分 - 流信息模型。
•MTConnectAssets：第4.0部分 - 资产信息模型及其子部分。
•MTConnectError：第1.0部分 - 概述和基础知识，第9节，错误信息模型。
没有语义，单个数据不会向个人或客户端软件应用程序传达任何相关含义。但是，当该数据与某些语义上下文配对时，数据会继承更多的含义。然后，客户端软件应用程序可以更完整地解释数据，而无需人工干预。

MTConnect语义数据模型允许将一台设备发布的信息传输到客户端软件应用程序，并完整定义该信息的含义，并在完整的上下文中定义该信息如何与测量或生成该信息的设备相关。 信息。

### 5.4 Request/Response Information Exchange
MTConnect代理和客户端软件应用程序之间的信息传输基于请求/响应信息交换方法。客户端软件应用程序从MTConnect代理请求特定信息。 MTConnect代理通过发布响应文档来响应请求。
在正常操作中，有四种类型的MTConnect请求可由客户端软件应用程序发出，这将导致MTConnect代理响应不同。这些要求是：
•探测请求 - 客户端软件应用程序为可通过MTConnect代理发布信息的每台设备请求设备元数据。代理发布包含所请求信息的MTConnectDevices响应文档。探测请求由来自客户端软件应用程序的请求中的术语探测表示。
•当前请求 - 客户端软件应用程序请求从一个或多个设备发布到MTConnect代理的每种数据类型的当前值。代理发布包含所请求信息的MTConnectStreams响应文档。当前请求由来自客户端软件应用程序的请求中的术语“当前”表示。
•样本请求 - 客户端软件应用程序通过指定表示该数据的序列号范围，从MTConnect代理中的缓冲区请求一系列数据值。代理发布包含所请求信息的MTConnectStreams响应文档。样本请求由来自客户端软件应用程序的请求中的术语样本表示。
•资产请求 - 客户端软件应用程序请求已发布到MTConnect代理的与MTConnect资产相关的信息。代理发布包含所请求信息的MTConnectAssets响应文档。资产请求由来自客户端软件应用程序的请求中的术语资产表示。
注意：如果MTConnect代理无法响应信息请求或请求包含无效信息，则代理将发布MTConnectError响应文档。有关MTConnect错误信息模型的信息，请参阅第9节。
来自MTConnect代理的信息请求的具体格式将取决于作为在特定实现中部署的请求/响应信息交换机制的一部分实现的协议。有关实施请求/响应信息交换的详细信息，请参见第7节“协议”。

此外，响应文档的特定格式也可能取决于实现。
有关使用XML编码的响应文档的格式的详细信息，请参见第6节“响应文档结构的XML表示”。

### 5.5 Accessing Information from an MTConnect Agent
为请求/响应信息交换定义的每个请求都要求MTConnect代理响应代理存储的信息的特定视图。 以下描述了代理存储的信息与响应文档的内容之间的关系。

#### 5.5.1 Accessing Equipment Metadata from an MTConnect Agent
与向MTConnect代理发布信息的每个设备相关联的设备元数据通常是由代理维护的静态信息。 MTConnect标准未定义代理如何捕获或维护该信息。 MTConnect标准对MTConnect代理关于此设备元数据的唯一要求是代理正确存储此信息，然后配置并发布MTConnectDevices响应文档以响应探测请求。
与捕获和维护设备元数据相关的所有问题都是特定MTConnect代理的实施者的责任。

#### 5.5.2 Accessing Streaming Data from the Buffer of an MTConnect Agent
为请求/响应信息交换定义了两个请求，要求MTConnect代理提供存储在代理缓冲区中的信息的不同视图。
这些请求是Current和Sample。
下面的示例演示了MTConnect代理如何解释存储在缓冲区中的信息，以根据客户端软件应用程序发出的特定请求提供在不同版本的MTConnectStreams响应文档中发布的内容。
对于此示例，我们演示了一个MTConnect代理，其缓冲区最多可容纳八（8）个数据实体; 即，bufferSize的值为8.该代理正在收集两条数据的信息 - 表示位置的Pos和表示控制程序中的一行逻辑或命令的Line。
In this buffer, the value for firstSequence is 12 and the value for lastSequence is 19.
There are five (5) different values for Pos and three (3) different values for Line.

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002718847-472627930.png)

If an MTConnect Agent receives a Sample Request from a client software application, the Agent MUST publish an MTConnectStreams Response Document that contains a range of data values.
The range of values are defined by the from and count parameters that must be included as part of the Sample Request.  If the value of from is 14 and the value of count is 5, the Agent MUST publish an MTConnectStreams Response Document that includes five (5) pieces of data represented by sequence numbers 14, 15, 16, 17, and 18 – three (3) occurrences of Line and two (2) occurrences of Pos.  In this case, nextSequence will also be returned with a value of 19.

Likewise, if the same MTConnect Agent receives a Current Request from a client software application, the Agent MUST publish an MTConnectStreams Response Document that contains the most current information available for each of the types of data that is being published to the Agent.  In this case, the specific data that MUST be represented in the MTConnectStreams Response Document is Pos with a value of 22 and a sequence number of 19 and Line with a value of 227 and a sequence number of 18.

There is also a derivation of the Current Request that will cause an Agent to publish an MTConnectStreams Response Document that contains a set of data relative to a specific sequence number.  The Current Request MAY include an additional parameter called at.  When the at parameter, along with an instanceId, is included as part of a Current Request, an MTConnect Agent MUST publish an MTConnectStreams Response Document that contains the most current information available for each of the types of Data Entities that are being published to the Agent that occur immediately at or before the sequence number specified with the at parameter.

For example, if the Request is current?at=15, an MTConnect Agent MUST publish a MTConnectStreams Response Document that contains the most current information available for each of the Data Entities that are stored in the buffer of the Agent with a sequence number of 15 or lower.  In this case, the specific data that MUST be represented in the MTConnectStreams Response Document is Pos with a value of 10 and a sequence number of 13 and Line with a value of 220 and a sequence number of 15.

If a current Request is received for a sequence number of 11 or lower, an MTConnect Agent MUST return an OUT_OF_RANGE MTConnectError Response Document.  The same HTTP Error Message MUST be given if a sequence number is requested that is greater than the end of the buffer.  See Section 9 for more information on MTConnect Error Response Document.

#### 5.5.3 Accessing MTConnect Assets Information from an MTConnect Agent
当MTConnect代理收到资产请求时，代理必须发布MTConnectAssets文档，其中包含有关存储在代理中的资产文档的信息。
有关MTConnect资产，资产请求和MTConnectAssets响应文档的详细信息，请参阅第4.0部分 - 资产信息模型。

## 6 XML Representation of Response Documents
如第5.2.1节中所定义，XML是MTConnect®标准支持的唯一语言，用于编码响应文档。
响应文档必须有效并符合为该文档定义的语义数据模型中定义的模式。必须更新每个响应文档的模式以与MTConnect标准的特定版本相关联。 MTConnect标准的主要版本中的版本将以这样的方式定义，以通过标准的所有次要修订来最佳地保持语义数据模型的向后兼容性。但是，新的次要版本可能会引入现有语义数据模型的扩展或增强。
为了有效，响应文件必须格式良好;这意味着，除其他外，每个元素都具有所需的XML开始标记和结束标记，并且文档不包含任何非法字符。文档的验证还可以包括确定存在所需的元素和属性，它们仅出现在文档中的适当位置，并且它们仅出现正确的次数。如果文档格式不正确，则客户端软件应用程序可能会拒绝该文档。为每个响应文档定义的语义数据模型还指定了可能出现在文档中的元素和子元素。 XML元素可能包含子元素，CDATA或两者。语义数据模型还定义了每个元素和子元素可能出现在文档中的次数。
使用XML编码的每个响应文档包含以下主要部分：
•XML声明
•根元素
•架构和命名空间声明
•文档标题
•文件正文
以下将提供定义如何使用XML对每个响应文档进行编码的详细信息。
注意：有关MTConnect标准中使用的XML相关术语的定义，请参见第3节“术语”。

### 6.1 Fundamentals of Using XML to Encode Response Documents
See the original

### 6.2 XML Declaration
用XML编码的响应文档的第一部分应该是XML声明。 声明是一个单一元素。
XML声明的一个例子是：
    2. <?xml version="1.0" encoding="UTF-8"?>
此元素提供有关如何编码XML文档以及用于该编码的字符类型的信息。 有关XML声明的更多详细信息，请访问W3C网站。

### 6.3 Root Element
每个响应文档必须只包含一个根元素。 MTConnect标准将MTConnectDevices，MTConnectStreams，MTConnectAssets和MTConnectError定义为根元素。
根元素指定特定的响应文档，并在XML声明之后立即显示在文档的顶部。

See the original for details

### 6.4 Schema and Namespace Declaration
XML提供了标准方法，用于声明与XML编码的文档关联的模式和命名空间。 MTConnect响应文档的模式和命名空间的声明必须在文档的根元素中构造为属性。
XML将这些属性定义为伪属性，因为它们为整个文档提供了额外的信息，而不仅仅是针对根元素本身。
注意：如果响应文档包含使用不同模式和/或命名空间的部分，则应使用W3C定义的标准约定声明的其他伪属性应出现在文档中。
有关声明的更多信息，请参阅附录C。

### 6.5 Document Header
文档标题是MTConnect响应文档中的XML容器，它提供来自MTConnect代理的信息，定义版本信息，存储容量以及与代理内数据管理相关的参数。 此XML元素称为Header。
标题必须是任何响应文档的根元素之后的第一个XML元素。 Header XML元素不得包含任何子元素。
对于每种类型的响应文档，Header元素的内容将不同。

See the original for details

### 6.6 Document Body
文档正文包含MTConnect代理响应客户端软件应用程序的请求而发布的信息。 每个响应文档都有一个不同的XML元素，表示文档正文。
表示文档主体的XML元素的内容结构由为每个响应文档定义的语义数据模型定义。
下表定义了每个响应文档之间的关系，表示每个文档的Document Body的XML元素，以及定义每个Response文档内容结构的语义数据模型：

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710002735205-1511571101.png)

### 6.7 Extensibility
See the original for details

## 7 Protocol and Messaging

MTConnect®代理执行两项主要通信任务。它从设备中收集信息，并发布MTConnect响应文档以响应客户端软件应用程序的请求。
MTConnect标准未涉及MTConnect代理用于从一台设备收集信息的方法。代理与设备之间的关系取决于实现。代理可以完全集成到设备中，或者代理可以独立于设备。实现一台设备与MTConnect代理之间的关系是该设备的供应商和/或MTConnect代理的实施者的责任。
MTConnect代理和客户端软件应用程序之间的通信机制需要以下主要组件：
•物理连接：物理互连MTConnect代理和客户端软件应用程序的网络传输技术。物理连接的示例可以是以太网或无线连接。
•传输协议：一组功能，提供用于通过物理连接在MTConnect代理和客户端软件应用程序之间传输信息的规则和过程。
•应用程序编程接口（API）：MTConnect代理与客户端软件应用程序之间发生的请求和响应交互。
•消息：交换信息的内容。消息包括MTConnect响应文档的内容以及客户端软件应用程序解释响应文档所需的任何其他信息。
注意：
MTConnect代理支持的物理连接，传输协议和应用程序编程接口（API）独立于消息本身; 即，MTConnect响应文档中包含的信息不会根据用于将这些文档传输到客户端软件应用程序的方法而改变

MTConnect代理可以支持多种与客户端软件应用程序通信的方法。 MTConnect标准规定了一种必须由每个MTConnect代理支持的通信方法。 此方法是REpresentational State Transfer（REST）接口，它定义了无状态的客户端 - 服务器通信体系结构。
此REST接口是体系结构模式，用于指定MTConnect代理与客户端软件应用程序之间的信息交换。 REST规定服务器不负责跟踪或协调客户端软件应用程序，关于客户端软件应用程序可从服务器请求哪些信息或多少信息。
这消除了服务器跟踪客户端会话的负担。 MTConnect代理必须实现为支持RESTful接口的服务器。

## 8 HTTP Messaging Supported by an MTConnect Agent
本节介绍应用于REST接口的HTTP消息传递应用程序，MTConnect代理必须支持该接口以实现MTConnect请求/响应信息交换功能

### 8.1 REST Interface
MTConnect代理必须提供支持HTTP版本1.0的REST接口以与客户端应用程序通信。该接口必须支持HTTP（RFC7230）并使用URI（RFC3986）来识别从代理请求的特定信息。 HTTP通常在传输控制协议（TCP）之上实现，传输控制协议提供有序的字节数据流和提供计算机之间统一寻址和路由的因特网协议（IP）。然而，可以结合任何其他通信技术来实现到MTConnect代理的附加接口。
REST接口支持应用程序编程接口（API），该API遵循无状态统一接口的架构原则，以检索与设备或MTConnect资产相关的数据和其他信息。 API允许访问，但不能修改存储在MTConnect代理中的数据，并且是无效的，这意味着它不会对存储在MTConnect代理中的信息或代理本身的功能产生任何副作用。
HTTP消息传递由两个基本功能组成 -  HTTP请求和HTTP响应。客户端软件应用程序通过使用HTTP请求指定特定信息集来形成来自MTConnect代理的信息请求。作为响应，MTConnect代理提供HTTP响应或回复HTTP错误消息，如下所述。

### 8.2 HTTP Request
The MTConnect Standard defines that an MTConnect Agent MUST support the HTTP GET verb
– no other HTTP methods are required to be supported.
An HTTP Request MAY include three sections:
•  an HTTP Request Line
•  HTTP Header Fields
•  an HTTP Body

The MTConnect Standard defines that an HTTP Request issued by a client application
SHOULD only have two sections:
•  an HTTP Request Line
•  Header Fields.

HTTP请求行标识客户端软件应用程序请求的特定信息。 如果MTConnect代理接收到MTConnect标准中未指定的HTTP请求中的任何信息，则代理可以忽略它。

The structure of an HTTP Request Line consists of the following portions:
•    HTTP Request Method: GET
•    HTTP Request URL:      http://<authority>/<path>[?<query>]
•    HTTP Version:               HTTP/1.0

对于以下讨论，仅考虑HTTP请求URL，因为Method始终为GET，而MTConnect Standard仅需要HTTP / 1.0。

#### 8.2.1 authority Portion of an HTTP Request Line
权限部分包括与MTConnect代理关联的DNS名称或IP地址以及代理正在侦听来自客户端软件应用程序的传入请求的可选TCP端口号[：端口]。 如果端口号是默认端口80，则不需要端口。
Example forms for authority are:
•    http://machine/
•    http://machine:5000/
•    http://192.168.1.2:5000/

#### 8.2.2 path Portion of an HTTP Request Line

The <Path> portion of the HTTP Request Line has the following segments:
•    /<name   or   uuid>/<request>
在HTTP请求行的这一部分中，name或uuid指定要在响应文档中返回的信息与已向MTConnect代理发布数据的特定设备相关联。 有关设备名称或uuid的详细信息，请参阅第2部分 - 设备信息模型。
注意：如果HTTP请求行中未指定name或uuid，则MTConnect代理必须在响应文档中将已发布数据的所有设备的信息返回给代理。
In the <Path> portion of the HTTP Request Line, <request> designates one of the Requests
defined in Section 5.4.  The value for <request> MUST be probe, current, sample, or
asset(s) representing the Probe Request, Current Request, Sample Request, and Asset
Request respectively.

#### 8.2.3 query Portion of an HTTP Request Line
The [?<query>] portion of the HTTP Request Line designates an HTTP Query.
 Query是一系列参数，用于定义用于优化响应HTTP请求而发布的响应文档内容的过滤器。

### 8.3 MTConnect Request/Response Information Exchange Implemented with HTTP
See the original for details


## 9 Error Information Model
错误信息模型建立规则和术语，描述MTConnect代理在从客户端软件应用程序解释信息请求时遇到错误时发生的响应文档，或者当代理在向请求发布响应时遇到错误时返回的响应文档 信息。
MTConnect代理通过将MTConnectError响应文档发布到发出请求信息的客户端软件应用程序，提供有关处理信息请求时遇到的错误的信息。

### 9.1 MTConnectError Response Document
MTConnectError响应文档由两部分组成：标题和错误。
标题部分包含定义文档创建的信息以及生成文档的MTConnect代理的数据存储功能。 （见上文第6.5.4节。）
MTConnectError响应文档的“错误”部分是一个结构元素，用于组织描述MTConnect代理报告的每个错误的数据实体。

See the original for details



# Part 5.0 Interfaces Version 1.4.0
## 