import pytest
from activities import say_hi


@pytest.mark.asyncio
async def test_say_hi_even_digit():
    result = await say_hi("Hello, World-2!")
    assert result == "hi"


@pytest.mark.asyncio
async def test_say_hi_odd_digit():
    result = await say_hi("Hello, World-3!")
    assert result == "what's up"
