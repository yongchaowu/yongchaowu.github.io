---
layout: post
title: BehaviorTree.CPP-ManualNotes
date: 2026-07-15 23:51:00
categories:
- Personal / Misc
tags:
- Open Source
- C++
- Code
- Open source library
- UML
---

- [Introduce](https://www.behaviortree.dev/)
- [BehaviorTree.CPP](https://github.com/BehaviorTree/BehaviorTree.CPP#)
- [Groot2](https://www.behaviortree.dev/groot/)

<!--more-->
- [ZeroMQ Project](https://github.com/zeromq?q=zmqp&type=all&language=&sort=)
- [zeromq/libzmq](https://github.com/zeromq/libzmq)
- [zeromq/zmqpp](https://github.com/zeromq/zmqpp)

## BehaviorTree.CPP 

The Industry Standard for Robot Behaviors

BehaviorTree.CPP is the most popular, production-ready framework for building reactive, modular, and debuggable robot behaviors.


1. More scalable than State Machines

Behavior Trees enable complex behaviors with less code and more modularity, making them easier to maintain and extend, compared to traditional state machines.

2. Async Actions

Non-blocking actions and reactive behaviors as first-class citizens.

3. Modular Architecture

Build reusable building blocks, load custom nodes at runtime.

4. XML-Defined Trees

Separation of concerns between logic (XML) and implementation (C++).

5. Built-in Logging

Record, replay, and analyze state transitions for easier debugging.

6. ROS2 Integration

The most widely used Robot Deliberation library in the ROS2 ecosystem. The main library is ROS-agnostic, but we provide seamless ROS2 integration.


[Document-Introduce](https://www.behaviortree.dev/docs/intro)

### Documentation

- Tutorials and general documentation: https://www.behaviortree.dev/
- Auto-generated Doxygen: https://behaviortree.github.io/BehaviorTree.CPP/
- Community support and forum: https://github.com/BehaviorTree/BehaviorTree.CPP/discussions


#### Basic Concepts

- tick() callback
- callback return [SUCCESS/FAILURE/RUNNING]
- node type [TreeNode:DecoratorNode/ControlNode/LeafNode(ConditionNode/ActionNode)]

|Type of TreeNode	|Children Count	|Notes|
|------|------|------|
|ControlNode	|1...N	|Usually, ticks a child based on the result of its siblings or/and its own state.|
|DecoratorNode	|1	|Among other things, it may alter the result of its child or tick it multiple times.|
|ConditionNode	|0	|Should not alter the system. Shall not return RUNNING.|
|ActionNode	|0	|This is the Node that "does something"|

- Create custom nodes with inheritance [ActionNodeBase/ConditionNode/DecoratorNode]

- Dataflow, Ports and Blackboard
    - A Blackboard is a key/value storage shared by all the Nodes of a Tree.
    - Ports are a mechanism that Nodes can use to exchange information between each other.
    - Ports are "connected" using the same key of the blackboard.
    - The number, name and kind of ports of a Node must be known at compilation-time (C++); connections between ports - are done at deployment-time (XML).
    - You can store as value any C++ type (we use a type erasure technique similar to std::any).


- xml schema

```xml
 <root BTCPP_format="4">
     <BehaviorTree ID="MainTree">
        <Sequence name="root_sequence">
            <SaySomething   name="action_hello" message="Hello"/>
            <OpenGripper    name="open_gripper"/>
            <ApproachObject name="approach_object"/>
            <CloseGripper   name="close_gripper"/>
        </Sequence>
     </BehaviorTree>
 </root>
```

The first tag of the tree is `<root>`. It should contain 1 or more tags `<BehaviorTree>`.

The tag `<BehaviorTree>` should have the attribute [ID].

The tag `<root>` should contain the attribute [BTCPP_format].

Each TreeNode is represented by a single tag. In particular:

    The name of the tag is the ID used to register the TreeNode in the factory.
    The attribute [name] refers to the name of the instance and is optional.
    Ports are configured using attributes. In the previous example, the action SaySomething requires the input port message.

In terms of number of children:

    ControlNodes contain 1 to N children.
    DecoratorNodes and Subtrees contain only 1 child.
    ActionNodes and ConditionNodes have no child.


Ports Remapping and pointers to Blackboards entries [BB key syntax:{key_name}]

Compact vs Explicit representation
```xml
 <SaySomething               name="action_hello" message="Hello World"/>
 <Action ID="SaySomething"   name="action_hello" message="Hello World"/>
```

Tools like Groot require either the explicit syntax or additional information, that can be added using the tag `<TreeNodeModel>`.

Subtrees,`<SubTree ID="xxx"/>`

Include external files,`<include path="relative_or_absolute_path_to_file">`


#### Tutorials(Basic)

##### First Behavior Tree

```xml
#my_tree.xml
 <root BTCPP_format="4" >
     <BehaviorTree ID="MainTree">
        <Sequence name="root_sequence">
            <CheckBattery   name="check_battery"/>
            <OpenGripper    name="open_gripper"/>
            <ApproachObject name="approach_object"/>
            <CloseGripper   name="close_gripper"/>
        </Sequence>
     </BehaviorTree>
 </root>
```

```c++
//C++ Demo

#include "behaviortree_cpp/bt_factory.h"

// file that contains the custom nodes definitions
#include "dummy_nodes.h"
using namespace DummyNodes;

int main()
{
    // We use the BehaviorTreeFactory to register our custom nodes
  BehaviorTreeFactory factory;

  // The recommended way to create a Node is through inheritance.
  factory.registerNodeType<ApproachObject>("ApproachObject");

  // Registering a SimpleActionNode using a function pointer.
  // You can use C++11 lambdas or std::bind
  factory.registerSimpleCondition("CheckBattery", [&](TreeNode&) { return CheckBattery(); });

  //You can also create SimpleActionNodes using methods of a class
  GripperInterface gripper;
  factory.registerSimpleAction("OpenGripper", [&](TreeNode&){ return gripper.open(); } );
  factory.registerSimpleAction("CloseGripper", [&](TreeNode&){ return gripper.close(); } );

  // Trees are created at deployment-time (i.e. at run-time, but only 
  // once at the beginning). 
    
  // IMPORTANT: when the object "tree" goes out of scope, all the 
  // TreeNodes are destroyed
   auto tree = factory.createTreeFromFile("./my_tree.xml");

  // To "execute" a Tree you need to "tick" it.
  // The tick is propagated to the children based on the logic of the tree.
  // In this case, the entire sequence is executed, because all the children
  // of the Sequence return SUCCESS.
  tree.tickWhileRunning();

  return 0;
}

/* Expected output:
*
  [ Battery: OK ]
  GripperInterface::open
  ApproachObject: approach_object
  GripperInterface::close
*/



// Example of custom SyncActionNode (synchronous action)
// without ports.
class ApproachObject : public BT::SyncActionNode
{
public:
  ApproachObject(const std::string& name) :
      BT::SyncActionNode(name, {})
  {}

  // You must override the virtual function tick()
  BT::NodeStatus tick() override
  {
    std::cout << "ApproachObject: " << this->name() << std::endl;
    return BT::NodeStatus::SUCCESS;
  }
};

using namespace BT;

// Simple function that return a NodeStatus
BT::NodeStatus CheckBattery()
{
  std::cout << "[ Battery: OK ]" << std::endl;
  return BT::NodeStatus::SUCCESS;
}

// We want to wrap into an ActionNode the methods open() and close()
class GripperInterface
{
public:
  GripperInterface(): _open(true) {}
    
  NodeStatus open() 
  {
	_open = true;
	std::cout << "GripperInterface::open" << std::endl;
	return NodeStatus::SUCCESS;
  }

  NodeStatus close() 
  {
    std::cout << "GripperInterface::close" << std::endl;
	_open = false;
	return NodeStatus::SUCCESS;
  }

private:
  bool _open; // shared information
};


```


##### Blackboard and ports

Type:
- InputPort
- OutputPort
- BidirectionalPort

Function:
- `TreeNode::getInput<T>(key).`
- `getLockedPortContent()`

Class Constructor:
- `MyCustomNode(const std::string& name, const NodeConfig& config);`

static method:
- `static MyCustomNode::PortsList providedPorts();`


```c++
///Demo Codes
// SyncActionNode (synchronous action) with an input port.
class SaySomething : public SyncActionNode
{
public:
  // If your Node has ports, you must use this constructor signature 
  SaySomething(const std::string& name, const NodeConfig& config)
    : SyncActionNode(name, config)
  { }

  // It is mandatory to define this STATIC method.
  static PortsList providedPorts()
  {
    // This action has a single input port called "message"
    return { InputPort<std::string>("message") };
  }

  // Override the virtual function tick()
  NodeStatus tick() override
  {
    Expected<std::string> msg = getInput<std::string>("message");
    // Check if expected is valid. If not, throw its error
    if (!msg)
    {
      throw BT::RuntimeError("missing required input [message]: ", 
                              msg.error() );
    }
    // use the method value() to extract the valid message.
    std::cout << "Robot says: " << msg.value() << std::endl;
    return NodeStatus::SUCCESS;
  }
};


class ThinkWhatToSay : public SyncActionNode
{
public:
  ThinkWhatToSay(const std::string& name, const NodeConfig& config)
    : SyncActionNode(name, config)
  { }

  static PortsList providedPorts()
  {
    return { OutputPort<std::string>("text") };
  }

  // This Action writes a value into the port "text"
  NodeStatus tick() override
  {
    // the output may change at each tick(). Here we keep it simple.
    setOutput("text", "The answer is 42" );
    return NodeStatus::SUCCESS;
  }
};

```

##### Ports with generic types

Parsing a string

a template specialization of `BT::convertFromString<Position2D>(StringView)`.

```c++
// We want to use this custom type
struct Position2D 
{ 
  double x;
  double y; 
};

// Template specialization to converts a string to Position2D.
namespace BT
{
    template <> inline Position2D convertFromString(StringView str)
    {
        // We expect real numbers separated by semicolons
        auto parts = splitString(str, ';');
        if (parts.size() != 2)
        {
            throw RuntimeError("(invalid input)");
        }
        else
        {
            Position2D output;
            output.x     = convertFromString<double>(parts[0]);
            output.y     = convertFromString<double>(parts[1]);
            return output;
        }
    }
} // end namespace BT
```

Example:
```c++
class CalculateGoal: public SyncActionNode
{
  public:
    CalculateGoal(const std::string& name, const NodeConfig& config):
      SyncActionNode(name,config)
    {}

    static PortsList providedPorts()
    {
      return { OutputPort<Position2D>("goal") };
    }

    NodeStatus tick() override
    {
      Position2D mygoal = {1.1, 2.3};
      setOutput<Position2D>("goal", mygoal);
      return NodeStatus::SUCCESS;
    }
};

class PrintTarget: public SyncActionNode
{
  public:
    PrintTarget(const std::string& name, const NodeConfig& config):
        SyncActionNode(name,config)
    {}

    static PortsList providedPorts()
    {
      // Optionally, a port can have a human readable description
      const char*  description = "Simply print the goal on console...";
      return { InputPort<Position2D>("target", description) };
    }
      
    NodeStatus tick() override
    {
      auto res = getInput<Position2D>("target");
      if( !res )
      {
        throw RuntimeError("error reading port [target]:", res.error());
      }
      Position2D target = res.value();
      printf("Target positions: [ %.1f, %.1f ]\n", target.x, target.y );
      return NodeStatus::SUCCESS;
    }
};


static const char* xml_text = R"(

 <root BTCPP_format="4" >
     <BehaviorTree ID="MainTree">
        <Sequence name="root">
            <CalculateGoal goal="{GoalPosition}" />
            <PrintTarget   target="{GoalPosition}" />
            <Script        code=" OtherGoal:='-1;3' " />
            <PrintTarget   target="{OtherGoal}" />
        </Sequence>
     </BehaviorTree>
 </root>
 )";

int main()
{
  BT::BehaviorTreeFactory factory;
  factory.registerNodeType<CalculateGoal>("CalculateGoal");
  factory.registerNodeType<PrintTarget>("PrintTarget");

  auto tree = factory.createTreeFromText(xml_text);
  tree.tickWhileRunning();

  return 0;
}
/* Expected output:

    Target positions: [ 1.1, 2.3 ]
    Converting string: "-1;3"
    Target positions: [ -1.0, 3.0 ]
*/
```


##### Reactive and Asynchronous behaviors

1. `StatefulActionNode`

A derived class of StatefulActionNode must override the following virtual methods, instead of tick():

    NodeStatus onStart(): called when the Node was in IDLE state. It may succeed or fail immediately or return RUNNING. In the latter case, the next time the tick is received the method onRunning will be executed.

    NodeStatus onRunning(): called when the Node is in RUNNING state. Return the new status.

    void onHalted(): called when this Node was aborted by another Node in the tree.


2. Sequence VS ReactiveSequence

3. sleeps
`Tree::sleep() ` 
    - instead of `std::this_thread::sleep_for()`
    - interrupted when the method `TreeNode::emitStateChanged()` invoked.

##### Compose behaviors using Subtrees

```xml
<root BTCPP_format="4">

    <BehaviorTree ID="MainTree">
        <Sequence>
            <Fallback>
                <Inverter>
                    <IsDoorClosed/>
                </Inverter>
                <SubTree ID="DoorClosed"/>
            </Fallback>
            <PassThroughDoor/>
        </Sequence>
    </BehaviorTree>

    <BehaviorTree ID="DoorClosed">
        <Fallback>
            <OpenDoor/>
            <RetryUntilSuccessful num_attempts="5">
                <PickLock/>
            </RetryUntilSuccessful>
            <SmashDoor/>
        </Fallback>
    </BehaviorTree>
    
</root>
```

```c++

class CrossDoor
{
public:
    void registerNodes(BT::BehaviorTreeFactory& factory);

    // SUCCESS if _door_open != true
    BT::NodeStatus isDoorClosed();

    // SUCCESS if _door_open == true
    BT::NodeStatus passThroughDoor();

    // After 3 attempts, will open a locked door
    BT::NodeStatus pickLock();

    // FAILURE if door locked
    BT::NodeStatus openDoor();

    // WILL always open a door
    BT::NodeStatus smashDoor();

private:
    bool _door_open   = false;
    bool _door_locked = true;
    int _pick_attempts = 0;
};

// Helper method to make registering less painful for the user
void CrossDoor::registerNodes(BT::BehaviorTreeFactory &factory)
{
  factory.registerSimpleCondition(
      "IsDoorClosed", std::bind(&CrossDoor::isDoorClosed, this));

  factory.registerSimpleAction(
      "PassThroughDoor", std::bind(&CrossDoor::passThroughDoor, this));

  factory.registerSimpleAction(
      "OpenDoor", std::bind(&CrossDoor::openDoor, this));

  factory.registerSimpleAction(
      "PickLock", std::bind(&CrossDoor::pickLock, this));

  factory.registerSimpleCondition(
      "SmashDoor", std::bind(&CrossDoor::smashDoor, this));
}

int main()
{
  BehaviorTreeFactory factory;

  CrossDoor cross_door;
  cross_door.registerNodes(factory);

  // In this example a single XML contains multiple <BehaviorTree>
  // To determine which one is the "main one", we should first register
  // the XML and then allocate a specific tree, using its ID

  factory.registerBehaviorTreeFromText(xml_text);
  auto tree = factory.createTree("MainTree");

  // helper function to print the tree
  printTreeRecursively(tree.rootNode());

  tree.tickWhileRunning();

  return 0;
}

```

##### Remapping ports of a SubTrees

- `debugMessage`

    `tree.subtrees[0]->blackboard->debugMessage();`

##### How to use multiple XML files

1. Load multiple files manually (recommended)
```xml
#SubTree_A.xml
<root>
    <BehaviorTree ID="SubTreeA">
        <SaySomething message="Executing Sub_A" />
    </BehaviorTree>
</root>

#SubTree_B.xml
<root>
    <BehaviorTree ID="SubTreeB">
        <SaySomething message="Executing Sub_B" />
    </BehaviorTree>
</root>

#main_tree.xml
<root>
    <BehaviorTree ID="MainTree">
        <Sequence>
            <SaySomething message="starting MainTree" />
            <SubTree ID="SubTreeA" />
            <SubTree ID="SubTreeB" />
        </Sequence>
    </BehaviorTree>
</root>
```
```c++
int main()
{
  BT::BehaviorTreeFactory factory;
  factory.registerNodeType<DummyNodes::SaySomething>("SaySomething");

  // Find all the XML files in a folder and register all of them.
  // We will use std::filesystem::directory_iterator
  std::string search_directory = "./";

  using std::filesystem::directory_iterator;
  for (auto const& entry : directory_iterator(search_directory)) 
  {
    if( entry.path().extension() == ".xml")
    {
      factory.registerBehaviorTreeFromFile(entry.path().string());
    }
  }
  // This, in our specific case, would be equivalent to
  // factory.registerBehaviorTreeFromFile("./main_tree.xml");
  // factory.registerBehaviorTreeFromFile("./subtree_A.xml");
  // factory.registerBehaviorTreeFromFile("./subtree_B.xml");

  // You can create the MainTree and the subtrees will be added automatically.
  std::cout << "----- MainTree tick ----" << std::endl;
  auto main_tree = factory.createTree("MainTree");
  main_tree.tickWhileRunning();

  // ... or you can create only one of the subtrees
  std::cout << "----- SubA tick ----" << std::endl;
  auto subA_tree = factory.createTree("SubTreeA");
  subA_tree.tickWhileRunning();

  return 0;
}
/* Expected output:

Registered BehaviorTrees:
 - MainTree
 - SubTreeA
 - SubTreeB
----- MainTree tick ----
Robot says: starting MainTree
Robot says: Executing Sub_A
Robot says: Executing Sub_B
----- SubA tick ----
Robot says: Executing Sub_A
```


2. Add multiple files with "include"
```xml
<root BTCPP_format="4">
    <include path="./subtree_A.xml" />
    <include path="./subtree_B.xml" />
    <BehaviorTree ID="MainTree">
        <Sequence>
            <SaySomething message="starting MainTree" />
            <SubTree ID="SubTreeA" />
            <SubTree ID="SubTreeB" />
        </Sequence>
    </BehaviorTree>
</root>
```
`factory.createTreeFromFile("main_tree.xml")`


##### Pass additional arguments to your Nodes

using ports or the blackboard is highly discouraged:
- The arguments are known at deployment-time (when building the tree).
- The arguments don't change at run-time.
- The arguments don't need to be set from the XML.

1. Add arguments to your constructor (recommended)

```c++

// Action_A has a different constructor than the default one.
class Action_A: public SyncActionNode
{

public:
    // additional arguments passed to the constructor
    Action_A(const std::string& name, const NodeConfig& config,
             int arg_int, std::string arg_str):
        SyncActionNode(name, config),
        _arg1(arg_int),
        _arg2(arg_str) {}

    // this example doesn't require any port
    static PortsList providedPorts() { return {}; }

    // tick() can access the private members
    NodeStatus tick() override;

private:
    int _arg1;
    std::string _arg2;
};



BT::BehaviorTreeFactory factory;
factory.registerNodeType<Action_A>("Action_A", 42, "hello world");

// If you prefer to specify the template parameters
// factory.registerNodeType<Action_A, int, std::string>("Action_A", 42, "hello world");

```


2. Use an "initialize" method , then visitor
```c++
class Action_B: public SyncActionNode
{

public:
    // The constructor looks as usual.
    Action_B(const std::string& name, const NodeConfig& config):
        SyncActionNode(name, config) {}

    // We want this method to be called ONCE and BEFORE the first tick()
    void initialize(int arg_int, const std::string& arg_str)
    {
        _arg1 = arg_int;
        _arg2 = arg_str;
    }

    // this example doesn't require any port
    static PortsList providedPorts() { return {}; }

    // tick() can access the private members
    NodeStatus tick() override;

private:
    int _arg1;
    std::string _arg2;
};


BT::BehaviorTreeFactory factory;

// Register as usual, but we still need to initialize
factory.registerNodeType<Action_B>("Action_B");

// Create the whole tree. Instances of Action_B are not initialized yet
auto tree = factory.createTreeFromText(xml_text);

// visitor will initialize the instances of 
auto visitor = [](TreeNode* node)
{
  if (auto action_B_node = dynamic_cast<Action_B*>(node))
  {
    action_B_node->initialize(69, "interesting_value");
  }
};

// Apply the visitor to ALL the nodes of the tree
tree.applyVisitor(visitor);
```

##### Introduction to the Scripting language

Script and Precondition nodes

supported : numbers (integers and reals), strings and registered ENUM

magic_enums:default range is [-128, 127]

```xml
<root BTCPP_format="4">
  <BehaviorTree>
    <Sequence>
      <Script code=" msg:='hello world' " />
      <Script code=" A:=THE_ANSWER; B:=3.14; color:=RED " />
      <Precondition if="A>B && color != BLUE" else="FAILURE">
        <Sequence>
          <SaySomething message="{A}"/>
          <SaySomething message="{B}"/>
          <SaySomething message="{msg}"/>
          <SaySomething message="{color}"/>
        </Sequence>
      </Precondition>
    </Sequence>
  </BehaviorTree>
</root>

```

```c++
enum Color
{
  RED = 1,
  BLUE = 2,
  GREEN = 3
};

int main()
{
  BehaviorTreeFactory factory;
  factory.registerNodeType<DummyNodes::SaySomething>("SaySomething");

  // We can add these enums to the scripting language.
  // Check the limits of magic_enum
  factory.registerScriptingEnums<Color>();

  // Or we can manually assign a number to the label "THE_ANSWER".
  // This is not affected by any range limitation
  factory.registerScriptingEnum("THE_ANSWER", 42);

  auto tree = factory.createTreeFromText(xml_text);
  tree.tickWhileRunning();

  return 0;
}
```

##### The logger interface

BT.CPP provides a way to add loggers to a tree at run-time, usually, after the tree is created and before you start ticking it.

A "logger" is a class that has a callback invoked every time a TreeNode changes its status; it is a non-intrusive implementation of the so-called observer pattern.

More specifically, the callback that will be invoked is:
```c++
  virtual void callback(
    BT::Duration timestamp, // When the transition happened
    const TreeNode& node,   // the node that changed its status
    NodeStatus prev_status, // the previous status
    NodeStatus status);     // the new status
```

The TreeObserver class:
```c++
//The TreeObserver class
//a simple logger implementation that collects the following statistics for each node of the tree:

struct NodeStatistics
  {
    // Last valid result, either SUCCESS or FAILURE
    NodeStatus last_result;
    // Last status. Can be any status, including IDLE or SKIPPED
    NodeStatus current_status;
    // count status transitions, excluding transition to IDLE
    unsigned transitions_count;
    // count number of transitions to SUCCESS
    unsigned success_count;
    // count number of transitions to FAILURE
    unsigned failure_count;
    // count number of transitions to SKIPPED
    unsigned skip_count;
    // timestamp of the last transition
    Duration last_timestamp;
  };
```

How to uniquely identify a Node

Two mechanisms can be used:

- the `TreeNode::UID()` that is a unique number corresponding to the depth-first traversal of the tree.

- the `TreeNode::fullPath()` that aims to be a unique but human-readable identifier of a specific Node.

`first_subtree/nested_subtree/node_name`:
The "node_name" is either the name attribute assigned in the XML or is assigned automatically, using the Node registration followed by "::" and the UID.

Example:
```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <Sequence>
     <Fallback>
       <AlwaysFailure name="failing_action"/>
       <SubTree ID="SubTreeA" name="mysub"/>
     </Fallback>
     <AlwaysSuccess name="last_action"/>
    </Sequence>
  </BehaviorTree>

  <BehaviorTree ID="SubTreeA">
    <Sequence>
      <AlwaysSuccess name="action_subA"/>
      <SubTree ID="SubTreeB" name="sub_nested"/>
      <SubTree ID="SubTreeB" />
    </Sequence>
  </BehaviorTree>

  <BehaviorTree ID="SubTreeB">
    <AlwaysSuccess name="action_subB"/>
  </BehaviorTree>
</root>
```

```shell
# UID -> fullPath
1 -> Sequence::1
2 -> Fallback::2
3 -> failing_action
4 -> mysub
5 -> mysub/Sequence::5
6 -> mysub/action_subA
7 -> mysub/sub_nested
8 -> mysub/sub_nested/action_subB
9 -> mysub/SubTreeB::9
10 -> mysub/SubTreeB::9/action_subB
11 -> last_action
```

```c++
// The following application will:

//     Print the structure of the tree recursively.
//     Attach the TreeObserver to the tree.
//     Print the UID / fullPath pairs.
//     Collect the statistics of a specific node called "last_action".
//     Show all the statistics collected by the observer.

int main()
{
  BT::BehaviorTreeFactory factory;

  factory.registerBehaviorTreeFromText(xml_text);
  auto tree = factory.createTree("MainTree");

  // Helper function to print the tree.
  BT::printTreeRecursively(tree.rootNode());

  // The purpose of the observer is to save some statistics about the number of times
  // a certain node returns SUCCESS or FAILURE.
  // This is particularly useful to create unit tests and to check if
  // a certain set of transitions happened as expected
  BT::TreeObserver observer(tree);

  // Print the unique ID and the corresponding human readable path
  // Path is also expected to be unique.
  std::map<uint16_t, std::string> ordered_UID_to_path;
  for(const auto& [name, uid]: observer.pathToUID()) {
    ordered_UID_to_path[uid] = name;
  }

  for(const auto& [uid, name]: ordered_UID_to_path) {
    std::cout << uid << " -> " << name << std::endl;
  }


  tree.tickWhileRunning();

  // You can access a specific statistic, using is full path or the UID
  const auto& last_action_stats = observer.getStatistics("last_action");
  assert(last_action_stats.transitions_count > 0);

  std::cout << "----------------" << std::endl;
  // print all the statistics
  for(const auto& [uid, name]: ordered_UID_to_path) {
    const auto& stats = observer.getStatistics(uid);

    std::cout << "[" << name
              << "] \tT/S/F:  " << stats.transitions_count
              << "/" << stats.success_count
              << "/" << stats.failure_count
              << std::endl;
  }

  return 0;
}

```

##### Connect to Groot2

Groot2 is the official IDE to Edit, Monitor and interact with a Behavior Tree created with BT.CPP.

1. TreeNodesModel

Groot requires a "TreeNode model".
- The Node type
- Name and type (input/output) of ports.
```xml
  <TreeNodesModel>
    <Action ID="SaySomething">
      <input_port name="message"/>
    </Action>
    <Action ID="ThinkWhatToSay">
      <output_port name="text"/>
    </Action>
  </TreeNodesModel>
```

```c++
  BT::BehaviorTreeFactory factory;
  //
  // register here your user-defined Nodes
  // 
  std::string xml_models = BT::writeTreeNodesModelXML(factory);

  // this xml_models should be saved to file and 
  // loaded in Groot2
```

2. Adding real-time visualization to Groot

Note:Currently, only the PRO version of Groot2 supports real-time visualization.

Only one line: `BT::Groot2Publisher publisher(tree);`

```c++
// This will create an inter-process communication service between your BT.CPP executor and Groot2 that:

//     Sends the entire tree structure to Groot2, including the Models mentioned above.
//     Periodically updates the status of the individual Nodes (RUNNING, SUCCESS, FAILURE, IDLE).
//     Sends the value of the blackboard(s); basic types such as integers, reals and strings are supported out of the box, others need to be added manually.
//     Allows Groot2 to insert breakpoints, perform a Node substitution or fault injection.

#xml
<root BTCPP_format="4">

  <BehaviorTree ID="MainTree">
    <Sequence>
      <Script code="door_open:=false" />
      <Fallback>
        <Inverter>
          <IsDoorClosed/>
        </Inverter>
        <SubTree ID="DoorClosed" _autoremap="true" door_open="{door_open}"/>
      </Fallback>
      <PassThroughDoor/>
    </Sequence>
  </BehaviorTree>

  <BehaviorTree ID="DoorClosed">
    <Fallback name="tryOpen" _onSuccess="door_open:=true">
      <OpenDoor/>
        <RetryUntilSuccessful num_attempts="5">
          <PickLock/>
        </RetryUntilSuccessful>
      <SmashDoor/>
    </Fallback>
  </BehaviorTree>

</root>

#c++
int main()
{
  BT::BehaviorTreeFactory factory;

  // Our set of simple Nodes, related to CrossDoor
  CrossDoor cross_door;
  cross_door.registerNodes(factory);

  // Groot2 editor requires a model of your registered Nodes.
  // You don't need to write that by hand, it can be automatically
  // generated using the following command.
  std::string xml_models = BT::writeTreeNodesModelXML(factory);

  factory.registerBehaviorTreeFromText(xml_text);
  auto tree = factory.createTree("MainTree");

  // Connect the Groot2Publisher. This will allow Groot2 to
  // get the tree and poll status updates.
  BT::Groot2Publisher publisher(tree);

  // we want to run this indefinitely
  while(1)
  {
    std::cout << "Start" << std::endl;
    cross_door.reset();
    tree.tickWhileRunning();
    std::this_thread::sleep_for(std::chrono::milliseconds(3000));
  }
  return 0;
}

```

3. Visualize custom types in the Blackboard

The content inside the blackboard is sent to Groot2 using a JSON format.

Basic types (integers, reals, strings) are supported out of the box. To allow Groot2 to visualize your own custom types, you need to include behaviortree_cpp/json_export.h and define a JSON converter.

- Using the BT_JSON_CONVERTER macro (recommended)
```c++
struct Position2D
{
  double x;
  double y;
};

#include "behaviortree_cpp/json_export.h"

BT_JSON_CONVERTER(Position2D, pos)
{
  add_field("x", &pos.x);
  add_field("y", &pos.y);
}

struct Waypoint
{
  std::string name;
  Position2D position;
  double speed = 1.0;
};

BT_JSON_CONVERTER(Waypoint, wp)
{
  add_field("name", &wp.name);
  add_field("position", &wp.position);
  add_field("speed", &wp.speed);
}

//register the types in your main (before creating the tree):
BT::RegisterJsonDefinition<Position2D>();
BT::RegisterJsonDefinition<Waypoint>();

```

- Manual converter (alternative)
```c++
void PositionToJson(nlohmann::json& dest, const Position2D& pos) {
  dest["x"] = pos.x;
  dest["y"] = pos.y;
}

// in main()
BT::RegisterJsonDefinition<Position2D>(PositionToJson);
```


#### Tutorials(Advanced)

##### Default Port values

1. Default values

```c++
BT::InputPort<Point2D>("pointB", "3,4", "..."); //convertFromString<Point2D>()
// should be equivalent to:
BT::InputPort<Point2D>("pointB", Point2D{3, 4}, "...");
```

2. Default blackboard entry

```c++
//If the name of the port and the blackboard entry are the same, you can use "{=}"
BT::InputPort<Point2D>("pointD", "{=}", "...");
// equivalent to:
BT::InputPort<Point2D>("pointD", "{pointD}", "...");
```

3. Default OutputPorts

```c++
//only point to a blackboard entry. 
//use "{=}" when the two names are the same.
BT::OutputPort<Point2D>("result", "{target}", "point by default to BB entry {target}");
```


##### Zero-copy access to the blackboard

- Blackboard uses value semantic
- the methods `getInput` and `setOutput` copy the value from/to the blackboard
- reference semantic, access the object stored in the Blackboard directly


Method
- Method 1: Blackboard entries as Share pointers, use `shared_ptr` to wrap data [NOT thread safe]
- Method 2: thread-safe castPtr (recommended since version 4.5.1), use `getLockedPortContent()`

```c++
PortsList AcquirePointCloud::providedPorts()
{
    return { OutputPort<Pointcloud>("cloud") };
}

PortsList SegmentObject::providedPorts()
{
    return { InputPort<std::string>("obj_name"),
             InputPort<Pointcloud>("cloud"),
             OutputPort<Pose3D>("obj_pose") };
}


// inside the scope below, as long as "any_locked" exists, a mutex protecting 
// the instance of "cloud" will remain locked
if(auto any_locked = getLockedPortContent("cloud"))
{
  if(any_locked->empty())
  {
    // the entry in the blackboard hasn't been initialized yet.
    // You can initialize it doing:
    any_locked.assign(my_initial_pointcloud);
  }
  else if(Pointcloud* cloud_ptr = any_locked->castPtr<Pointcloud>())
  {
    // Succesful cast to Pointcloud* (original type).
    // Modify the pointcloud instance, using cloud_ptr
  }
}
```

##### Subtree Models and autoremap

TreeNodesModel

```xml
# every SubTree need copy the following part
<SubTree ID="MoveRobot" target="{target}"  frame="{frame}" result="{result}" />


# define default values in <TreeNodesModel>
  <TreeNodesModel>
    <SubTree ID="MoveRobot">
      <input_port  name="target"  default="{move_goal}"/>
      <input_port  name="frame"   default="world"/>
      <output_port name="result"  default="{error_code}"/>
    </SubTree>
  </TreeNodesModel>


# overriding the value of "frame", but keeping the default remapping otherwise.
<SubTree ID="MoveRobot" frame="map" />

```

Autoremap

```xml
<SubTree ID="MoveRobot" target="{target}"  frame="{frame}" result="{result}" />

# Can be Replaced by
<SubTree ID="MoveRobot" _autoremap="true" />

# override a specific value, and autoremap the others
<SubTree ID="MoveRobot" _autoremap="true" frame="world" />

```

The attribute `_autoremap="true"` will automatically remap all the entries in the SubTree, unless their name start with an underscore (character "_").

This could be a convenient way to mark an entry in a SubTree as "private".

##### Mock testing in BT.CPP

An example

```shell
# Given example
<SaySomething name="talk" message="hello world"/>

# called after the nodes are registered and before the actual tree is instantiated.
# substitute this node with TestMessage:
factory.addSubstitutionRule("talk", "TestMessage"); //First parameter is TreeNode::fullPath
```

The TestNode is an Action that can be configured to:

- return a specific status, either SUCCESS or FAILURE
- be synchronous or asynchronous; in the latter case, a timeout should be specified.
- a post-condition script, generally used to simulate an OutputPort.

This simple dummy Node will not cover 100% of the cases, but can be the default solution for many substitution rules.



Full example:

- We can use the substitution rule to substitute a node with another one.
- How to use the built-in TestNode.
- Examples of wildcard matching.
- How to pass these rules using a JSON file, at run-time.

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <SaySomething name="talk" message="hello world"/>
        <Fallback>
          <AlwaysFailure name="failing_action"/>
          <SubTree ID="MySub" name="mysub"/>
        </Fallback>
        <SaySomething message="before last_action"/>
        <Script code="msg:='after last_action'"/>
        <AlwaysSuccess name="last_action"/>
        <SaySomething message="{msg}"/>
    </Sequence>
  </BehaviorTree>

  <BehaviorTree ID="MySub">
    <Sequence>
      <AlwaysSuccess name="action_subA"/>
      <AlwaysSuccess name="action_subB"/>
    </Sequence>
  </BehaviorTree>
</root>
```

```c++
int main(int argc, char** argv)
{
  BT::BehaviorTreeFactory factory;
  factory.registerNodeType<SaySomething>("SaySomething");

  // We use lambdas and registerSimpleAction, to create
  // a "dummy" node, that we want to substitute to a given one.

  // Simple node that just prints its name and return SUCCESS
  factory.registerSimpleAction("DummyAction", [](BT::TreeNode& self){
    std::cout << "DummyAction substituting: "<< self.name() << std::endl;
    return BT::NodeStatus::SUCCESS;
  });

  // Action that is meant to substitute SaySomething.
  // It will try to use the input port "message"
  factory.registerSimpleAction("TestSaySomething", [](BT::TreeNode& self){
    auto msg = self.getInput<std::string>("message");
    if (!msg)
    {
      throw BT::RuntimeError( "missing required input [message]: ", msg.error() );
    }
    std::cout << "TestSaySomething: " << msg.value() << std::endl;
    return BT::NodeStatus::SUCCESS;
  });

  //----------------------------
  // pass "no_sub" as first argument to avoid adding rules
  bool skip_substitution = (argc == 2) && std::string(argv[1]) == "no_sub";

  if(!skip_substitution)
  {
    // we can use a JSON file to configure the substitution rules
    // or do it manually
    bool const USE_JSON = true;

    if(USE_JSON)
    {
      factory.loadSubstitutionRuleFromJSON(json_text);
    }
    else {
      // Substitute nodes which match this wildcard pattern with TestAction
      factory.addSubstitutionRule("mysub/action_*", "TestAction");

      // Substitute the node with name [talk] with TestSaySomething
      factory.addSubstitutionRule("talk", "TestSaySomething");

      // This configuration will be passed to a TestNode
      BT::TestNodeConfig test_config;
      // Convert the node in asynchronous and wait 2000 ms
      test_config.async_delay = std::chrono::milliseconds(2000);
      // Execute this postcondition, once completed
      test_config.post_script = "msg ='message SUBSTITUED'";

      // Substitute the node with name [last_action] with a TestNode,
      // configured using test_config
      factory.addSubstitutionRule("last_action", test_config);
    }
  }

  factory.registerBehaviorTreeFromText(xml_text);

  // During the construction phase of the tree, the substitution
  // rules will be used to instantiate the test nodes, instead of the
  // original ones.
  auto tree = factory.createTree("MainTree");
  tree.tickWhileRunning();

  return 0;
}
```

```json
//The JSON file, equivalent to the branch executed when USE_JSON == false is:
{
  "TestNodeConfigs": {
    "MyTest": {
      "async_delay": 2000,
      "return_status": "SUCCESS",
      "post_script": "msg ='message SUBSTITUED'"
    }
  },

  "SubstitutionRules": {
    "mysub/action_*": "TestAction",
    "talk": "TestSaySomething",
    "last_action": "MyTest"
  }
}
```

two main sections:

- TestNodeConfigs, where the parameters and name of one or multiple TestNode are set.

- SubstitutionRules where the actual rules are specified.


##### The global blackboard idiom

1. An external "global blackboard":

```c++
auto global_bb = BT::Blackboard::create();
auto maintree_bb = BT::Blackboard::create(global_bb);
auto tree = factory.createTree("MainTree", maintree_bb);
```

The instance global_bb lives "outside" the behavior tree and will persist if the object tree is destroyed.

Furthermore, it can be easily accessed using set and get methods.


2. Access the top-level blackboard from the tree: without remapping, by adding the prefix @ to the name of the entry.
    `<PrintNumber val="{@value}" />`


3. Full example

```xml
  <BehaviorTree ID="MainTree">
    <Sequence>
      <PrintNumber name="main_print" val="{@value}" />
      <SubTree ID="MySub"/>
    </Sequence>
  </BehaviorTree>

  <BehaviorTree ID="MySub">
    <Sequence>
      <PrintNumber name="sub_print" val="{@value}" />
      <Script code="@value_sqr := @value * @value" />
    </Sequence>
  </BehaviorTree>
```

```c++
class PrintNumber : public BT::SyncActionNode
{
public:
  PrintNumber(const std::string& name, const BT::NodeConfig& config)
    : BT::SyncActionNode(name, config)
  {}
  
  static BT::PortsList providedPorts()
  {
    return { BT::InputPort<int>("val") };
  }

  NodeStatus tick() override
  {
    const int val = getInput<int>("val").value();
    std::cout << "[" << name() << "] val: " << val << std::endl;
    return NodeStatus::SUCCESS;
  }
};

int main()
{
  BehaviorTreeFactory factory;
  factory.registerNodeType<PrintNumber>("PrintNumber");
  factory.registerBehaviorTreeFromText(xml_main);

  // No one will take the ownership of this blackboard
  auto global_bb = BT::Blackboard::create();
  // "MainTree" will own maintree_bb
  auto maintree_bb = BT::Blackboard::create(global_bb);
  auto tree = factory.createTree("MainTree", maintree_bb);

  // we can interact directly with global_bb
  for(int i = 1; i <= 3; i++)
  {
    // write the entry "value"
    global_bb->set("value", i);
    // tick the tree
    tree.tickOnce();
    // read the entry "value_sqr"
    auto value_sqr = global_bb->get<int>("value_sqr");
    // print 
    std::cout << "[While loop] value: " << i 
              << " value_sqr: " << value_sqr << "\n\n";
  }
  return 0;
}
```

```bash
[main_print] val: 1
[sub_print] val: 1
[While loop] value: 1 value_sqr: 1

[main_print] val: 2
[sub_print] val: 2
[While loop] value: 2 value_sqr: 4

[main_print] val: 3
[sub_print] val: 3
[While loop] value: 3 value_sqr: 9
```

Notes:

- The prefix "@" works both when used in an Input / Output Port or in the scripting language.
- No remapping is needed in the Subtrees.
- When accessing the blackboard directly in the main loop, no prefix "@" is needed.


#### Guides

##### Introduction to Scripting

a scripting language within XML.

The implemented scripting language has a familiar syntax; it allows the user to quickly read from / write to the variables of the blackboard.

1. Assignment operators, strings and numbers

```xml
param_A := 42
param_B = 3.14
message = 'hello world'

///The difference between the operator ":=" and "=" is that the former may create a new entry in the blackboard, if it doesn't exist, whilst the latter will throw an exception if the blackboard doesn't contain the entry.

A:= 42; B:=24  //use semicolons to add multiple commands in a single script
```
2. Arithmetic operators and parenthesis

```xml
param_A := 7
param_B := 5
param_B *= 2
param_C := (param_A * 3) + param_B

//The resulting values of param_B is 10 and param_C is 31.
```

|Operator	|Assign Operator	|Description|
|:---|:---|:---|
|+	|+=	|Add|
|-	|-=	|Subtract|
|*	|*=	|Multiply|
|/	|/=	|Divide|


Note that the addition operator is the only one that also works with string (used to concatenate two strings).

3. Bitwise operator and hexadecimal numbers

These operators work only if the value can be cast to an integer number.

Using them with a string or real number will cause an exception.

```xml
value:= 0x7F
val_A:= value & 0x0F
val_B:= value | 0xF0

//The value of val_A is 0x0F (or 15); val_B is 0xFF (or 255).
```

|Binary |Operators	|Description|
|:---|:---|:---|
|\|	|Bitwise |or|
|&	|Bitwise |and|
|^	|Bitwise |xor|


|Unary Operators|	Description|
|:---|:---|
|~	|Negate|

4. Logic and comparison operators

Operators which return a boolean.

```xml
val_A := true
val_B := 5 > 3
val_C := (val_A == val_B)
val_D := (val_A && val_B) || !val_C
```

|Operators	|Description|
|:---|:---|
|true/false	|Booleans. Castable to 1 and 0 respectively|
|&&	|Logic and|
||	|Logic or|
|!	|Negation|
|==	|Equality|
|!=	|Inequality|
|<	|Less|
|<=	|Less equal|
|>	|Greater|
|>=	|Greater equal|

Ternary operator if-then-else : `val_B = (val_A > 1) ? 42 : 24`

5. Boolean Values

Boolean values can be one of true or false and are saved to the blackboard as 1 and 0 respectively.

```xml
val_A = true
val_B := !false
//The logical ! works with boolean literals. !false is the equivalent of true. val_A and val_B above are equivalent.
```

```xml
<Precondition if="val_A" else="FAILURE">
<Precondition if="val_A == true" else="FAILURE">
<Precondition if="val_A == 1" else="FAILURE">
```

Note that capitalization of the words "true" and "false" in any manner will not work.

6. C++ example

Demonstration of the scripting language, including how to use enums to represent integer values.

```xml
<root >
    <BehaviorTree>
        <Sequence>
            <Script code=" msg:='hello world' " />
            <Script code=" A:=THE_ANSWER; B:=3.14; color:=RED " />
            <Precondition if="A>B && color!=BLUE" else="FAILURE">
                <Sequence>
                  <SaySomething message="{A}"/>
                  <SaySomething message="{B}"/>
                  <SaySomething message="{msg}"/>
                  <SaySomething message="{color}"/>
                </Sequence>
            </Precondition>
        </Sequence>
    </BehaviorTree>
</root>
```

```c++
int main()
{
  // Simple tree: a sequence of two asynchronous actions,
  // but the second will be halted because of the timeout.

  BehaviorTreeFactory factory;
  factory.registerNodeType<SaySomething>("SaySomething");

  enum Color { RED=1, BLUE=2, GREEN=3 };
  // We can add these enums to the scripting language
  factory.registerScriptingEnums<Color>();

  // Or we can do it manually
  factory.registerScriptingEnum("THE_ANSWER", 42);

  auto tree = factory.createTreeFromText(xml_text);
  tree.tickWhileRunning();
  return 0;
}
```

```bash
Robot says: 42.000000
Robot says: 3.140000
Robot says: hello world
Robot says: 1.000000
```


##### Pre and Post conditions

scripts that can run either before or after the actual tick() of a Node.

Pre and Post conditions are supported by all the nodes and don't need any modifications in your C++ code.

1. Pre conditions

|Name	|Description	|When Evaluated|
|:---|:---|:---|
|_skipIf	|Skip the execution of this Node, if the condition is true	|IDLE only (once)|
|_failureIf	|Skip and return FAILURE, if the condition is true	|IDLE only (once)|
|_successIf	|Skip and return SUCCESS, if the condition is true	|IDLE only (once)|
|_while	|If false when IDLE, skip. If false when RUNNING, halt the node and return SKIPPED.	|IDLE and RUNNING (every tick)|

`_skipIf, _failureIf, and _successIf` are evaluated only once when the node transitions from IDLE to another state. They are NOT re-evaluated while the node is RUNNING.

Only _while is checked on every tick, including while the node is running.

If you need a condition to be re-evaluated on every tick, use the `<Precondition>` decorator node with `else="RUNNING"` instead of these attributes.


Pre conditions are evaluated in this order: `_failureIf -> _successIf -> _skipIf -> _while`. The first condition that is satisfied will determine the result.


2. Post conditions

|Name	|Description|
|:---|:---|
|_onSuccess	|Execute this script, if the Node returned SUCCESS|
|_onFailure	|Execute this script, if the Node returned FAILURE|
|_post	|Execute this script, if the Node returned either SUCCESS or FAILURE|
|_onHalted	|Script executed if a RUNNING Node was halted|


##### Asynchronous Actions

two main concepts:
- what we mean by "Asynchronous" Actions VS "Synchronous" ones.
- The difference between Concurrency and Parallelism in the context of BT.CPP.

1. Concurrency vs Parallelism

Concurrency is when two or more tasks can start, run, and complete in overlapping time periods. It doesn't necessarily mean they'll ever both be running at the same instant.

Parallelism is when tasks run at the same time in different threads, e.g., on a multicore processor.

BT.CPP executes all the nodes concurrently. In other words:
- The Tree execution engine is single-threaded.
- All the tick() methods are executed sequentially.
- If any tick() method is blocking, the entire flow of execution will be blocked.


2. Asynchronous vs Synchronous

In general, an Asynchronous Node is one that:
- May return RUNNING instead of SUCCESS or FAILURE, when ticked.
- Can be stopped as fast as possible when the method halt() is invoked.

Frequently, the method `halt()` must be implemented by the developer.

- `StatefulActionNode`


3. Avoid blocking the execution of the tree

4. The problem with multi-threading

```c++
// I will create my own thread here, for no good reason
class ThreadedSleepNode : public BT::ThreadedAction
{
  public:
    ThreadedSleepNode(const std::string& name, const BT::NodeConfig& config)
      : BT::ThreadedAction(name, config)
    {}

    static BT::PortsList providedPorts()
    {
      return{ BT::InputPort<int>("msec") };
    }

    NodeStatus tick() override
    {  
      // This code runs in its own thread, therefore the Tree is still running.
      int msec = 0;
      getInput("msec", msec);

      using namespace std::chrono;
      const auto deadline = system_clock::now() + milliseconds(msec);

      // Periodically check isHaltRequested() 
      // and sleep for a small amount of time only (1 millisecond)
      while( !isHaltRequested() && system_clock::now() < deadline )
      {
        std::this_thread::sleep_for( std::chrono::milliseconds(1) );
      }
      return NodeStatus::SUCCESS;
    }

    // The halt() method will set isHaltRequested() to true 
    // and stop the while loop in the spawned thread.
};
```
As you can see, this looks more complicated than the version we implemented first, using BT::StatefulActionNode. This pattern can still be useful in some case, but you must remember that introducing multi-threading makes things more complicated and should be avoided by default.

5. Advanced example: client / server communication

Frequently, people using BT.CPP execute the actual task in a different process.

A typical (and recommended) way to do this in ROS is using ActionLib.

More generally, we may assume that the developer has their own inter-process communication, with a client/server relationship between the BT executor and the actual service provider.


##### Ports VS Blackboard

Input/Output Ports, as an alternative to Blackboards.

Summary: never use the Blackboard directly
```c++
/// should do 
// example code in your tick()
getInput("goal", goal);
setOutput("result", result);


/// avoid as much as possible
// example code in your tick()
config().blackboard->get("goal", goal);
config().blackboard->set("result", result);
```


#### Nodes Library

##### Parallel Nodes

Parallel nodes execute all their children concurrently, but not in separate threads. All children are ticked in sequence within a single tick of the tree, and multiple children may be in the RUNNING state at the same time.

"Parallel" refers to the fact that multiple children can be RUNNING concurrently. The children are still ticked sequentially within the same thread. For actual multi-threaded execution, children must be asynchronous nodes internally.

Currently the framework provides two kinds of nodes:

- Parallel
- ParallelAll

The Parallel Nodes are the only ones that can have multiple children RUNNING at the same time.


1. Parallel

It is completed when either the SUCCESS or FAILURE threshold is reached. Any remaining running children are halted.

| Port           | Type             | Default | Description                                                              |
| :------------- | :--------------- | :------ | :----------------------------------------------------------------------- |
| success_count  | InputPort<int>   | -1      | Number of children that must succeed to return SUCCESS.                 |
| failure_count  | InputPort<int>   | 1       | Number of children that must fail to return FAILURE.                     |

Threshold values support Python-style negative indexing: -1 is equivalent to the total number of children. For example, with 4 children, success_count="-1" means all 4 must succeed.

Default behavior (success_count=-1, failure_count=1): all children must succeed; if any single child fails, the node returns FAILURE.

```xml
# Example
<Parallel success_count="2" failure_count="2">
    <ActionA/>
    <ActionB/>
    <ActionC/>
</Parallel>

#In this example with 3 children:
#    If 2 children return SUCCESS (before 2 fail), the node returns SUCCESS.
#    If 2 children return FAILURE (before 2 succeed), the node returns FAILURE.
#    Remaining RUNNING children are halted when either threshold is reached.
```

2. ParallelAll

Unlike Parallel, the ParallelAll node always executes ALL children to completion. It never halts children early. This is useful when you need all side effects to complete.

| Port         | Type           | Default | Description                                                              |
| :----------- | :------------- | :------ | :----------------------------------------------------------------------- |
| max_failures | InputPort<int> | 1       | Maximum number of child failures allowed before returning FAILURE.        |

- Returns SUCCESS if the number of FAILUREs is less than max_failures.
- Returns FAILURE if the number of FAILUREs equals or exceeds max_failures.
- Use max_failures="-1" (number of children) to always return SUCCESS regardless of child results.

```xml
# Example
<ParallelAll max_failures="2">
    <ActionA/>
    <ActionB/>
    <ActionC/>
</ParallelAll>
```

3. Parallel vs ParallelAll

| Feature             | Parallel                                             | ParallelAll                                  |
| :------------------ | :--------------------------------------------------- | :------------------------------------------- |
| Early termination  | Yes (halts children when threshold reached)          | No (always runs all children)                |
| Success threshold   | Configurable (success_count)                         | All non-failed children                      |
| Failure threshold   | Configurable (failure_count)                         | Configurable (max_failures)                  |
| Use case            | Race conditions, N-of-M success                     | All tasks must attempt completion            |


##### Conditional Control Nodes

These control nodes select which child to execute based on the result of a condition (the first child).

Currently the framework provides two kinds:

- IfThenElse
- WhileDoElse

Both must have exactly 2 or 3 children.


1. IfThenElse

IfThenElse is a non-reactive conditional node.

- The 1st child is the condition ("if").
- The 2nd child is executed if the condition returns SUCCESS ("then").
- The 3rd child (optional) is executed if the condition returns FAILURE ("else").

If only 2 children are provided and the condition returns FAILURE, the node returns FAILURE (equivalent to having AlwaysFailure as the 3rd child).

The condition is evaluated only once. If the 2nd or 3rd child returns RUNNING, the condition is not re-evaluated on subsequent ticks.

```xml
<IfThenElse>
    <IsDoorOpen/>          <!-- condition -->
    <WalkThrough/>         <!-- then branch -->
    <TryAnotherPath/>      <!-- else branch (optional) -->
</IfThenElse>
```

2. WhileDoElse

WhileDoElse is the reactive variant of IfThenElse. It re-evaluates the condition at every tick.

- The 1st child is the condition, evaluated on every tick ("while").
- The 2nd child is executed while the condition returns SUCCESS ("do").
- The 3rd child (optional) is executed while the condition returns FAILURE ("else").

If the 2nd or 3rd child is RUNNING and the condition result changes, the running child is halted before switching to the other branch.

```xml
<WhileDoElse>
    <IsBatteryOK/>         <!-- condition, re-evaluated each tick -->
    <ContinueMission/>     <!-- do branch -->
    <GoToChargingStation/> <!-- else branch (optional) -->
</WhileDoElse>
```

3. IfThenElse vs WhileDoElse

| Feature                                  | IfThenElse | WhileDoElse        |
| :--------------------------------------- | :--------- | :----------------- |
| Re-evaluates condition?                  | No         | Yes (every tick)   |
| Reactive                                 | No         | Yes                |
| Halts running child on condition change? | N/A        | Yes                |
| Use case                                 | One-time branching | Continuous monitoring |


##### Switch Node

The SwitchNode is equivalent to a switch statement: it selects which child to execute based on the value of a blackboard variable.

Available variants: Switch2, Switch3, Switch4, Switch5, Switch6, where the number indicates how many case branches are supported.

A SwitchN node must have exactly N + 1 children: N case branches plus one default branch (always the last child).

| Port     | Type               | Description                                   |
| :------- | :----------------- | :-------------------------------------------- |
| variable | InputPort<string>  | The blackboard variable to compare against cases. |
| case_1   | InputPort<string>  | Value to match for the 1st child.             |
| case_2   | InputPort<string>  | Value to match for the 2nd child.             |
| ...      | ...                | Additional cases up to N.                     |

The variable value is compared to each case_N string in order. The child corresponding to the first match is executed. If no case matches, the last child (the default branch) is executed.

Comparison supports strings, integers, and doubles. Enum values registered via ScriptingEnumsRegistry are also supported.

```xml
<Switch3 variable="{robot_state}" case_1="IDLE" case_2="WORKING" case_3="ERROR">
    <HandleIdle/>          <!-- executed when robot_state == "IDLE" -->
    <HandleWorking/>       <!-- executed when robot_state == "WORKING" -->
    <HandleError/>         <!-- executed when robot_state == "ERROR" -->
    <HandleUnknownState/>  <!-- default: executed when no case matches -->
</Switch3>
```

If a previously matched child is RUNNING and the variable value changes on a subsequent tick, the running child is halted before the newly matched child is executed.


##### Decorators

A decorator is a node that must have a single child.

It is up to the Decorator to decide if, when and how many times the child should be ticked.

###### Inverter

Tick the child once and return SUCCESS if the child failed or FAILURE if the child succeeded.

If the child returns RUNNING, this node returns RUNNING too.

###### ForceSuccess

If the child returns RUNNING, this node returns RUNNING too.

Otherwise, it returns always SUCCESS.

###### ForceFailure

If the child returns RUNNING, this node returns RUNNING too.

Otherwise, it returns always FAILURE.

###### Repeat

Tick the child up to N times, as long as the child returns SUCCESS.

| Port        | Type           | Default    | Description                                      |
| :---------- | :------------- | :--------- | :----------------------------------------------- |
| num_cycles  | InputPort<int> | (required) | Number of repetitions. Use -1 for infinite loop.  |

- Returns SUCCESS after all N repetitions complete successfully.
- Returns FAILURE immediately if the child returns FAILURE (loop is interrupted).
- Returns RUNNING if the child returns RUNNING; the counter is not incremented and the same iteration resumes on the next tick.
- If the child returns SKIPPED, the child is reset but the counter is not incremented.

```xml
<Repeat num_cycles="3">
    <ClapYourHandsOnce/>
</Repeat>
```

###### RetryUntilSuccessful

Tick the child up to N times, as long as the child returns FAILURE.

| Port         | Type           | Default    | Description                                       |
| :----------- | :------------- | :--------- | :------------------------------------------------ |
| num_attempts | InputPort<int> | (required) | Number of attempts. Use -1 for infinite retries.  |

- Returns SUCCESS immediately if the child returns SUCCESS (loop is interrupted).
- Returns FAILURE after all N attempts are exhausted.
- Returns RUNNING if the child returns RUNNING; the attempt counter is not  incremented and the same iteration resumes on the next tick.
- If the child returns SKIPPED, the child is reset and SKIPPED is returned.

```xml
<RetryUntilSuccessful num_attempts="3">
    <OpenDoor/>
</RetryUntilSuccessful>
```

###### KeepRunningUntilFailure

The KeepRunningUntilFailure node returns always FAILURE (FAILURE in child) or RUNNING (SUCCESS or RUNNING in child).

###### Delay

Tick the child after a specified time has passed. The delay is specified as Input Port `delay_msec`. If the child returns RUNNING, this node returns RUNNING too and will tick the child on next tick of the Delay node. Otherwise, return the status of the child node.

###### Timeout

Halt a running child if it has been RUNNING longer than a given duration. This is the opposite of Delay: while Delay waits before ticking the child, Timeout interrupts a child that takes too long.

| Port | Type                  | Default    | Description                               |
| :--- | :-------------------- | :--------- | :---------------------------------------- |
| msec | InputPort<unsigned>   | (required) | Timeout duration in milliseconds.         |

- If the child completes (SUCCESS or FAILURE) before the timeout, its status is returned.
- If the child is still RUNNING when the timeout expires, it is halted and FAILURE is returned.

```xml
<Timeout msec="5000">
    <KeepYourBreath/>
</Timeout>
```

```xml
# Combine Timeout with RetryUntilSuccessful for a robust retry-with-timeout pattern:
<RetryUntilSuccessful num_attempts="3">
    <Timeout msec="5000">
        <LongRunningAction/>
    </Timeout>
</RetryUntilSuccessful>
```

###### RunOnce

The RunOnce node is used when you want to execute the child only once. If the child is asynchronous, it will tick until either SUCCESS or FAILURE is returned.

After that first execution, you can set value of the Input Port `then_skip` to:

- TRUE (default), the node will be skipped in the future.
- FALSE, return synchronously the same status returned by the child, forever.


###### Precondition

The Precondition decorator evaluates a script condition before ticking its child.


| Port | Type                      | Default    | Description                                  |
| :--- | :------------------------ | :--------- | :------------------------------------------- |
| if   | InputPort<std::string>    | (required) | Script condition to evaluate                 |
| else | InputPort<NodeStatus>     | FAILURE    | Status to return if condition is false       |

- If the condition is true, the child is ticked.
- If the condition is false, the node returns the status specified in else.
- Once the child starts (returns RUNNING), the condition is not re-evaluated until the child completes.

```xml
<Precondition if="battery_level > 20" else="FAILURE">
    <MoveToGoal/>
</Precondition>
```

If you need the condition to be checked on every tick while the child is running (e.g., to interrupt a running action when a condition changes), use `else="RUNNING"`:
```xml
<Precondition if="battery_ok" else="RUNNING">
    <LongRunningAction/>
</Precondition>
```
With `else="RUNNING"`, if the condition becomes false, the decorator returns RUNNING instead of FAILURE, allowing the tree to continue ticking and re-check the condition.


###### SubTree

###### Other decorators requiring registration in C++

SimpleDecoratorNode

Register a simple decorator node with `void BehaviorTreeFactory::registerSimpleDecorator("MyDecorator", tick_function, ports)`, which uses `SimpleDecoratorNode` internally and where `tick_function` is a function with signature `std::function<NodeStatus(NodeStatus, TreeNode&)>` and ports is a variable of type `PortsList`.



##### Fallbacks (Controls)

This family of nodes are known as "Selector" or "Priority" in other frameworks.

Their purpose is to try different strategies, until we find one that "works".

Currently the framework provides three kinds of nodes:

- Fallback
- AsyncFallback
- ReactiveFallback

They share the following rules:

- Before ticking the first child, the node status becomes RUNNING.
- If a child returns FAILURE, the fallback ticks the next child.
- If the last child returns FAILURE too, all the children are halted and the fallback returns FAILURE.
- If a child returns SUCCESS, it stops and returns SUCCESS. All the children are halted.


1. Synchronous vs Asynchronous

Fallback and AsyncFallback share the same logic, but differ in how they handle the transition between children:

- Fallback ticks all children in a single tick of the tree. When a child returns FAILURE, the next child is ticked immediately within the same call.
- AsyncFallback yields execution back to the tree after each child fails, returning RUNNING and emitting a wake-up signal. This makes the fallback interruptible between children, allowing other parts of the tree (e.g., a ReactiveSequence parent) to re-evaluate conditions before the next child starts.

| Type of ControlNode | Child returns RUNNING | Yields between children |
| :------------------ | :-------------------- | :---------------------- |
| Fallback            | Tick again            | No                      |
| AsyncFallback       | Tick again            | Yes                     |
| ReactiveFallback    | Restart               | No                      |



- "Restart" means that the entire fallback is restarted from the first child of the list.

- "Tick again" means that the next time the fallback is ticked, the same child is ticked again. Previous siblings, which returned FAILURE already, are not ticked again.


2. Fallback

3. AsyncFallback

AsyncFallback behaves like Fallback, but yields execution back to the tree after each child returns FAILURE. It returns RUNNING and emits a wake-up signal, allowing a reactive parent to re-evaluate conditions before the next child is ticked.

```xml
<ReactiveSequence>
    <IsRobotHungry/>
    <AsyncFallback>
        <FindFoodInBackpack/>
        <FindNearbyRestaurant/>
        <OrderFoodDelivery/>
    </AsyncFallback>
</ReactiveSequence>
```

In this example, IsRobotHungry is re-checked between each attempt of the AsyncFallback. If the robot is no longer hungry after FindFoodInBackpack fails, the fallback is interrupted before FindNearbyRestaurant starts.

4. ReactiveFallback

This ControlNode is used when we want to interrupt an asynchronous child if one of the previous Conditions changes its state from FAILURE to SUCCESS.



##### Sequences

A Sequence ticks all its children as long as they return SUCCESS. If any child returns FAILURE, the sequence is aborted.

Currently the framework provides four kinds of nodes:

- Sequence
- AsyncSequence
- SequenceWithMemory
- ReactiveSequence


They share the following rules:

- Before ticking the first child, the node status becomes RUNNING.
- If a child returns SUCCESS, it ticks the next child.
- If the last child returns SUCCESS too, all the children are halted and the sequence returns SUCCESS.


1. Synchronous vs Asynchronous

Sequence and AsyncSequence share the same logic, but differ in how they handle the transition between children:

- Sequence ticks all children in a single tick of the tree. When a child returns SUCCESS, the next child is ticked immediately within the same call.
- AsyncSequence yields execution back to the tree after each child succeeds, returning RUNNING and emitting a wake-up signal. This makes the sequence interruptible between children, allowing other parts of the tree (e.g., a ReactiveSequence parent) to re-evaluate conditions before the next child starts.


Use AsyncSequence when the sequence is inside a reactive parent and you need conditions to be re-checked between each step.

| Type of ControlNode | Child returns FAILURE | Child returns RUNNING | Yields between children |
| :------------------ | :-------------------- | :-------------------- | :---------------------- |
| Sequence            | Restart               | Tick again           | No                      |
| AsyncSequence       | Restart               | Tick again           | Yes                     |
| ReactiveSequence    | Restart               | Restart              | No                      |
| SequenceWithMemory  | Tick again            | Tick again           | No                      |


- "Restart" means that the entire sequence is restarted from the first child of the list.

- "Tick again" means that the next time the sequence is ticked, the same child is ticked again. Previous siblings, which returned SUCCESS already, are not ticked again.


2. Sequence


3. AsyncSequence

AsyncSequence behaves like Sequence, but yields execution back to the tree after each child returns SUCCESS. It returns RUNNING and emits a wake-up signal, allowing a reactive parent to re-evaluate conditions before the next child is ticked.

```xml
<ReactiveSequence>
    <IsEnemyVisible/>
    <AsyncSequence>
        <AimWeapon/>
        <FireWeapon/>
        <ReloadWeapon/>
    </AsyncSequence>
</ReactiveSequence>
```

In this example, IsEnemyVisible is re-checked between each step of the AsyncSequence. If the enemy disappears after AimWeapon succeeds, the sequence is interrupted before FireWeapon starts.

4. ReactiveSequence

This node is particularly useful to continuously check Conditions; but the user should also be careful when using asynchronous children, to be sure that they are not ticked more often than expected.


5. SequenceWithMemory

Use this ControlNode when you don't want to tick children again that already returned SUCCESS.



### Code Demo




---

## Compile

[Github Address](https://github.com/BehaviorTree/BehaviorTree.CPP#)

BT.CPP requires a compiler that supports C++17.

Three build systems are supported:

    - colcon (ament), if you use ROS2
    - conan otherwise (Linux/Windows).
    - straight cmake if you want to be personally responsible for dependencies :)


The following is straight cmake way:

```shell
sudo apt install cmake g++ pkg-config
sudo apt install libzmq3-dev libsqlite3-dev 

cd BehaviorTree.CPP-master

mkdir build

cmake -S . -B build
# -DBTCPP_GROOT_INTERFACE=ON  enable Groot2 connection via ZeroMQ (default ON)
# -DBUILD_TESTING=OFF          disable gtest function.
# -DBTCPP_SQLITE_LOGGING=OFF   disable sqlite3.
# -DCMAKE_BUILD_TYPE=Debug     compile with debug type, carry symbol link.

cmake --build build --parallel

#################################################
# File Location
./BehaviorTree.CPP-master/build/libbehaviortree_cpp.so
./BehaviorTree.CPP-master/include

#################################################
# CMakeLists.txt

set(BTCPP_GROOT_INTERFACE OFF CACHE BOOL "" FORCE)
set(BTCPP_SQLITE_LOGGING OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BTCPP_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
set(BTCPP_EXAMPLES OFF CACHE BOOL "" FORCE)

# add_subdirectory(BehaviorTree.CPP-master behaviortree_cpp)
include_directories(/include)
link_directories(/lib)
```

## Offline install zmq

### libzmq

```shell
sudo apt install build-essential git libtool pkg-config autoconf automake

git checkout v4.3.5

./autogen.sh

./configure

make -j$(nproc)

sudo make install

sudo ldconfig

```

### zmqpp
```shell
mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig
```

## Groot2
The most advanced IDE to create and debug Behavior Trees.

[Groot Address](https://www.behaviortree.dev/groot/)

### BT Editor

- Create and edit trees, using a simple drag and drop interface.
- Manage large projects using multiple files.
- Compatible with both BT.CPP 3 and 4.
- Split view to visualize two trees at once.
- Preview the XML in real-time.
- PRO: search Nodes in large trees.

### Real-time Monitor

- Connect to a running BT.CPP executor and visualize the state of the tree in real-time.
- Record all transitions into a log file, that you can analyze later.
- PRO: Visualize the content of the blackboard.
- PRO: Add interactive breakpoints and fault injection.
- PRO: Substitute any Nodes with dummy ones, at run-time.

### Log Visualization

- Open logs and replay the execution of the tree at different speeds.
- Visualize how long a Node was in the RUNNING state and how many times it returned a new status.
- Filter transitions by name or time range.



## BehaviorTreeMonitor
[BehaviorTreeMonitor](https://github.com/riyuexingchennnn/BehaviorTreeMonitor)
