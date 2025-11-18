"""
Author information: Thomas I. EDER
To contact me: thomas@katagames.io
----------------------------------

PMDI stands for: Py-Multiple Dependency Injection.
This module defines the *core primitives* of the PMDI pattern:

- CustomizableCode: abstract base class that knows how to instantiate
  multiple dependencies in one go (via instantiate_dependencies).

- wire_dependencies: function that creates a *new concrete subclass*
  with all required dependencies wired.

Mini-guide:
-----------
1) You define an abstract "*Base" class that subclasses CustomizableCode
   and declares:

       required_dependencies = {"dep1", "dep2", ...}

   and in __init__ you call:

       self.instantiate_dependencies(dep1_kwargs={...}, dep2_kwargs={...})

2) You then call:
       ConcreteClass = wire_dependencies(BaseClass, dep1=Dep1Cls, dep2=Dep2Cls)

   BaseClass remains abstract (cannot be instantiated) as long as
   required_dependencies is non-empty. ConcreteClass is the wired,
   instanciable variant.

This keeps a clean separation between *what* a component needs(expressed in the Base cls)
and *how* those needs are fulfilled (expressed in the wiring step).
"""
from abc import ABC
import re
from typing import Optional, Dict, Any, Set, Type


def _extract_prefix_before_kwargs(kwargs_name: str) -> Optional[str]:
    """
    Helper function used by instantiate_dependencies.

    It takes a keyword argument name like "cylinder_kwargs" and returns
    the logical dependency name "cylinder".

    If the name does not follow the "<name>_kwargs" convention,
    None is returned and an error will be raised by the caller.
    """
    match = re.match(r"(.+)_kwargs$", kwargs_name)
    if match:
        return match.group(1)
    return None  # Return None if it doesn't match the expected pattern


class CustomizableCode(ABC):
    """
    Base class for PMDI-enabled components.

    Subclasses should:
    ------------------
    1) Declare which dependencies they *require* at the class level:

           required_dependencies = {"cylinder", "bumper", ...}

    2) Inside __init__, call:

           self.instantiate_dependencies(
               cylinder_kwargs={...},
               bumper_kwargs={...},
           )

       The PMDI system will create attributes self.cylinder, self.bumper
       using the wired dependency classes.

    Abstract behavior:
    ------------------
    CustomizableCode also enforces that a subclass with non-empty
    required_dependencies *cannot* be instantiated unless it has been
    wired with wire_dependencies(...). This is done via __new__.
    """

    # Names of dependencies that MUST be wired at the class level
    required_dependencies: Set[str] = set()

    def __new__(cls, *args, **kwargs):
        """
        Enforces that the class behaves as "abstract until wired".

        If required_dependencies is non-empty, we check that the class
        has a declared_dependencies dict, and that it contains entries
        for all required names. If not, a TypeError is raised.

        This prevents accidental instantiation of a partially wired class.
        """
        required = getattr(cls, "required_dependencies", set())
        if required:
            declared = getattr(cls, "declared_dependencies", {})
            missing = set(required) - set(declared.keys())
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise TypeError(
                    f"Cannot instantiate '{cls.__name__}' – missing wired dependencies: "
                    f"{missing_str}. Use wire_dependencies({cls.__name__}, ...) first."
                )
        return super().__new__(cls)

    def instantiate_dependencies(self, **kwargs: Dict[str, Any]) -> None:
        """
        Instantiate all declared dependencies at once.

        Expected usage in a subclass __init__:

            self.instantiate_dependencies(
                cylinder_kwargs={...},
                bumper_kwargs={...},
            )

        Convention:
        -----------
        - Each keyword must end with "_kwargs" (e.g. "cylinder_kwargs")
        - The prefix before "_kwargs" corresponds to the dependency name
          declared at wiring time (e.g. cylinder=CylinderClass).

        Side effects:
        -------------
        For each dependency 'x', an attribute self.x is created and set
        to an instance of the corresponding dependency class.
        """
        cls = self.__class__
        required = getattr(cls, "required_dependencies", set())

        # 1) Check that all required deps have a corresponding *_kwargs
        missing_kwargs = [
            dep for dep in required
            if f"{dep}_kwargs" not in kwargs
        ]
        if missing_kwargs:
            missing_str = ", ".join(sorted(missing_kwargs))
            raise RuntimeError(
                f"During instantiation of {cls.__name__}, missing kwargs for "
                f"dependencies: {missing_str}."
            )

        # 2) Instantiate each provided dependency
        declared = getattr(cls, "declared_dependencies", {})

        for dep_kw_name, dep_kwargs in kwargs.items():
            infotag = _extract_prefix_before_kwargs(dep_kw_name)
            if infotag is None:
                raise RuntimeError(
                    f"Dependency kwarg name '{dep_kw_name}' is invalid. Expected a name "
                    f"like '<dependency>_kwargs'."
                )

            if infotag not in declared:
                raise RuntimeError(
                    f"Dependency '{infotag}' not declared for class '{cls.__name__}'. "
                    f"Did you forget to wire it with wire_dependencies(...) ?"
                )

            dep_class = declared[infotag]
            # Instantiate the dependency and attach it as an attribute on self
            setattr(self, infotag, dep_class(**dep_kwargs))


def wire_dependencies(base_cls: Type[CustomizableCode], **dependencies: Type) -> Type[CustomizableCode]:
    """
    Create a *new* concrete subclass of base_cls with the given dependencies wired.

    This is the core of the PMDI Pattern B:

    - base_cls expresses *what* dependencies are needed (via required_dependencies
      and calls to instantiate_dependencies).
    - wire_dependencies decides *which* exact classes are used for each dependency,
      and returns a concrete, instanciable subclass.

    Example:
    --------

        class EngineBase(CustomizableCode):
            required_dependencies = {"cylinder"}

            def __init__(self):
                self.instantiate_dependencies(
                    cylinder_kwargs={},
                )

        class CylinderClass: ...

        Engine = wire_dependencies(EngineBase, cylinder=CylinderClass)
        engine = Engine()   # OK
        EngineBase()        # TypeError: abstract until wired
    """
    # Name of the new concrete class
    name = base_cls.__name__ + "Wired"

    # Create a new subclass that inherits from base_cls
    new_cls = type(name, (base_cls,), {})

    # Attach declared_dependencies on the new class.
    # We lower-case the keys to be tolerant about naming.
    new_cls.declared_dependencies = {k.lower(): v for k, v in dependencies.items()}

    # Optional but useful: check that all required deps are now present.
    required = getattr(base_cls, "required_dependencies", set())
    missing = set(required) - set(new_cls.declared_dependencies.keys())
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise TypeError(
            f"wire_dependencies({base_cls.__name__}, ...) is incomplete – still missing: "
            f"{missing_str}"
        )

    return new_cls
