from contextlib import contextmanager
from unittest.mock import MagicMock, patch
import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

"""Fixtures providing sample meal combatants for the tests."""
@pytest.fixture()
def sample_combatant1():
    return Meal(0, "popcorn", "american", 25.00, "LOW")

@pytest.fixture()
def sample_combatant2():
    return Meal(1, "pasta", "italian", 30.00, "MED")

@pytest.fixture()
def sample_combatant3():
    return Meal(2, "pizza", "italian", 20.00, "HIGH")

"""Fixtures providing sample battles for the tests."""
@pytest.fixture()
def sample_battle(sample_combatant1, sample_combatant2):
    return [sample_combatant1, sample_combatant2]

@pytest.fixture()
def sample_battle2(sample_combatant1, sample_combatant2, sample_combatant3):
    return [sample_combatant1, sample_combatant2, sample_combatant3]

"""Fixtures that mock existing functions"""
@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

@pytest.fixture
def mock_get_random(mocker):
    """Mock the get_random function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.get_random", return_value=0.5)

##################################################
# Combatant Management Test Cases
##################################################

def test_clear_combatants(battle_model, sample_combatant1):
    """Test removing all combatants that are prepped."""
    battle_model.prep_combatant(sample_combatant1)
    battle_model.clear_combatants()

    combatant_list = battle_model.get_combatants()
    assert len(combatant_list) == 0

def test_get_combatants(battle_model, sample_battle):
    """Test retrieving all combatants that have been prepped."""
    battle_model.prep_combatant(sample_battle[0])
    battle_model.prep_combatant(sample_battle[1])
    all_combatants = battle_model.get_combatants()

    assert len(all_combatants) == 2
    assert all_combatants[0].id == 0
    assert all_combatants[1].id == 1

def test_prep_combatant(battle_model, sample_battle2):
    """Test adding combatants to battle and error if more than 2 combatants are added."""
    battle_model.prep_combatant(sample_battle2[0])

    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "popcorn"

    battle_model.prep_combatant(sample_battle2[1])

    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[1].meal == "pasta"

    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_battle2[2])

##################################################
# Battle Test Cases
##################################################
def test_get_battle_score(battle_model, sample_combatant1):
    """Test successfully retrieving the correct score"""
    score = battle_model.get_battle_score(sample_combatant1)
    difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
    assert score == (sample_combatant1.price * len(sample_combatant1.cuisine)) - difficulty_modifier[sample_combatant1.difficulty]
    ## or just assert score == 37 bc that's the result for combatant1

def test_battle(mock_update_meal_stats, mock_get_random, battle_model, sample_battle):
    """Test successfully retrieving the winner from battle."""
    combatant_1 = sample_battle[0]  # popcorn
    combatant_2 = sample_battle[1]  # pasta
    
    battle_model.prep_combatant(combatant_1)
    battle_model.prep_combatant(combatant_2)
    
    #score_1 = battle_model.get_battle_score(combatant_1)
    #score_2 = battle_model.get_battle_score(combatant_2)
    #delta = abs(score_1 - score_2) / 100
   
    #mock_get_random.return_value = delta + 0.06  
    
    winner = battle_model.battle()
    
    assert winner == combatant_2.meal
    
    mock_update_meal_stats.assert_any_call(combatant_2.id, "win")
    mock_update_meal_stats.assert_any_call(combatant_1.id, "loss")
    
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0] == combatant_2

def test_battle_not_enough_combatants(battle_model, sample_combatant1):
    """Test that battling with less than 2 combatants raises a ValueError."""
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
    
    battle_model.prep_combatant(sample_combatant1)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
