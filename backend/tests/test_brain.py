"""
Test Brain Module - Unit tests for command processing
Run with: pytest backend/tests/test_brain.py
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.core import brain


def test_get_time():
    """Test time command"""
    result = brain.process_command("what time is it")
    
    assert result["success"] is True
    assert result["intent"] == "time"
    assert ":" in result["response"]  # Should contain time like "10:30"


def test_get_date():
    """Test date command"""
    result = brain.process_command("what's the date")
    
    assert result["success"] is True
    assert result["intent"] == "date"
    assert "day" in result["response"].lower() or "202" in result["response"]


def test_empty_command():
    """Test empty input handling"""
    result = brain.process_command("")
    
    assert result["success"] is False
    assert result["intent"] == "unknown"


@patch('backend.core.brain.qwen_api')
def test_llm_fallback(mock_qwen):
    """Test LLM fallback for unknown commands"""
    # Mock Qwen responses
    mock_qwen.classify_intent.return_value = {
        "intent": "unknown",
        "params": {}
    }
    mock_qwen.chat_completion.return_value = "I'm sorry, I don't understand that."
    
    result = brain.process_command("tell me about quantum physics")
    
    assert result["intent"] == "chat"
    assert mock_qwen.classify_intent.called
    assert mock_qwen.chat_completion.called


def test_open_app_command():
    """Test open app command parsing"""
    result = brain.process_command("open chrome")
    
    assert result["intent"] == "open_app"
    assert "app_name" in result
    assert result["app_name"] == "chrome"


def test_alarm_command():
    """Test alarm command detection"""
    result = brain.process_command("set an alarm for 7 am")
    
    assert result["intent"] == "alarm"


def test_pdf_command():
    """Test PDF summarization command"""
    result = brain.process_command("summarize this pdf")
    
    assert result["intent"] == "summarize_pdf"
    assert result["success"] is False  # Should fail without file path


@patch('backend.core.brain.qwen_api')
def test_intent_classification(mock_qwen):
    """Test intent classification with Qwen"""
    # Mock Qwen to return a specific intent
    mock_qwen.classify_intent.return_value = {
        "intent": "weather",
        "params": {"location": "London"}
    }
    mock_qwen.chat_completion.return_value = "The weather in London is sunny."
    
    result = brain.process_command("what's the weather like in London")
    
    assert mock_qwen.classify_intent.called
    # Should fall back to chat since 'weather' skill not registered
    assert result["intent"] == "chat"


def test_skill_registration():
    """Test dynamic skill registration"""
    def test_skill():
        return "Test skill executed"
    
    # Register new skill
    brain.register_skill("test", test_skill)
    
    # Verify it's in the registry
    assert "test" in brain.SKILLS
    assert brain.SKILLS["test"] == test_skill
    
    # Clean up
    del brain.SKILLS["test"]


def test_list_skills():
    """Test listing available skills"""
    skills = brain.list_skills()
    
    assert isinstance(skills, list)
    assert "time" in skills
    assert "date" in skills


# ============================================================================
# INTEGRATION TESTS (require services)
# ============================================================================

@pytest.mark.integration
def test_time_command_integration():
    """Integration test - actual time command"""
    result = brain.process_command("time")
    
    assert result["success"] is True
    assert "AM" in result["response"] or "PM" in result["response"]


@pytest.mark.integration
@patch('backend.core.brain.qwen_api')
def test_full_llm_integration(mock_qwen):
    """Integration test - full LLM flow"""
    mock_qwen.classify_intent.return_value = {
        "intent": "chat",
        "params": {}
    }
    mock_qwen.chat_completion.return_value = "Hello! How can I help you?"
    
    result = brain.process_command("hello")
    
    assert result["success"] is True
    assert "Hello" in result["response"]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_qwen_api():
    """Fixture to mock Qwen API"""
    with patch('backend.core.brain.qwen_api') as mock:
        mock.classify_intent.return_value = {"intent": "unknown", "params": {}}
        mock.chat_completion.return_value = "Mock response"
        yield mock
