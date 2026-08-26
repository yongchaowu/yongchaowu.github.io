---
layout: post
title: "OpenSource-BehaviorTree.CPP_v4.9_Complete_Guide(LLM Generated)"
date: 2026-07-15 23:52:00
categories: ["OpenSource"]
tags: ["OpenSource", "LLM", "Open source library"]
---

{% raw %}
> Version: **4.9.0** | Last updated: 2026-07 | License: MIT
> Based on official documentation, Doxygen API reference, and source code verification (v4.9.0).
> For official docs: https://www.behaviortree.dev/ | API: https://behaviortree.github.io/BehaviorTree.CPP/

<!--more-->
---

## Table of Contents

1. [What is a Behavior Tree?](#1-what-is-a-behavior-tree)
2. [Core Concepts](#2-core-concepts)
3. [Quick Start](#3-quick-start)
4. [Node Types and Class Hierarchy](#4-node-types-and-class-hierarchy)
   - 4.1 [Constructor Patterns](#41-constructor-patterns)
   - 4.2 [TreeNode Public API Reference](#42-treenode-public-api-reference)
5. [Control Nodes](#5-control-nodes)
   - 5.17 [ControlNode Programmatic API](#517-controlnode-programmatic-api)
6. [Decorator Nodes](#6-decorator-nodes)
   - 6.14 [DecoratorNode Programmatic API](#614-decoratornode-programmatic-api)
7. [Built-in Action Nodes](#7-built-in-action-nodes)
8. [Blackboard and Port System](#8-blackboard-and-port-system)
   - 8.10 [Blackboard Public API Reference](#810-blackboard-public-api-reference)
9. [XML Format](#9-xml-format)
10. [Scripting Language](#10-scripting-language)
11. [Pre/Post Conditions](#11-prepost-conditions)
12. [Asynchronous Actions](#12-asynchronous-actions)
    - 12.6 [Action Node API Reference](#126-action-node-api-reference)
13. [SubTrees](#13-subtrees)
14. [Logging and Debugging](#14-logging-and-debugging)
15. [Groot2 Integration](#15-groot2-integration)
16. [Substitution Rules and Mock Testing](#16-substitution-rules-and-mock-testing)
17. [Global Blackboard Pattern](#17-global-blackboard-pattern)
18. [Registration Methods](#18-registration-methods)
    - 18.9 [BehaviorTreeFactory Public API Reference](#189-behaviortreefactory-public-api-reference)
19. [Migration from v3.x to v4.x](#19-migration-from-v3x-to-v4x)
20. [Advanced Features](#20-advanced-features)
21. [Complete Tutorial Examples](#21-complete-tutorial-examples)
22. [Best Practices](#22-best-practices)

---

## 1. What is a Behavior Tree?

A Behavior Tree (BT) is a hierarchical node structure for organizing task switching in autonomous agents (robots, game AI). Compared to Finite State Machines (FSM):

| Aspect | Behavior Tree | FSM |
|--------|--------------|-----|
| Hierarchy | Native, composable subtrees | Manual state management |
| Reusability | Subtrees are reusable | States hard to reuse |
| Readability | Graphical, clear semantics | Transitions hard to follow |
| Reactivity | Built-in reactive nodes | Requires extra design |
| Debugging | Visual, recordable, replayable | Few standard tools |

---

## 2. Core Concepts

### 2.1 Tick Mechanism

The tree executes via **tick** signals propagated from root to leaves. Each tick:
1. Root receives the tick signal
2. Signal propagates down to leaf nodes
3. Leaf nodes execute and return a status
4. Status propagates up to determine next execution

### 2.2 Node Status

```cpp
enum class NodeStatus {
  IDLE = 0,     // Not executed yet (never returned by user code)
  RUNNING = 1,  // Currently executing
  SUCCESS = 2,  // Completed successfully
  FAILURE = 3,  // Completed with failure
  SKIPPED = 4   // Skipped (v4+, used by PreConditions)
};
```

Utility functions (defined in `basic_types.h:42-50`):
```cpp
bool isStatusActive(const NodeStatus& status);    // !IDLE && !SKIPPED
bool isStatusCompleted(const NodeStatus& status); // SUCCESS || FAILURE
```

> Custom leaf nodes must NEVER return `IDLE` or `SKIPPED`. `SKIPPED` is reserved for PreConditions.

### 2.3 NodeType Enum

```cpp
enum class NodeType {
  UNDEFINED = 0,
  ACTION,
  CONDITION,
  CONTROL,
  DECORATOR,
  SUBTREE
};
```

### 2.4 Service-Oriented Architecture

BT.CPP follows a service-oriented model: **leaf nodes** (actions/conditions) are client code that communicates with external server components (sensors, actuators, planners) via a middleware like ROS 2, shared memory, or custom IPC. The tree itself is a **coordinator** — it decides *when* and *in what order* to invoke services, but does not own the services themselves.

This separation of concerns means:
- Leaf nodes are thin wrappers around service calls
- The BT logic is entirely in XML, independent of service implementation
- Services can be developed, tested, and debugged in isolation

### 2.5 Synchronous vs Asynchronous

| Type | Behavior | Use Case |
|------|----------|----------|
| Synchronous | Blocks until done, returns SUCCESS/FAILURE | Quick checks, simple actions |
| Asynchronous | Returns RUNNING, resumed later, halt-able | Long operations, external service calls |

---

## 3. Quick Start

### 3.1 Building from Source

```bash
git clone https://github.com/BehaviorTree/BehaviorTree.CPP.git
cd BehaviorTree.CPP && mkdir build && cd build
cmake .. -DBTCPP_GROOT_INTERFACE=OFF -DBTCPP_SQLITE_LOGGING=OFF
cmake --build . --parallel
sudo cmake --install .
```

### 3.2 Hello World

```cpp
#include <behaviortree_cpp/bt_factory.h>

BT::NodeStatus SayHello()
{
  std::cout << "Hello World!\n";
  return BT::NodeStatus::SUCCESS;
}

int main()
{
  BT::BehaviorTreeFactory factory;

  // Register a simple action using a function pointer
  factory.registerSimpleAction("SayHello", std::bind(SayHello));

  // Trees are defined at deployment-time with XML
  std::string xml = R"(
    <root BTCPP_format="4">
      <BehaviorTree ID="MainTree">
        <Sequence>
          <SayHello />
        </Sequence>
      </BehaviorTree>
    </root>
  )";

  auto tree = factory.createTreeFromText(xml);
  tree.tickWhileRunning();  // v4+ recommended execution loop
  return 0;
}
```

### 3.3 Execution Loop Methods

```cpp
// v4+ recommended: internal loop with sleep (interruptible)
NodeStatus status = tree.tickWhileRunning(sleep_ms);

// Equivalent to v3.8 behavior: single tick, no internal loop
NodeStatus status = tree.tickExactlyOnce();

// Tick once, but re-tick if RUNNING with pending wake-up (no sleep)
NodeStatus status = tree.tickOnce();
```

`Tree::sleep(timeout)` can be interrupted by `TreeNode::emitWakeUpSignal()`, allowing immediate re-ticking. This is the **event-driven** mechanism: instead of busy-waiting, the tree sleeps and wakes up instantly when a running node signals a state change (e.g., a response arrives from an external server). Use `emitWakeUpSignal()` inside `onRunning()` of `StatefulActionNode` when new data is available.

```cpp
// In a StatefulActionNode's onRunning():
if (response_received) {
  return NodeStatus::SUCCESS;
}
emitWakeUpSignal();  // wake the tree immediately when more data expected
return NodeStatus::RUNNING;
```

**Tree class API** (defined in `include/behaviortree_cpp/bt_factory.h`):
```cpp
// Lifecycle
void initialize();                              // Create WakeUpSignal and bind to all nodes
void haltTree();                                // Halt all nodes recursively

// Node lookup
template <typename NodeType = TreeNode>
std::vector<const TreeNode*> getNodesByPath(
    StringView wildcard_filter) const;           // Type+wildcard filtered search

// Introspection
uint16_t getUID();                              // Incrementing unique numeric ID
// NOTE: Tree only exposes emitWakeUpSignal(); there is no wakeUpSignal() accessor
Blackboard::Ptr rootBlackboard();               // Root blackboard (for @ prefix)
```

---

## 4. Node Types and Class Hierarchy

```cpp
TreeNode
├── LeafNode
│   ├── ActionNodeBase
│   │   ├── SyncActionNode        (tick() → SUCCESS/FAILURE synchronously)
│   │   │   └── EntryUpdatedAction  (registered as WasEntryUpdated)
│   │   ├── StatefulActionNode    (onStart/onRunning/onHalted lifecycle)
│   │   ├── ThreadedAction        (tick() runs in a separate thread)
│   │   ├── CoroActionNode        (coroutine-based async via setStatusRunningAndYield())
│   │   └── SimpleActionNode      (wraps a std::function for convenience)
│   └── ConditionNode
│       └── SimpleConditionNode   (wraps a std::function for convenience)
├── ControlNode                   (1..N children)
│   ├── SequenceNode              (also AsyncSequence with make_async=true)
│   ├── SequenceWithMemory
│   ├── ReactiveSequence
│   ├── FallbackNode              (also AsyncFallback with make_asynch=true)
│   ├── ReactiveFallback
│   ├── ParallelNode
│   ├── ParallelAllNode
│   ├── IfThenElseNode
│   ├── WhileDoElseNode
│   ├── SwitchNode (2..6)
│   ├── TryCatchNode
│   └── ManualSelectorNode
└── DecoratorNode                 (1 child)
    ├── InverterNode
    ├── ForceSuccessNode
    ├── ForceFailureNode
    ├── RepeatNode
    ├── RetryNode
    ├── KeepRunningUntilFailureNode
    ├── TimeoutNode
    ├── DelayNode
    ├── RunOnceNode
    ├── PreconditionNode
    ├── SubTreeNode
    ├── LoopNode<T>               (template, replaces removed ConsumeQueue)
    ├── EntryUpdatedDecorator     (SkipUnlessUpdated / WaitValueUpdate)
```

### 4.1 Constructor Patterns

All node types that declare ports MUST use this constructor:
```cpp
MyNode(const std::string& name, const BT::NodeConfig& config);
```

Nodes without ports can use the shorter form:
```cpp
MyNode(const std::string& name);
```

### 4.2 TreeNode Public API Reference

```cpp
#include <behaviortree_cpp/tree_node.h>
```

| Method | Return Type | Description |
|--------|-------------|-------------|
| `status()` | `NodeStatus` | Current node status |
| `haltNode()` | `void` | Interrupt execution of this node (calls `halt()`, then executes `_onHalted` post-condition script) |
| `isHalted()` | `bool` | Whether the node was halted |
| `waitValidStatus()` | `NodeStatus` | Block until status is RUNNING/SUCCESS/FAILURE |
| `name()` | `const std::string&` | Instance name (not the type) |
| `registrationName()` | `const std::string&` | Factory registration ID (type name, e.g. "MyAction") |
| `UID()` | `uint16_t` | Unique numeric ID (depth-first traversal order) |
| `fullPath()` | `const std::string&` | Hierarchical path: `"subtree_name/node_name"` |
| `config()` | `const NodeConfig&` | Read-only node configuration (blackboard, ports, manifest) |
| `executeTick()` | `NodeStatus` | Public tick entry point: checks pre-conditions (IDLE/SKIPPED only), runs pre-tick callback, calls `tick()` with exception wrapping + duration monitoring, checks post-conditions, runs post-tick callback, then `setStatus()` (SKIPPED preserves IDLE internally) |
| `tick()` | `NodeStatus` | User-defined logic (protected, override this) |
| `getInput<T>(key, dest)` | `Result` | Read port into existing variable |
| `getInput<T>(key)` | `Expected<T>` | Read port returning optional value |
| `setOutput<T>(key, value)` | `Result` | Write to output port |
| `getRawPortValue(key)` | `StringView` | Raw port value without any type conversion |
| `getInputStamped<T>(key, dest)` | `Expected<Timestamp>` | Read port with timestamp |
| `getInputStamped<T>(key)` | `Expected<StampedValue<T>>` | Read port returning stamped value |
| `getLockedPortContent(key)` | `AnyPtrLocked` | Thread-safe zero-copy port access |
| `emitWakeUpSignal()` | `void` | Notify tree to tick again |
| `requiresWakeUp()` | `bool` | Whether node needs wake-up signal |
| `subscribeToStatusChange(cb)` | `StatusChangeSubscriber` | Subscribe to status transitions |
| `setPreTickFunction(cb)` | `void` | Callback executed before tick |
| `setPostTickFunction(cb)` | `void` | Callback executed after tick |
| `setTickMonitorCallback(cb)` | `void` | Callback for tick duration monitoring |

**Static utility methods:**
```cpp
static bool isBlackboardPointer(StringView str, StringView* stripped = nullptr);
static StringView stripBlackboardPointer(StringView str);
static Expected<StringView> getRemappedKey(StringView port_name, StringView remapped_port);
template <class DerivedT, typename... ExtraArgs>
static std::unique_ptr<TreeNode> Instantiate(const std::string& name,
                                             const NodeConfig& config,
                                             ExtraArgs... args);
```

`isBlackboardPointer()` checks if a string matches the `{...}` pattern. `Instantiate<>()` creates a node instance using either the full constructor `(name, config, args...)` or the name-only constructor `(name)` — detected at compile time.

**Runtime port remapping (protected, available to derived classes):**
```cpp
void modifyPortsRemapping(const PortsRemapping& new_remapping);
```

This allows a node to change its port bindings at runtime, e.g. to point to different blackboard keys based on dynamic conditions.

---

## 5. Control Nodes

### 5.1 Sequence

Executes children **in order**. All must succeed for the sequence to succeed.

```xml
<Sequence>
  <Action1 />  <!-- SUCCESS → continue -->
  <Action2 />  <!-- SUCCESS → continue -->
  <Action3 />  <!-- SUCCESS → overall SUCCESS -->
</Sequence>
```

- `FAILURE` → reset, return FAILURE
- `RUNNING` → return RUNNING, re-tick same child next time
- `SKIPPED` → skip to next child

**Common BT design pattern — "Find the BUG!":** A naive `Sequence` can leave the system in a bad state when a middle child fails:

```xml
<!-- BUG: If GrabBeer fails, the fridge stays open! -->
<Sequence>
  <OpenFridge />    <!-- SUCCESS → fridge is now open -->
  <GrabBeer />      <!-- FAILURE → sequence resets, but fridge stays open -->
  <CloseFridge />   <!-- never executed -->
</Sequence>
```

**Fix:** Use a `Fallback` to ensure cleanup, or restructure with guarded actions:

```xml
<!-- Fix: use Inverter + Fallback to guard open/close -->
<Fallback>
  <Sequence>
    <OpenFridge />
    <GrabBeer />
    <CloseFridge />
  </Sequence>
  <CloseFridge />   <!-- cleanup: always close -->
</Fallback>
```

### 5.2 AsyncSequence

Same logic as Sequence, but **yields once after each async child succeeds** (IDLE→SUCCESS) to allow interruption by a reactive parent. Sync children that complete in one tick pass through without yielding. Implemented by registering `SequenceNode` with `make_async=true`.

```xml
<AsyncSequence>
  <SyncActionA />  <!-- SUCCESS → yield, return RUNNING -->
  <SyncActionB />  <!-- next tick -->
</AsyncSequence>
```

```cpp
// Declaration (include/behaviortree_cpp/controls/sequence_node.h):
SequenceNode(const std::string& name, bool make_async = false,
             const NodeConfiguration& conf = NodeConfiguration());
```

### 5.3 ReactiveSequence

Re-evaluates **all children** every tick. When any child returns RUNNING, **halts all other children** (both earlier and later). Only one child may be RUNNING at a time; throws if a second child also returns RUNNING (can be disabled via `ReactiveSequence::EnableException(false)`).

```xml
<ReactiveSequence>
  <IsEnemyVisible />      <!-- re-checked every tick -->
  <ApproachEnemy />       <!-- halted if condition becomes false -->
</ReactiveSequence>
```

### 5.4 SequenceWithMemory

Skips children that already succeeded. If a middle child fails, the **index is NOT reset** (unlike Sequence), so earlier succeeded children are NOT retried. On halt, the index is also NOT reset.

```xml
<SequenceWithMemory>
  <GoTo location="A" />
  <GoTo location="B" />
  <GoTo location="C" />
</SequenceWithMemory>
```

### 5.5 Comparison Table

| Node | FAILURE | RUNNING | Yields Between Children | Re-evaluates Completed |
|------|---------|---------|------------------------|----------------------|
| `Sequence` | Reset, FAILURE | Re-tick same | No | No |
| `AsyncSequence` | Reset, FAILURE | Re-tick same | Yes | No |
| `ReactiveSequence` | Reset, FAILURE | Restart sequence | No | Yes (every tick) |
| `SequenceWithMemory` | Re-tick same | Re-tick same | No | No (skips succeeded) |

### 5.6 Fallback

Tries children **in order**. Returns SUCCESS as soon as one child succeeds. Also known as "Selector" or "Priority" in other frameworks.

```xml
<Fallback>
  <PlanA />  <!-- FAILURE → try next -->
  <PlanB />  <!-- SUCCESS → overall SUCCESS -->
</Fallback>
```

**Common BT pattern — guarded action with Inverter:** Use `Inverter` + condition to skip an action when the condition is already met:

```xml
<!-- Tick: if door is NOT closed, go open it -->
<Fallback>
  <Inverter>
    <IsDoorClosed />   <!-- if door IS closed → SUCCESS → Inverter → FAILURE -->
  </Inverter>
  <OpenDoor />         <!-- executed only if IsDoorClosed returned FAILURE (door open) -->
</Fallback>
```

This pattern prevents calling `OpenDoor` when the door is already closed. Same logic as an `if` guard in code.

### 5.7 AsyncFallback

Same as Fallback, but **yields once after each async child fails** (IDLE→FAILURE) to allow interruption. Sync children pass through without yielding. Implemented by registering `FallbackNode` with `make_asynch=true`.

### 5.8 ReactiveFallback

Re-evaluates all children every tick. If a condition in an earlier child changes from FAILURE to SUCCESS, halts the running child.

```xml
<ReactiveFallback>
  <AreYouRested />    <!-- re-checked every tick -->
  <Sleep />           <!-- halted if condition becomes true -->
</ReactiveFallback>
```

### 5.9 Fallback Comparison

| Node | RUNNING | All Children SKIPPED | Yields Between Children |
|------|---------|----------------------|------------------------|
| `Fallback` | Re-tick same | SKIPPED | No |
| `AsyncFallback` | Re-tick same | SKIPPED | Yes |
| `ReactiveFallback` | Restart sequence | SKIPPED | No |

If **all** children return SKIPPED, the Fallback returns SKIPPED. The SKIPPED status propagates to the parent control node.

### 5.10 Parallel

Ticks all children each time. Children may be in RUNNING simultaneously. **Thresholds are checked after each child** (early termination; does NOT wait for all children). Configurable thresholds:

```xml
<!-- Default: all must succeed, any failure fails -->
<Parallel>
  <ActionA />
  <ActionB />
</Parallel>

<!-- Custom: 2 succeed → SUCCESS, 2 fail → FAILURE -->
<Parallel success_count="2" failure_count="2">
  <ActionA />
  <ActionB />
  <ActionC />
</Parallel>
```

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `success_count` | InputPort\<int\> | -1 (all) | Required successes |
| `failure_count` | InputPort\<int\> | 1 | Failure threshold |

Negative values mean "all children" (same as `num_children`).

**Programmatic API** (defined in `include/behaviortree_cpp/controls/parallel_node.h`):
```cpp
size_t successThreshold() const;   // Current success threshold
size_t failureThreshold() const;   // Current failure threshold
void setSuccessThreshold(int threshold);
void setFailureThreshold(int threshold);
virtual void halt() override;
```

These allow reading/writing thresholds at runtime without XML ports.

### 5.11 ParallelAll

Executes ALL children regardless of results. Never halts early (waits for every child to complete before evaluating thresholds).

```xml
<ParallelAll max_failures="2">
  <ActionA />
  <ActionB />
  <ActionC />
</ParallelAll>
```

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `max_failures` | InputPort\<int\> | 1 | Max allowed failures |

### 5.12 IfThenElse

Condition evaluated **once**. Two or three children: condition, then-branch, optional else-branch.

```xml
<IfThenElse>
  <IsDoorOpen />        <!-- condition (once) -->
  <WalkThrough />       <!-- then (if condition succeeded) -->
  <TryAnotherPath />    <!-- else (optional, if condition failed) -->
</IfThenElse>
```

### 5.13 WhileDoElse

Condition evaluated **every tick**. Reactive: if condition changes while child is RUNNING, halts and switches branches.

```xml
<WhileDoElse>
  <IsBatteryOK />       <!-- re-checked every tick -->
  <ContinueMission />   <!-- if condition is true -->
  <GoToCharge />        <!-- else (optional) -->
</WhileDoElse>
```

### 5.14 Switch (Switch2–Switch6)

Selects child based on blackboard variable value:

```xml
<Switch3 variable="{robot_state}"
         case_1="IDLE"
         case_2="WORKING"
         case_3="ERROR">
  <HandleIdle />
  <HandleWorking />
  <HandleError />
  <HandleUnknown />    <!-- default (last child) -->
</Switch3>
```

- Supported: string, int, float, registered enums
- If variable changes mid-execution, running child is halted
- If the matching child returns SKIPPED, Switch also returns SKIPPED

### 5.15 TryCatch

Executes children 1..N-1 as a "try" block. If any try-child fails, executes child N as "catch".

```xml
<TryCatch>
  <Sequence>
    <Step1 />
    <Step2 />
  </Sequence>
  <Cleanup />    <!-- executed only if try-block fails -->
</TryCatch>
```

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `catch_on_halt` | InputPort\<bool\> | false | Execute catch if halted during try |

Requires at least 2 children.

### 5.16 ManualSelectorNode

Uses ncurses TUI to let the user manually select which child to execute.

> **Note**: Not a built-in. Must be registered explicitly: `factory.registerNodeType<ManualSelectorNode>("ManualSelector");`

Port:

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `repeat_last_selection` | InputPort\<bool\> | false | Re-use last selection on next tick |

---

### 5.17 ControlNode Programmatic API

The `ControlNode` base class (`include/behaviortree_cpp/control_node.h`) provides methods for managing children programmatically:

```cpp
#include <behaviortree_cpp/control_node.h>

// Child management
void addChild(TreeNode* child);                              // Append child
size_t childrenCount() const;                                // Number of children
const std::vector<TreeNode*>& children() const;              // All children
const TreeNode* child(size_t index) const;                   // Child at index (const only)

// Halting
virtual void halt() override;                                // Halt this node (and reset children)
void haltChildren();                                         // Same as resetChildren()
void haltChild(size_t i);                                    // Halt single child at index
void haltChildren(size_t first);              // Halt children from index first onward

// Reset
void resetChildren();                                        // Reset all children to IDLE + halt RUNNING ones
```

Example — iterating over children:
```cpp
for (size_t i = 0; i < childrenCount(); i++)
{
  auto status = child(i)->executeTick();
  // ...
}
```

---

## 6. Decorator Nodes

### 6.1 Inverter

Inverts child result: SUCCESS ↔ FAILURE, RUNNING → RUNNING, SKIPPED → SKIPPED (passthrough).

### 6.2 ForceSuccess / ForceFailure

Forces the child's result to SUCCESS or FAILURE (passes RUNNING and SKIPPED through).

### 6.3 Repeat

Ticks child N times. Child must return SUCCESS each time.

```xml
<Repeat num_cycles="3">
  <ClapYourHandsOnce />
</Repeat>
```

| Port | Type | Description |
|------|------|-------------|
| `num_cycles` | InputPort\<int\> | Repeat count, -1 = infinite |

- Child FAILURE → immediate FAILURE (counter reset to 0)
- Child RUNNING → counter NOT incremented
- Child SKIPPED → reset child but counter NOT incremented
- Counter resets to 0 on SUCCESS and on halt
- Async optimization: yields RUNNING between cycles when child is async

### 6.4 RetryUntilSuccessful

Ticks child up to N times until it succeeds.

```xml
<RetryUntilSuccessful num_attempts="5">
  <OpenDoor />
</RetryUntilSuccessful>
```

| Port | Type | Description |
|------|------|-------------|
| `num_attempts` | InputPort\<int\> | Max attempts, -1 = infinite |

- Child SUCCESS → immediate SUCCESS (counter reset to 0)
- Child RUNNING → counter NOT incremented
- Child SKIPPED → child is reset, return SKIPPED
- **`num_attempts` is re-read from the port on each failure**, allowing dynamic in-flight modification
- Counter resets to 0 on SUCCESS and on halt
- Async optimization: yields RUNNING between attempts when child is async

### 6.5 Timeout

Halts child if it runs longer than specified milliseconds.

```xml
<Timeout msec="5000">
  <LongRunningAction />
</Timeout>
```

| Port | Type | Description |
|------|------|-------------|
| `msec` | InputPort\<unsigned\> | Timeout in milliseconds (0 = no timeout) |

- `msec=0` disables the timer entirely (child runs with no time limit)

### 6.6 Delay

Waits specified milliseconds before ticking child.

```xml
<Delay delay_msec="5000">
  <Action />
</Delay>
```

| Port | Type | Description |
|------|------|-------------|
| `delay_msec` | InputPort\<unsigned\> | Delay in milliseconds |

### 6.7 RunOnce

Executes child only once. After completion, behavior depends on `then_skip`:

| `then_skip` | Behavior |
|-------------|----------|
| TRUE (default) | Return SKIPPED on subsequent ticks |
| FALSE | Return same status forever |

```xml
<RunOnce then_skip="false">
  <Initialize />
</RunOnce>
```

Note: If the child is async (returns RUNNING), the node continues ticking it until it completes (SUCCESS/FAILURE) before the "once" behavior takes effect. A perpetually RUNNING child will be ticked indefinitely.

### 6.8 KeepRunningUntilFailure

Returns RUNNING as long as child returns SUCCESS. Stops when child fails.

```xml
<KeepRunningUntilFailure>
  <MonitorSensor />
</KeepRunningUntilFailure>
```

> **Warning**: If child returns SKIPPED, behavior is undefined (no explicit handler). Avoid using SKIPPED children under this decorator.

### 6.9 Precondition

Evaluates a script condition before ticking child:

```xml
<Precondition if="battery_level > 20" else="FAILURE">
  <MoveToGoal />
</Precondition>

<!-- With else="RUNNING": condition re-evaluated while child is running -->
<Precondition if="sensor_ok" else="RUNNING">
  <LongRunningAction />
</Precondition>
```

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `if` | InputPort\<string\> | (required) | Script condition |
| `else` | InputPort\<NodeStatus\> | FAILURE | Status if condition false |

- Once child starts RUNNING, condition is NOT re-evaluated until child completes
- Use `else="RUNNING"` for per-tick re-evaluation pattern
- Note: Precondition does NOT explicitly set its own status to RUNNING (unlike other decorators)

### 6.10 SubTree

Wraps a sub-tree with a separate blackboard (see [§13 Subtrees](#13-subtrees)).

### 6.11 LoopNode

Replacement for deprecated ConsumeQueue. Pops elements from a `std::deque` and ticks child for each element.

```xml
<LoopInt queue="{waypoints}" value="{wp}" if_empty="SUCCESS">
  <UseWaypoint waypoint="{wp}" />
</LoopInt>
```

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `queue` | BidirectionalPort | (required) | Queue (SharedQueue\<T\> or std::vector\<T\>) |
| `value` | OutputPort\<T\> | — | Popped element |
| `if_empty` | InputPort\<NodeStatus\> | SUCCESS | Status when queue is empty |

Pre-registered types:
- `LoopInt` (int)
- `LoopBool` (bool)
- `LoopDouble` (double)
- `LoopString` (std::string)

If the child returns FAILURE, the loop **aborts immediately** and returns FAILURE (does not continue to next element).

For custom types, register manually:
```cpp
factory.registerNodeType<LoopNode<MyType>>("LoopMyType");
```

### 6.12 EntryUpdatedDecorator

Checks whether a blackboard entry was updated since last checked.

| Port | Type | Default | Description |
|------|------|---------|-------------|
| `entry` | InputPort\<BT::Any\> | (required) | Entry to check |

```xml
<!-- Returns SKIPPED if not updated -->
<SkipUnlessUpdated entry="{sensor_data}">
  <ProcessData />
</SkipUnlessUpdated>

<!-- Returns RUNNING if not updated (keeps tree active) -->
<WaitValueUpdate entry="{command}">
  <ExecuteCommand />
</WaitValueUpdate>
```

Two built-in variants:
- `SkipUnlessUpdated` — returns SKIPPED when not updated
- `WaitValueUpdate` — returns RUNNING when not updated

### 6.13 ConsumeQueue (Deprecated)

> Deprecated in v4.9. Use `LoopNode` instead.

The `ConsumeQueue` template class (in `decorators/consume_queue.h`) is marked `[[deprecated]]` and is **not** a built-in. The header still exists and you may register it manually:
```cpp
factory.registerNodeType<ConsumeQueue<Pose2D>>("ConsumeQueue");
```
but `LoopNode<T>` is the recommended replacement. See §6.11.

---

### 6.14 DecoratorNode Programmatic API

The `DecoratorNode` base class (`include/behaviortree_cpp/decorator_node.h`) provides methods for managing the single child:

```cpp
#include <behaviortree_cpp/decorator_node.h>

// Child management
void setChild(TreeNode* child);     // Set the single child
const TreeNode* child() const;      // Read-only child access
TreeNode* child();                  // Mutable child access

// Halting
virtual void halt() override;       // Halt this decorator

// Reset
void resetChild();                   // Reset child to IDLE + halt if RUNNING

// Execution
NodeStatus executeTick() override;  // Override of TreeNode::executeTick()
```

`SimpleDecoratorNode` (used by `registerSimpleDecorator`) wraps a `TickFunctor`:
```cpp
using TickFunctor = std::function<NodeStatus(NodeStatus, TreeNode&)>;
SimpleDecoratorNode(const std::string& name, TickFunctor tick_functor,
                    const NodeConfig& config);
```

---

## 7. Built-in Action Nodes

These are registered automatically by the factory. No manual registration needed.

| Node Name | Description | Ports |
|-----------|-------------|-------|
| `AlwaysSuccess` | Always returns SUCCESS | (none) |
| `AlwaysFailure` | Always returns FAILURE | (none) |
| `Script` | Execute script code | InputPort\<string\> "code" |
| `ScriptCondition` | Evaluate script, SUCCESS if true | InputPort\<string\> "code" |
| `SetBlackboard` | Write value to blackboard | InputPort "value", BidirectionalPort "output_key" |
| `UnsetBlackboard` | Remove blackboard entry | InputPort\<string\> "key" |
| `Sleep` | Sleep for N milliseconds (async) | InputPort\<unsigned\> "msec" |
| `WasEntryUpdated` | Check if entry was updated (class: `EntryUpdatedAction`) | InputPort\<BT::Any\> "entry" |

Source: all registered in `src/bt_factory.cpp:114-173`. AlwaysSuccess, AlwaysFailure, Sleep, etc. are auto-registered. `PopFromQueue<T>` and `QueueSize<T>` are template classes that require manual registration (see §7.6).

### 7.1 Script

```xml
<Script code="answer := 42; msg := 'hello'" />
```

Always returns SUCCESS. See §10 for script syntax.

### 7.2 ScriptCondition

```xml
<ScriptCondition code="battery_level > 20" />
```

Returns SUCCESS if script evaluates to true, FAILURE otherwise.

### 7.3 SetBlackboard

```xml
<!-- Static value: stores string "42" -->
<SetBlackboard value="42" output_key="the_answer" />

<!-- Copy from another port -->
<SetBlackboard value="{src_port}" output_key="dst_port" />
```

### 7.4 Sleep

```cpp
class SleepNode : public BT::StatefulActionNode { ... };
```

Asynchronous sleep. Can be interrupted via halt(). Use `<Timeout>` decorator for bounded waits.

```xml
<Sleep msec="5000" />
```

### 7.5 WasEntryUpdated (class: `EntryUpdatedAction`)

Checks if a blackboard entry has been updated (via `sequence_id` comparison) since the last check.

```xml
<WasEntryUpdated entry="{sensor_value}" />
```

Returns SUCCESS if the entry was written since last check, FAILURE if not updated or missing.

The class hierarchy for this node is `EntryUpdatedAction` (`actions/updated_action.h`), registered with XML name `WasEntryUpdated` in `src/bt_factory.cpp:171`. Companion decorators (§6.12) provide `SkipUnlessUpdated` and `WaitValueUpdate` for blocking/conditional variants.

### 7.6 Template Actions (not built-in, need manual registration)

These are defined as templates and must be registered explicitly:

| Node | Description | Header |
|------|-------------|--------|
| `PopFromQueue<T>` | Pop front from ProtectedQueue | `actions/pop_from_queue.hpp` |
| `QueueSize<T>` | Get queue size | `actions/pop_from_queue.hpp` |

---

## 8. Blackboard and Port System

### 8.1 Blackboard

A key-value store shared by all nodes in a tree (and its subtrees).

```cpp
// Direct access (not recommended)
config().blackboard->get("key", value);
config().blackboard->set("key", value);
```

### 8.2 Ports

Abstracted, **type-safe** layer over the blackboard. Ports are the **recommended** way to exchange data.

```cpp
// Through ports (recommended)
auto val = getInput<int>("input_key");     // Returns Expected<T>
setOutput("output_key", result);           // Returns Result
```

### 8.3 Port Types

| Port Type | Direction | Access |
|-----------|-----------|--------|
| `InputPort<T>` | Read | `getInput<T>(key)` |
| `OutputPort<T>` | Write | `setOutput(key, value)` |
| `BidirectionalPort<T>` | Read/Write | `getInput<T>(key)` + `setOutput(key, value)` |

### 8.4 Port with Default Values

```cpp
// Default value as string (parsed via convertFromString)
BT::InputPort<Point2D>("pointB", "3,4");

// Default value as same type
BT::InputPort<Point2D>("pointB", Point2D{3, 4});

// Default blackboard pointer (port name = blackboard key)
BT::InputPort<Point2D>("pointD", "{=}");  // equivalent to "{pointD}"

// Output port default pointing to blackboard entry
BT::OutputPort<Point2D>("result", "{target}");
```

### 8.5 Declaring Ports in a Node

```cpp
class MyNode : public BT::SyncActionNode
{
public:
  MyNode(const std::string& name, const BT::NodeConfig& config)
    : BT::SyncActionNode(name, config) {}

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<std::string>("message"),
      BT::OutputPort<int>("result"),
      BT::BidirectionalPort<std::vector<int>>("data")
    };
  }

  BT::NodeStatus tick() override
  {
    auto msg = getInput<std::string>("message");
    setOutput("result", 42);
    return BT::NodeStatus::SUCCESS;
  }
};
```

### 8.6 Custom Types and convertFromString

```cpp
struct Position2D { double x, y; };

// Template specialization (must be in namespace BT)
namespace BT {
template <> inline Position2D convertFromString(StringView str)
{
  auto parts = splitString(str, ';');
  if (parts.size() != 2)
    throw RuntimeError("invalid input");
  return { convertFromString<double>(parts[0]),
           convertFromString<double>(parts[1]) };
}
}
```

The `"json:"` prefix triggers JSON parsing:
```cpp
template <typename T>
inline T convertFromString(StringView str)
{
  if (StartWith(str, "json:")) {
    str.remove_prefix(5);
    return convertFromJSON<T>(str);
  }
  // ... normal string conversion
}
```

### 8.7 Zero-Copy Access (`getLockedPortContent`)

Avoid copying large data with `getLockedPortContent()` (v4.5.1+, thread-safe):

```cpp
if (auto any_locked = getLockedPortContent("cloud"))
{
  if (any_locked->empty())
  {
    any_locked.assign(my_initial_pointcloud);
  }
  else if (Pointcloud* cloud_ptr = any_locked->castPtr<Pointcloud>())
  {
    // Modify in-place (mutex locked until any_locked goes out of scope)
  }
}
```

### 8.8 Stamped Access (`getInputStamped`)

Access blackboard entry with timestamp/sequence info (v4+):

```cpp
// Returns Expected<Timestamp> with sequence_id and stamp
auto result = getInputStamped<int>("sensor_value", destination);
// or
auto stamped = getInputStamped<int>("sensor_value");
// stamped->value, stamped->stamp.seq, stamped->stamp.time
```

### 8.9 Why Ports Instead of Direct Blackboard Access?

1. **Self-documenting**: `providedPorts()` is the node's data contract
2. **Remappable**: XML bindings can change without recompilation
3. **Type-safe**: Runtime type checking on port connections
4. **Factory-aware**: Factory can introspect port connections for static analysis
5. **Subtree-safe**: Port remapping prevents naming collisions

---

### 8.10 Blackboard Public API Reference

```cpp
#include <behaviortree_cpp/blackboard.h>
using Ptr = std::shared_ptr<Blackboard>;
```

**Creation:**
```cpp
static Blackboard::Ptr create(Blackboard::Ptr parent = {});
```

**Type-safe read/write:**
```cpp
template <typename T> bool get(const std::string& key, T& value) const;  // Returns false if missing
template <typename T> T get(const std::string& key) const;               // Throws if missing
template <typename T> void set(const std::string& key, const T& value);
void unset(const std::string& key);                                       // Remove entry
[[deprecated]] void clear();                                              // Remove ALL entries (unsafe)
```

**Stamped access (with timestamp/sequence_id):**
```cpp
template <typename T> Expected<Timestamp> getStamped(const std::string& key, T& value) const;
template <typename T> Expected<StampedValue<T>> getStamped(const std::string& key) const;
```

**Low-level access:**
```cpp
std::shared_ptr<Entry> getEntry(const std::string& key);       // Direct entry (has .value, .stamp, .sequence_id)
AnyPtrLocked getAnyLocked(const std::string& key);             // Thread-safe raw Any pointer
[[deprecated]] Any* getAny(const std::string& key);            // Use getAnyLocked instead
const TypeInfo* entryInfo(const std::string& key);             // Type introspection
void createEntry(const std::string& key, const TypeInfo& info); // Pre-create entry without value
```

**Introspection:**
```cpp
std::vector<StringView> getKeys() const;   // List all keys in this blackboard
void debugMessage() const;                  // Print all entries to stdout
```

**Subtree remapping (internal ↔ external port mapping):**
```cpp
void addSubtreeRemapping(StringView internal, StringView external);
```

**Parent/root traversal:**
```cpp
Blackboard::Ptr parent();                // Parent blackboard (may be null)
Blackboard* rootBlackboard();            // Root of the hierarchy (for @ prefix)
const Blackboard* rootBlackboard() const;
```

**Polymorphic cast support:**
```cpp
void setPolymorphicCastRegistry(std::shared_ptr<PolymorphicCastRegistry> registry);
const PolymorphicCastRegistry* polymorphicCastRegistry() const;
template <typename T> Expected<T> tryCastWithPolymorphicFallback(const Any* any) const;
```

**Auto-remapping:**
```cpp
void enableAutoRemapping(bool remapping);
```

**Entry struct fields:**
```cpp
struct Entry {
  Any value;                        // Stored value
  TypeInfo info;                    // Type information
  StringConverter string_converter; // String parsing function
  mutable std::mutex entry_mutex;   // Thread-safety lock
  uint64_t sequence_id;             // Incremented on each write
  std::chrono::nanoseconds stamp;   // Timestamp of last write
};
```

---

### 8.11 Port Type System Details

**Type Compatibility Rules** (from `gtest_port_type_rules.cpp`):
- Same type always compatible (e.g., `int`↔`int`)
- `AnyTypeAllowed` / `BT::Any` ports accept any type (generic)
- `std::string` output acts as "universal donor" — converts to target type via `convertFromString<T>()`
- Writing a string to a non-string entry creates an `AnyTypeAllowed` entry (not strongly typed)
- **Type locks** after the first strongly-typed write: subsequent writes must match or be safely castable
- Safe numeric casting: `int64_t`↔`uint8_t` etc. with bounds checking
- A `BT::Any` entry bypasses type checking (accepts any subsequent type)
- String-to-number auto-conversion: writing `"42"` to an `int` entry works if a `StringConverter` is registered

**Reserved Port Names:**
| Name | Reserved As | Purpose |
|------|-------------|---------|
| `name` | `.xml` attribute | Node instance name |
| `ID` | `.xml` attribute | Node registration type |
| `_autoremap` | SubTree attribute | Enables auto-remapping |
| `_failureIf`, `_successIf`, `_skipIf`, `_while` | Pre-condition | Script conditions |
| `_onHalted`, `_onFailure`, `_onSuccess`, `_post` | Post-condition | Script callbacks |

Additionally, `"Root"` and `"root"` are reserved and cannot be used as `BehaviorTree ID`.

Port names must start with an alphabetic character and must not contain: `< > & " ' / \ : * ? | .` or whitespace. Utility functions:
```cpp
bool IsAllowedPortName(StringView str);          // Full validation
char findForbiddenChar(StringView name);         // Returns first forbidden char (or '\0')
bool IsReservedAttribute(StringView str);        // Checks against reserved names
```

**String conversion utilities** (`basic_types.h`):
```cpp
std::string toStr(NodeStatus s, bool colored = false);  // Colored ANSI output available
std::string toStr(PortDirection d);
std::string toStr(NodeType t);
std::string toStr(bool b);
```

---

## 9. XML Format

### 9.1 Basic Structure

```xml
<root BTCPP_format="4" main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <SaySomething message="Hello" />
    </Sequence>
  </BehaviorTree>
</root>
```

- `<root>` should have `BTCPP_format` attribute (missing emits a warning; XSD requires it)
- `<BehaviorTree>` must have `ID` attribute
- Multiple `<BehaviorTree>` definitions in one file
- Maximum XML nesting depth: **256 levels**

### 9.2 Compact vs Explicit Syntax

```xml
<!-- Compact (recommended) -->
<SaySomething name="hello" message="Hello World"/>

<!-- Explicit (required by Groot for full model) -->
<Action ID="SaySomething" name="hello" message="Hello"/>
```

### 9.3 Port Bindings

```xml
<!-- Static string value -->
<SaySomething message="Hello"/>

<!-- Blackboard binding -->
<SaySomething message="{my_message}"/>

<!-- Self-binding ({=} → {attr_name}, i.e., message → {message}) -->
<SaySomething message="{=}"/>
```

**Port default values** are specified in `providedPorts()` and used when the XML attribute is **omitted**. An empty attribute (`message=""`) overrides the default and may cause a parse error if the type rejects empty strings.

**Non-port underscore-prefixed attributes** (e.g., `_my_custom="value"`) are saved in `TreeNode::config().other_attributes` and ignored by port resolution. Attributes without `_` prefix that don't match a registered port trigger a `WrongPort` warning.

### 9.4 Including External Files

```xml
<root BTCPP_format="4">
  <include path="subtree_a.xml" />
  <include path="subtree_b.xml" />
  <BehaviorTree ID="MainTree">
    <Sequence>
      <SubTree ID="SubTreeA" />
      <SubTree ID="SubTreeB" />
    </Sequence>
  </BehaviorTree>
</root>
```

ROS2 package paths (requires `ament_index_cpp`):
```xml
<include ros_pkg="my_package" path="trees/grasp.xml"/>
```

### 9.5 TreeNodeModel (for Groot)

```xml
<TreeNodesModel>
  <Action ID="SaySomething">
    <input_port name="message" type="std::string" />
  </Action>
  <Action ID="OpenGripper"/>
</TreeNodesModel>
```

Or generate automatically:
```cpp
std::string xml_models = BT::writeTreeNodesModelXML(factory);
std::string xsd = BT::writeTreeXSD(factory);            // XSD schema for validation
```

**Serializing a tree back to XML** (used internally by Groot2Publisher):
```cpp
#include <behaviortree_cpp/xml_parsing.h>
std::string xml = BT::WriteTreeToXML(tree, true, true);  // add metadata + builtin models
```

---

## 10. Scripting Language

BT.CPP 4.x introduces an XML-embedded scripting language for blackboard operations.

### 10.1 Assignment

```xml
<Script code="param_A := 42" />    <!-- Create if not exists -->
<Script code="param_B = 3.14" />   <!-- Update (error if missing) -->
<Script code="msg = 'hello world'" />  <!-- Strings -->
```

Multi-statement: `A:=42; B:=24; C:=A+B`. Semicolons separate statements; trailing and consecutive semicolons are allowed.

### 10.2 Arithmetic

```
+, -, *, / and assignment operators +=, -=, *=, /=
```

String concat: `..` (any type: `string+string`, `number+string`, `string+number`). `+` also concatenates strings.

Note: `+=` works for strings too (`msg += 'world'`).

Number formats: integers (`42`), hex (`0xFF`), reals (`3.14`, `1e5`).

### 10.3 Comparison and Logic

```
==, !=, <, <=, >, >=, &&, ||, !
```

Chained comparisons supported: `1 < x < 10` (equivalent to `1 < x && x < 10`).

String-to-number comparison works: strings are converted to double for comparison (e.g., `'3' == 3` is true).

Ternary: `val := (A > 1) ? 42 : 24` (right-associative).

### 10.4 Bitwise (integers only)

```
&, |, ^, ~
```

Throws if either operand is not an integer.

### 10.5 Booleans

```xml
<Script code="val_A = true; val_B := !false" />
```

Stored as `double` (`1.0`/`0.0`).

### 10.6 Identifiers

Variable names start with a letter, `_`, or `@`. The `@` prefix is used for root/nested blackboard references.

### 10.7 Operator Precedence (highest to lowest)

| Level | Operators | Assoc |
|-------|-----------|-------|
| Prefix | unary `-`, `~`, `!` | — |
| 18 | `*`, `/` | Left |
| 16 | `+`, `-`, `..` | Left |
| 14 | `&` | Left |
| 12 | `\|`, `^` | Left |
| 10 | `==`, `!=`, `<`, `>`, `<=`, `>=` | Chain |
| 8 | `&&` | Left |
| 6 | `\|\|` | Left |
| 4 | `? :` | Right |
| 2 | `:=`, `=`, `+=`, `-=`, `*=`, `/=` | — |

### 10.8 Multi-statement Return Value

A multi-statement script returns the **value of the last expression**. This is used in condition contexts (`_skipIf`, `_successIf`, `ScriptCondition`).

### 10.9 Enums

```cpp
enum Color { RED=1, BLUE=2, GREEN=3 };
factory.registerScriptingEnums<Color>();
factory.registerScriptingEnum("THE_ANSWER", 42);
```

```xml
<Script code="color := RED; answer := THE_ANSWER" />
```

Default magic_enum range: [-128, 128]. Use manual registration for values outside this range.

### 10.10 Scripting Utility Functions

```cpp
#include <behaviortree_cpp/scripting/script_parser.hpp>

// Validate script syntax without executing:
BT::Result res = BT::ValidateScript("x := 42");       // true if valid
bool is_valid = static_cast<bool>(res);

// Parse script into a callable function (for repeated execution):
auto func = BT::ParseScript("x := 42; y := x + 1");
BT::Ast::Environment env = { blackboard, enums_table };
BT::Any result = func(env);  // evaluate, returns last expression value

// Parse and execute in one step:
auto result = BT::ParseScriptAndExecute(env, "x := 42; x + 1");
```

---

## 11. Pre/Post Conditions

Inline attributes (no C++ changes needed) to add conditions to any node.

### 11.1 Pre-conditions

| Attribute | Description | Evaluated |
|-----------|-------------|-----------|
| `_skipIf` | Skip if condition is true | When IDLE or SKIPPED |
| `_failureIf` | Return FAILURE if condition is true | When IDLE or SKIPPED |
| `_successIf` | Return SUCCESS if condition is true | When IDLE or SKIPPED |
| `_while` | Skip/halt if condition is false | Every tick (IDLE, SKIPPED, RUNNING) |

**Evaluation order**: `_failureIf` → `_successIf` → `_skipIf` → `_while`
Pre-conditions fire when `status()` is IDLE or SKIPPED (not re-evaluated while RUNNING, except `_while`). The `_while` condition is also checked while RUNNING: if it becomes false, the node is halted and returns SKIPPED.

```xml
<OpenDoor _skipIf="!door_closed" />
<MoveToGoal _failureIf="battery_level < 20" />
```

### 11.2 Post-conditions

| Attribute | Description |
|-----------|-------------|
| `_onSuccess` | Execute script on SUCCESS |
| `_onFailure` | Execute script on FAILURE |
| `_post` | Execute script on SUCCESS or FAILURE |
| `_onHalted` | Execute script when halted |

```xml
<MoveBase goal="{target}"
          _onSuccess="result:=OK"
          _onFailure="result:=ERROR"/>
```

Execution context:
- `_onSuccess`, `_onFailure`, `_post` execute in `checkPostConditions()`, called from `executeTick()` when the tick completes with SUCCESS or FAILURE.
- `_onHalted` executes in `haltNode()`, called when the node is halted externally — NOT from `checkPostConditions()`.
- Execution order within `checkPostConditions()`: `_onSuccess`/`_onFailure` (mutually exclusive, depending on status) → `_post` (always).

### 11.3 Inline vs Precondition Decorator

| Feature | Inline (`_skipIf`, etc.) | `<Precondition>` Decorator |
|---------|-------------------------|---------------------------|
| Evaluated | Once (IDLE → active) | Per-tick (with `else="RUNNING"`) |
| Can halt running child | No | Yes |
| Use case | One-time checks | Continuous monitoring |

---

## 12. Asynchronous Actions

### 12.1 Concurrency vs Parallelism

BT.CPP is **single-threaded**. All `tick()` methods execute sequentially. Asynchronous nodes return `RUNNING` and are resumed in future ticks. **Do not block in tick()**.

### 12.2 StatefulActionNode (Recommended)

Lifecycle: `onStart()` → `onRunning()`* → `onHalted()` (if interrupted)

```cpp
class SleepNode : public BT::StatefulActionNode
{
public:
  SleepNode(const std::string& name, const BT::NodeConfig& config)
    : BT::StatefulActionNode(name, config) {}

  static BT::PortsList providedPorts()
  {
    return { BT::InputPort<int>("msec") };
  }

  NodeStatus onStart() override
  {
    int msec = 0;
    getInput("msec", msec);
    if (msec <= 0)
      return NodeStatus::SUCCESS;
    deadline_ = std::chrono::system_clock::now() +
                std::chrono::milliseconds(msec);
    return NodeStatus::RUNNING;
  }

  NodeStatus onRunning() override
  {
    return (std::chrono::system_clock::now() >= deadline_)
             ? NodeStatus::SUCCESS
             : NodeStatus::RUNNING;
  }

  void onHalted() override
  {
    std::cout << "SleepNode interrupted" << std::endl;
  }

private:
  std::chrono::system_clock::time_point deadline_;
};
```

### 12.3 CoroActionNode (Coroutine-based)

Alternative async pattern using `setStatusRunningAndYield()`:

```cpp
class MyCoroAction : public BT::CoroActionNode
{
public:
  MyCoroAction(const std::string& name, const BT::NodeConfig& config)
    : BT::CoroActionNode(name, config) {}

  BT::NodeStatus tick() override
  {
    // Send request
    sendRequest();
    setStatusRunningAndYield();  // Pause, return RUNNING

    // Resume in next tick: check response
    if (responseReceived())
      return BT::NodeStatus::SUCCESS;

    setStatusRunningAndYield();  // Continue waiting
    // ...
    return BT::NodeStatus::SUCCESS;
  }

  void halt() override
  {
    std::cout << "Coroutine interrupted" << std::endl;
    CoroActionNode::halt();
  }
};
```

### 12.4 ThreadedAction (Use with Caution)

Runs `tick()` in a **separate thread**. Must check `isHaltRequested()` regularly.

```cpp
// CORRECT: must check isHaltRequested() periodically
class ThreadedSleepNode : public BT::ThreadedAction
{
public:
  ThreadedSleepNode(const std::string& name, const BT::NodeConfig& config)
    : BT::ThreadedAction(name, config) {}  // NOT ActionNodeBase

  static BT::PortsList providedPorts()
  {
    return { BT::InputPort<int>("msec") };
  }

  NodeStatus tick() override
  {
    int msec = 0;
    getInput("msec", msec);
    const auto deadline = std::chrono::system_clock::now() +
                          std::chrono::milliseconds(msec);
    while (!isHaltRequested() && std::chrono::system_clock::now() < deadline)
    {
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    return NodeStatus::SUCCESS;
  }
};
```

> **Warning**: `ThreadedAction` is-a `ActionNodeBase`, not a wrapper. A derived class constructor **must** call `BT::ThreadedAction(name, config)`, not `BT::ActionNodeBase(name, config)`. The former initializes the `ThreadedAction` base class; the latter skips `ThreadedAction`'s own initialization and is a bug found in earlier guides.

### 12.5 Which Async Pattern to Use

| Pattern | Complexity | Use Case |
|---------|-----------|----------|
| `StatefulActionNode` | Low | Most async operations (recommended) |
| `CoroActionNode` | Medium | Stateful request/response with yield points |
| `ThreadedAction` | High | Truly parallel execution (avoid if possible) |

---

### 12.6 Action Node API Reference

All action classes are in `include/behaviortree_cpp/action_node.h`.

**ActionNodeBase** — base for all actions:
```cpp
class ActionNodeBase : public LeafNode {
  // type() returns NodeType::ACTION (override final)
};
```

**SyncActionNode** — synchronous (no RUNNING):
```cpp
class SyncActionNode : public ActionNodeBase {
  virtual NodeStatus executeTick() override;  // Throws if derived returns RUNNING
  virtual void halt() override final;         // Calls resetStatus()
};
```

**StatefulActionNode** — async lifecycle (recommended):
```cpp
class StatefulActionNode : public ActionNodeBase {
  virtual NodeStatus onStart() = 0;    // Called once when IDLE → RUNNING
  virtual NodeStatus onRunning() = 0;  // Called each tick while RUNNING
  virtual void onHalted() = 0;         // Called when halted
  bool isHaltRequested() const;        // Check if halt was requested
  // tick() and halt() are override final (do not override)
};
```

**ThreadedAction** — true multi-threading:
```cpp
class ThreadedAction : public ActionNodeBase {
  virtual NodeStatus executeTick() override final;  // Spawns std::async thread
  virtual void halt() override;                     // Stops (waits for thread)
  bool isHaltRequested() const;                     // Check periodically in tick()
};
```
Emits `emitWakeUpSignal()` on completion so the tree's `tickOnce()`/`tickWhileRunning()` can react immediately.

**CoroActionNode** — coroutine-based async:
```cpp
class CoroActionNode : public ActionNodeBase {
  void setStatusRunningAndYield();       // Pause and return RUNNING
  virtual NodeStatus executeTick() override final;
  void halt() override;                  // Call CoroActionNode::halt() if overriding
  void tickImpl();                       // Internal (but public)
};
```

**SimpleActionNode** — functor wrapper (used by `registerSimpleAction`):
```cpp
using TickFunctor = std::function<NodeStatus(TreeNode&)>;
SimpleActionNode(const std::string& name, TickFunctor tick_functor,
                 const NodeConfig& config);
```
Note: `tick()` sets status to RUNNING before calling the functor (only when IDLE). The functor must return SUCCESS or FAILURE; RUNNING from a simple action is not supported.

---

## 13. Subtrees

### 13.1 Basic SubTree

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <SubTree ID="GraspObject" />
  </BehaviorTree>

  <BehaviorTree ID="GraspObject">
    <Sequence>
      <OpenGripper />
      <ApproachObject />
      <CloseGripper />
    </Sequence>
  </BehaviorTree>
</root>
```

### 13.2 Port Remapping

```xml
<SubTree ID="MoveRobot"
         target="{move_goal}"
         frame="map"
         result="{error_code}" />
```

### 13.3 Subtree Models (Default Remapping)

Define default remappings in `<TreeNodesModel>`:

```xml
<TreeNodesModel>
  <SubTree ID="MoveRobot">
    <input_port  name="target" default="{move_goal}" />
    <input_port  name="frame"  default="world" />
    <output_port name="result" default="{error_code}" />
  </SubTree>
</TreeNodesModel>
```

Then override selectively:
```xml
<SubTree ID="MoveRobot" frame="map" />
```

### 13.4 Autoremap

Automatically remap all ports with matching names:

```xml
<!-- Explicit remapping -->
<SubTree ID="MoveRobot" target="{target}" frame="{frame}" result="{result}" />

<!-- Autoremap (same effect) -->
<SubTree ID="MoveRobot" _autoremap="true" />

<!-- Autoremap + override specific -->
<SubTree ID="MoveRobot" _autoremap="true" frame="world" />
```

Entries starting with `_` are treated as private and excluded from autoremap.

### 13.5 Debugging Subtrees

```cpp
tree.subtrees[0]->blackboard->debugMessage();
```

### 13.6 Multiple XML Files

```cpp
// Register all XMLs in a directory
for (auto const& entry : std::filesystem::directory_iterator("./"))
{
  if (entry.path().extension() == ".xml")
    factory.registerBehaviorTreeFromFile(entry.path().string());
}

// Then create specific trees by ID
auto tree = factory.createTree("MainTree");
```

---

## 14. Logging and Debugging

### 14.1 Logger Interface

All loggers inherit from `StatusChangeLogger` and receive callbacks on every node status transition.

```cpp
virtual void callback(
  BT::Duration timestamp,       // When the transition happened
  const TreeNode& node,         // The node that changed status
  NodeStatus prev_status,       // Previous status
  NodeStatus status);           // New status
```

Base class API (`loggers/abstract_logger.h`):
```cpp
void setEnabled(bool enabled);                          // Enable/disable logging
bool enabled() const;
void setTimestampType(TimestampType type);               // absolute (default) or relative
void enableTransitionToIdle(bool enable);                // Show/hide IDLE transitions (default: true)
bool showsTransitionToIdle() const;
```

### 14.2 Built-in Loggers

| Logger | Header | Description |
|--------|--------|-------------|
| `StdCoutLogger` | `loggers/bt_cout_logger.h` | Prints to stdout |
| `FileLogger2` | `loggers/bt_file_logger_v2.h` | Binary file, requires `.btlog` extension (Groot2) |
| `SqliteLogger` | `loggers/bt_sqlite_logger.h` | SQLite database, requires `.db3`/`.btdb` extension; supports `append` mode; `setAdditionalCallback()` to inject extra data per transition; `execSqlStatement()` for raw SQL |
| `MinitraceLogger` | `loggers/bt_minitrace_logger.h` | Chrome tracing JSON |
| `Groot2Publisher` | `loggers/groot2_publisher.h` | TCP to Groot2 via ZeroMQ (REP on `server_port`, PUB on `server_port+1`); default port 1667 |
| `TreeObserver` | `loggers/bt_observer.h` | In-memory statistics collection |

```cpp
auto tree = factory.createTreeFromText(xml);

// Console logger
BT::StdCoutLogger cout_logger(tree);

// File logger
BT::FileLogger2 file_logger(tree, "output.btlog");

// SQLite logger
BT::SqliteLogger sqlite_logger(tree, "output.db3");

tree.tickWhileRunning();
```

### 14.3 TreeObserver

Collects execution statistics for each node:

```cpp
BT::TreeObserver observer(tree);

tree.tickWhileRunning();

// Access statistics for a specific node
const auto& stats = observer.getStatistics("last_action");
// stats.transitions_count, stats.success_count,
// stats.failure_count, stats.skip_count
```

`NodeStatistics` struct (from `loggers/bt_observer.h:34-51`):
```cpp
struct NodeStatistics {
  NodeStatus last_result = NodeStatus::IDLE;        // Last SUCCESS or FAILURE
  NodeStatus current_status = NodeStatus::IDLE;     // Current status (any)
  unsigned transitions_count = 0;                   // Status transition count
  unsigned success_count = 0;                       // Times returned SUCCESS
  unsigned failure_count = 0;                       // Times returned FAILURE
  unsigned skip_count = 0;                          // Times returned SKIPPED
  Duration last_timestamp = {};                     // Last transition timestamp
};
```

Additional API:
```cpp
void resetStatistics();                            // Clear all collected statistics
const std::unordered_map<std::string, uint16_t>& pathToUID() const;  // Full path → UID
const std::map<uint16_t, std::string>& uidToPath() const;            // UID → full path (ordered)
```

### 14.4 Node Identification

Two mechanisms:
- `TreeNode::UID()` — unique numeric ID (depth-first traversal order)
- `TreeNode::fullPath()` — human-readable unique path: `subtree_name/node_name`

### 14.5 Status Change Subscriptions

```cpp
auto sub = node->subscribeToStatusChange(
  [](TimePoint timestamp, const TreeNode& node,
     NodeStatus prev_status, NodeStatus new_status) {
    // React to status changes
  });
```

### 14.6 Pre/Post Tick Callbacks

```cpp
node->setPreTickFunction([](TreeNode& self) -> NodeStatus {
  // Called before tick()
  return NodeStatus::SUCCESS;  // Return to skip actual tick
});

node->setPostTickFunction([](TreeNode& self, NodeStatus result) -> NodeStatus {
  // Called after tick(), can modify the return status
  return result;
});
```

---

## 15. Groot2 Integration

### 15.1 Basic Setup

```cpp
#include <behaviortree_cpp/loggers/groot2_publisher.h>

auto tree = factory.createTreeFromText(xml);
BT::Groot2Publisher publisher(tree, 1667);  // Default port (REP socket)

tree.tickWhileRunning();
```

Run Groot2, connect to `localhost:1667`. A second PUB port at `1668` (port+1) is used for real-time status streaming. Requires ZeroMQ.

### 15.2 JSON Export for Custom Types

```cpp
#include "behaviortree_cpp/json_export.h"

struct Position2D { double x, y; };

BT_JSON_CONVERTER(Position2D, pos) {
  add_field("x", &pos.x);
  add_field("y", &pos.y);
}

// In main():
BT::RegisterJsonDefinition<Position2D>();
```

The macro auto-generates `to_json`/`from_json` functions. Exported JSON includes a `"__type"` field (set to `BT::demangle(typeid(T))`). `std::vector<T>` conversions are auto-registered.

Or manually:
```cpp
void PositionToJson(nlohmann::json& dest, const Position2D& pos) {
  dest["x"] = pos.x;
  dest["y"] = pos.y;
}
BT::RegisterJsonDefinition<Position2D>(PositionToJson);
```

### 15.3 File Logging for Replay

```cpp
BT::FileLogger2 logger(tree, "output.btlog");
// BT::SqliteLogger logger(tree, "output.db3");
tree.tickWhileRunning();
// Open .btlog or .db3 in Groot2 for replay
```

### 15.4 Tree Export to JSON

```cpp
nlohmann::json json = BT::ExportTreeToJSON(tree);
BT::ImportTreeFromJSON(json, tree);
```

---

## 16. Substitution Rules and Mock Testing

### 16.1 C++ Substitution Rules

Replace nodes at construction time for testing:

```cpp
// Replace a node with another registered node (by fullPath pattern)
factory.addSubstitutionRule("talk", "TestSaySomething");

// Wildcard matching
factory.addSubstitutionRule("mysub/action_*", "TestAction");

// Use TestNode with configuration
BT::TestNodeConfig test_config;
test_config.async_delay = std::chrono::milliseconds(2000);
test_config.post_script = "msg ='message SUBSTITUTED'";
factory.addSubstitutionRule("last_action", test_config);
```

### 16.2 JSON Substitution Rules

```json
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

```cpp
factory.loadSubstitutionRuleFromJSON(json_text);
```

### 16.3 TestNodeConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `return_status` | NodeStatus | SUCCESS | Status to return |
| `async_delay` | milliseconds | 0 | If >0, makes node async |
| `success_script` | string | "" | Script on SUCCESS |
| `failure_script` | string | "" | Script on FAILURE |
| `post_script` | string | "" | Script on completion |
| `complete_func` | function | nullptr | Custom completion logic |

---

## 17. Global Blackboard Pattern

Share data between the main loop and the tree using an external blackboard.

```cpp
auto global_bb = BT::Blackboard::create();
auto maintree_bb = BT::Blackboard::create(global_bb);  // global_bb is parent
auto tree = factory.createTree("MainTree", maintree_bb);

for (int i = 1; i <= 3; i++)
{
  global_bb->set("value", i);
  tree.tickOnce();
  auto result = global_bb->get<int>("value_sqr");
}
```

Access global entries in XML with `@` prefix:

```xml
<PrintNumber val="{@value}" />
<Script code="@value_sqr := @value * @value" />
```

No remapping needed in subtrees — `@` always accesses the root blackboard.

---

## 18. Registration Methods

### 18.1 registerNodeType (Inheritance, Recommended)

```cpp
class MyNode : public BT::SyncActionNode
{
public:
  MyNode(const std::string& name, const BT::NodeConfig& config)
    : BT::SyncActionNode(name, config) {}
  static BT::PortsList providedPorts() { return { ... }; }
  BT::NodeStatus tick() override { ... }
};
factory.registerNodeType<MyNode>("MyNode");
```

### 18.2 registerSimpleAction

```cpp
factory.registerSimpleAction("MyAction",
  [](BT::TreeNode& self) {
    auto val = self.getInput<int>("value");
    self.setOutput("result", val.value() * 2);
    return BT::NodeStatus::SUCCESS;
  },
  { BT::InputPort<int>("value"), BT::OutputPort<int>("result") }
);
```

### 18.3 registerSimpleCondition

```cpp
factory.registerSimpleCondition("IsReady",
  [](BT::TreeNode& self) {
    return BT::NodeStatus::SUCCESS;
  }
);
```

### 18.4 registerSimpleDecorator

```cpp
factory.registerSimpleDecorator("MyDecorator",
  [](BT::NodeStatus child_status, BT::TreeNode& self) {
    return child_status;  // Pass through or modify
  },
  { BT::InputPort<int>("param") }
);
```

### 18.5 Constructor with Additional Arguments

```cpp
class Action_A : public BT::SyncActionNode
{
public:
  Action_A(const std::string& name, const BT::NodeConfig& config,
           int arg_int, std::string arg_str)
    : BT::SyncActionNode(name, config), _arg1(arg_int), _arg2(arg_str) {}
  // ...
};
factory.registerNodeType<Action_A>("Action_A", 42, "hello world");
```

### 18.6 Post-Construction Initialization (Visitor)

```cpp
class Action_B : public BT::SyncActionNode
{
public:
  Action_B(const std::string& name, const BT::NodeConfig& config)
    : BT::SyncActionNode(name, config) {}
  void initialize(int arg_int, const std::string& arg_str) { ... }
};

factory.registerNodeType<Action_B>("Action_B");
auto tree = factory.createTreeFromText(xml);
tree.applyVisitor([](TreeNode* node) {
  if (auto b = dynamic_cast<Action_B*>(node))
    b->initialize(69, "interesting_value");
});
```

### 18.7 Plugin Registration

```cpp
BTCPP_EXPORT void BT_RegisterNodesFromPlugin(BT::BehaviorTreeFactory& factory);

// In main:
factory.registerFromPlugin("path/to/plugin.so");
```

### 18.8 Unregistering Builders

```cpp
factory.unregisterBuilder("MyNode");  // Cannot unregister built-in nodes
```

---

### 18.9 BehaviorTreeFactory Public API Reference

```cpp
#include <behaviortree_cpp/bt_factory.h>
```

**Builder registration (low-level):**
```cpp
void registerBuilder(const TreeNodeManifest& manifest, const NodeBuilder& builder);
template <typename T> void registerBuilder(const std::string& ID, const NodeBuilder& builder);
```

Where `NodeBuilder` is:
```cpp
using NodeBuilder = std::function<std::unique_ptr<TreeNode>(
    const std::string&, const NodeConfig&)>;
```

And `TreeNodeManifest` contains:
```cpp
struct TreeNodeManifest {
  NodeType type;
  std::string registration_ID;
  PortsList ports;
  KeyValueVector metadata;
};
```

**Plugin support (deprecated):**
```cpp
[[deprecated]] void registerFromROSPlugins();
```

**Tree definition registration (parsing without instantiation):**
```cpp
void registerBehaviorTreeFromFile(const std::filesystem::path& filename);
void registerBehaviorTreeFromText(const std::string& xml_text);
std::vector<std::string> registeredBehaviorTrees() const;
void clearRegisteredBehaviorTrees();
```

**Low-level node instantiation:**
```cpp
std::unique_ptr<TreeNode> instantiateTreeNode(const std::string& name,
                                              const std::string& ID,
                                              const NodeConfig& config) const;
```

**Introspection:**
```cpp
const std::unordered_map<std::string, NodeBuilder>& builders() const;
const std::unordered_map<std::string, TreeNodeManifest>& manifests() const;
const std::set<std::string>& builtinNodes() const;
```

**Substitution rule management:**
```cpp
void clearSubstitutionRules();
const std::unordered_map<std::string, SubstitutionRule>& substitutionRules() const;
```

`SubstitutionRule` is:
```cpp
using SubstitutionRule = std::variant<std::string, TestNodeConfig,
                                      std::shared_ptr<TestNodeConfig>>;
```

**Scripting enum registration:**
```cpp
void registerScriptingEnum(StringView name, int value);       // Single enum
template <typename EnumType>
void registerScriptingEnums();                                 // All values via magic_enum
```

Example:
```cpp
registerScriptingEnum("THE_ANSWER", 42);
registerScriptingEnums<Color>();
// Then in XML: <Script code="my_color := Red" />
```

**Polymorphic cast registry:**
```cpp
PolymorphicCastRegistry& polymorphicCastRegistry();
const PolymorphicCastRegistry& polymorphicCastRegistry() const;
std::shared_ptr<PolymorphicCastRegistry> polymorphicCastRegistryPtr() const;
```

The registry is shared with all trees created from this factory, allowing trees to outlive the factory while maintaining access to polymorphic cast relationships.

**Tree creation alternatives:**
```cpp
Tree createTree(const std::string& tree_name,
                Blackboard::Ptr blackboard = Blackboard::create());
Tree createTreeFromFile(const std::filesystem::path& file_path,
                        Blackboard::Ptr blackboard = Blackboard::create());
Tree createTreeFromText(const std::string& xml_text,
                        Blackboard::Ptr blackboard = Blackboard::create());
```

The `Tree` copies all needed registry data and holds a shared pointer to the `PolymorphicCastRegistry`. The factory can be safely destroyed after `createTree()` — the tree continues to work independently.

**Extra-args registration overload (ports list provided explicitly, bypassing `providedPorts()`):**
```cpp
template <typename T, typename... ExtraArgs>
void registerNodeType(const std::string& ID, const PortsList& ports,
                      ExtraArgs... args);
```

---

## 19. Migration from v3.x to v4.x

### 19.1 Class Renaming

| v3.x | v4.x |
|------|------|
| `NodeConfiguration` | `NodeConfig` |
| `SequenceStar` | `SequenceWithMemory` |
| `AsyncActionNode` | `ThreadedAction` |
| `Optional<T>` | `Expected<T>` |

Temporary backward compatibility:
```cpp
namespace BT {
  using NodeConfiguration = NodeConfig;
  using AsyncActionNode = ThreadedAction;
  using Optional = Expected;
}
```

### 19.2 Removed Features

| v3.x Feature | v4.x Replacement |
|---|---|
| `UseBlockingAction` | `ThreadedAction` (manual) or `StatefulActionNode` (recommended) |
| `BlackboardCheckInt/Double/String` | `ScriptCondition` or `_failureIf` pre-condition |
| `SetBlackboard` (for simple values) | `<Script code="key := value" />` (SetBlackboard still exists in v4 but `<Script>` is preferred for simple constant values) |
| `SubTreePlus` | `SubTree` (new default) |

### 19.3 XML Changes

```xml
<!-- v3.x -->
<root>

<!-- v4.x -->
<root BTCPP_format="4">
```

A Python conversion script is available: `convert_v3_to_v4.py` (thanks to user SubaruArai).

### 19.4 SubTree Changes

```xml
<!-- v3.x -->
<SubTreePlus ID="MySubTree"/>

<!-- v4.x (SubTreePlus is now the default, renamed to SubTree) -->
<SubTree ID="MySubTree"/>
```

### 19.5 Script Replaces SetBlackboard + BlackboardCheck

```xml
<!-- v3.x -->
<SetBlackboard output_key="port_A" value="42" />
<BlackboardCheckInt value_A="{port_A}" value_B="{port_B}"
                    return_on_mismatch="FAILURE">
  <MyAction/>
</BlackboardCheckInt>

<!-- v4.x -->
<Script code="port_A := 42; port_B := 69" />
<MyAction _failureIf="port_A != port_B" />
```

### 19.6 Execution Loop

```cpp
// v3.x
while (status != NodeStatus::SUCCESS || status == NodeStatus::FAILURE) {
  status = tree.tickRoot();
  std::this_thread::sleep_for(sleep_ms);
}

// v4.x (recommended)
tree.tickWhileRunning(sleep_ms);

// v4.x alternative
while (!isStatusCompleted(status)) {
  status = tree.tickOnce();
  tree.sleep(sleep_ms);
}
```

### 19.7 SKIPPED Status

v4 adds `SKIPPED` status for PreConditions. Custom leaf nodes must NOT return it; control nodes must handle it (skip to next child).

### 19.8 AsyncSequence / AsyncFallback

New control nodes (v4+) to address the "atomic sequence" problem — they yield after each synchronous child, allowing reactive parents to intervene.

### 19.9 Support for Polymorphic Pointers

v4.5+ supports polymorphic downcasting via `registerPolymorphicCast<Derived, Base>()`:
```cpp
factory.registerPolymorphicCast<DerivedType, BaseType>();
```
This enables `setOutput<BaseType>` and `getInput<std::shared_ptr<BaseType>>` when the blackboard entry contains a `std::shared_ptr<DerivedType>`.

---

## 20. Advanced Features

### 20.1 Blackboard::cloneInto

Copy all entries from one blackboard to another:
```cpp
src_bb->cloneInto(dst_bb);
```

### 20.2 Blackboard Backup/Restore

Save and restore entire tree state:
```cpp
auto backup = BT::BlackboardBackup(tree);
// ... tick tree ...
BT::BlackboardRestore(backup, tree);
```

### 20.3 Polymorphic Cast Registry

Register polymorphic downcast rules:
```cpp
factory.registerPolymorphicCast<Derived, Base>();
```
This enables `getInput<std::shared_ptr<Base>>()` even when the blackboard stores `std::shared_ptr<Derived>`.

### 20.4 Metadata

Add metadata to node manifests:
```cpp
factory.addMetadataToManifest("MyNode", {{"version", "2.0"}, {"author", "me"}});
```

### 20.5 Exception Types

Exception hierarchy (from `include/behaviortree_cpp/exceptions.h`):
```cpp
BehaviorTreeException : std::exception    // Base, variadic StrCat constructor
├── LogicError                            // Code refactoring required (compile-time issues)
└── RuntimeError                          // Runtime data/condition errors
    └── NodeExecutionError                // tick() threw (includes node path + type)
```

`NodeExecutionError` wraps a `TickBacktraceEntry` with `failedNode()` and `originalMessage()`:
```cpp
catch(const BT::NodeExecutionError& ex) {
  auto& node = ex.failedNode();
  std::cerr << "Failed at " << node.node_path
            << " [" << node.registration_name << "]: "
            << ex.originalMessage();
}
```

### 20.6 PreTick / PostTick Functions

Attach callbacks that run before/after a node's tick:
```cpp
node->setPreTickFunction([](TreeNode& self) -> NodeStatus {
  // Called before tick(). Return non-IDLE to skip actual tick.
  return {};
});
node->setPostTickFunction([](TreeNode& self, NodeStatus result) -> NodeStatus {
  // Called after tick(). Can modify the return value.
  return result;
});
```

### 20.6 Watchdog / Tick Monitor

Monitor total tick execution time:
```cpp
node->setTickMonitorCallback(
  [](TreeNode& node, NodeStatus status, std::chrono::microseconds duration) {
    if (duration > std::chrono::milliseconds(100))
      std::cerr << "Slow tick: " << node.name() << std::endl;
  });
```

### 20.7 JSON Conversion

Export/import entire trees as JSON:
```cpp
nlohmann::json json = BT::ExportTreeToJSON(tree);
BT::ImportTreeFromJSON(json, tree);
```

Also blackboard-specific:
```cpp
nlohmann::json bb_json = BT::ExportBlackboardToJSON(blackboard);
BT::ImportBlackboardFromJSON(json, blackboard);
```

---

## 21. Complete Tutorial Examples

### 21.1 First Behavior Tree — Full Example

From `tutorial_01_first_tree.md`. Demonstrates three registration patterns: inheritance, free function, and class method.

**XML (`my_tree.xml`):**
```xml
<root BTCPP_format="4">
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

**C++ (full program):**
```cpp
#include "behaviortree_cpp/bt_factory.h"
#include <iostream>

using namespace BT;

// Pattern 1: Inheritance — SyncActionNode
class ApproachObject : public SyncActionNode
{
public:
  ApproachObject(const std::string& name, const NodeConfig& config)
    : SyncActionNode(name, config) {}

  NodeStatus tick() override
  {
    std::cout << "ApproachObject: " << name() << std::endl;
    return NodeStatus::SUCCESS;
  }
};

// Pattern 2: Free function → registerSimpleCondition
NodeStatus CheckBattery()
{
  std::cout << "[ Battery: OK ]" << std::endl;
  return NodeStatus::SUCCESS;
}

// Pattern 3: Class method → registerSimpleAction
class GripperInterface
{
public:
  GripperInterface() : _open(true) {}
  NodeStatus open() {
    _open = true;
    std::cout << "GripperInterface::open" << std::endl;
    return NodeStatus::SUCCESS;
  }
  NodeStatus close() {
    _open = false;
    std::cout << "GripperInterface::close" << std::endl;
    return NodeStatus::SUCCESS;
  }
private:
  bool _open;
};

int main()
{
  BehaviorTreeFactory factory;

  // 1. Inheritance — most common for complex nodes
  factory.registerNodeType<ApproachObject>("ApproachObject");

  // 2. Simple condition from a free function
  factory.registerSimpleCondition("CheckBattery", [](BT::TreeNode&){ return CheckBattery(); });

  // 3. Simple action wrapping class methods
  GripperInterface gripper;
  factory.registerSimpleAction("OpenGripper",
    [&](TreeNode&) { return gripper.open(); });
  factory.registerSimpleAction("CloseGripper",
    [&](TreeNode&) { return gripper.close(); });

  auto tree = factory.createTreeFromFile("./my_tree.xml");
  tree.tickWhileRunning();

  return 0;
}
/* Expected output:
  [ Battery: OK ]
  GripperInterface::open
  ApproachObject: approach_object
  GripperInterface::close
*/
```

### 21.2 Asynchronous StatefulActionNode — Full Example

From `tutorial_04_sequence.md`. Demonstrates async pattern with `onStart`/`onRunning`/`onHalted`.

```cpp
class MoveBaseAction : public StatefulActionNode
{
public:
  MoveBaseAction(const std::string& name, const NodeConfig& config)
    : StatefulActionNode(name, config) {}

  static PortsList providedPorts() {
    return { InputPort<Pose2D>("goal") };
  }

  NodeStatus onStart() override {
    if (!getInput("goal", goal_)) {
      throw RuntimeError("Missing goal");
    }
    std::cout << "Moving to: " << goal_ << std::endl;
    start_time_ = std::chrono::system_clock::now();
    return NodeStatus::RUNNING;
  }

  NodeStatus onRunning() override {
    auto elapsed = std::chrono::system_clock::now() - start_time_;
    if (elapsed > std::chrono::seconds(2)) {
      std::cout << "Goal reached!" << std::endl;
      return NodeStatus::SUCCESS;
    }
    return NodeStatus::RUNNING;
  }

  void onHalted() override {
    std::cout << "MoveTo halted, cleaning up" << std::endl;
  }

private:
  Pose2D goal_;
  std::chrono::system_clock::time_point start_time_;
};

// Register and use:
// factory.registerNodeType<MoveBaseAction>("MoveBase");
```

### 21.3 SubTrees and CrossDoor — Full Example

From `tutorial_05_subtrees.md`. Demonstrates tree composition with multiple `<BehaviorTree>` definitions.

**XML (`crossdoor.xml`):**
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

**C++:**
```cpp
class CrossDoor
{
public:
  void registerNodes(BehaviorTreeFactory& factory);

  NodeStatus isDoorClosed();
  NodeStatus passThroughDoor();
  NodeStatus pickLock();
  NodeStatus openDoor();
  NodeStatus smashDoor();

private:
  bool _door_open = false;
  bool _door_locked = true;
  int _pick_attempts = 0;
};

void CrossDoor::registerNodes(BehaviorTreeFactory& factory)
{
  factory.registerSimpleCondition(
      "IsDoorClosed", [this](TreeNode&) { return isDoorClosed(); });
  factory.registerSimpleAction(
      "PassThroughDoor", [this](TreeNode&) { return passThroughDoor(); });
  factory.registerSimpleAction(
      "OpenDoor", [this](TreeNode&) { return openDoor(); });
  factory.registerSimpleAction(
      "PickLock", [this](TreeNode&) { return pickLock(); });
  factory.registerSimpleCondition(
      "SmashDoor", [this](TreeNode&) { return smashDoor(); });
}

NodeStatus CrossDoor::isDoorClosed() {
  return _door_open ? NodeStatus::FAILURE : NodeStatus::SUCCESS;
}
NodeStatus CrossDoor::passThroughDoor() {
  return _door_open ? NodeStatus::SUCCESS : NodeStatus::FAILURE;
}
NodeStatus CrossDoor::pickLock() {
  _pick_attempts++;
  if (_pick_attempts >= 3) {
    _door_locked = false;
    _door_open = true;
    return NodeStatus::SUCCESS;
  }
  return NodeStatus::FAILURE;
}
NodeStatus CrossDoor::openDoor() {
  if (!_door_locked) { _door_open = true; return NodeStatus::SUCCESS; }
  return NodeStatus::FAILURE;
}
NodeStatus CrossDoor::smashDoor() {
  _door_open = true; return NodeStatus::SUCCESS;
}

int main()
{
  BehaviorTreeFactory factory;
  CrossDoor cross_door;
  cross_door.registerNodes(factory);
  factory.registerBehaviorTreeFromFile("./crossdoor.xml");

  auto tree = factory.createTree("MainTree");
  printTreeRecursively(tree.rootNode());
  tree.tickWhileRunning();
  return 0;
}
```

### 21.4 TreeObserver — Full Example

From `tutorial_10_observer.md`. Demonstrates logging, statistics collection, and UID/fullPath mapping.

**XML (`demo_observer.xml`):**
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
    </Sequence>
  </BehaviorTree>
</root>
```

**C++:**
```cpp
int main()
{
  BehaviorTreeFactory factory;
  factory.registerBehaviorTreeFromFile("./demo_observer.xml");
  auto tree = factory.createTree("MainTree");

  BT::printTreeRecursively(tree.rootNode());

  // Observer collects per-node statistics
  BT::TreeObserver observer(tree);

  // Print UID ↔ fullPath mapping
  std::map<uint16_t, std::string> ordered;
  for (const auto& [name, uid] : observer.pathToUID()) {
    ordered[uid] = name;
  }
  for (const auto& [uid, name] : ordered) {
    std::cout << uid << " -> " << name << std::endl;
  }

  tree.tickWhileRunning();

  // Query statistics by full path or UID
  const auto& stats = observer.getStatistics("last_action");
  std::cout << "last_action transitions: " << stats.transitions_count
            << " success: " << stats.success_count << std::endl;

  return 0;
}
```

---

## 22. Best Practices

1. **Use ports instead of direct blackboard access** — self-documenting, remappable, type-safe
2. **Prefer `StatefulActionNode`** over `ThreadedAction` — simpler, safer
3. **Never block in `tick()`** — use `StatefulActionNode` with `onStart/onRunning`
4. **Check `isHaltRequested()` in `ThreadedAction`** — required for clean halting
5. **Use `Script` instead of `SetBlackboard`** — cleaner syntax
6. **Use `_failureIf`/`_skipIf` for simple pre-conditions** — no C++ changes needed
7. **Use `<Precondition>` with `else="RUNNING"`** for per-tick re-evaluation
8. **Use `LoopNode` instead of deprecated `ConsumeQueue`**
9. **Use `_autoremap="true"`** to reduce boilerplate in subtrees
10. **Use `AsyncSequence`/`AsyncFallback`** inside `ReactiveSequence`/`ReactiveFallback` for interruptible sequences
11. **Use `convertFromString` template specialization** for custom types
12. **Use `getLockedPortContent()` for zero-copy** access to large data
13. **Use `TreeObserver` for unit testing** — verify expected transitions
14. **Use substitution rules for mock testing** — replace nodes without recompilation
15. **Use `@` prefix for global blackboard** — simple cross-tree data sharing

---

## Reference

- **Official Documentation**: https://www.behaviortree.dev/
- **GitHub**: https://github.com/BehaviorTree/BehaviorTree.CPP
- **API Reference**: https://behaviortree.github.io/BehaviorTree.CPP/
- **Groot2**: https://www.behaviortree.dev/groot/
- **Version**: 4.9.0 (CMake: `project(behaviortree_cpp VERSION 4.9.0)`)
- **License**: MIT

{% endraw %}
