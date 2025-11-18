"""
Author information: Thomas I. EDER
To contact me: thomas@katagames.io
----------------------------------
PMDI stands for: Py- Multiple Dependency Injection.

This file showcases the PMDI pattern using a simple Car / Engine example.

We use the *Pattern B* style:
- Define abstract "*Base" classes that inherit from CustomizableCode
  and declare which dependencies they need.
- Use wire_dependencies(...) to create *concrete*, wired classes that
  can actually be instantiated.

Why this pattern is useful:
---------------------------
It lets you:
- Define high-level behavior (what a Car or Engine needs) in one place.
- Provide concrete implementations (which Bumper, which Engine, etc.)
  in a separate wiring step.
- Keep modules with complex logic loosely coupled, while still allowing
  code to be shared between them in a controlled, explicit way.

This is especially useful in large codebases (like pyved_engine) where
you want to:
- Import high-level definitions (events, abstractions, etc.)
- Define custom classes at a lower level using those definitions
- Inject these custom classes back into the high-level module in a clean,
  explicit manner.
"""
from abc import ABC, abstractmethod
from cd_patterns import CustomizableCode, wire_dependencies


# ------------------------------
# Abstract Component Interfaces
# ------------------------------
class AbstractBumper(ABC):
    @abstractmethod
    def protect(self):
        """
        Method to be implemented by the concrete bumper class.
        It defines how the bumper protects the car.
        """
        pass


class AbstractWindshield(ABC):
    @abstractmethod
    def shield(self):
        """
        Method to be implemented by the concrete windshield class.
        It defines how the windshield shields the car.
        """
        pass


class AbstractCylinder(ABC):
    @abstractmethod
    def fire(self):
        """
        Method to be implemented by the concrete cylinder class.
        It defines how the cylinder fires, typically representing engine combustion.
        """
        pass


class AbstractEngine(ABC):
    @abstractmethod
    def start(self):
        """
        Method to be implemented by the concrete engine class.
        Defines how the engine starts.
        """
        pass

    @abstractmethod
    def overheat(self):
        """
        Method to be implemented by the concrete engine class.
        Defines the behavior when the engine overheats.
        """
        pass


# ------------------------------
# Concrete Implementations of Components
# ------------------------------
class BumperClass(AbstractBumper):
    def __init__(self, hp: int):
        """
        Initializes the bumper with its hit points (hp).
        """
        self.hp = hp

    def protect(self):
        """
        Simulates the bumper protecting the car.
        """
        print("Bumper protects the car!")


class WindshieldClass(AbstractWindshield):
    def shield(self):
        """
        Simulates the windshield shielding the car.
        """
        print("Windshield shields the car!")


class CylinderClass(AbstractCylinder):
    def fire(self):
        """
        Simulates the cylinder firing (engine combustion).
        """
        print("Vroum vroum!")


# ------------------------------
# Customizable Pattern Demo (Pattern B)
# EngineBase and CarBase are *abstract* customizable classes.
# Concrete Engine and Car classes are produced via wire_dependencies.
# ------------------------------
class EngineBase(AbstractEngine, CustomizableCode):
    """
    Abstract engine definition that says:
    - "I need a 'cylinder' dependency"
    - "At construction, please instantiate it for me"

    The actual class used for 'cylinder' will be provided later, via
    wire_dependencies(...). As long as EngineBase is not wired, it is
    considered abstract and cannot be instantiated.
    """
    required_dependencies = {"cylinder"}  # it answers: Which dependencies required for this base class?

    def __init__(self, etype, producer_name):
        """
        Initializes the engine with its type and producer's name.
        Also ensures that the 'cylinder' dependency is instantiated.
        """
        self.instantiate_dependencies(
            cylinder_kwargs={}  # The wired Cylinder class will be called with these kwargs
        )
        print(f"An engine has been built, type: {etype}, produced by: {producer_name}")

    def start(self):
        """
        Starts the engine and fires the cylinder.
        """
        print("Engine starts.")
        print(f"Engine has cylinder: {self.cylinder}")
        self.cylinder.fire()

    def overheat(self):
        """
        Simulates engine overheating.
        """
        print("Engine needs more cooling!")


class CarBase(CustomizableCode):
    """
    Abstract car definition that says:
    - "I need bumper, windshield, and engine dependencies"
    - "At construction, please instantiate them for me"

    The concrete classes for bumper, windshield, and engine will be
    provided later using wire_dependencies(...).
    """
    required_dependencies = {"bumper", "windshield", "engine"}

    def __init__(self):
        """
        Initializes the car by injecting all necessary dependencies
        (bumper, windshield, engine).
        """
        self.instantiate_dependencies(
            bumper_kwargs={'hp': 95},
            windshield_kwargs={},
            engine_kwargs={'etype': 6, 'producer_name': 'BMW'}
        )
        print("The car gets out of the factory!")

    def test_car(self):
        """
        Simulates testing the car by activating its components.
        """
        self.bumper.protect()
        self.windshield.shield()
        self.engine.start()


# ------------------------------
# Wiring Step: Produce Concrete Classes
# ------------------------------

# Here we decide *which* actual classes are used to satisfy the dependencies
# declared in EngineBase and CarBase. The result are two fully wired,
# concrete classes: Engine and Car.

# EngineBase requires a 'cylinder' dependency
Engine = wire_dependencies(EngineBase, cylinder=CylinderClass)

# CarBase requires 'bumper', 'windshield', and 'engine' dependencies.
# Note that we pass the *wired* Engine class as the 'engine' dependency.
Car = wire_dependencies(
    CarBase,
    bumper=BumperClass,
    windshield=WindshieldClass,
    engine=Engine,
)


# ------------------------------
# Showcasing PMDI / Le "cas d'école"
# ------------------------------
try:
    # Trying to instantiate EngineBase() or CarBase() directly would raise TypeError,
    # because they are "abstract until wired".
    #
    # engine_base = EngineBase("V6", "ACME")  # -> TypeError
    # car_base = CarBase()                       # -> TypeError

    # Instantiating the wired Car class works as expected:
    car = Car()
    print('-')
    car.test_car()       # Testing the car by calling its methods
    print('+')
    car.engine.overheat()  # Testing the engine's overheat functionality
    print('Bumper status?', car.bumper.hp)  # Printing the bumper's hit points

except (RuntimeError, TypeError) as e:
    print(f"Showcasing PMDI raised an exception: {e}")
