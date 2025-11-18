
# PMDI — Python Multiple Dependency Injection

*A lightweight, explicit wiring pattern for large Python codebases*

PMDI (Python Multiple Dependency Injection) is a small but powerful design pattern that makes **complex object wiring** easy, explicit, and maintainable — without relying on heavy DI frameworks or opaque decorators.

PMDI is especially suited for:

- game engines
- simulations
- trading bots
- plugin-based architectures
- large systems where components need to be configured *outside* their own modules

If your project has objects that depend on several other objects, PMDI helps you cleanly separate:

- **WHAT a component needs** → declared in an abstract `*Base` class
- **HOW those needs are fulfilled** → declared once in a wiring step

This leads to clearer architecture, better testing, and more modular code.

---

## Why PMDI Exists?

In many Python projects you will find classes like this:

```python
class Engine:
    def __init__(self):
        self.cylinder = CylinderClass()
        self.cooling = CoolingSystem()
        self.injector = FuelInjector()
```

This works well… Until you want:

- a different engine configuration
- mocks for testing
- dynamic loading of modules
- multiple implementations of the same dependency

Suddenly, the class looks tangled due to hard-coded dependencies.

**PMDI solves this by externalizing all dependency choice and instantiation.**

---

## Core Idea of the PMDI Pattern

PMDI revolves around **two core primitives**:

### 1. CustomizableCode
The base class that:
- declares which dependencies are *required*
- instantiates all dependencies in a single call
- prevents instantiation until dependencies are correctly wired
  (“**abstract until wired**” behavior)

### 2. wire_dependencies(BaseClass, dep1=Cls1, dep2=Cls2, …)
This function creates a **new concrete subclass** with all dependencies injected.

Your original base class remains abstract.

This mirrors patterns like:
- Strategy / Abstract Factory
- Dependency Injection Containers
but without the complexity.

---

## A Short Example

### Step 1 — declare what the class *needs*

```python
class EngineBase(CustomizableCode):
    required_dependencies = {"cylinder"}

    def __init__(self):
        self.instantiate_dependencies(
            cylinder_kwargs={}
        )
```

This class **cannot be instantiated** yet.

### Step 2 — declare *which* implementations to use

```python
Engine = wire_dependencies(
    EngineBase,
    cylinder=CylinderClass
)
```

### Step 3 — use it

```python
e = Engine()
e.cylinder.fire()
```

Clean, explicit, zero magic.

---

## When Should I Use PMDI?

Using PMDI can be a good fit with your project, whenever your system has:

- objects with 2+ dependencies
- multiple components that are "swappable"
- high-level modules that should not know about low-level implementations
- a very modular/plugin-oriented architecture

… Or when you have a rather large project where wiring should be centralized for readability.

I do not recommend using the PMDI, if:
- your large object/class only uses 1 dependency
- your codebase is small and therefore easy to read and maintain
- you prefer to use a more complete framework to handle code dependencies (a dependency-injection container, or a D.I. system)

---

## License
(C) 2024- Author is: Thomas I. Eder (contact: thomas@katagames.io), code in this repo is released under the MIT License.
