"""
Groq Integration Test Script
Tests all Groq components without running full server
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.config import AgentConfig
from src.agents.groq_client import GroqClient
from src.agents.runner import AgentRunner
from src.logging_config import get_logger

logger = get_logger(__name__)


async def test_groq_client():
    """Test Groq client initialization and basic functionality"""
    print("\n" + "=" * 60)
    print("TEST 1: Groq Client Initialization")
    print("=" * 60)

    try:
        client = GroqClient(
            model=AgentConfig.GROQ_MODEL,
            temperature=AgentConfig.TEMPERATURE,
            max_tokens=AgentConfig.MAX_TOKENS,
            top_p=AgentConfig.TOP_P,
            reasoning_effort=AgentConfig.REASONING_EFFORT,
        )

        print(f"✓ Groq Client initialized")
        print(f"  Model: {client.model}")
        print(f"  Temperature: {client.temperature}")
        print(f"  Max Tokens: {client.max_tokens}")
        print(f"  Reasoning Effort: {client.reasoning_effort}")
        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_agent_config():
    """Test agent configuration"""
    print("\n" + "=" * 60)
    print("TEST 2: Agent Configuration")
    print("=" * 60)

    try:
        print(f"✓ Config loaded")
        print(f"  Model: {AgentConfig.GROQ_MODEL}")
        print(f"  Temperature: {AgentConfig.TEMPERATURE}")
        print(f"  Max Tokens: {AgentConfig.MAX_TOKENS}")
        print(f"  Top P: {AgentConfig.TOP_P}")
        print(f"  Reasoning: {AgentConfig.REASONING_EFFORT}")
        print(f"  Timeout: {AgentConfig.TIMEOUT_SECONDS}s")
        print(f"  System Prompt: {AgentConfig.SYSTEM_PROMPT[:80]}...")

        tool_schema = AgentConfig.get_tool_schema()
        print(f"  Tool Schema: {len(tool_schema)} chars")

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_agent_runner():
    """Test agent runner initialization"""
    print("\n" + "=" * 60)
    print("TEST 3: Agent Runner Initialization")
    print("=" * 60)

    try:
        runner = AgentRunner()
        success = await runner.initialize_agent()

        if success and runner.groq_client:
            print(f"✓ Agent runner initialized")
            print(f"  Groq Client: {runner.groq_client.model}")
            print(f"  System Prompt: Set")
            print(f"  Tool Schema: Set")
            return True
        else:
            print(f"✗ Initialization failed")
            return False

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_message_conversion():
    """Test message format conversion"""
    print("\n" + "=" * 60)
    print("TEST 4: Message Format Conversion")
    print("=" * 60)

    try:
        runner = AgentRunner()
        await runner.initialize_agent()

        # ThreadItem format
        thread_items = [
            {
                "type": "message",
                "role": "user",
                "content": {"type": "text", "text": "Add a task to buy milk"},
            },
            {
                "type": "message",
                "role": "assistant",
                "content": {"type": "text", "text": "I'll add that for you."},
            },
        ]

        converted = runner._convert_messages(thread_items)

        print(f"✓ Messages converted")
        print(f"  Input format: ThreadItem")
        print(f"  Output format: Standard")
        print(f"  Count: {len(converted)}")

        for i, msg in enumerate(converted):
            print(
                f"  Message {i + 1}: role={msg['role']}, content_len={len(msg['content'])}"
            )

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_tool_schema():
    """Test tool schema structure"""
    print("\n" + "=" * 60)
    print("TEST 5: Tool Schema Structure")
    print("=" * 60)

    try:
        import json

        schema = AgentConfig.get_tool_schema()
        parsed = json.loads(schema)

        print(f"✓ Tool schema is valid JSON")
        print(f"  Tools defined: {len(parsed['tools'])}")

        for tool in parsed["tools"]:
            params = tool.get("params", {})
            print(f"  - {tool['name']}: {len(params)} parameters")

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_api_key():
    """Test API key availability"""
    print("\n" + "=" * 60)
    print("TEST 6: API Key Verification")
    print("=" * 60)

    try:
        import os

        key = os.getenv("GROQ_API_KEY")
        if key:
            masked = key[:10] + "..." + key[-4:]
            print(f"✓ GROQ_API_KEY found: {masked}")
            return True
        else:
            print(f"✗ GROQ_API_KEY not set in environment")
            return False

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "#" * 60)
    print("# GROQ INTEGRATION TEST SUITE")
    print("#" * 60)

    results = {
        "Groq Client": await test_groq_client(),
        "Agent Config": await test_agent_config(),
        "Agent Runner": await test_agent_runner(),
        "Message Conversion": await test_message_conversion(),
        "Tool Schema": await test_tool_schema(),
        "API Key": await test_api_key(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Groq integration is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
