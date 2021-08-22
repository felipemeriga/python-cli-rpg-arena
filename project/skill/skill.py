import sys
from typing import Dict, List

from project.conf import get_configuration
from project.interface import IPlayer, ISkill
from project.utils import SKILLS_SECTION

"""
This is the base class for defining a Skill, as all the skills are defined dynamically on the skills.yaml file, 
there is a set of attributes required for each skill, and their behavior will be basically the same, inflicting or 
healing players.

For extending this game functionality, concrete classes that extends Skill base class can be created, for modifying 
what happens when a character uses that skill. 

For example, the skill Fireball doesn't need to be override, only defined on skills.yaml file, because the purpose of 
that skill it's only inflicting damage.

Now, imagine Steal skill, instead of inflicting/healing, the purpose it's stealing someone's item. So that skill can
be overrided by a concrete classes, and we can call them custom skills.

So we have dynamic skills that follows the imposed behavior of the parent class Skill, and the custom Skills that 
extents that.
"""


class Skill(ISkill):
    def __init__(self, name: str, description: str, base: int, cost: int,
                 kind: str, level_requirement: int, field: int, job: str) -> None:
        """
        Constructor of the Skill parent class.

        :param str name: The name of the skill.
        :param str name: The name of the skill.
        :param str name: The name of the skill.
        :param str name: The name of the skill.

        :rtype: None.
        """
        self.name = name
        self.description = description
        self.base = base
        self.cost = cost
        self.kind = kind
        self.level_requirement = level_requirement
        self.field = field
        self.job = job

    def execute(self, player: IPlayer) -> None:
        pass


instantiated_skills: Dict = {}


def dynamic_skill_class_factory(name: str, argument_names: List, base_class: type):
    """
    Skills are defined in the configuration file conf.yaml, this class helps in dynamically creating,
    at runtime, classes that can be instantiated with the name of the skill.

    :param str name: The name of the dynamic class.
    :param List argument_names: The attributes list of the class.
    :param type base_class: The base class, from where the dynamic class will inherit properties.

    :rtype: None.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in argument_names:
                raise TypeError("Argument %s not valid for %s"
                                % (key, self.__class__.__name__))
        base_class.__init__(self, **kwargs)

    new_class = type(name, (base_class,), {"__init__": __init__})
    return new_class


def get_instantiated_skill(skill_dict: Dict) -> ISkill:
    """
    Receiving a dictionary with all the characteristics of a Skill, this dictionary will be instantiated in a class that
    represents this Skill.

    :param Dict skill_dict: The name of the dynamic class.

    :rtype: ISkill.
    """
    custom_skill = None
    skill_key = list(skill_dict.keys())[0]
    if skill_key not in instantiated_skills:
        skill_values = skill_dict.get(skill_key)
        skill_pkg = sys.modules[__package__].__getattribute__('skill')
        if skill_key in skill_pkg.__dict__:
            prev_defined_class = getattr(skill_pkg, skill_key)
            custom_skill = prev_defined_class(
                name=skill_values.get('name'),
                description=skill_values.get('description'),
                base=skill_values.get('base'),
                cost=skill_values.get('cost'),
                kind=skill_values.get('kind'),
                level_requirement=skill_values.get('level_requirement'),
                field=skill_values.get('field'),
                job=skill_values.get('job'),
            )
        else:
            dynamic_skill_class = dynamic_skill_class_factory(skill_key, list(skill_values), Skill)
            custom_skill = dynamic_skill_class(name=skill_values.get('name'),
                                               description=skill_values.get('description'),
                                               base=skill_values.get('base'),
                                               cost=skill_values.get('cost'),
                                               kind=skill_values.get('kind'),
                                               level_requirement=skill_values.get('level_requirement'),
                                               field=skill_values.get('field'),
                                               job=skill_values.get('job'))
        instantiated_skills[skill_key] = custom_skill
    else:
        custom_skill = instantiated_skills[skill_key]

    return custom_skill


def get_player_available_skills(player: IPlayer) -> List[ISkill]:
    """
    Skills can be unlocked/revealed for players depending their levels and jobs, this method compare the current
    attributes of a player, will all the skills, to check which ones this current player has eligibility to use.

    :param IPlayer player: The current player to discover new skills.

    :rtype: List[ISkill].
    """
    skill_dicts = get_configuration(SKILLS_SECTION)
    available_skills: List[ISkill] = []

    for key, value in skill_dicts.items():
        if player.job.get_name() == value.get('job') and player.level == value.get('level_requirement'):
            available_skills.append(get_instantiated_skill({key: value}))

    return available_skills


"""
--------------- EXTENDED SKILLS ---------------

For default, skills are intended to heal or cause damage to one player, that is why all the skills present in the
skills configuration file, has a default instantiating mechanism that inherits from Skill parent class, that has the 
execute method, which simply executes the skill. But you can override the functionality of skills from configuration
file, creating a concrete class above here and override the methods from Skill class.

This functionally extends the basic implementation, adding more possibilities to the skills in the game. For example,
the Steal skill from Rogue class, instead of it causing damage or healing someone, this class is written above, 
making possible from a player to steal the item from another one.

"""


class Steal(Skill):

    def __init__(self, name: str, description: str, base: int, cost: int, kind: str, level_requirement: int, field: int,
                 job: str) -> None:
        super().__init__(name, description, base, cost, kind, level_requirement, field, job)
